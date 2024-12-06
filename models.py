from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=db.func.now())