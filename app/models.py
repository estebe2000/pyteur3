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
    sexe = db.Column(db.String(1))  # G ou F
    besoins_particuliers = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True)
    role = db.Column(db.String(20), nullable=False)  # admin, professeur, eleve
    date_entree = db.Column(db.Date)
    date_sortie = db.Column(db.Date)
    tuteur = db.Column(db.String(100))
    connexion_eleve = db.Column(db.String(100))
    connexion_responsable = db.Column(db.String(100))
    option1 = db.Column(db.String(100))
    option2 = db.Column(db.String(100))
    option3 = db.Column(db.String(100))
    autres_options = db.Column(db.String(200))
    regime = db.Column(db.String(100))
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

class ExerciseAssignment(db.Model):
    __tablename__ = 'exercise_assignments'
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=True)

    exercise = db.relationship('Document', backref='assignments')
    user = db.relationship('User', backref='exercise_assignments')
    group = db.relationship('Group', backref='exercise_assignments')
    school_class = db.relationship('SchoolClass', backref='exercise_assignments')


class DocumentAssignment(db.Model):
    __tablename__ = 'document_assignments'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=True)

    document = db.relationship('Document', backref='doc_assignments')
    user = db.relationship('User', backref='document_assignments')
    group = db.relationship('Group', backref='document_assignments')
    school_class = db.relationship('SchoolClass', backref='document_assignments')


class TodoList(db.Model):
    __tablename__ = 'todo_lists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    owner = db.relationship('User', backref='todo_lists')
    items = db.relationship('TodoItem', backref='list', cascade='all, delete-orphan')
    assignments = db.relationship('TodoListAssignment', backref='list', cascade='all, delete-orphan')


class TodoItem(db.Model):
    __tablename__ = 'todo_items'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todo_lists.id'), nullable=False)


class TodoListAssignment(db.Model):
    __tablename__ = 'todo_list_assignments'
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('todo_lists.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref='todo_list_assignments')
