# TheHub — Creator Gig Marketplace

**Hackathon ID:** `AZIS-72KJSK`   
**Track:** Track 2 — Real-World AI Products (Option: Creator Gig Marketplace)
**Stack:** Python · FastAPI · SQLite · Streamlit

## Standard API

**Yes — the standard API is implemented.** Feature checks can be run by script
against the endpoints below. See `test_api.py` for the exact contract.

Base URL: `{DEPLOYED_BACKEND}/api`

| # | Feature             | Method + Path                        |
|---|---------------------|--------------------------------------|
| 1 | Post a gig          | `POST /gigs`                         |
| 2 | Browse & search     | `GET /gigs?search=&category=&sort_by=` |
| 3 | Book a gig          | `POST /bookings`                     |
| 4 | Creator dashboard   | `GET /creator/bookings`              |
| 4 | Accept / decline    | `PATCH /bookings/{id}`               |
| 5 | My bookings         | `GET /client/bookings?client_name=`  |
|   | Stats               | `GET /stats`                         |

Full backend: `server.py` · Frontend: `app.py`

## Decision Points

**DP1 · Rejection** — Client sees the status change to *Declined* together with the
creator's optional reason, plus a **“Browse similar creators”** button so they stay
in the marketplace instead of leaving after a refusal.

**DP2 · Double booking** — **Yes**, a gig can receive multiple *Pending* bookings
at once. Creators juggle workloads; blocking concurrent inquiries would create
bottlenecks whenever an early inquirer goes quiet or is declined.

**DP3 · Discovery** — **Hybrid ranking**, default **newest-first**, with client
sort toggles for *cheapest*, *priciest*, and *top-rated*. Newest-first gives new
listings a fair shot; the sort toggles let buyers optimise for budget or quality.

## No Authentication

Per the brief, **there is no login or signup**. The UI exposes a **role switcher**
in the sidebar (`View as → Client / Creator`). Graders can reach every feature
in one click with pre-set demo identities:

| Role    | Name         | Email                 |
|---------|--------------|-----------------------|
| Client  | Ava Johnson  | client@thehub.com     |
| Creator | Alex Rivera  | creator@thehub.com    |

## Run Locally

```bash
pip install -r requirements.txt

# Terminal 1 — backend
uvicorn server:app --reload --port 8000

# Terminal 2 — frontend
export API_URL="http://localhost:8000/api"
streamlit run app.py