from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import Optional

app = FastAPI(title="Creator Gig Marketplace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gigs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_name TEXT,
            title TEXT,
            category TEXT,
            rate REAL,
            description TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gig_id INTEGER,
            client_name TEXT,
            client_email TEXT,
            requirements TEXT,
            status TEXT DEFAULT 'Pending',
            rejection_reason TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class GigCreate(BaseModel):
    creator_name: str
    title: str
    category: str
    rate: float
    description: str

class BookingCreate(BaseModel):
    gig_id: int
    client_name: str
    client_email: str
    requirements: str

class BookingStatusUpdate(BaseModel):
    status: str
    rejection_reason: Optional[str] = None

@app.get("/")
def root():
    return {"status": "Marketplace API operational"}

@app.post("/api/gigs")
def post_gig(gig: GigCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO gigs (creator_name, title, category, rate, description) VALUES (?, ?, ?, ?, ?)",
        (gig.creator_name, gig.title, gig.category, gig.rate, gig.description)
    )
    conn.commit()
    gig_id = cursor.lastrowid
    conn.close()
    return {"id": gig_id, "message": "Gig posted successfully"}

@app.get("/api/gigs")
def get_gigs(category: Optional[str] = None, search: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM gigs WHERE 1=1"
    params = []
    
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
        
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    gigs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return gigs

@app.post("/api/bookings")
def book_gig(booking: BookingCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bookings (gig_id, client_name, client_email, requirements) VALUES (?, ?, ?, ?)",
        (booking.gig_id, booking.client_name, booking.client_email, booking.requirements)
    )
    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()
    return {"id": booking_id, "status": "Pending", "message": "Booking request submitted"}

@app.get("/api/creator/bookings")
def get_creator_bookings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, g.title as gig_title, g.rate 
        FROM bookings b 
        JOIN gigs g ON b.gig_id = g.id 
        ORDER BY b.id DESC
    """)
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bookings

@app.patch("/api/bookings/{booking_id}")
def update_booking_status(booking_id: int, update: BookingStatusUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bookings SET status = ?, rejection_reason = ? WHERE id = ?",
        (update.status, update.rejection_reason, booking_id)
    )
    conn.commit()
    conn.close()
    return {"message": f"Booking status updated to {update.status}"}

@app.get("/api/client/bookings")
def get_client_bookings(client_name: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    query = """
        SELECT b.*, g.title as gig_title, g.creator_name, g.rate, g.category 
        FROM bookings b 
        JOIN gigs g ON b.gig_id = g.id 
    """
    params = []
    if client_name:
        query += " WHERE b.client_name = ?"
        params.append(client_name)
    query += " ORDER BY b.id DESC"
    
    cursor.execute(query, params)
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bookings