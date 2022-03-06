from enum import unique
from flask_sqlalchemy import SQLAlchemy

db= SQLAlchemy()

class consultas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date=db.Column(db.String(200),unique=True, nullable=False)
    data=db.Column(db.Text, nullable=False)

    def serialize(self):
        return{
            "id":self.id,
            "date":self.date,
            "data":self.data
        }

