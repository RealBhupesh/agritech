# AgriPulse (Flask + PostgreSQL)

Minimalist website for agriculture use-cases:

- Agriculture-UseofIoTDevices (IoT)
- Drones in agriculture
- Management of water
- Distribution (farm to market)

## Tech

- Backend: Flask
- Database: PostgreSQL (via SQLAlchemy ORM)
- Frontend: Server-rendered Jinja templates + modern minimalist CSS

## Setup

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Configure environment:
   - Copy `.env.example` to `.env`
   - Update `DATABASE_URL` to point to your PostgreSQL database
3. Run:
   - `python app.py`
4. Open:
   - `http://localhost:5000`

## Database

On startup, the app creates the `inquiries` table automatically (for first-time local use) when `DATABASE_URL` is set.

If you start the app without `DATABASE_URL`, the frontend pages still work, but demo requests are blocked until PostgreSQL is configured.

## Notes

- The contact form stores inquiries in PostgreSQL.
- In the app code, it uses SQLAlchemy ORM (no handwritten raw SQL).

