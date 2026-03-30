import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db import db


class Inquiry(db.Model):
    __tablename__ = "inquiries"

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic contact info
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)

    # Which topic they’re interested in
    topic = db.Column(db.String(60), nullable=False, index=True)

    # Freeform message
    message = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

