# Shelfing System MVP (Phase 1)

Minimal, **independent** web system for parcel putaway / pick / dashboard.
- Backend: **FastAPI + PostgreSQL** (Docker Compose)
- Frontend: **Static HTML + JS** (no build step). Can be hosted on **GitHub Pages** or any static host.
- Scan-friendly: works with **keyboard-wedge scanners**; camera scanning can be added later.
- Print bin QR codes from the frontend page.

## Quick Start (Dev)

### 1) Start DB + Backend
```bash
docker compose up --build
# Backend: http://localhost:8000  (Docs: http://localhost:8000/docs)
# Postgres: localhost:5432 (app/app, db=shelf)
```

### 2) Open Frontend
Open `frontend/index.html` directly in your browser, or serve statically:
```bash
# Option A: open the file directly (file://). Some browsers restrict fetch; prefer a static server:
# Option B: Python simple server
cd frontend
python -m http.server 5173
# visit http://localhost:5173
```

> If you host the frontend on GitHub Pages, set `BACKEND_BASE` in `frontend/index.html` to your deployed backend URL.

---

## Deploy Notes

- **Frontend**: push `/frontend` to GitHub and enable GitHub Pages (main branch / `frontend` folder or root of a `gh-pages` branch).  
- **Backend**: deploy the FastAPI image to your provider (e.g., Fly.io, Render, Railway, a VPS, or on-prem). Set env `DB_URL` accordingly.
- **GitHub**: use Issues/Projects for tasks; PRs for change control; Actions for CI/CD.

---

## API (Phase 1)
- `POST /bins` { code }
- `POST /packages` { tracking }
- `POST /putaway` { bin_code, tracking } → status `STORED`, logs action
- `POST /pick` { tracking } → status `PICKED`, logs action
- `GET /packages/{tracking}`
- `GET /export/scan_logs` → CSV

Auth/roles, tasks, wave picking, offline/PWA, etc. are phase‑2+.

---

## Database (tables)
- **bins**(code PK)
- **packages**(tracking PK, status, bin_code, first_in_at, last_scan_at)
- **scan_logs**(id, ts, user, action, tracking, from_bin, to_bin, ok, reason)

---

## Why static frontend?
- You can **edit all content on GitHub**, host on GitHub Pages, and keep backend deploy separate.
- No Node build needed for MVP. Later you can replace with React/Vite easily.

Enjoy!
