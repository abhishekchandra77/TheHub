"""
Creator Gig Marketplace API
Code2Career AI Hackathon 2026 - Track 2
Full backend: gigs, orders, deliverables, reviews, messages, notifications.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

app = FastAPI(
    title="Creator Gig Marketplace API",
    description="Code2Career AI Hackathon 2026 - Track 2",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).resolve().parent / "database.db"

ORDER_STATUSES = [
    "Pending", "Accepted", "In Progress", "Delivered",
    "Revision Requested", "Completed", "Declined", "Cancelled",
]

CREATOR_TRANSITIONS = {
    "Pending": {"Accepted", "Declined"},
    "Accepted": {"In Progress", "Cancelled"},
    "In Progress": {"Delivered"},
    "Revision Requested": {"In Progress", "Delivered"},
}
CLIENT_TRANSITIONS = {
    "Pending": {"Cancelled"},
    "Accepted": {"Cancelled"},
    "Delivered": {"Completed", "Revision Requested"},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def add_column_if_missing(cursor, table: str, column: str, definition: str):
    cols = {row[1] for row in cursor.execute(f"PRAGMA table_info({table})")}
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS gigs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_name TEXT NOT NULL,
            owner_email TEXT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            rate REAL NOT NULL,
            description TEXT NOT NULL,
            deliverables TEXT DEFAULT '',
            delivery_time TEXT DEFAULT '',
            skills TEXT DEFAULT '',
            thumbnail_url TEXT DEFAULT '',
            status TEXT DEFAULT 'Active',
            views INTEGER DEFAULT 0,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gig_id INTEGER NOT NULL,
            client_email TEXT NOT NULL,
            client_name TEXT NOT NULL,
            creator_email TEXT,
            requirements TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            rejection_reason TEXT,
            delivery_date TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (gig_id) REFERENCES gigs(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deliverables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            file_url TEXT DEFAULT '',
            uploaded_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL UNIQUE,
            gig_id INTEGER NOT NULL,
            client_email TEXT NOT NULL,
            client_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            sender_email TEXT NOT NULL,
            receiver_email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            read_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_email TEXT NOT NULL,
            notification_type TEXT NOT NULL,
            message TEXT NOT NULL,
            related_type TEXT,
            related_id INTEGER,
            is_read INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS saved_gigs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gig_id INTEGER NOT NULL,
            client_email TEXT NOT NULL,
            UNIQUE(gig_id, client_email),
            FOREIGN KEY (gig_id) REFERENCES gigs(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS creator_profiles (
            creator_email TEXT PRIMARY KEY,
            creator_name TEXT NOT NULL,
            username TEXT DEFAULT '',
            bio TEXT DEFAULT '',
            skills TEXT DEFAULT '',
            categories TEXT DEFAULT '',
            portfolio TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            updated_at TEXT NOT NULL
        )
    """)

    # Legacy migrations (safe on existing DBs)
    for col, ddl in [
        ("owner_email", "TEXT"),
        ("status", "TEXT DEFAULT 'Active'"),
        ("deliverables", "TEXT DEFAULT ''"),
        ("delivery_time", "TEXT DEFAULT ''"),
        ("skills", "TEXT DEFAULT ''"),
        ("views", "INTEGER DEFAULT 0"),
        ("rating", "REAL DEFAULT 0"),
        ("review_count", "INTEGER DEFAULT 0"),
        ("thumbnail_url", "TEXT DEFAULT ''"),
        ("created_at", "TEXT"),
    ]:
        add_column_if_missing(cur, "gigs", col, ddl)

    cur.execute(
        "UPDATE gigs SET owner_email = 'creator@thehub.com' "
        "WHERE owner_email IS NULL AND LOWER(creator_name) = 'alex rivera'"
    )
    cur.execute(
        "UPDATE gigs SET created_at = COALESCE(created_at, ?) WHERE created_at IS NULL",
        (now_iso(),),
    )
    conn.commit()

    if cur.execute("SELECT COUNT(*) FROM gigs").fetchone()[0] == 0:
        seed_gigs(cur)
        conn.commit()

    conn.close()


def seed_gigs(cur):
    samples = [
        ("Alex Rivera", "creator@thehub.com",
         "High-Converting TikTok & Reels UGC Video Ads", "Video & UGC", 95.0,
         "Authentic, engaging user-generated content filmed in 4K. Includes hook ideation, caption scripts, and licensed trending audio.",
         "3 short-form videos, 2 hooks each, raw + edited files, 2 revisions", "3 days",
         "TikTok, Reels, Shorts, UGC, Scriptwriting"),
        ("Maya Chen", "maya@thehub.com",
         "Viral YouTube Thumbnails & Complete Branding Kit", "Design & Graphics", 45.0,
         "Custom 3D-rendered facial expressions, high-contrast typography, and CTR-tested layout guaranteed to lift your impressions.",
         "3 thumbnail concepts, brand kit, source Figma file", "2 days",
         "Figma, Photoshop, Branding, Thumbnails"),
        ("Dev Patel", "dev@thehub.com",
         "Custom AI Automation Workflow (Zapier / Make / OpenAI)", "Tech & AI", 120.0,
         "Automate customer lead capture, email nurturing, and AI summarization without touching complex code. Includes 3 revisions.",
         "Working automation, documentation, 3 revisions", "5 days",
         "Zapier, Make, OpenAI, Python"),
        ("Sarah Jenkins", "sarah@thehub.com",
         "SEO-Optimized Tech & Founder Newsletters", "Writing & Translation", 60.0,
         "Deeply researched, entertaining newsletters tailored for Substack and Beehiiv readers. Boosts open rates with killer subject lines.",
         "1 long-form newsletter, 3 subject line options", "4 days",
         "SEO, Copywriting, Substack, Beehiiv"),
        ("Marcus Brody", "marcus@thehub.com",
         "Podcast Audio Cleanup & Multi-Platform Social Clips", "Video & UGC", 80.0,
         "Turn 1 hour raw audio/video into crystal-clear masters plus 5 vertical shorts with animated subtitles and sound effects.",
         "1 audio master, 5 vertical shorts, subtitle file", "2 days",
         "Audacity, Premiere Pro, Captions"),
        ("Elena Rostova", "elena@thehub.com",
         "Full-Stack MVP Landing Page in Streamlit / FastAPI", "Tech & AI", 150.0,
         "Rapid interactive prototype deployed to cloud in 48 hours. Clean modern UI, responsive controls, and documented backend API.",
         "Deployed app, source code, deployment guide", "4 days",
         "Streamlit, FastAPI, Python, SQLite"),
    ]
    cur.executemany(
        """INSERT INTO gigs
        (creator_name, owner_email, title, category, rate, description,
         deliverables, delivery_time, skills, status, views, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', 0, ?)""",
        [(*row[:9], now_iso()) for row in samples],
    )


init_db()


# ---------------- Pydantic models ----------------

class GigCreate(BaseModel):
    creator_name: str = Field(..., min_length=1)
    owner_email: Optional[str] = None
    title: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    rate: float = Field(..., gt=0)
    description: str = Field(..., min_length=1)
    deliverables: str = ""
    delivery_time: str = ""
    skills: str = ""
    thumbnail_url: str = ""
    status: str = "Active"


class GigUpdate(BaseModel):
    owner_email: str = Field(..., min_length=3)
    creator_name: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None
    rate: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    deliverables: Optional[str] = None
    delivery_time: Optional[str] = None
    skills: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: Optional[str] = None


class OrderCreate(BaseModel):
    gig_id: int
    client_name: str = Field(..., min_length=1)
    client_email: str = Field(..., min_length=3)
    requirements: str = Field(..., min_length=1)
    delivery_date: Optional[str] = None
    amount: Optional[float] = None


class OrderStatusUpdate(BaseModel):
    actor_email: str = Field(..., min_length=3)
    actor_role: str = Field(..., pattern="^(creator|client)$")
    status: str
    rejection_reason: Optional[str] = None


class DeliverableCreate(BaseModel):
    creator_email: str = Field(..., min_length=3)
    title: str = Field(..., min_length=1)
    description: str = ""
    file_url: str = ""


class ReviewCreate(BaseModel):
    client_email: str = Field(..., min_length=3)
    client_name: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)
    comment: str = ""


class MessageCreate(BaseModel):
    sender_email: str = Field(..., min_length=3)
    receiver_email: str = Field(..., min_length=3)
    message: str = Field(..., min_length=1)
    order_id: Optional[int] = None


class CreatorProfileUpdate(BaseModel):
    creator_email: str = Field(..., min_length=3)
    creator_name: str = Field(..., min_length=1)
    username: str = ""
    bio: str = ""
    skills: str = ""
    categories: str = ""
    portfolio: str = ""
    avatar_url: str = ""


# ---------------- Helpers ----------------

def create_notification(cur, recipient_email, ntype, message, rtype, rid):
    if not recipient_email:
        return
    cur.execute(
        """INSERT INTO notifications
        (recipient_email, notification_type, message, related_type, related_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (recipient_email.strip().lower(), ntype, message, rtype, rid, now_iso()),
    )


def order_row(cur, order_id):
    cur.execute(
        """SELECT o.*, g.title AS gig_title, g.category, g.creator_name,
                  g.delivery_time, g.thumbnail_url
           FROM orders o JOIN gigs g ON g.id = o.gig_id
           WHERE o.id = ?""",
        (order_id,),
    )
    row = cur.fetchone()
    return dict(row) if row else None


def recompute_gig_rating(cur, gig_id):
    cur.execute(
        "SELECT AVG(rating) AS r, COUNT(*) AS c FROM reviews WHERE gig_id = ?",
        (gig_id,),
    )
    row = cur.fetchone()
    avg = round(row["r"] or 0, 2)
    cnt = row["c"] or 0
    cur.execute("UPDATE gigs SET rating = ?, review_count = ? WHERE id = ?", (avg, cnt, gig_id))


# ---------------- Routes ----------------

@app.get("/")
def root():
    return {
        "status": "Marketplace API operational",
        "service": "Creator Gig Marketplace",
        "version": "2.0.0",
        "hackathon": "Code2Career 2026",
    }


@app.get("/api/stats")
def get_stats():
    conn = get_db()
    cur = conn.cursor()
    total_gigs = cur.execute("SELECT COUNT(*) AS c FROM gigs").fetchone()["c"]
    total_orders = cur.execute("SELECT COUNT(*) AS c FROM orders").fetchone()["c"]
    pending = cur.execute("SELECT COUNT(*) AS c FROM orders WHERE status='Pending'").fetchone()["c"]
    completed = cur.execute("SELECT COUNT(*) AS c FROM orders WHERE status='Completed'").fetchone()["c"]
    volume = cur.execute(
        "SELECT COALESCE(SUM(amount),0) AS v FROM orders WHERE status IN ('Accepted','In Progress','Delivered','Completed')"
    ).fetchone()["v"]
    creators = cur.execute(
        "SELECT COUNT(DISTINCT LOWER(owner_email)) AS c FROM gigs WHERE owner_email IS NOT NULL"
    ).fetchone()["c"]
    conn.close()
    return {
        "total_gigs": total_gigs,
        "total_orders": total_orders,
        "pending_orders": pending,
        "completed_orders": completed,
        "total_volume": round(volume, 2),
        "creators": creators,
    }


# Gigs

@app.get("/api/gigs")
def list_gigs(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("newest", pattern="^(newest|cheapest|priciest|rating)$"),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    conn = get_db()
    cur = conn.cursor()
    q = "SELECT * FROM gigs WHERE status = 'Active'"
    params = []
    if category and category != "All":
        q += " AND category = ?"
        params.append(category)
    if search:
        q += " AND (title LIKE ? OR description LIKE ? OR creator_name LIKE ? OR skills LIKE ?)"
        w = f"%{search.strip()}%"
        params.extend([w, w, w, w])
    if sort_by == "cheapest":
        q += " ORDER BY rate ASC, id DESC"
    elif sort_by == "priciest":
        q += " ORDER BY rate DESC, id DESC"
    elif sort_by == "rating":
        q += " ORDER BY rating DESC, review_count DESC, id DESC"
    else:
        q += " ORDER BY id DESC"
    q += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    cur.execute(q, params)
    gigs = [dict(r) for r in cur.fetchall()]
    conn.close()
    return gigs


@app.get("/api/gigs/{gig_id}")
def get_gig(gig_id: int):
    conn = get_db()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM gigs WHERE id = ?", (gig_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, detail=f"Gig with ID {gig_id} not found")
    cur.execute("UPDATE gigs SET views = COALESCE(views,0) + 1 WHERE id = ?", (gig_id,))
    conn.commit()
    row = cur.execute("SELECT * FROM gigs WHERE id = ?", (gig_id,)).fetchone()
    conn.close()
    return dict(row)


@app.post("/api/gigs", status_code=201)
def create_gig(gig: GigCreate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO gigs
        (creator_name, owner_email, title, category, rate, description,
         deliverables, delivery_time, skills, thumbnail_url, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            gig.creator_name.strip(),
            gig.owner_email.strip().lower() if gig.owner_email else None,
            gig.title.strip(),
            gig.category.strip(),
            float(gig.rate),
            gig.description.strip(),
            gig.deliverables.strip(),
            gig.delivery_time.strip(),
            gig.skills.strip(),
            gig.thumbnail_url.strip(),
            gig.status,
            now_iso(),
        ),
    )
    conn.commit()
    gid = cur.lastrowid
    conn.close()
    return {"id": gid, "message": "Gig posted successfully"}


@app.patch("/api/gigs/{gig_id}")
def update_gig(gig_id: int, update: GigUpdate):
    conn = get_db()
    cur = conn.cursor()
    existing = cur.execute("SELECT * FROM gigs WHERE id = ?", (gig_id,)).fetchone()
    if not existing or not existing["owner_email"] or existing["owner_email"].lower() != update.owner_email.strip().lower():
        conn.close()
        raise HTTPException(404, detail="Gig not found for this creator")
    fields = {
        "creator_name": update.creator_name,
        "title": update.title,
        "category": update.category,
        "rate": update.rate,
        "description": update.description,
        "deliverables": update.deliverables,
        "delivery_time": update.delivery_time,
        "skills": update.skills,
        "thumbnail_url": update.thumbnail_url,
        "status": update.status,
    }
    changes = [(k, v) for k, v in fields.items() if v is not None]
    if changes:
        clause = ", ".join(f"{k} = ?" for k, _ in changes)
        cur.execute(
            f"UPDATE gigs SET {clause} WHERE id = ? AND LOWER(owner_email) = LOWER(?)",
            [v for _, v in changes] + [gig_id, update.owner_email.strip()],
        )
        conn.commit()
    row = cur.execute("SELECT * FROM gigs WHERE id = ?", (gig_id,)).fetchone()
    conn.close()
    return dict(row)


@app.delete("/api/gigs/{gig_id}")
def delete_gig(gig_id: int, owner_email: str):
    conn = get_db()
    cur = conn.cursor()
    owned = cur.execute(
        "SELECT id FROM gigs WHERE id = ? AND LOWER(owner_email) = LOWER(?)",
        (gig_id, owner_email.strip()),
    ).fetchone()
    if not owned:
        conn.close()
        raise HTTPException(404, detail="Gig not found for this creator")
    cur.execute("DELETE FROM saved_gigs WHERE gig_id = ?", (gig_id,))
    cur.execute("DELETE FROM deliverables WHERE order_id IN (SELECT id FROM orders WHERE gig_id = ?)", (gig_id,))
    cur.execute("DELETE FROM reviews WHERE gig_id = ?", (gig_id,))
    cur.execute("DELETE FROM orders WHERE gig_id = ?", (gig_id,))
    cur.execute("DELETE FROM gigs WHERE id = ?", (gig_id,))
    conn.commit()
    conn.close()
    return {"message": "Gig deleted", "id": gig_id}


@app.get("/api/creator/gigs")
def creator_gigs(creator_email: str, limit: int = Query(100, ge=1, le=100)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM gigs WHERE LOWER(owner_email) = LOWER(?) ORDER BY id DESC LIMIT ?",
        (creator_email.strip(), limit),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# Orders

@app.post("/api/orders", status_code=201)
def create_order(order: OrderCreate):
    conn = get_db()
    cur = conn.cursor()
    gig = cur.execute("SELECT * FROM gigs WHERE id = ?", (order.gig_id,)).fetchone()
    if not gig:
        conn.close()
        raise HTTPException(404, detail=f"Gig ID {order.gig_id} does not exist.")
    amount = float(order.amount) if order.amount else float(gig["rate"])
    cur.execute(
        """INSERT INTO orders
        (gig_id, client_email, client_name, creator_email, requirements, amount,
         status, delivery_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?, ?, ?)""",
        (
            order.gig_id,
            order.client_email.strip().lower(),
            order.client_name.strip(),
            (gig["owner_email"] or "").lower(),
            order.requirements.strip(),
            amount,
            order.delivery_date,
            now_iso(),
            now_iso(),
        ),
    )
    oid = cur.lastrowid
    if gig["owner_email"]:
        create_notification(
            cur, gig["owner_email"], "ORDER",
            f"New order #{oid} for '{gig['title']}' from {order.client_name}",
            "order", oid,
        )
    conn.commit()
    conn.close()
    return {"id": oid, "status": "Pending"}


# Backwards-compatible alias
@app.post("/api/bookings", status_code=201)
def create_booking(order: OrderCreate):
    return create_order(order)


@app.get("/api/orders")
def list_orders(
    actor_email: str,
    actor_role: str = Query(..., pattern="^(creator|client)$"),
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=200),
):
    conn = get_db()
    cur = conn.cursor()
    where = []
    params = []
    if actor_role == "creator":
        where.append("(LOWER(o.creator_email) = LOWER(?) OR LOWER(g.owner_email) = LOWER(?))")
        params.extend([actor_email.strip(), actor_email.strip()])
    else:
        where.append("LOWER(o.client_email) = LOWER(?)")
        params.append(actor_email.strip())
    if status:
        where.append("o.status = ?")
        params.append(status)
    q = f"""SELECT o.*, g.title AS gig_title, g.category, g.creator_name,
                   g.thumbnail_url, g.delivery_time
            FROM orders o JOIN gigs g ON g.id = o.gig_id
            WHERE {' AND '.join(where)}
            ORDER BY o.id DESC LIMIT ?"""
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.get("/api/orders/{order_id}")
def get_order(order_id: int):
    conn = get_db()
    cur = conn.cursor()
    row = order_row(cur, order_id)
    if not row:
        conn.close()
        raise HTTPException(404, detail="Order not found")
    cur.execute("SELECT * FROM deliverables WHERE order_id = ? ORDER BY id ASC", (order_id,))
    row["deliverables"] = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT * FROM reviews WHERE order_id = ?", (order_id,))
    review = cur.fetchone()
    row["review"] = dict(review) if review else None
    conn.close()
    return row


@app.patch("/api/orders/{order_id}/status")
def update_order_status(order_id: int, update: OrderStatusUpdate):
    conn = get_db()
    cur = conn.cursor()
    order = cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        raise HTTPException(404, detail="Order not found")

    # Authorization
    actor = update.actor_email.strip().lower()
    if update.actor_role == "creator":
        if (order["creator_email"] or "").lower() != actor:
            conn.close()
            raise HTTPException(403, detail="Not your order")
        allowed = CREATOR_TRANSITIONS.get(order["status"], set())
    else:
        if order["client_email"].lower() != actor:
            conn.close()
            raise HTTPException(403, detail="Not your order")
        allowed = CLIENT_TRANSITIONS.get(order["status"], set())

    target = update.status
    if target not in ORDER_STATUSES:
        conn.close()
        raise HTTPException(400, detail="Invalid status")
    if target not in allowed:
        conn.close()
        raise HTTPException(400, detail=f"Cannot move {order['status']} -> {target} as {update.actor_role}")

    cur.execute(
        "UPDATE orders SET status = ?, rejection_reason = ?, updated_at = ? WHERE id = ?",
        (target, update.rejection_reason, now_iso(), order_id),
    )

    # Notify the other party
    other = order["client_email"] if update.actor_role == "creator" else order["creator_email"]
    if other:
        create_notification(
            cur, other, "ORDER_STATUS",
            f"Order #{order_id} is now {target}.",
            "order", order_id,
        )
    conn.commit()
    result = order_row(cur, order_id)
    conn.close()
    return result


@app.post("/api/orders/{order_id}/deliverables", status_code=201)
def add_deliverable(order_id: int, deliverable: DeliverableCreate):
    conn = get_db()
    cur = conn.cursor()
    order = cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        raise HTTPException(404, detail="Order not found")
    if (order["creator_email"] or "").lower() != deliverable.creator_email.strip().lower():
        conn.close()
        raise HTTPException(403, detail="Not your order")
    cur.execute(
        """INSERT INTO deliverables (order_id, title, description, file_url, uploaded_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (
            order_id, deliverable.title.strip(), deliverable.description.strip(),
            deliverable.file_url.strip(), deliverable.creator_email.strip().lower(), now_iso(),
        ),
    )
    did = cur.lastrowid
    if order["client_email"]:
        create_notification(
            cur, order["client_email"], "DELIVERABLE",
            f"New work uploaded for order #{order_id}: {deliverable.title}",
            "order", order_id,
        )
    conn.commit()
    conn.close()
    return {"id": did, "message": "Deliverable uploaded"}


@app.get("/api/orders/{order_id}/deliverables")
def list_deliverables(order_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM deliverables WHERE order_id = ? ORDER BY id ASC", (order_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.post("/api/orders/{order_id}/review", status_code=201)
def create_review(order_id: int, review: ReviewCreate):
    conn = get_db()
    cur = conn.cursor()
    order = cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        raise HTTPException(404, detail="Order not found")
    if order["client_email"].lower() != review.client_email.strip().lower():
        conn.close()
        raise HTTPException(403, detail="Not your order")
    if order["status"] != "Completed":
        conn.close()
        raise HTTPException(400, detail="You can only review completed orders")
    existing = cur.execute("SELECT id FROM reviews WHERE order_id = ?", (order_id,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(400, detail="You already reviewed this order")
    cur.execute(
        """INSERT INTO reviews (order_id, gig_id, client_email, client_name, rating, comment, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            order_id, order["gig_id"], review.client_email.strip().lower(),
            review.client_name.strip(), int(review.rating), review.comment.strip(), now_iso(),
        ),
    )
    recompute_gig_rating(cur, order["gig_id"])
    if order["creator_email"]:
        create_notification(
            cur, order["creator_email"], "REVIEW",
            f"New {review.rating}-star review on order #{order_id}",
            "gig", order["gig_id"],
        )
    conn.commit()
    conn.close()
    return {"message": "Review submitted"}


@app.get("/api/gigs/{gig_id}/reviews")
def get_gig_reviews(gig_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reviews WHERE gig_id = ? ORDER BY id DESC", (gig_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.get("/api/creator/reviews")
def get_creator_reviews(creator_email: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """SELECT r.*, g.title AS gig_title
           FROM reviews r JOIN gigs g ON g.id = r.gig_id
           WHERE LOWER(g.owner_email) = LOWER(?) ORDER BY r.id DESC""",
        (creator_email.strip(),),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# Saved gigs

@app.get("/api/client/saved-gigs")
def get_saved_gigs(client_email: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """SELECT g.* FROM saved_gigs s JOIN gigs g ON g.id = s.gig_id
           WHERE LOWER(s.client_email) = LOWER(?) ORDER BY s.id DESC""",
        (client_email.strip(),),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.post("/api/client/saved-gigs/{gig_id}", status_code=201)
def save_gig(gig_id: int, client_email: str):
    conn = get_db()
    cur = conn.cursor()
    if not cur.execute("SELECT id FROM gigs WHERE id = ?", (gig_id,)).fetchone():
        conn.close()
        raise HTTPException(404, detail="Gig not found")
    cur.execute(
        "INSERT OR IGNORE INTO saved_gigs (gig_id, client_email) VALUES (?, ?)",
        (gig_id, client_email.strip().lower()),
    )
    conn.commit()
    conn.close()
    return {"message": "Saved", "gig_id": gig_id}


@app.delete("/api/client/saved-gigs/{gig_id}")
def unsave_gig(gig_id: int, client_email: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM saved_gigs WHERE gig_id = ? AND LOWER(client_email) = LOWER(?)",
        (gig_id, client_email.strip()),
    )
    conn.commit()
    conn.close()
    return {"message": "Removed", "gig_id": gig_id}


# Messages

@app.get("/api/messages")
def get_messages(user_email: str, order_id: Optional[int] = None, limit: int = Query(100, ge=1, le=200)):
    conn = get_db()
    cur = conn.cursor()
    q = """SELECT * FROM messages
           WHERE (LOWER(sender_email) = LOWER(?) OR LOWER(receiver_email) = LOWER(?))"""
    params = [user_email.strip(), user_email.strip()]
    if order_id is not None:
        q += " AND order_id = ?"
        params.append(order_id)
    q += " ORDER BY id ASC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.post("/api/messages", status_code=201)
def post_message(message: MessageCreate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO messages (order_id, sender_email, receiver_email, message, created_at)
        VALUES (?, ?, ?, ?, ?)""",
        (
            message.order_id,
            message.sender_email.strip().lower(),
            message.receiver_email.strip().lower(),
            message.message.strip(),
            now_iso(),
        ),
    )
    mid = cur.lastrowid
    create_notification(
        cur, message.receiver_email, "MESSAGE",
        f"New message from {message.sender_email}", "message", mid,
    )
    conn.commit()
    conn.close()
    return {"id": mid}


# Notifications

@app.get("/api/notifications")
def get_notifications(recipient_email: str, limit: int = Query(50, ge=1, le=200)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM notifications WHERE LOWER(recipient_email) = LOWER(?) ORDER BY id DESC LIMIT ?",
        (recipient_email.strip(), limit),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.patch("/api/notifications/{notification_id}/read")
def mark_read(notification_id: int, recipient_email: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE notifications SET is_read = 1 WHERE id = ? AND LOWER(recipient_email) = LOWER(?)",
        (notification_id, recipient_email.strip()),
    )
    conn.commit()
    conn.close()
    return {"id": notification_id, "is_read": True}


# Creator profile + dashboard

@app.get("/api/creator/profile")
def get_creator_profile(creator_email: str, creator_name: str = ""):
    conn = get_db()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT * FROM creator_profiles WHERE LOWER(creator_email) = LOWER(?)",
        (creator_email.strip(),),
    ).fetchone()
    if not row:
        cur.execute(
            """INSERT INTO creator_profiles (creator_email, creator_name, username, updated_at)
            VALUES (?, ?, ?, ?)""",
            (
                creator_email.strip().lower(),
                creator_name.strip() or creator_email.split("@")[0],
                creator_email.split("@")[0],
                now_iso(),
            ),
        )
        conn.commit()
        row = cur.execute(
            "SELECT * FROM creator_profiles WHERE LOWER(creator_email) = LOWER(?)",
            (creator_email.strip(),),
        ).fetchone()
    result = dict(row)
    conn.close()
    return result


@app.put("/api/creator/profile")
def update_creator_profile(profile: CreatorProfileUpdate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO creator_profiles
        (creator_email, creator_name, username, bio, skills, categories, portfolio, avatar_url, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(creator_email) DO UPDATE SET
            creator_name=excluded.creator_name,
            username=excluded.username,
            bio=excluded.bio,
            skills=excluded.skills,
            categories=excluded.categories,
            portfolio=excluded.portfolio,
            avatar_url=excluded.avatar_url,
            updated_at=excluded.updated_at""",
        (
            profile.creator_email.strip().lower(), profile.creator_name.strip(),
            profile.username.strip(), profile.bio.strip(), profile.skills.strip(),
            profile.categories.strip(), profile.portfolio.strip(),
            profile.avatar_url.strip(), now_iso(),
        ),
    )
    conn.commit()
    row = cur.execute(
        "SELECT * FROM creator_profiles WHERE LOWER(creator_email) = LOWER(?)",
        (profile.creator_email.strip(),),
    ).fetchone()
    conn.close()
    return dict(row)


@app.get("/api/creator/dashboard")
def creator_dashboard(creator_email: str):
    conn = get_db()
    cur = conn.cursor()
    email = creator_email.strip().lower()
    gigs = cur.execute(
        "SELECT * FROM gigs WHERE LOWER(owner_email) = LOWER(?) ORDER BY id DESC",
        (email,),
    ).fetchall()
    orders = cur.execute(
        """SELECT o.*, g.title AS gig_title FROM orders o
           JOIN gigs g ON g.id = o.gig_id
           WHERE LOWER(o.creator_email) = LOWER(?) ORDER BY o.id DESC""",
        (email,),
    ).fetchall()
    total_earnings = sum(
        float(o["amount"]) for o in orders if o["status"] in ("Accepted", "In Progress", "Delivered", "Completed")
    )
    completed = [o for o in orders if o["status"] == "Completed"]
    pending = [o for o in orders if o["status"] == "Pending"]
    active = [o for o in orders if o["status"] in ("Accepted", "In Progress", "Revision Requested", "Delivered")]
    total_views = sum(int(g["views"] or 0) for g in gigs)
    avg_rating_rows = [float(g["rating"]) for g in gigs if g["rating"]]
    avg_rating = round(sum(avg_rating_rows) / len(avg_rating_rows), 2) if avg_rating_rows else 0
    per_gig = []
    for g in gigs:
        gig_orders = [o for o in orders if o["gig_id"] == g["id"]]
        gig_orders_completed = [o for o in gig_orders if o["status"] == "Completed"]
        per_gig.append({
            "id": g["id"],
            "title": g["title"],
            "category": g["category"],
            "rate": g["rate"],
            "status": g["status"],
            "views": g["views"] or 0,
            "orders": len(gig_orders),
            "completed": len(gig_orders_completed),
            "revenue": round(sum(float(o["amount"]) for o in gig_orders_completed), 2),
            "rating": g["rating"] or 0,
            "review_count": g["review_count"] or 0,
        })
    conn.close()
    return {
        "total_gigs": len(gigs),
        "active_gigs": sum(1 for g in gigs if g["status"] == "Active"),
        "total_orders": len(orders),
        "pending_orders": len(pending),
        "active_orders": len(active),
        "completed_orders": len(completed),
        "total_earnings": round(total_earnings, 2),
        "total_views": total_views,
        "avg_rating": avg_rating,
        "per_gig": per_gig,
    }


@app.get("/api/creator/earnings")
def creator_earnings(creator_email: str):
    conn = get_db()
    cur = conn.cursor()
    orders = cur.execute(
        """SELECT o.*, g.title AS gig_title FROM orders o
           JOIN gigs g ON g.id = o.gig_id
           WHERE LOWER(o.creator_email) = LOWER(?)""",
        (creator_email.strip().lower(),),
    ).fetchall()
    total = sum(float(o["amount"]) for o in orders if o["status"] in ("Accepted", "In Progress", "Delivered", "Completed"))
    completed = sum(float(o["amount"]) for o in orders if o["status"] == "Completed")
    pending = sum(float(o["amount"]) for o in orders if o["status"] == "Pending")
    in_progress = sum(float(o["amount"]) for o in orders if o["status"] in ("Accepted", "In Progress", "Delivered", "Revision Requested"))
    avg = round(completed / len([o for o in orders if o["status"] == "Completed"]), 2) if any(o["status"] == "Completed" for o in orders) else 0
    conn.close()
    return {
        "total_earnings": round(total, 2),
        "completed_earnings": round(completed, 2),
        "pending_earnings": round(pending, 2),
        "in_progress_earnings": round(in_progress, 2),
        "orders": len(orders),
        "average_order_value": avg,
    }


@app.get("/api/client/dashboard")
def client_dashboard(client_email: str):
    conn = get_db()
    cur = conn.cursor()
    orders = cur.execute(
        """SELECT o.*, g.title AS gig_title, g.creator_name FROM orders o
           JOIN gigs g ON g.id = o.gig_id
           WHERE LOWER(o.client_email) = LOWER(?) ORDER BY o.id DESC""",
        (client_email.strip().lower(),),
    ).fetchall()
    saved = cur.execute(
        "SELECT COUNT(*) AS c FROM saved_gigs WHERE LOWER(client_email) = LOWER(?)",
        (client_email.strip().lower(),),
    ).fetchone()["c"]
    total_spent = sum(float(o["amount"]) for o in orders if o["status"] == "Completed")
    conn.close()
    return {
        "total_orders": len(orders),
        "active_orders": sum(1 for o in orders if o["status"] in ("Accepted", "In Progress", "Delivered", "Revision Requested")),
        "completed_orders": sum(1 for o in orders if o["status"] == "Completed"),
        "saved_gigs": saved,
        "total_spent": round(total_spent, 2),
    }


@app.post("/api/seed")
def reset_seed():
    conn = get_db()
    cur = conn.cursor()
    for t in ["deliverables", "reviews", "messages", "notifications", "saved_gigs", "orders", "gigs"]:
        cur.execute(f"DELETE FROM {t}")
    seed_gigs(cur)
    conn.commit()
    conn.close()
    return {"message": "Database reset and re-seeded"}