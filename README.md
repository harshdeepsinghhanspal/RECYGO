# ♻️ RecyGo — Smart Recycling Reward System

RecyGo is a web-based recycling reward platform built with FastAPI. Users sign up, log in, photograph their recyclable item, enter its weight, and submit it — earning tokens based on weight. Those tokens can be redeemed for products in a built-in shop. An optional Arduino integration can control a physical bin lid servo if hardware is present, but the app works fully without it.

---

## 📸 Features

- **User authentication** — Sign up / log in with persistent accounts
- **Multi-step recycling flow** — Material selection → camera capture → weight entry → 10s countdown → token reward
- **Token economy** — 100 tokens awarded per kg of recyclable waste
- **Reward shop** — Redeem tokens for products configured by the admin
- **Admin dashboard** — Manage products, view all users and token balances, see platform stats
- **Optional Arduino support** — If an Arduino is connected on `COM3`, a servo can open/close a bin lid during the countdown

---

## 🗂️ Project Structure

```
recygo/
├── main.py           # FastAPI backend — all routes and business logic
├── models.py         # SQLAlchemy ORM models (User, Product)
├── database.py       # DB engine and session setup (SQLite)
├── recygo.db         # SQLite database (auto-created on first run)
├── recygo.ino        # (Optional) Arduino sketch for servo control
└── templates/
    ├── index.html    # Main user-facing UI
    └── admin.html    # Admin dashboard
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI |
| Database | SQLite · SQLAlchemy |
| Frontend | Vanilla HTML / CSS / JS |
| Serial (optional) | PySerial · Arduino |

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.9+

### 1. Clone the repository

```bash
git clone https://github.com/your-username/recygo.git
cd recygo
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy pyserial
```

> `pyserial` is only needed if you plan to use Arduino. The app runs fine without it if you remove the serial block in `main.py`.

### 3. Run the server

```bash
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🔑 Admin Access

The admin account is hardcoded:

- **Username:** `admin`
- **Password:** `admin`

> ⚠️ Change this before any public deployment.

The admin panel is at [http://localhost:8000/admin](http://localhost:8000/admin).

---

## 🪙 Token Calculation

```
tokens = weight_in_kg × 100
```

Minimum of **1 token** is always awarded. Weight can be entered in grams or kilograms — the UI handles the conversion automatically.

---

## 🔁 Recycling Flow

```
Login → Select Material → Capture Photos (up to 3)
     → Enter Weight → 10s Countdown → Tokens Awarded → Redeem in Shop
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/signup` | Create a new user account |
| `POST` | `/login` | Log in |
| `GET` | `/logout` | Log out |
| `GET` | `/user_tokens` | Get current user's token balance |
| `POST` | `/servo_open` | Open bin lid (Arduino only, no-op if not connected) |
| `POST` | `/process` | Close lid + award tokens based on weight |
| `GET` | `/products` | List all redeemable products |
| `POST` | `/buy` | Purchase a product with tokens |
| `POST` | `/add_product` | *(Admin)* Add a new product |
| `POST` | `/delete_product` | *(Admin)* Delete a product |
| `GET` | `/users` | *(Admin)* List all users |
| `GET` | `/admin_stats` | *(Admin)* Platform stats |

---

## ⚠️ Known Limitations

- Session management uses a simple global variable (`current_user`) — not suitable for concurrent multi-user access. Replace with proper cookies or JWT for production.
- Passwords are stored in plaintext. Hash with `bcrypt` before real deployment.
- Admin credentials are hardcoded in `main.py`.

---

## 🚀 Future Improvements

- [ ] Hashed passwords & proper auth (JWT / sessions)
- [ ] Material classification using an ML model on captured photos
- [ ] Token transaction history per user
- [ ] QR code or receipt after each recycling session
- [ ] Docker support for easy deployment

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
