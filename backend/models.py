from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime

db = SQLAlchemy()

# ---------------- USER MODEL ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Relationship → one user can have many files
    files = db.relationship('File', backref='owner', lazy=True)


# ---------------- FILE MODEL ----------------
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Original filename (what user uploads)
    original_filename = db.Column(db.String(200), nullable=False)

    # Stored filename (UUID used in server storage)
    stored_filename = db.Column(db.String(200), nullable=False)

    # Public file ID (used in download link)
    file_id = db.Column(
        db.String(200),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    # 🔥 NEW: Link file to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Upload timestamp
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # (For next step - expiry)
    expiry_time = db.Column(db.DateTime, nullable=True)