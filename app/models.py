from app import db
from flask_login import UserMixin

class SchoolClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    niveau = db.Column(db.String(20), nullable=False)  # 6e, 5e, 4e, 3e, 2nde, 1ère, Terminale
    groups = db.relationship('Group', backref='school_class', lazy=True)
    users = db.relationship('User', backref='school_class', lazy=True)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=False)
    users = db.relationship('User', backref='group', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date)
    besoins_particuliers = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True)
    role = db.Column(db.String(20), nullable=False)  # admin, professeur, eleve
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    original_filename = db.Column(db.String(100))
    tags = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    type = db.Column(db.String(20), default='document')  # 'document' ou 'exercise'
