import time
import threading
import serial

from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, User, Product

# ---------- INIT ----------
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ---------- DB ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- SIMPLE SESSION (TEMP) ----------
current_user = {"id": None}

# ---------- ARDUINO ----------
try:
    arduino = serial.Serial("COM3", 9600, timeout=1)
    time.sleep(2)
    print("Arduino connected on COM3")
except Exception as e:
    arduino = None
    print(f"Arduino not connected: {e}")

def run_servo_open():
    """Send open signal to Arduino servo."""
    if arduino:
        try:
            arduino.write(b'O')
            print("Servo OPEN signal sent")
        except Exception as e:
            print(f"Servo open error: {e}")

def run_servo_close():
    """Send close signal to Arduino servo."""
    if arduino:
        try:
            arduino.write(b'C')
            print("Servo CLOSE signal sent")
        except Exception as e:
            print(f"Servo close error: {e}")

# ---------- FRONTEND ----------
@app.get("/", response_class=HTMLResponse)
def home():
    # FIX: always open with utf-8 encoding to avoid Windows cp1252 decode errors
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/admin", response_class=HTMLResponse)
def admin():
    if current_user["id"] != "admin":
        return RedirectResponse("/")
    with open("templates/admin.html", encoding="utf-8") as f:
        return f.read()

# ---------- AUTH ----------
@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=username).first():
        return {"error": "User already exists"}
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    return {"message": "Account created successfully"}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Admin hardcoded check
    if username == "admin" and password == "admin":
        current_user["id"] = "admin"
        return {"admin": True}

    user = db.query(User).filter_by(username=username, password=password).first()
    if user:
        current_user["id"] = user.id
        return {"message": "Logged in", "tokens": user.tokens}

    return {"error": "Invalid credentials"}

@app.get("/logout")
def logout():
    current_user["id"] = None
    return RedirectResponse("/")

# ---------- USER TOKENS ----------
@app.get("/user_tokens")
def user_tokens(db: Session = Depends(get_db)):
    if current_user["id"] is None or current_user["id"] == "admin":
        return {"tokens": 0}
    user = db.get(User, current_user["id"])
    if not user:
        return {"tokens": 0}
    return {"tokens": user.tokens}

# ---------- SERVO OPEN ----------
@app.post("/servo_open")
def servo_open():
    """Frontend calls this at start of countdown — opens the servo."""
    if current_user["id"] is None or current_user["id"] == "admin":
        return {"error": "Login required"}
    threading.Thread(target=run_servo_open, daemon=True).start()
    return {"message": "Servo opening"}

# ---------- PROCESS (close servo + award tokens) ----------
@app.post("/process")
def process(weight: float = Form(...), db: Session = Depends(get_db)):
    if current_user["id"] is None or current_user["id"] == "admin":
        return {"error": "Login required"}

    user = db.get(User, current_user["id"])
    if not user:
        return {"error": "User not found"}

    # Close servo after countdown completes
    threading.Thread(target=run_servo_close, daemon=True).start()

    # Token calculation: 10 tokens per 100g = 0.1 tokens/g = 100 tokens/kg
    # weight param is always in KG from frontend
    tokens_earned = int(round(weight * 100))
    if tokens_earned < 1:
        tokens_earned = 1  # minimum 1 token

    user.tokens += tokens_earned
    db.commit()
    db.refresh(user)

    print(f"User {user.username}: earned {tokens_earned} tokens, total {user.tokens}")

    return {
        "tokens": user.tokens,
        "session_tokens": tokens_earned,
        "message": f"Earned {tokens_earned} tokens"
    }

# ---------- PRODUCTS ----------
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [{"id": p.id, "name": p.name, "price": p.price} for p in products]

@app.post("/add_product")
def add_product(name: str = Form(...), price: int = Form(...), db: Session = Depends(get_db)):
    if current_user["id"] != "admin":
        return {"error": "Admin only"}
    p = Product(name=name, price=price)
    db.add(p)
    db.commit()
    return {"message": "Product added"}

@app.post("/buy")
def buy(product_id: int = Form(...), db: Session = Depends(get_db)):
    if current_user["id"] is None or current_user["id"] == "admin":
        return {"error": "Login required"}

    user = db.get(User, current_user["id"])
    product = db.get(Product, product_id)

    if not product:
        return {"error": "Invalid product"}
    if user.tokens < product.price:
        return {"error": "Not enough tokens"}

    user.tokens -= product.price
    db.commit()
    db.refresh(user)
    return {"message": "Purchased", "tokens": user.tokens}

# ---------- ADMIN ----------
@app.post("/delete_product")
def delete_product(id: int = Form(...), db: Session = Depends(get_db)):
    if current_user["id"] != "admin":
        return {"error": "Admin only"}
    p = db.get(Product, id)
    if p:
        db.delete(p)
        db.commit()
        return {"message": "Deleted"}
    return {"error": "Not found"}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    if current_user["id"] != "admin":
        return []
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "tokens": u.tokens} for u in users]

@app.get("/admin_stats")
def admin_stats(db: Session = Depends(get_db)):
    if current_user["id"] != "admin":
        return {"error": "Admin only"}
    total_users = db.query(User).count()
    total_products = db.query(Product).count()
    users = db.query(User).all()
    total_tokens = sum(u.tokens for u in users)
    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_tokens": total_tokens
    }