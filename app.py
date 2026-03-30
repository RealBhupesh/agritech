from flask import Flask, jsonify, flash, redirect, render_template, request, url_for

from config import Config
from db import db
from models import Inquiry
from iot_sim import sim_metrics

app = Flask(__name__)
app.config.from_object(Config)
app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

_database_url = app.config.get("DATABASE_URL")
if _database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = _database_url
    app.config["DB_ENABLED"] = True
else:
    # Allow the frontend pages to run without a configured database.
    # Submissions will be blocked until you set DATABASE_URL.
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql+psycopg2://invalid:invalid@localhost:5432/invalid"
    )
    app.config["DB_ENABLED"] = False

db.init_app(app)


TOPICS = {
    "water": {
        "slug": "water",
        "title": "Management of Water",
        "kicker": "Higher water efficiency, better crop outcomes",
        "overview": [
            "Water usage visibility using sensor + analytics pipelines.",
            "Improved scheduling for drip systems and irrigation channels.",
            "Better sustainability through measurable reduction in waste.",
        ],
        "use_cases": [
            {"h": "Leak & flow monitoring", "p": "Detect anomalies early."},
            {"h": "Scheduling", "p": "Time irrigation around crop and soil needs."},
            {"h": "Compliance reporting", "p": "Track improvements over seasons."},
        ],
        "cta_topic": "Management of Water",
    },
    "distribution": {
        "slug": "distribution",
        "title": "Distribution (Farm to Market)",
        "kicker": "More reliable movement of produce with better visibility",
        "overview": [
            "Track batches and reduce delays with operational planning signals.",
            "Coordinate storage, transport, and delivery handoffs.",
            "Reduce spoilage through better timing and routing decisions.",
        ],
        "use_cases": [
            {"h": "Cold-chain planning", "p": "Protect quality from farm to buyer."},
            {"h": "Demand coordination", "p": "Align harvest and dispatch schedules."},
            {"h": "Loss reduction", "p": "Identify bottlenecks and improve flow."},
        ],
        "cta_topic": "Distribution",
    },
}


@app.route("/")
def index():
    return render_template("index.html", topics=TOPICS.values())


@app.route("/topic/<slug>")
def topic(slug: str):
    data = TOPICS.get(slug)
    if not data:
        return render_template("404.html"), 404
    return render_template("topic.html", topic=data)


@app.route("/contact", methods=["GET"])
def contact_get():
    # Optional: pre-select topic when user clicks CTA.
    topic_name = request.args.get("topic", "")
    return render_template("contact.html", topics=TOPICS.values(), selected_topic=topic_name)


@app.route("/inquiries", methods=["POST"])
def inquiries_post():
    if not app.config.get("DB_ENABLED"):
        flash("Database is not configured yet. Please set DATABASE_URL in .env.", "error")
        return redirect(url_for("contact_get"))

    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    topic_name = (request.form.get("topic") or "").strip()
    message = (request.form.get("message") or "").strip()

    if not name or not email or not topic_name or not message:
        flash("Please fill in all fields.", "error")
        return redirect(
            url_for("contact_get", topic=topic_name if topic_name else "")
        )

    inquiry = Inquiry(name=name, email=email, topic=topic_name, message=message)
    db.session.add(inquiry)
    db.session.commit()

    flash("Thanks! Your request has been submitted.", "success")
    return redirect(url_for("index"))


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/iot/sim/next", methods=["GET"])
def api_iot_sim_next():
    # The frontend polls repeatedly. We use a monotonically increasing step_index.
    step = request.args.get("step", default="0")
    try:
        step_index = int(step)
    except ValueError:
        step_index = 0

    data = sim_metrics(step_index=step_index)
    return jsonify(data)


@app.errorhandler(404)
def not_found(_e):
    return render_template("404.html"), 404


def init_db():
    # Create tables for first-time local use.
    if not app.config.get("DB_ENABLED"):
        return
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))

