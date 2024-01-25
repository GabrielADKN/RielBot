from app import app
from models import db, User, connect_db, FunFact

db.drop_all()
db.create_all()

db.session.commit()
