# Ubuntu / 宝塔 部署与运行

适合：阿里云等 Ubuntu 服务器，网站目录常用 `/www/wwwroot/`。瑞学调试机端口是 **8001**，页面和 `/api` 在同一个端口。生产地址和端口先留空。

Windows 请用 [07_Windows部署与运行.md](./07_Windows部署与运行.md)。从本机直接发布到某一家公司的目录：

```powershell
pwsh -File .\deploy\deploy.ps1 -Site ruixue
```

每家公司的调试机、生产机地址和端口在 `deploy/sites/<站点>/site.env`。生产项为空时，加 `-Target prod` 会直接停下，不会连接服务器。

## 1. 服务器先装基础软件

用 SSH 登录（宝塔「终端」也可以），执行：

```bash
apt update
apt install -y python3 python3-venv python3-pip unzip
```

若你的 zip **里面已经有** `frontend/dist/index.html`，**可以不装 Node**。

若 zip 里只有前端源码、没有 dist，则还要安装 Node.js（宝塔：软件商店 → Node.js 版本管理器）。

## 2. 上传 zip（注意真实路径）

在 Windows 打好 `RxWeb-deploy.zip`（见 [06_打包方法.md](./06_打包方法.md)），用宝塔文件管理上传。

常见位置是：

```text
/www/wwwroot/RxWeb-deploy.zip
```

**不要**假设它在 `/tmp/`。以你在服务器上 `ls` 看到的为准。

## 3. 解压（这是上次失败的原因）

上次失败是因为：zip 在 `/www/wwwroot/`，命令却去解 `/tmp/RxWeb-deploy.zip`，并且还没有 `RxWeb` 目录。

正确做法：

```bash
mkdir -p /www/wwwroot/RxWeb
unzip -o /www/wwwroot/RxWeb-deploy.zip -d /www/wwwroot/RxWeb
ls /www/wwwroot/RxWeb
```

`ls` 必须能看到 `start.sh` 和 `backend`。如果看到多套了一层文件夹，进入那一层，确认 `start.sh` 的**真实路径**，后面命令改成那个路径。

Windows 换行符修复（建议每次更新脚本都做一次）：

```bash
sed -i 's/\r$//' /www/wwwroot/RxWeb/start.sh
```

## 4. 一条命令启动（后台）

```bash
bash /www/wwwroot/RxWeb/start.sh --daemon
```

浏览器访问：`http://你的服务器公网IP:8001`

停止 / 状态：

```bash
bash /www/wwwroot/RxWeb/start.sh --stop
bash /www/wwwroot/RxWeb/start.sh --status
```

日志：`/www/wwwroot/RxWeb/logs/rxweb.log`

前台调试（关掉 SSH 会停止，仅适合当场看报错）：

```bash
bash /www/wwwroot/RxWeb/start.sh
```

## 5. 防火墙与安全组（打不开网页时优先查）

要同时放行 **8001**：

1. 云厂商控制台：安全组入方向 TCP 8001
2. 宝塔：安全 → 防火墙 → 放行 8001
3. 若开了 `ufw`：`ufw allow 8001/tcp`

以前用过 8080 时，先 `bash /www/wwwroot/RxWeb/start.sh --stop`，换新脚本后再 `--daemon`。瑞学调试机放行 **8001** 即可。

## 6. 可选：开机自启（systemd）

项目里的 `rxweb.service` 给熟悉 Linux 服务的人用。先保证第 4 步能手动跑通，再考虑。

```bash
# 按实际用户修改 User=www（宝塔常用 www）
cp /www/wwwroot/RxWeb/rxweb.service /etc/systemd/system/rxweb.service
# 先用启动脚本创建好 .venv 和 dist
bash /www/wwwroot/RxWeb/start.sh --daemon
bash /www/wwwroot/RxWeb/start.sh --stop
systemctl daemon-reload
systemctl enable --now rxweb
systemctl status rxweb
```

`rxweb.service` 假定虚拟环境已在 `/www/wwwroot/RxWeb/.venv`，监听 **8001**。若网站目录不是这个路径，要改服务文件里的路径。若以前按 8080 装过 systemd，覆盖 `rxweb.service` 后再 `systemctl daemon-reload && systemctl restart rxweb`。

## 7. 常见错误对照

| 现象 | 原因 | 处理 |
|------|------|------|
| `No such file or directory` 指向 `start.sh` | 还没解压，或路径不对 | `ls` 找到真正的 `start.sh` |
| `unzip: cannot find or open /tmp/...` | zip 不在 `/tmp` | 改成 zip 的真实路径 |
| `bad interpreter` 或 `$'\r'` | Windows 换行符 | `sed -i 's/\r$//' start.sh` |
| 只有 JSON 欢迎语 | 没有 `frontend/dist` | 本机构建后重传 dist，或服务器装 Node 后 `--rebuild` |
| 浏览器超时 | 安全组 / 宝塔防火墙没放行 8001 | 见第 5 节 |
| 虚拟环境报错 | 把 Windows 的 `backend/venv` 传上来了 | 删掉它，让 `start.sh` 生成 `.venv` |

## 8. 以后改代码如何更新

1. Windows 重新打包并上传 zip
2. `unzip -o` 覆盖代码（小心不要误覆盖要保留的 `company.db`）
3. `bash .../start.sh --stop` 再 `--daemon`

数据在 `company.db`，更新代码前先复制一份备份。
