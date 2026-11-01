from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import secrets
import traceback

from app.auth import (
    create_token,
    find_user_by_email,
    get_current_user,
    hash_password,
    hash_token,
    optional_admin,
    require_admin,
    require_user,
    user_payload,
    verify_password,
)
from app.db import connect, init_schema
from app.mail import public_base_url, send_email
from app.media_store import (
    clean_image_url,
    delete_uploaded_product_image,
    list_product_image_names,
    resolve_media_file,
    save_product_image,
    uploaded_product_path,
)
from app.oplog import write_log


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_schema()
    yield


SITE_NAME = (os.environ.get("SITE_NAME") or os.environ.get("RXWEB_SITE_NAME") or "官网").strip() or "官网"

app = FastAPI(
    title=f"{SITE_NAME}-官网API",
    description=f"{SITE_NAME}官方网站的后端API服务。",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))


class LoginIn(BaseModel):
    email: str = ""
    username: str = ""
    password: str


class RegisterIn(BaseModel):
    email: str
    password: str
    name: str = ""


class ForgotPasswordIn(BaseModel):
    email: str


class ResetPasswordIn(BaseModel):
    token: str
    password: str


class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str


class NewsIn(BaseModel):
    title: str
    date: str
    source: str
    summary: str
    content: str
    status: str = "published"


class ProductIn(BaseModel):
    name: str
    price: str
    category: str
    image: str = ""
    description: str = ""
    sort_order: Optional[int] = None


class MessageIn(BaseModel):
    name: str
    email: str
    subject: str
    content: str


class MessageReplyIn(BaseModel):
    reply: str


def standard_response(data=None, code=0, message="ok"):
    return {"code": code, "message": message, "data": data}


def row_to_product(row):
    sort_order = row["sort_order"] if "sort_order" in row.keys() else row["id"]
    return {
        "id": str(row["id"]),
        "name": str(row["name"] or ""),
        "price": str(row["price"] or ""),
        "category": str(row["category"] or ""),
        "image": str(row["image"] or ""),
        "description": str(row["description"] or ""),
        "sort_order": int(row["id"] if sort_order is None else sort_order),
    }


def news_status(row) -> str:
    if "status" not in row.keys():
        return "published"
    value = row["status"] or ""
    return value if value in ("draft", "published") else "published"


def row_to_news(row, include_content=False):
    item = {
        "id": row["id"],
        "title": row["title"],
        "date": row["date"],
        "source": row["source"],
        "summary": row["summary"],
        "status": news_status(row),
    }
    if include_content:
        item["content"] = row["content"]
    return item


def published_clause(column="status") -> str:
    return f"COALESCE(NULLIF({column}, ''), 'published') = 'published'"


def normalize_news_status(value: str) -> str:
    return value if value in ("draft", "published") else ""


def prepare_product(product: ProductIn, conn, product_id: Optional[int] = None):
    name = product.name.strip()
    price = product.price.strip()
    category = product.category.strip()
    description = (product.description or "").strip()
    if not name or not price or not category or not description:
        return None, "请填写名称、价格、分类和描述"
    try:
        image = clean_image_url(product.image)
    except ValueError as exc:
        return None, str(exc)
    if product.sort_order is None:
        if product_id is not None:
            current = conn.execute("SELECT sort_order FROM products WHERE id = ?", (product_id,)).fetchone()
            sort_order = int(current["sort_order"]) if current and current["sort_order"] is not None else product_id
        else:
            sort_order = int(conn.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM products").fetchone()[0])
    else:
        sort_order = int(product.sort_order)
        if sort_order < 0 or sort_order > 999999:
            return None, "排序请填 0 到 999999"
    return {
        "name": name,
        "price": price,
        "category": category,
        "image": image,
        "description": description,
        "sort_order": sort_order,
    }, ""


def row_to_message(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "subject": row["subject"],
        "content": row["content"],
        "created_at": row["created_at"],
        "status": row["status"],
        "reply": row["reply"],
        "replied_at": row["replied_at"],
    }


@app.get("/")
def read_root():
    index_file = os.path.join(DIST_DIR, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)
    return {"message": f"欢迎访问{SITE_NAME}后端API"}


@app.post("/api/auth/login")
def login(payload: LoginIn, request: Request):
    email = (payload.email or payload.username or "").strip()
    if not email or not payload.password:
        return standard_response(code=400, message="请输入邮箱和密码")
    row = find_user_by_email(email)
    if not row or not verify_password(payload.password, row["password_hash"]):
        write_log(
            "login_fail",
            username=email,
            target_type="auth",
            detail="登录失败：邮箱或密码错误",
            result="fail",
            request=request,
        )
        return standard_response(code=401, message="邮箱或密码错误")
    user = user_payload(row)
    token = create_token(user["email"], user["role"], user["name"])
    write_log(
        "login_success",
        username=user["email"],
        target_type="auth",
        detail=f"{'管理员' if user['role'] == 'admin' else '用户'}登录成功",
        request=request,
    )
    return standard_response({"token": token, **user})


@app.post("/api/auth/register")
def register(payload: RegisterIn, request: Request):
    email = payload.email.strip()
    name = (payload.name or "").strip() or email.split("@")[0]
    if "@" not in email or "." not in email.split("@")[-1]:
        return standard_response(code=400, message="请输入有效邮箱")
    if len(payload.password) < 6:
        return standard_response(code=400, message="密码至少 6 位")
    if find_user_by_email(email):
        return standard_response(code=400, message="该邮箱已注册")
    conn = connect()
    conn.execute(
        "INSERT INTO users (email, password_hash, name, role, created_at) VALUES (?, ?, ?, 'user', ?)",
        (email, hash_password(payload.password), name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()
    write_log("register", username=email, target_type="auth", detail="用户注册", request=request)
    row = find_user_by_email(email)
    user = user_payload(row)
    token = create_token(user["email"], user["role"], user["name"])
    return standard_response({"token": token, **user})


@app.post("/api/auth/forgot-password")
def forgot_password(payload: ForgotPasswordIn, request: Request):
    email = payload.email.strip()
    row = find_user_by_email(email)
    reset_url = ""
    emailed = False
    if row:
        raw = secrets.token_urlsafe(32)
        expires = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        conn = connect()
        conn.execute(
            "UPDATE users SET reset_token = ?, reset_expires = ? WHERE id = ?",
            (hash_token(raw), expires, row["id"]),
        )
        conn.commit()
        conn.close()
        reset_url = f"{public_base_url(request)}/reset-password?token={raw}"
        emailed = send_email(
            email,
            f"{SITE_NAME} - 重置密码",
            f"您好，请在 1 小时内打开以下链接重置密码：\n\n{reset_url}\n\n如果不是您本人操作，请忽略此邮件。",
        )
        write_log(
            "password_reset_request",
            username=email,
            target_type="auth",
            detail="申请重置密码" + ("，邮件已发送" if emailed else "，邮件未发送"),
            request=request,
        )
    data = {"emailed": emailed}
    if reset_url and not emailed:
        data["reset_url"] = reset_url
    return standard_response(data, message="如果该邮箱已注册，将收到重置说明")


@app.post("/api/auth/reset-password")
def reset_password(payload: ResetPasswordIn, request: Request):
    if len(payload.password) < 6:
        return standard_response(code=400, message="密码至少 6 位")
    digest = hash_token(payload.token.strip())
    conn = connect()
    row = conn.execute(
        "SELECT id, email, reset_expires FROM users WHERE reset_token = ?",
        (digest,),
    ).fetchone()
    if not row:
        conn.close()
        return standard_response(code=400, message="重置链接无效或已过期")
    try:
        expires = datetime.strptime(row["reset_expires"] or "", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        expires = datetime.min
    if expires < datetime.now():
        conn.close()
        return standard_response(code=400, message="重置链接无效或已过期")
    conn.execute(
        "UPDATE users SET password_hash = ?, reset_token = NULL, reset_expires = NULL WHERE id = ?",
        (hash_password(payload.password), row["id"]),
    )
    conn.commit()
    conn.close()
    write_log("password_reset", username=row["email"], target_type="auth", detail="密码已重置", request=request)
    return standard_response({"message": "密码已重置，请使用新密码登录"})


@app.post("/api/auth/logout")
def logout(request: Request, user: dict = Depends(require_user)):
    write_log("logout", username=user["email"], target_type="auth", detail="退出登录", request=request)
    return standard_response({"message": "已退出"})


@app.get("/api/auth/me")
def auth_me(user: dict = Depends(require_user)):
    return standard_response(user)


@app.post("/api/auth/change-password")
def change_password(payload: ChangePasswordIn, request: Request, user: dict = Depends(require_user)):
    if len(payload.new_password) < 6:
        return standard_response(code=400, message="新密码至少 6 位")
    row = find_user_by_email(user["email"])
    if not row or not verify_password(payload.old_password, row["password_hash"]):
        return standard_response(code=400, message="当前密码不正确")
    conn = connect()
    conn.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (hash_password(payload.new_password), row["id"]),
    )
    conn.commit()
    conn.close()
    write_log("password_change", username=user["email"], target_type="auth", detail="修改了登录密码", request=request)
    return standard_response({"message": "密码已更新"})


@app.get("/api/news")
def get_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    admin: Optional[dict] = Depends(optional_admin),
):
    conn = connect()
    filters = []
    params = []
    visible = status if admin and status in ("all", "draft", "published") else "published"
    if visible == "draft":
        filters.append("status = 'draft'")
    elif visible == "published":
        filters.append(published_clause())
    if keyword is not None and keyword.strip() != "":
        filters.append("(title LIKE ? OR summary LIKE ? OR source LIKE ?)")
        kw = f"%{keyword.strip()}%"
        params.extend([kw, kw, kw])
    if source is not None and source.strip() != "":
        filters.append("source = ?")
        params.append(source.strip())
    where = (" WHERE " + " AND ".join(filters)) if filters else ""
    sql = "SELECT id, title, date, source, summary, status FROM news" + where
    sql += " ORDER BY date DESC, id DESC LIMIT ? OFFSET ?"
    rows = conn.execute(sql, [*params, page_size, (page - 1) * page_size]).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM news" + where, params).fetchone()[0]
    conn.close()
    return standard_response({
        "list": [row_to_news(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@app.get("/api/news/{news_id}")
def get_news_detail(news_id: int, admin: Optional[dict] = Depends(optional_admin)):
    conn = connect()
    row = conn.execute(
        "SELECT id, title, date, source, summary, content, status FROM news WHERE id = ?",
        (news_id,),
    ).fetchone()
    conn.close()
    if not row or (news_status(row) == "draft" and not admin):
        return standard_response(code=404, message="未找到该新闻")
    return standard_response(row_to_news(row, include_content=True))


@app.post("/api/news")
def create_news(news: NewsIn, request: Request, user: dict = Depends(require_admin)):
    status = normalize_news_status(news.status)
    if not status:
        return standard_response(code=400, message="状态只能是草稿或已发布")
    try:
        conn = connect()
        cur = conn.execute(
            "INSERT INTO news (title, date, source, summary, content, status) VALUES (?, ?, ?, ?, ?, ?)",
            (news.title, news.date, news.source, news.summary, news.content, status),
        )
        conn.commit()
        news_id = cur.lastrowid
        conn.close()
        write_log(
            "news_create",
            username=user["email"],
            target_type="news",
            target_id=news_id,
            detail=f"新增新闻《{news.title}》",
            request=request,
        )
        return standard_response({"id": news_id, **news.dict(), "status": status})
    except Exception as e:
        traceback.print_exc()
        write_log(
            "news_create",
            username=user["email"],
            target_type="news",
            detail=f"新增新闻失败：{e}",
            result="fail",
            request=request,
        )
        return standard_response(code=500, message="新增新闻API异常", data=str(e))


@app.put("/api/news/{news_id}")
def update_news(news_id: int, news: NewsIn, request: Request, user: dict = Depends(require_admin)):
    status = normalize_news_status(news.status)
    if not status:
        return standard_response(code=400, message="状态只能是草稿或已发布")
    try:
        conn = connect()
        conn.execute(
            "UPDATE news SET title=?, date=?, source=?, summary=?, content=?, status=? WHERE id=?",
            (news.title, news.date, news.source, news.summary, news.content, status, news_id),
        )
        conn.commit()
        conn.close()
        write_log(
            "news_update",
            username=user["email"],
            target_type="news",
            target_id=news_id,
            detail=f"编辑新闻《{news.title}》",
            request=request,
        )
        return standard_response({"id": news_id, **news.dict(), "status": status})
    except Exception as e:
        traceback.print_exc()
        write_log(
            "news_update",
            username=user["email"],
            target_type="news",
            target_id=news_id,
            detail=f"编辑新闻失败：{e}",
            result="fail",
            request=request,
        )
        return standard_response(code=500, message="编辑新闻API异常", data=str(e))


@app.delete("/api/news/{news_id}")
def delete_news(news_id: int, request: Request, user: dict = Depends(require_admin)):
    try:
        conn = connect()
        row = conn.execute("SELECT title FROM news WHERE id=?", (news_id,)).fetchone()
        title = row["title"] if row else ""
        conn.execute("DELETE FROM news WHERE id=?", (news_id,))
        conn.commit()
        conn.close()
        write_log(
            "news_delete",
            username=user["email"],
            target_type="news",
            target_id=news_id,
            detail=f"删除新闻《{title or news_id}》",
            request=request,
        )
        return standard_response({"message": "删除成功"})
    except Exception as e:
        traceback.print_exc()
        write_log(
            "news_delete",
            username=user["email"],
            target_type="news",
            target_id=news_id,
            detail=f"删除新闻失败：{e}",
            result="fail",
            request=request,
        )
        return standard_response(code=500, message="删除新闻API异常", data=str(e))


@app.get("/api/products")
def get_products(keyword: Optional[str] = Query(None)):
    try:
        conn = connect()
        sql = "SELECT id, name, price, category, image, description, sort_order FROM products"
        params = []
        if keyword and keyword.strip():
            sql += " WHERE name LIKE ? OR category LIKE ? OR description LIKE ?"
            kw = f"%{keyword.strip()}%"
            params.extend([kw, kw, kw])
        sql += " ORDER BY sort_order ASC, id ASC"
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return standard_response([row_to_product(row) for row in rows])
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": "产品列表API异常", "detail": str(e)})


@app.get("/api/products/{product_id}")
def get_product_detail(product_id: int):
    try:
        conn = connect()
        row = conn.execute(
            "SELECT id, name, price, category, image, description, sort_order FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        conn.close()
        if not row:
            return JSONResponse(status_code=404, content={"message": "未找到该产品"})
        return standard_response(row_to_product(row))
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": "产品详情API异常", "detail": str(e)})


@app.post("/api/products")
def create_product(product: ProductIn, request: Request, user: dict = Depends(require_admin)):
    conn = connect()
    fields, error = prepare_product(product, conn)
    if error:
        conn.close()
        return standard_response(code=400, message=error)
    cur = conn.execute(
        "INSERT INTO products (name, price, category, image, description, sort_order) VALUES (?, ?, ?, ?, ?, ?)",
        (fields["name"], fields["price"], fields["category"], fields["image"], fields["description"], fields["sort_order"]),
    )
    conn.commit()
    product_id = cur.lastrowid
    conn.close()
    write_log(
        "product_create",
        username=user["email"],
        target_type="product",
        target_id=product_id,
        detail=f"新增产品《{product.name}》",
        request=request,
    )
    return standard_response({"id": str(product_id), **fields})


@app.put("/api/products/{product_id}")
def update_product(product_id: int, product: ProductIn, request: Request, user: dict = Depends(require_admin)):
    conn = connect()
    fields, error = prepare_product(product, conn, product_id)
    if error:
        conn.close()
        return standard_response(code=400, message=error)
    conn.execute(
        "UPDATE products SET name=?, price=?, category=?, image=?, description=?, sort_order=? WHERE id=?",
        (fields["name"], fields["price"], fields["category"], fields["image"], fields["description"], fields["sort_order"], product_id),
    )
    conn.commit()
    conn.close()
    write_log(
        "product_update",
        username=user["email"],
        target_type="product",
        target_id=product_id,
        detail=f"编辑产品《{product.name}》",
        request=request,
    )
    return standard_response({"id": str(product_id), **fields})


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, request: Request, user: dict = Depends(require_admin)):
    conn = connect()
    row = conn.execute("SELECT name FROM products WHERE id=?", (product_id,)).fetchone()
    name = row["name"] if row else ""
    conn.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    write_log(
        "product_delete",
        username=user["email"],
        target_type="product",
        target_id=product_id,
        detail=f"删除产品《{name or product_id}》",
        request=request,
    )
    return standard_response({"message": "删除成功"})


@app.post("/api/messages")
def create_message(message: MessageIn, request: Request):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    email = message.email.strip()
    name = message.name.strip()
    auth = request.headers.get("authorization")
    if auth:
        try:
            current = get_current_user(auth)
            email = current["email"]
            name = current["name"] or name
        except HTTPException:
            pass
    conn = connect()
    cur = conn.execute(
        """
        INSERT INTO messages (name, email, subject, content, created_at, status)
        VALUES (?, ?, ?, ?, ?, 'pending')
        """,
        (name, email, message.subject.strip(), message.content.strip(), created_at),
    )
    conn.commit()
    message_id = cur.lastrowid
    conn.close()
    write_log(
        "message_create",
        username=message.name.strip(),
        target_type="message",
        target_id=message_id,
        detail=f"访客留言《{message.subject.strip()}》",
        request=request,
    )
    return standard_response({"id": message_id, "created_at": created_at})


@app.get("/api/messages")
def list_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    _user: dict = Depends(require_admin),
):
    conn = connect()
    sql = "SELECT * FROM messages"
    params = []
    if status in ("pending", "replied"):
        sql += " WHERE status = ?"
        params.append(status)
    sql += " ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?"
    params.extend([page_size, (page - 1) * page_size])
    rows = conn.execute(sql, params).fetchall()
    count_sql = "SELECT COUNT(*) FROM messages"
    count_params = []
    if status in ("pending", "replied"):
        count_sql += " WHERE status = ?"
        count_params.append(status)
    total = conn.execute(count_sql, count_params).fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'pending'").fetchone()[0]
    conn.close()
    return standard_response({
        "list": [row_to_message(row) for row in rows],
        "total": total,
        "pending": pending,
        "page": page,
        "page_size": page_size,
    })


@app.put("/api/messages/{message_id}/reply")
def reply_message(message_id: int, payload: MessageReplyIn, request: Request, user: dict = Depends(require_admin)):
    reply = payload.reply.strip()
    if not reply:
        return standard_response(code=400, message="回复内容不能为空")
    conn = connect()
    row = conn.execute("SELECT id, name, email, subject FROM messages WHERE id = ?", (message_id,)).fetchone()
    if not row:
        conn.close()
        return standard_response(code=404, message="未找到该留言")
    replied_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE messages SET reply = ?, replied_at = ?, status = 'replied' WHERE id = ?",
        (reply, replied_at, message_id),
    )
    conn.commit()
    subject = row["subject"]
    visitor_name = row["name"]
    visitor_email = row["email"]
    conn.close()
    smtp_ready = bool(os.environ.get("SMTP_HOST", "").strip())
    email_status = "skipped"
    if smtp_ready:
        account_url = f"{public_base_url(request)}/account"
        sent = send_email(
            visitor_email,
            f"{SITE_NAME}已回复您的留言",
            (
                f"{visitor_name}，您好：\n\n"
                f"您在{SITE_NAME}的留言「{subject}」已有回复：\n\n"
                f"{reply}\n\n"
                f"也可登录网站，在「我的留言」中查看：\n{account_url}\n"
            ),
        )
        email_status = "sent" if sent else "failed"
    write_log(
        "message_reply",
        username=user["email"],
        target_type="message",
        target_id=message_id,
        detail=f"回复留言《{subject}》" + {"sent": "，已发邮件", "failed": "，邮件发送失败", "skipped": ""}[email_status],
        request=request,
    )
    return standard_response({
        "id": message_id,
        "reply": reply,
        "replied_at": replied_at,
        "status": "replied",
        "email_status": email_status,
    })


@app.get("/api/my/messages")
def my_messages(user: dict = Depends(require_user)):
    conn = connect()
    rows = conn.execute(
        "SELECT * FROM messages WHERE lower(email) = lower(?) ORDER BY created_at DESC, id DESC",
        (user["email"],),
    ).fetchall()
    conn.close()
    return standard_response({"list": [row_to_message(row) for row in rows]})


@app.get("/api/logs")
def list_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    _user: dict = Depends(require_admin),
):
    conn = connect()
    sql = "SELECT * FROM operation_logs"
    params = []
    if keyword and keyword.strip():
        sql += " WHERE username LIKE ? OR action LIKE ? OR detail LIKE ? OR ip LIKE ?"
        kw = f"%{keyword.strip()}%"
        params.extend([kw, kw, kw, kw])
    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([page_size, (page - 1) * page_size])
    rows = conn.execute(sql, params).fetchall()
    count_sql = "SELECT COUNT(*) FROM operation_logs"
    count_params = []
    if keyword and keyword.strip():
        count_sql += " WHERE username LIKE ? OR action LIKE ? OR detail LIKE ? OR ip LIKE ?"
        count_params.extend([kw, kw, kw, kw])
    total = conn.execute(count_sql, count_params).fetchone()[0]
    conn.close()
    return standard_response({
        "list": [dict(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@app.get("/api/media/products")
def list_product_images(_user: dict = Depends(require_admin)):
    conn = connect()
    used = {
        str(row["image"] or "")
        for row in conn.execute("SELECT image FROM products").fetchall()
    }
    conn.close()
    items = []
    for name in list_product_image_names():
        url = f"/media/products/{name}"
        path = uploaded_product_path(name)
        items.append({
            "name": name,
            "url": url,
            "used": url in used,
            "deletable": bool(path and os.path.isfile(path) and url not in used),
        })
    return standard_response({"list": items})


@app.post("/api/media/products")
async def upload_product_image(
    request: Request,
    file: UploadFile = File(...),
    user: dict = Depends(require_admin),
):
    data = await file.read(2 * 1024 * 1024 + 1)
    try:
        name = save_product_image(data)
    except ValueError as exc:
        return standard_response(code=400, message=str(exc))
    url = f"/media/products/{name}"
    write_log(
        "media_upload",
        username=user["email"],
        target_type="media",
        detail=f"上传产品图 {name}",
        request=request,
    )
    return standard_response({"name": name, "url": url})


@app.delete("/api/media/products/{name}")
def delete_product_image(name: str, request: Request, user: dict = Depends(require_admin)):
    url = f"/media/products/{name}"
    conn = connect()
    used = conn.execute("SELECT id FROM products WHERE image = ?", (url,)).fetchone()
    conn.close()
    if used:
        return standard_response(code=400, message="仍有产品在使用这张图片，不能删除")
    try:
        delete_uploaded_product_image(name)
    except ValueError as exc:
        return standard_response(code=400, message=str(exc))
    write_log(
        "media_delete",
        username=user["email"],
        target_type="media",
        detail=f"删除未使用的产品图 {name}",
        request=request,
    )
    return standard_response({"message": "已删除"})


@app.get("/media/{file_path:path}")
def serve_media(file_path: str):
    found = resolve_media_file(file_path)
    if not found:
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(found)


if os.path.isdir(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        reserved = ("api/", "docs", "redoc", "openapi.json")
        if full_path.startswith("api/") or full_path in reserved:
            raise HTTPException(status_code=404, detail="Not Found")
        candidate = os.path.abspath(os.path.join(DIST_DIR, full_path))
        dist_prefix = DIST_DIR if DIST_DIR.endswith(os.sep) else DIST_DIR + os.sep
        if candidate.startswith(dist_prefix) and os.path.isfile(candidate):
            return FileResponse(candidate)
        index_file = os.path.join(DIST_DIR, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Not Found")
