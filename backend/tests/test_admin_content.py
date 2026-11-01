"""后台草稿、排序、产品图和改密码。用临时数据库，不碰本机 company.db。"""

import os
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp(prefix="rxweb-admin-")
os.environ["RXWEB_DB"] = str(Path(_tmp) / "company.db")
os.environ["RXWEB_MEDIA_DIR"] = str(Path(_tmp) / "media")
os.environ["RXWEB_ADMIN_EMAIL"] = "admin@test.com"
os.environ["RXWEB_ADMIN_PASS"] = "rxweb123"
os.environ["SITE_ID"] = "aierde"
os.environ["SMTP_HOST"] = ""

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
)


def _data(resp):
    body = resp.json()
    assert body["code"] == 0, body
    return body["data"]


def test_draft_sort_image_and_password():
    with TestClient(app) as client:
        login = _data(client.post("/api/auth/login", json={"email": "admin@test.com", "password": "rxweb123"}))
        headers = {"Authorization": f"Bearer {login['token']}"}

        created = _data(client.post("/api/news", headers=headers, json={
            "title": "草稿新闻",
            "date": "2026-11-01",
            "source": "测试",
            "summary": "摘要",
            "content": "正文",
            "status": "draft",
        }))
        news_id = created["id"]

        public = _data(client.get("/api/news"))
        assert all(item["id"] != news_id for item in public["list"])
        hidden = client.get(f"/api/news/{news_id}").json()
        assert hidden["code"] == 404

        admin_list = _data(client.get("/api/news", headers=headers, params={"status": "draft"}))
        assert any(item["id"] == news_id and item["status"] == "draft" for item in admin_list["list"])
        detail = _data(client.get(f"/api/news/{news_id}", headers=headers))
        assert detail["content"] == "正文"

        _data(client.put(f"/api/news/{news_id}", headers=headers, json={
            "title": "草稿新闻",
            "date": "2026-11-01",
            "source": "测试",
            "summary": "摘要",
            "content": "正文",
            "status": "published",
        }))
        public = _data(client.get("/api/news", params={"keyword": "草稿新闻"}))
        assert any(item["id"] == news_id for item in public["list"])

        later = _data(client.post("/api/products", headers=headers, json={
            "name": "靠后的产品",
            "price": "面议",
            "category": " 护理防护耗材 ",
            "description": "说明",
            "sort_order": 50,
        }))
        earlier = _data(client.post("/api/products", headers=headers, json={
            "name": "靠前的产品",
            "price": "12",
            "category": "护理防护耗材",
            "description": "说明",
            "sort_order": 1,
        }))
        products = _data(client.get("/api/products"))
        ids = [item["id"] for item in products]
        assert ids.index(earlier["id"]) < ids.index(later["id"])
        assert later["category"] == "护理防护耗材"

        uploaded = _data(client.post(
            "/api/media/products",
            headers=headers,
            files={"file": ("a.png", PNG, "image/png")},
        ))
        assert uploaded["url"].startswith("/media/products/")
        assert client.get(uploaded["url"]).status_code == 200
        names = _data(client.get("/api/media/products", headers=headers))["list"]
        item = next(row for row in names if row["url"] == uploaded["url"])
        assert item["deletable"] is True

        _data(client.put(f"/api/products/{earlier['id']}", headers=headers, json={
            "name": "靠前的产品",
            "price": "12",
            "category": "护理防护耗材",
            "description": "说明",
            "image": uploaded["url"],
            "sort_order": 1,
        }))
        blocked = client.delete(f"/api/media/products/{item['name']}", headers=headers).json()
        assert blocked["code"] == 400

        shipped = client.delete("/api/media/products/mask-care.png", headers=headers).json()
        assert shipped["code"] == 400

        _data(client.delete(f"/api/products/{earlier['id']}", headers=headers))
        _data(client.delete(f"/api/media/products/{item['name']}", headers=headers))
        assert client.get(uploaded["url"]).status_code == 404

        huge = b"\xff\xd8\xff" + b"0" * (2 * 1024 * 1024)
        too_big = client.post(
            "/api/media/products",
            headers=headers,
            files={"file": ("a.jpg", huge, "image/jpeg")},
        ).json()
        assert too_big["code"] == 400
        bad = client.post(
            "/api/media/products",
            headers=headers,
            files={"file": ("a.txt", b"hello", "text/plain")},
        ).json()
        assert bad["code"] == 400

        message = _data(client.post("/api/messages", json={
            "name": "访客",
            "email": "guest@example.com",
            "subject": "询价",
            "content": "请问有货吗",
        }))
        replied = _data(client.put(
            f"/api/messages/{message['id']}/reply",
            headers=headers,
            json={"reply": "有现货"},
        ))
        assert replied["email_status"] == "skipped"

        wrong = client.post("/api/auth/change-password", headers=headers, json={
            "old_password": "nope",
            "new_password": "newpass1",
        }).json()
        assert wrong["code"] == 400
        _data(client.post("/api/auth/change-password", headers=headers, json={
            "old_password": "rxweb123",
            "new_password": "newpass1",
        }))
        again = _data(client.post("/api/auth/login", json={"email": "admin@test.com", "password": "newpass1"}))
        assert again["role"] == "admin"


if __name__ == "__main__":
    test_draft_sort_image_and_password()
    print("ok")
