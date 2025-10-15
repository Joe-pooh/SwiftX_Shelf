# 上下架系统（Phase 1）— 云端 + 登录认证

**前端**：静态 HTML/JS（单页），**登录后可用**；4 个功能板块拆成独立 JS 模块。  
**后端**：FastAPI（JWT 登录 + bcrypt 密码）；默认 **SQLite**，支持 Postgres。  
**二维码打印**：`/qr.png?text=...` 由后端生成 PNG（无需外链 CDN）。  
**部署**：自带 GitHub Pages 工作流（自动识别 `frontend/` 或 `docs/`）。

---

## 本地启动
### 后端（默认 SQLite）
```bash
cd backend
pip install -r requirements.txt
# 环境变量（首次可不设置，默认 admin/admin & 本地SQLite）
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=admin
set JWT_SECRET=change_me
set DB_URL=sqlite:///./shelf.db
python -m app.main
# API: http://localhost:8000
```

### 前端
```bash
cd frontend
python -m http.server 5173
# 打开 http://localhost:5173
# 页面顶部把“后端地址”设为 http://localhost:8000 点“保存”
```

---

## 云端部署
- **前端**：推到 GitHub，启用 Pages（本仓库内含 Actions workflow）。
- **后端**：任意平台（Render/Railway/Fly.io/VPS）。设置环境变量：
  - `DB_URL`：Postgres 或 SQLite 连接串（例：`postgresql://user:pass@host:5432/db` 或 `sqlite:///./shelf.db`）
  - `ADMIN_USERNAME`、`ADMIN_PASSWORD`：首次启动自动创建管理员
  - `JWT_SECRET`：随机长字符串
- **统一域名（可选）**：Nginx 前端 `/`，后端 `/api` 反代；前端默认后端地址用 `location.origin + '/api'`。

---

## API（认证 + 核心）
- Auth：
  - `POST /auth/login` { username, password } → 返回 token（也写入 cookie）
  - `POST /auth/logout`
  - `GET /auth/me`
- 受保护（需 Bearer token 或 cookie）：
  - `POST /bins` { code }
  - `POST /packages` { tracking }
  - `POST /putaway` { bin_code, tracking }
  - `POST /pick` { tracking }
  - `GET /packages/{tracking}`
  - `GET /export/scan_logs` → CSV
- 工具：
  - `GET /qr.png?text=...&size=256` → PNG 二维码

**表结构**：`users`、`bins`、`packages`、`scan_logs`。

---

## 四个功能板块（前端拆分的 JS 文件）
- `js/putaway.js`：上架
- `js/pick.js`：下架/拣选
- `js/dashboard.js`：看板/导出
- `js/printbins.js`：库位码打印（后端生成二维码）

> 后续你要扩展时，直接在对应 JS 文件里迭代即可。
