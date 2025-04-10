from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db, csrf
from app.models import Document, DocumentAssignment, User, Group, SchoolClass
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_
import json

document_bp = Blueprint('document', __name__)

@document_bp.route('/documents')
@login_required
def documents():
    # Documents personnels
    personal_docs = Document.query.filter_by(user_id=current_user.id, type='document')

    filters = [DocumentAssignment.user_id == current_user.id]

    if current_user.group_id is not None:
        filters.append(DocumentAssignment.group_id == current_user.group_id)

    if current_user.group and current_user.group.school_class:
        filters.append(DocumentAssignment.class_id == current_user.group.school_class.id)

    assigned_docs = Document.query.join(DocumentAssignment).filter(
        Document.type == 'document',
        or_(*filters)
    )

    docs = personal_docs.union(assigned_docs).all()

    return render_template('documents.html', documents=docs)

@document_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Aucun fichier sélectionné')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{current_user.id}_{filename}"

        upload_folder = os.path.join('app', 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)

        file.save(os.path.join(upload_folder, unique_filename))
        
        new_doc = Document(
            filename=unique_filename,
            original_filename=filename,
            tags=request.form.get('tags', ''),
            user_id=current_user.id,
            type='document'
        )
        db.session.add(new_doc)
        db.session.commit()
        
        flash('Document uploadé avec succès')
        return redirect(url_for('document.documents'))
    
    flash('Type de fichier non autorisé (PDF uniquement)')
    return redirect(url_for('document.documents'))

@document_bp.route('/assign_document/<int:document_id>', methods=['GET', 'POST'])
@login_required
def assign_document(document_id):
    if current_user.role != 'admin':
        return "Accès non autorisé", 403

    from app.models import User, Group, SchoolClass, DocumentAssignment, Document

    document = Document.query.get_or_404(document_id)

    if request.method == 'POST':
        DocumentAssignment.query.filter_by(document_id=document_id).delete()

        user_ids = request.form.getlist('users')
        for uid in user_ids:
            assign = DocumentAssignment(document_id=document_id, user_id=int(uid))
            db.session.add(assign)

        group_ids = request.form.getlist('groups')
        for gid in group_ids:
            assign = DocumentAssignment(document_id=document_id, group_id=int(gid))
            db.session.add(assign)

        class_ids = request.form.getlist('classes')
        for cid in class_ids:
            assign = DocumentAssignment(document_id=document_id, class_id=int(cid))
            db.session.add(assign)

        db.session.commit()
        flash("Affectations mises à jour")
        return redirect(url_for('document.documents'))

    users = User.query.filter_by(role='eleve').all()
    groups = Group.query.all()
    classes = SchoolClass.query.all()

    existing = DocumentAssignment.query.filter_by(document_id=document_id).all()
    assigned_users = [a.user_id for a in existing if a.user_id]
    assigned_groups = [a.group_id for a in existing if a.group_id]
    assigned_classes = [a.class_id for a in existing if a.class_id]

    return render_template('assign_exercise.html',
                           exercise=document,
                           users=users,
                           groups=groups,
                           classes=classes,
                           assigned_users=assigned_users,
                           assigned_groups=assigned_groups,
                           assigned_classes=assigned_classes)

@csrf.exempt
@document_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    try:
        os.remove(os.path.join('app', 'static', 'uploads', doc.filename))
        db.session.delete(doc)
        db.session.commit()
        return '', 204
    except Exception as e:
        return str(e), 500

@csrf.exempt
@document_bp.route('/export_pronote', methods=['POST'])
@login_required
def export_pronote():
    try:
        data = request.get_json(force=True)
        qcm_name = data.get('name', 'qcm_export')
        questions = data.get('questions', [])

        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n'

        xml += '  <question type="category">\n'
        xml += '    <category>\n'
        xml += f'      <text><![CDATA[<infos><name>{qcm_name}</name><answernumbering>123</answernumbering><niveau>2NDE</niveau><matiere>SC.NUMERIQ.TECHNOL.</matiere></infos>]]></text>\n'
        xml += '    </category>\n'
        xml += '  </question>\n'

        for q in questions:
            question_text = q.get('question', '').replace('&', '&').replace('<', '<').replace('>', '>')
            propositions = q.get('propositions', [])
            bonne_reponse = q.get('bonne_reponse', 0)

            xml += '  <question type="multichoice">\n'
            xml += '    <name>\n'
            xml += f'      <text><![CDATA[{question_text}]]></text>\n'
            xml += '    </name>\n'
            xml += '    <questiontext format="html">\n'
            xml += '      <text><![CDATA[]]></text>\n'
            xml += '    </questiontext>\n'
            xml += '    <externallink/>\n'
            xml += '    <usecase>1</usecase>\n'
            xml += '    <defaultgrade>1</defaultgrade>\n'
            xml += '    <editeur>0</editeur>\n'
            xml += '    <single>true</single>\n'

            for idx, prop in enumerate(propositions):
                prop_text = prop.replace('&', '&').replace('<', '<').replace('>', '>')
                fraction = "100" if idx == bonne_reponse else "0"
                xml += f'    <answer fraction="{fraction}" format="plain_text">\n'
                xml += f'      <text><![CDATA[{prop_text}]]></text>\n'
                xml += '      <feedback>\n'
                xml += '        <text><![CDATA[]]></text>\n'
                xml += '      </feedback>\n'
                xml += '    </answer>\n'

            xml += '  </question>\n'

        xml += '</quiz>\n'

        from flask import Response
        return Response(
            xml,
            mimetype='application/xml',
            headers={
                'Content-Disposition': f'attachment; filename={qcm_name}.xml'
            }
        )
    except Exception as e:
        return str(e), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}
