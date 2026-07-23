# Amazon Clone — SQLite Version: How to Run & Test

MongoDB has been completely removed. Everything now lives in one file:
`backend/db.sqlite3` (created automatically the first time you run migrations).
No MongoDB install, no separate database container, nothing else to set up.

---

## Part 1 — Run it locally (no Docker)

### Backend
```
cd "AC project d4v10/backend"
python -m venv venv
venv\Scripts\activate          (Windows)   or   source venv/bin/activate   (Mac/Linux)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Leave this terminal open.

### Frontend (new terminal)
```
cd "AC project d4v10/frontend"
npm install
npm run dev
```
Open the printed `http://localhost:5173` link.

That's it — no MongoDB, no MongoDB Compass, no separate service to start.

---

## Part 2 — Run it with Docker Compose

The compose file no longer has a `mongodb` service (it's not needed anymore):
```
docker compose -f Docker-compose.yaml up --build
```
Backend → `http://localhost:8000`, Frontend → `http://localhost:3000`.

**Data now persists automatically.** `Docker-compose.yaml` mounts a volume at
`backend/data` (where `db.sqlite3` now lives) and the backend's Dockerfile
runs `migrate` on every startup, so `docker compose up --build` no longer
wipes your sellers/products/accounts — only that one data folder is
persisted, and your actual code always comes fresh from the image on
rebuild. (Don't be tempted to mount the whole `/app` as the volume instead —
that would shadow your code with whatever was there the first time the
volume was created, so code changes would stop taking effect until you
deleted the volume.)

For Minikube/Kubernetes, the same idea applies: mount a PersistentVolume at
`/app/data` in the pod spec so the SQLite file survives pod restarts —
ask me for the manifest when you get to that stage.

After first startup (locally or in a container), always run once:
```
python manage.py createsuperuser
```
to get a SuperAdmin account.

---

## Part 3 — Full test checklist

Same flow as before, all verified working against real SQLite in my own test run (not just guessed):

1. **Customer**: `/register` → create account
2. **Seller**: `/seller/register` → fill form → lands on dashboard, "pending" status
3. Seller adds a product → confirm it does **not** show on `/shop`
4. **Admin**: register via `/admin/register` (grants real admin rights automatically now) → `/admin/panel` → Sellers tab → **Mark as verified**
5. Back on `/shop` → product now appears
6. Click the product → real detail page loads → **Add to Cart** / **Buy Now** both work
7. `/cart` → **Proceed to Checkout** → fill shipping → **Cash on Delivery** → Place Order
8. Lands on `/orders` with a green "Order placed successfully" banner, order listed below
9. `/help` → submit a query (as customer) → log in as the seller → Seller Dashboard → Customer Queries tab → reply → log in as admin → Queries tab → reply/escalate/resolve
10. As Admin: **Flag** a seller/product/customer (never a direct remove)
11. Log in as your **SuperAdmin** (the `createsuperuser` account) → "🚩 Flagged" tab appears → **Remove permanently**

If anything errors, check the Django terminal for the actual traceback (it'll be much shorter/clearer now — no more MongoDB connection errors possible) and send it to me.
