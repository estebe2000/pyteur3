from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db, csrf
from app.models import Message, MessageRecipient, User, Group, SchoolClass

messagerie_bp = Blueprint('messagerie', __name__)

@messagerie_bp.route('/messagerie')
@login_required
def messagerie():
    return render_template('messagerie.html')

@messagerie_bp.route('/api/recipients', methods=['GET'])
@login_required
def get_recipients():
    users = User.query.filter(User.id != current_user.id).all()
    groups = Group.query.all()
    classes = SchoolClass.query.all()

    return jsonify({
        "users": [{"id": u.id, "name": f"{u.prenom} {u.nom}"} for u in users],
        "groups": [{"id": g.id, "name": g.nom} for g in groups],
        "classes": [{"id": c.id, "name": c.nom} for c in classes]
    })

@messagerie_bp.route('/api/messages', methods=['GET'])
@login_required
def get_messages():
    direct_msgs = MessageRecipient.query.filter_by(recipient_user_id=current_user.id).all()

    group_msgs = []
    if current_user.group_id:
        group_msgs = MessageRecipient.query.filter_by(recipient_group_id=current_user.group_id).all()

    class_msgs = []
    if current_user.group and current_user.group.school_class:
        class_groups = current_user.group.school_class.groups
        group_ids = [g.id for g in class_groups]
        if group_ids:
            class_msgs = MessageRecipient.query.filter(MessageRecipient.recipient_group_id.in_(group_ids)).all()

    all_recipient_msgs = direct_msgs + group_msgs + class_msgs

    unique_recipient_msgs = {}
    for mr in all_recipient_msgs:
        unique_recipient_msgs[mr.message_id] = mr

    sent_msgs = Message.query.filter_by(sender_id=current_user.id).all()

    messages = []

    for mr in unique_recipient_msgs.values():
        messages.append({
            'id': mr.message.id,
            'content': mr.message.content,
            'sender_id': mr.message.sender_id,
            'sender_name': f"{mr.message.sender.prenom} {mr.message.sender.nom}",
            'timestamp': mr.message.timestamp.isoformat(),
            'is_read': mr.is_read,
            'sent': False
        })

    for m in sent_msgs:
        messages.append({
            'id': m.id,
            'content': m.content,
            'sender_id': m.sender_id,
            'sender_name': f"{current_user.prenom} {current_user.nom}",
            'timestamp': m.timestamp.isoformat(),
            'is_read': True,
            'sent': True
        })

    messages.sort(key=lambda m: m['timestamp'])

    return jsonify(messages)

@csrf.exempt
@messagerie_bp.route('/api/messages/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json(force=True)
    content = data.get('content', '').strip()
    recipient_user_id = data.get('recipient_user_id')
    recipient_group_id = data.get('recipient_group_id')
    recipient_class_id = data.get('recipient_class_id')

    if not content:
        return jsonify({'error': 'Message vide'}), 400

    message = Message(sender_id=current_user.id, content=content)
    db.session.add(message)
    db.session.flush()

    recipients = []

    if recipient_user_id:
        user = User.query.get(recipient_user_id)
        if user:
            recipients.append(MessageRecipient(message_id=message.id, recipient_user_id=user.id))

    if recipient_group_id:
        group = Group.query.get(recipient_group_id)
        if group:
            recipients.append(MessageRecipient(message_id=message.id, recipient_group_id=group.id))

    if recipient_class_id:
        school_class = SchoolClass.query.get(recipient_class_id)
        if school_class:
            groups = school_class.groups
            for group in groups:
                recipients.append(MessageRecipient(message_id=message.id, recipient_group_id=group.id))

    if not recipients:
        return jsonify({'error': 'Aucun destinataire valide'}), 400

    db.session.add_all(recipients)
    db.session.commit()

    return jsonify({'success': True})

@csrf.exempt
@messagerie_bp.route('/api/messages/delete/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message.sender_id != current_user.id:
        return {'error': 'Non autorisé'}, 403

    MessageRecipient.query.filter_by(message_id=message_id).delete()
    db.session.delete(message)
    db.session.commit()
    return {'success': True}

@csrf.exempt
@messagerie_bp.route('/api/messages/mark_read', methods=['POST'])
@login_required
def mark_message_read():
    try:
        data = request.get_json(force=True)
        message_id = data.get('message_id')
        if not message_id:
            return {'error': 'ID manquant'}, 400

        mr = MessageRecipient.query.filter_by(message_id=message_id, recipient_user_id=current_user.id).first()
        if not mr:
            return {'error': 'Message non trouvé'}, 404

        mr.is_read = True
        db.session.commit()
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}, 500

@csrf.exempt
@messagerie_bp.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({'error': f'Erreur parsing JSON: {str(e)}'}), 400

    if data is None:
        return jsonify({'error': 'Requête JSON invalide ou en-tête Content-Type manquant'}), 400

    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'Message vide'}), 400

    try:
        from app.ia_client import generate_text
        ai_response = generate_text(user_message)
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
