from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import User, Document, SchoolClass
from app import csrf

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def home():
    import datetime
    nb_eleves = User.query.filter_by(role='eleve').count()
    nb_profs = User.query.filter_by(role='professeur').count()
    nb_classes = SchoolClass.query.count()
    nb_exercices = Document.query.filter_by(type='exercise').count()
    nb_documents = Document.query.filter_by(type='document').count()
    return render_template('dashboard.html',
                           user=current_user,
                           now=datetime.datetime.now(),
                           nb_eleves=nb_eleves,
                           nb_profs=nb_profs,
                           nb_classes=nb_classes,
                           nb_exercices=nb_exercices,
                           nb_documents=nb_documents)

@dashboard_bp.route('/projets')
@login_required
def projets():
    return render_template('projets.html')

@dashboard_bp.route('/drive')
@login_required
def drive():
    return render_template('drive.html')

@dashboard_bp.route('/sandbox')
@login_required
def sandbox():
    # Vérifier si la requête vient d'un iframe
    is_iframe = request.args.get('iframe', 'false') == 'true'
    
    # Récupérer les labels pour le titre
    from app.lang.lang_fr import LABELS as labels_fr
    from app.lang.lang_en import LABELS as labels_en
    lang = request.cookies.get('lang', 'fr')
    labels = labels_fr if lang == 'fr' else labels_en
    
    if is_iframe:
        return render_template('sandbox.html', title=labels.get('sandbox', 'Bac à sable'))
    else:
        return render_template('sandbox.html')

@dashboard_bp.route('/ia')
@login_required
def ia():
    return render_template('ia.html')

@dashboard_bp.route('/statistiques')
@login_required
def statistiques():
    return render_template('statistiques.html')
