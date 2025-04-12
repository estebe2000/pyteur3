from flask import Blueprint, render_template
from flask_login import login_required, current_user

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/document-viewer')
@login_required
def debug_document_viewer():
    """Page de débogage pour la fenêtre de visualisation de document."""
    # Vérifier si l'utilisateur est un administrateur
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
    
    return render_template('debug-document-viewer.html')

@debug_bp.route('/debug/test-document-viewer')
@login_required
def test_document_viewer():
    """Page de test pour la fenêtre de visualisation de document."""
    # Vérifier si l'utilisateur est un administrateur
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
    
    return render_template('test-document-viewer.html')
