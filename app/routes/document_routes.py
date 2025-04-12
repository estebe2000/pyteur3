from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db, csrf
from app.models import Document, DocumentAssignment, User, Group, SchoolClass, Rubrique
import os
import datetime
from werkzeug.utils import secure_filename
from sqlalchemy import or_
import json

document_bp = Blueprint('document', __name__)

@document_bp.route('/documents')
@login_required
def documents():
    # Documents personnels
    personal_docs = Document.query.filter_by(user_id=current_user.id, type='document')
    personal_documents = personal_docs.all()

    filters = [DocumentAssignment.user_id == current_user.id]

    if current_user.group_id is not None:
        filters.append(DocumentAssignment.group_id == current_user.group_id)

    if current_user.group and current_user.group.school_class:
        filters.append(DocumentAssignment.class_id == current_user.group.school_class.id)

    assigned_docs = Document.query.join(DocumentAssignment).filter(
        Document.type == 'document',
        or_(*filters)
    )
    
    # Récupérer toutes les rubriques
    rubriques = Rubrique.query.all()
    
    # Organiser les documents par rubrique
    documents_by_rubrique = {}
    
    # Initialiser avec "Non classé" pour les documents sans rubrique
    documents_by_rubrique['non_classe'] = {
        'nom': 'Non classé',
        'description': 'Documents sans rubrique',
        'documents': []
    }
    
    # Initialiser avec toutes les rubriques existantes
    for rubrique in rubriques:
        documents_by_rubrique[rubrique.id] = {
            'nom': rubrique.nom,
            'description': rubrique.description,
            'documents': []
        }
    
    # Récupérer tous les documents partagés
    shared_documents = assigned_docs.all()
    
    # Organiser les documents par rubrique
    for doc in shared_documents:
        # Trouver l'affectation pour ce document
        assignment = DocumentAssignment.query.filter_by(document_id=doc.id).first()
        
        if assignment and assignment.rubrique_id and assignment.rubrique_id in documents_by_rubrique:
            documents_by_rubrique[assignment.rubrique_id]['documents'].append(doc)
        else:
            documents_by_rubrique['non_classe']['documents'].append(doc)
    
    # Vérifier si la requête vient d'un iframe
    is_iframe = request.args.get('iframe', 'false') == 'true'
    
    # Récupérer les labels pour le titre
    from app.lang.lang_fr import LABELS as labels_fr
    from app.lang.lang_en import LABELS as labels_en
    lang = request.cookies.get('lang', 'fr')
    labels = labels_fr if lang == 'fr' else labels_en
    
    # Vérifier si l'utilisateur est un professeur ou un administrateur
    is_teacher = current_user.role in ['admin', 'professeur']
    
    if is_iframe:
        return render_template('documents.html', 
                              personal_documents=personal_documents, 
                              shared_documents=shared_documents,
                              documents_by_rubrique=documents_by_rubrique,
                              is_teacher=is_teacher,
                              title=labels.get('documents', 'Documents'))
    else:
        return render_template('documents.html', 
                              personal_documents=personal_documents, 
                              shared_documents=shared_documents,
                              documents_by_rubrique=documents_by_rubrique,
                              is_teacher=is_teacher)

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
        
        # Créer une structure de répertoires organisée
        # Format: uploads/documents/[année]/[utilisateur_id]/
        current_year = datetime.datetime.now().strftime('%Y')
        user_folder = str(current_user.id)
        
        # Chemin relatif pour la base de données (utiliser des slashes pour les URLs)
        relative_path = f"documents/{current_year}/{user_folder}"
        
        # Chemin complet pour le stockage
        upload_folder = os.path.join('app', 'static', 'uploads', relative_path.replace('/', os.sep))
        
        # Créer les répertoires s'ils n'existent pas
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
        
        # Générer un nom de fichier unique avec timestamp pour éviter les collisions
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # Chemin complet du fichier
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Chemin relatif pour la base de données (ce qui sera stocké)
        db_filename = f"{relative_path}/{unique_filename}"
        
        # Sauvegarder le fichier
        file.save(file_path)
        
        new_doc = Document(
            filename=db_filename,
            original_filename=filename,
            tags=request.form.get('tags', ''),
            user_id=current_user.id,
            type='document'
        )
        db.session.add(new_doc)
        db.session.commit()
        
        flash('Document uploadé avec succès')
        # Rediriger vers la page documents au lieu du dashboard
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
        group_ids = request.form.getlist('groups')
        class_ids = request.form.getlist('classes')
        rubrique_id = request.form.get('rubrique_id')
        
        # Convertir en entier si une rubrique est sélectionnée
        if rubrique_id and rubrique_id != '':
            rubrique_id = int(rubrique_id)
        else:
            rubrique_id = None

        for uid in user_ids:
            assign = DocumentAssignment(
                document_id=document_id, 
                user_id=int(uid),
                rubrique_id=rubrique_id
            )
            db.session.add(assign)

        for gid in group_ids:
            assign = DocumentAssignment(
                document_id=document_id, 
                group_id=int(gid),
                rubrique_id=rubrique_id
            )
            db.session.add(assign)

        for cid in class_ids:
            assign = DocumentAssignment(
                document_id=document_id, 
                class_id=int(cid),
                rubrique_id=rubrique_id
            )
            db.session.add(assign)

        db.session.commit()
        flash("Affectations mises à jour")
        return redirect(url_for('document.documents'))

    users = User.query.filter_by(role='eleve').all()
    groups = Group.query.all()
    classes = SchoolClass.query.all()
    rubriques = Rubrique.query.all()

    existing = DocumentAssignment.query.filter_by(document_id=document_id).all()
    assigned_users = [a.user_id for a in existing if a.user_id]
    assigned_groups = [a.group_id for a in existing if a.group_id]
    assigned_classes = [a.class_id for a in existing if a.class_id]
    
    # Récupérer la rubrique si elle existe
    current_rubrique_id = None
    if existing and existing[0].rubrique_id:
        current_rubrique_id = existing[0].rubrique_id

    return render_template('assign_exercise.html',
                           exercise=document,
                           users=users,
                           groups=groups,
                           classes=classes,
                           rubriques=rubriques,
                           assigned_users=assigned_users,
                           assigned_groups=assigned_groups,
                           assigned_classes=assigned_classes,
                           current_rubrique_id=current_rubrique_id)

@csrf.exempt
@document_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    try:
        # Supprimer le fichier physique
        file_path = os.path.join('app', 'static', 'uploads', doc.filename.replace('/', os.sep))
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Supprimer l'enregistrement de la base de données
        db.session.delete(doc)
        db.session.commit()
        
        # Vérifier si le répertoire est vide et le supprimer si c'est le cas
        directory = os.path.dirname(file_path)
        if os.path.exists(directory) and not os.listdir(directory):
            os.rmdir(directory)
            
            # Vérifier si le répertoire parent est vide et le supprimer si c'est le cas
            parent_dir = os.path.dirname(directory)
            if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                os.rmdir(parent_dir)
        
        return '', 204
    except Exception as e:
        return str(e), 500

# Route pour corriger les chemins de fichiers existants
@document_bp.route('/fix_file_paths')
@login_required
def fix_file_paths():
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
    
    # Récupérer tous les documents
    documents = Document.query.all()
    fixed_count = 0
    
    for doc in documents:
        # Vérifier si le chemin contient des backslashes
        if '\\' in doc.filename:
            # Remplacer les backslashes par des slashes
            doc.filename = doc.filename.replace('\\', '/')
            fixed_count += 1
    
    # Sauvegarder les modifications
    if fixed_count > 0:
        db.session.commit()
        return f"Chemins corrigés pour {fixed_count} documents."
    else:
        return "Aucun chemin à corriger."

# Route pour afficher les chemins des fichiers dans la base de données
@document_bp.route('/debug_file_paths')
@login_required
def debug_file_paths():
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
    
    # Récupérer tous les documents
    documents = Document.query.all()
    
    # Créer une liste de dictionnaires avec les informations des documents
    docs_info = []
    for doc in documents:
        docs_info.append({
            'id': doc.id,
            'filename': doc.filename,
            'original_filename': doc.original_filename,
            'user_id': doc.user_id,
            'type': doc.type,
            'created_at': doc.created_at.strftime('%Y-%m-%d %H:%M:%S') if doc.created_at else None,
            'file_exists': os.path.exists(os.path.join('app', 'static', 'uploads', doc.filename.replace('/', os.sep)))
        })
    
    return jsonify(docs_info)

# Route pour servir directement un fichier
@document_bp.route('/view_document/<int:doc_id>')
@login_required
def view_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    # Chemin absolu du fichier
    base_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, '..', '..'))
    
    # Construire le chemin absolu du fichier
    file_path = os.path.join(project_root, 'app', 'static', 'uploads', doc.filename.replace('/', os.sep))
    
    # Vérifier si le fichier existe
    if os.path.exists(file_path):
        # Servir directement le fichier
        from flask import send_file
        return send_file(file_path, mimetype='application/pdf', as_attachment=False)
    
    # Si le fichier n'existe pas, essayer un autre chemin
    alt_file_path = os.path.join(project_root, 'static', 'uploads', doc.filename.replace('/', os.sep))
    if os.path.exists(alt_file_path):
        # Servir directement le fichier
        from flask import send_file
        return send_file(alt_file_path, mimetype='application/pdf', as_attachment=False)
    
    # Afficher les chemins essayés pour le débogage
    return f"Fichier non trouvé. Chemins essayés: {file_path}, {alt_file_path}", 404

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

# Routes pour la gestion des rubriques
@document_bp.route('/rubriques')
@login_required
def manage_rubriques():
    if current_user.role not in ['admin', 'professeur']:
        return "Accès non autorisé", 403
    
    rubriques = Rubrique.query.all()
    
    # Récupérer les labels pour le titre
    from app.lang.lang_fr import LABELS as labels_fr
    from app.lang.lang_en import LABELS as labels_en
    lang = request.cookies.get('lang', 'fr')
    labels = labels_fr if lang == 'fr' else labels_en
    
    return render_template('manage_rubriques.html', rubriques=rubriques, labels=labels)

@document_bp.route('/rubriques/add', methods=['POST'])
@login_required
def add_rubrique():
    if current_user.role not in ['admin', 'professeur']:
        return "Accès non autorisé", 403
    
    nom = request.form.get('nom')
    description = request.form.get('description', '')
    
    if not nom:
        flash("Le nom de la rubrique est obligatoire")
        return redirect(url_for('document.manage_rubriques'))
    
    rubrique = Rubrique(nom=nom, description=description)
    db.session.add(rubrique)
    db.session.commit()
    
    flash("Rubrique ajoutée avec succès")
    return redirect(url_for('document.manage_rubriques'))

@document_bp.route('/rubriques/edit', methods=['POST'])
@login_required
def edit_rubrique():
    if current_user.role not in ['admin', 'professeur']:
        return "Accès non autorisé", 403
    
    rubrique_id = request.form.get('rubrique_id')
    nom = request.form.get('nom')
    description = request.form.get('description', '')
    
    if not rubrique_id or not nom:
        flash("Informations incomplètes")
        return redirect(url_for('document.manage_rubriques'))
    
    rubrique = Rubrique.query.get_or_404(rubrique_id)
    rubrique.nom = nom
    rubrique.description = description
    
    db.session.commit()
    
    flash("Rubrique modifiée avec succès")
    return redirect(url_for('document.manage_rubriques'))

@csrf.exempt
@document_bp.route('/rubriques/delete/<int:rubrique_id>', methods=['POST'])
@login_required
def delete_rubrique(rubrique_id):
    if current_user.role not in ['admin', 'professeur']:
        return "Accès non autorisé", 403
    
    rubrique = Rubrique.query.get_or_404(rubrique_id)
    
    # Mettre à jour les affectations de documents pour supprimer la référence à cette rubrique
    DocumentAssignment.query.filter_by(rubrique_id=rubrique_id).update({DocumentAssignment.rubrique_id: None})
    
    db.session.delete(rubrique)
    db.session.commit()
    
    return '', 204

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}
