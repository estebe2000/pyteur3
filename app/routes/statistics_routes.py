from flask import Blueprint, jsonify, send_file, request
from app import db
from app.models import User, SchoolClass, Group, Document, ExerciseAssignment, DocumentAssignment, Message, MessageRecipient, TodoList, TodoItem, QcmAttempt
import csv
import io
from sqlalchemy import func, desc

statistics_bp = Blueprint('statistics', __name__)

# --- QCM ---
@statistics_bp.route('/api/statistics/qcm')
def get_qcm_stats():
    """
    Récupère les statistiques globales des QCM pour tous les élèves
    """
    # Total des tentatives de QCM
    total_attempts = QcmAttempt.query.count()
    
    # Score moyen global
    avg_score = db.session.query(func.avg(QcmAttempt.score)).scalar() or 0
    
    # Nombre de QCM distincts
    distinct_qcms = db.session.query(QcmAttempt.qcm_id).distinct().count()
    
    # Top 5 des élèves avec les meilleurs scores moyens
    top_students = db.session.query(
        User.id,
        User.nom,
        User.prenom,
        func.avg(QcmAttempt.score).label('avg_score'),
        func.count(QcmAttempt.id).label('attempts')
    ).join(QcmAttempt, QcmAttempt.student_id == User.id)\
     .group_by(User.id)\
     .order_by(desc('avg_score'))\
     .limit(5).all()
    
    top_students_data = [
        {
            'id': student.id,
            'nom': student.nom,
            'prenom': student.prenom,
            'avg_score': float(student.avg_score),
            'attempts': student.attempts
        }
        for student in top_students
    ]
    
    # Top 5 des QCM les plus difficiles (scores moyens les plus bas)
    difficult_qcms = db.session.query(
        QcmAttempt.qcm_id,
        func.avg(QcmAttempt.score).label('avg_score'),
        func.count(QcmAttempt.id).label('attempts')
    ).group_by(QcmAttempt.qcm_id)\
     .having(func.count(QcmAttempt.id) > 3)\
     .order_by('avg_score')\
     .limit(5).all()
    
    difficult_qcms_data = [
        {
            'qcm_id': qcm.qcm_id,
            'avg_score': float(qcm.avg_score),
            'attempts': qcm.attempts
        }
        for qcm in difficult_qcms
    ]
    
    # Répartition des scores par tranches
    score_ranges = [
        {'min': 0, 'max': 20, 'count': 0},
        {'min': 20, 'max': 40, 'count': 0},
        {'min': 40, 'max': 60, 'count': 0},
        {'min': 60, 'max': 80, 'count': 0},
        {'min': 80, 'max': 100, 'count': 0}
    ]
    
    for range_data in score_ranges:
        count = QcmAttempt.query.filter(
            QcmAttempt.score >= range_data['min'],
            QcmAttempt.score < range_data['max']
        ).count()
        range_data['count'] = count
    
    # Liste détaillée des tentatives de QCM
    qcm_attempts = []
    attempts = QcmAttempt.query.order_by(QcmAttempt.created_at.desc()).limit(100).all()
    
    for attempt in attempts:
        student = User.query.get(attempt.student_id)
        qcm_attempts.append({
            'id': attempt.id,
            'student_id': attempt.student_id,
            'student_name': f"{student.nom} {student.prenom}" if student else "N/A",
            'qcm_id': attempt.qcm_id,
            'score': attempt.score,
            'total_questions': attempt.total_questions,
            'correct_answers': attempt.correct_answers,
            'created_at': attempt.created_at.isoformat()
        })
    
    return jsonify({
        'total_attempts': total_attempts,
        'avg_score': avg_score,
        'distinct_qcms': distinct_qcms,
        'top_students': top_students_data,
        'difficult_qcms': difficult_qcms_data,
        'score_ranges': score_ranges,
        'attempts': qcm_attempts
    })

@statistics_bp.route('/api/statistics/export/qcm')
def export_qcm_csv():
    """
    Exporte les données des QCM au format CSV
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Élève', 'QCM ID', 'Score', 'Questions', 'Réponses correctes', 'Date'])
    
    attempts = QcmAttempt.query.order_by(QcmAttempt.created_at.desc()).all()
    for attempt in attempts:
        student = User.query.get(attempt.student_id)
        student_name = f"{student.nom} {student.prenom}" if student else "N/A"
        
        writer.writerow([
            attempt.id,
            student_name,
            attempt.qcm_id,
            attempt.score,
            attempt.total_questions,
            attempt.correct_answers,
            attempt.created_at.isoformat()
        ])
    
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='qcm_statistics.csv')

# --- Utilisateurs ---
@statistics_bp.route('/api/statistics/users')
def get_users_stats():
    from sqlalchemy import func
    # Total utilisateurs
    total = User.query.count()

    # Répartition par rôle
    roles = db.session.query(User.role, func.count(User.id)).group_by(User.role).all()
    roles_data = [{"role": r, "count": c} for r, c in roles]

    # Répartition par besoins particuliers (avec/sans)
    besoins = db.session.query(
        db.case(
            (User.besoins_particuliers.is_(None), "sans"),
            (User.besoins_particuliers == "", "sans"),
            else_="avec"
        ).label('besoins'),
        func.count(User.id)
    ).group_by('besoins').all()
    besoins_data = [{"besoins": b, "count": c} for b, c in besoins]

    # Répartition par niveau scolaire
    niveaux = db.session.query(SchoolClass.niveau, func.count(User.id))\
        .join(SchoolClass, User.class_id == SchoolClass.id)\
        .group_by(SchoolClass.niveau).all()
    niveaux_data = [{"niveau": n, "count": c} for n, c in niveaux]

    # Inscriptions par mois
    inscriptions = db.session.query(
        func.strftime('%Y-%m', User.date_entree), func.count(User.id)
    ).group_by(func.strftime('%Y-%m', User.date_entree)).all()
    inscriptions_data = [{"mois": m, "count": c} for m, c in inscriptions]

    # Liste complète des utilisateurs
    users_list = []
    users = User.query.all()
    for u in users:
        niveau = None
        if u.class_id:
            classe = SchoolClass.query.get(u.class_id)
            niveau = classe.niveau if classe else None
        users_list.append({
            "nom": u.nom,
            "prenom": u.prenom,
            "role": u.role,
            "sexe": u.sexe,
            "niveau": niveau,
            "date_entree": u.date_entree.isoformat() if u.date_entree else None,
            "date_sortie": u.date_sortie.isoformat() if u.date_sortie else None
        })

    return jsonify({
        "total": total,
        "roles": roles_data,
        "besoins": besoins_data,
        "niveaux": niveaux_data,
        "inscriptions": inscriptions_data,
        "users": users_list
    })

@statistics_bp.route('/api/statistics/export/users')
def export_users_csv():
    # TODO: exporter CSV utilisateurs
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Nom', 'Prénom', 'Rôle', 'Sexe', 'Niveau', 'Date entrée', 'Date sortie'])
    # Boucle sur les utilisateurs
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='utilisateurs.csv')


# --- Classes & Groupes ---
@statistics_bp.route('/api/statistics/classes')
def get_classes_stats():
    from sqlalchemy import func

    # Classes avec nombre d'élèves
    classes = db.session.query(
        SchoolClass.id,
        SchoolClass.nom,
        SchoolClass.niveau,
        func.count(User.id)
    ).outerjoin(User, User.class_id == SchoolClass.id)\
     .group_by(SchoolClass.id).all()

    classes_data = [
        {
            "id": cid,
            "nom": nom,
            "niveau": niveau,
            "nb_eleves": nb
        }
        for cid, nom, niveau, nb in classes
    ]

    # Groupes avec nombre d'élèves
    groupes = db.session.query(
        Group.id,
        Group.nom,
        SchoolClass.nom,
        func.count(User.id)
    ).outerjoin(User, User.group_id == Group.id)\
     .join(SchoolClass, Group.class_id == SchoolClass.id)\
     .group_by(Group.id).all()

    groupes_data = [
        {
            "id": gid,
            "nom": gnom,
            "classe": classe_nom,
            "nb_eleves": nb
        }
        for gid, gnom, classe_nom, nb in groupes
    ]

    # Moyennes
    moyenne_classe = sum(c["nb_eleves"] for c in classes_data) / len(classes_data) if classes_data else 0
    moyenne_groupe = sum(g["nb_eleves"] for g in groupes_data) / len(groupes_data) if groupes_data else 0

    return jsonify({
        "classes": classes_data,
        "groupes": groupes_data,
        "moyenne_classe": moyenne_classe,
        "moyenne_groupe": moyenne_groupe
    })

@statistics_bp.route('/api/statistics/export/classes')
def export_classes_csv():
    # TODO: exporter CSV classes/groupes
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Classe', 'Groupe', "Nombre d'élèves"])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='classes_groupes.csv')


# --- Exercices & Documents ---
@statistics_bp.route('/api/statistics/exercices')
def get_exercices_stats():
    from sqlalchemy import func

    # Total exercices
    total_exercices = Document.query.filter_by(type='exercise').count()

    # Total documents
    total_documents = Document.query.filter_by(type='document').count()

    # Répartition exercices/documents
    repartition = [
        {"type": "exercise", "count": total_exercices},
        {"type": "document", "count": total_documents}
    ]

    # Exercices assignés (à au moins un user/groupe/classe)
    total_assignes = ExerciseAssignment.query.count()

    # Exercices par classe
    exercices_par_classe = db.session.query(
        SchoolClass.nom,
        func.count(ExerciseAssignment.id)
    ).join(SchoolClass, ExerciseAssignment.class_id == SchoolClass.id)\
     .group_by(SchoolClass.nom).all()
    exercices_classe_data = [{"classe": nom, "count": c} for nom, c in exercices_par_classe]

    # Exercices par groupe
    exercices_par_groupe = db.session.query(
        Group.nom,
        func.count(ExerciseAssignment.id)
    ).join(Group, ExerciseAssignment.group_id == Group.id)\
     .group_by(Group.nom).all()
    exercices_groupe_data = [{"groupe": nom, "count": c} for nom, c in exercices_par_groupe]

    # Exercices par utilisateur
    exercices_par_user = db.session.query(
        User.nom,
        User.prenom,
        func.count(ExerciseAssignment.id)
    ).join(User, ExerciseAssignment.user_id == User.id)\
     .group_by(User.id).all()
    exercices_user_data = [{"nom": nom, "prenom": prenom, "count": c} for nom, prenom, c in exercices_par_user]

    # Liste détaillée des documents/exercices
    docs_list = []
    docs = Document.query.all()
    for d in docs:
        # Créateur
        user = User.query.get(d.user_id) if d.user_id else None
        creator = f"{user.nom} {user.prenom}" if user else "N/A"
        # Assigné à (simplifié)
        assignations = [a for a in d.assignments] if hasattr(d, 'assignments') else []
        assigned_to = ', '.join(
            f"{User.query.get(a.user_id).nom} {User.query.get(a.user_id).prenom}" if a.user_id else
            f"Groupe {Group.query.get(a.group_id).nom}" if a.group_id else
            f"Classe {SchoolClass.query.get(a.class_id).nom}" if a.class_id else "N/A"
            for a in assignations
        )
        docs_list.append({
            "nom": d.original_filename or d.filename,
            "type": d.type,
            "createur": creator,
            "date_creation": d.created_at.isoformat() if d.created_at else "",
            "assigne_a": assigned_to
        })

    return jsonify({
        "total_exercices": total_exercices,
        "total_documents": total_documents,
        "repartition": repartition,
        "total_assignes": total_assignes,
        "exercices_par_classe": exercices_classe_data,
        "exercices_par_groupe": exercices_groupe_data,
        "exercices_par_user": exercices_user_data,
        "documents": docs_list
    })

@statistics_bp.route('/api/statistics/export/exercices')
def export_exercices_csv():
    # TODO: exporter CSV exercices/documents
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Nom', 'Type', 'Créateur', 'Date création', 'Assigné à'])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='exercices_documents.csv')


# --- Messagerie ---
@statistics_bp.route('/api/statistics/messages')
def get_messages_stats():
    from sqlalchemy import func

    # Total messages envoyés
    total_envoyes = Message.query.count()

    # Total messages reçus
    total_recus = MessageRecipient.query.count()

    # Messages lus / non lus
    lus = db.session.query(
        MessageRecipient.is_read,
        func.count(MessageRecipient.id)
    ).group_by(MessageRecipient.is_read).all()
    lus_data = [{"is_read": is_read, "count": c} for is_read, c in lus]

    # Messages envoyés par utilisateur
    envoyes_par_user = db.session.query(
        User.nom,
        User.prenom,
        func.count(Message.id)
    ).join(User, Message.sender_id == User.id)\
     .group_by(User.id).all()
    envoyes_data = [{"nom": nom, "prenom": prenom, "count": c} for nom, prenom, c in envoyes_par_user]

    # Messages reçus par utilisateur
    recus_par_user = db.session.query(
        User.nom,
        User.prenom,
        func.count(MessageRecipient.id)
    ).join(User, MessageRecipient.recipient_user_id == User.id)\
     .group_by(User.id).all()
    recus_data = [{"nom": nom, "prenom": prenom, "count": c} for nom, prenom, c in recus_par_user]

    # Liste détaillée des messages
    messages_list = []
    messages = Message.query.all()
    for m in messages:
        sender = User.query.get(m.sender_id)
        sender_name = f"{sender.nom} {sender.prenom}" if sender else "N/A"
        for r in m.recipients:
            recipient = None
            if r.recipient_user_id:
                user = User.query.get(r.recipient_user_id)
                recipient = f"{user.nom} {user.prenom}" if user else "N/A"
            elif r.recipient_group_id:
                group = Group.query.get(r.recipient_group_id)
                recipient = f"Groupe {group.nom}" if group else "N/A"
            else:
                recipient = "N/A"
            messages_list.append({
                "expediteur": sender_name,
                "destinataire": recipient,
                "contenu": m.content,
                "date": m.timestamp.isoformat() if m.timestamp else "",
                "lu": r.is_read
            })

    return jsonify({
        "total_envoyes": total_envoyes,
        "total_recus": total_recus,
        "lus": lus_data,
        "envoyes_par_user": envoyes_data,
        "recus_par_user": recus_data,
        "messages": messages_list
    })

@statistics_bp.route('/api/statistics/export/messages')
def export_messages_csv():
    # TODO: exporter CSV messagerie
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Expéditeur', 'Destinataire', 'Contenu', 'Date', 'Lu'])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='messagerie.csv')


# --- ToDo Lists ---
@statistics_bp.route('/api/statistics/todos')
def get_todos_stats():
    from sqlalchemy import func

    # Total listes
    total_listes = TodoList.query.count()

    # Total tâches
    total_taches = TodoItem.query.count()

    # Tâches terminées / non terminées
    taches_done = db.session.query(
        TodoItem.done,
        func.count(TodoItem.id)
    ).group_by(TodoItem.done).all()
    taches_done_data = [{"done": done, "count": c} for done, c in taches_done]

    # Listes par utilisateur
    listes_par_user = db.session.query(
        User.nom,
        User.prenom,
        func.count(TodoList.id)
    ).join(User, TodoList.owner_id == User.id)\
     .group_by(User.id).all()
    listes_user_data = [{"nom": nom, "prenom": prenom, "count": c} for nom, prenom, c in listes_par_user]

    # Tâches par utilisateur (via owner des listes)
    taches_par_user = db.session.query(
        User.nom,
        User.prenom,
        func.count(TodoItem.id)
    ).join(TodoList, TodoList.owner_id == User.id)\
     .join(TodoItem, TodoItem.list_id == TodoList.id)\
     .group_by(User.id).all()
    taches_user_data = [{"nom": nom, "prenom": prenom, "count": c} for nom, prenom, c in taches_par_user]

    # Liste détaillée des tâches
    todos_list = []
    todo_items = TodoItem.query.all()
    for item in todo_items:
        todo_list = TodoList.query.get(item.list_id)
        owner = User.query.get(todo_list.owner_id) if todo_list else None
        todos_list.append({
            "utilisateur": f"{owner.nom} {owner.prenom}" if owner else "N/A",
            "liste": todo_list.title if todo_list else "N/A",
            "tache": item.content,
            "terminee": item.done
        })

    return jsonify({
        "total_listes": total_listes,
        "total_taches": total_taches,
        "taches_done": taches_done_data,
        "listes_par_user": listes_user_data,
        "taches_par_user": taches_user_data,
        "todos": todos_list
    })

@statistics_bp.route('/api/statistics/export/todos')
def export_todos_csv():
    # TODO: exporter CSV todo lists
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Utilisateur', 'Liste', 'Tâche', 'Terminée'])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='todo_lists.csv')
