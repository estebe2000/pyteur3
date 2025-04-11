from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models import User, QcmAttempt, Homework, HomeworkCompletion, HomeworkResult
from datetime import datetime, timedelta
import json
from sqlalchemy import func, desc

student_performance_bp = Blueprint('student_performance', __name__)

@student_performance_bp.route('/api/student/qcm/stats/<int:student_id>')
@login_required
def get_qcm_stats(student_id):
    """
    Récupère les statistiques des QCM pour un élève donné
    """
    # Vérifier que l'utilisateur a le droit d'accéder à ces données
    if current_user.role != 'admin' and current_user.id != student_id:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Récupérer tous les résultats de QCM pour cet élève
    qcm_results = QcmAttempt.query.filter_by(student_id=student_id).all()
    
    if not qcm_results:
        return jsonify({
            'global': {
                'avg_score': 0,
                'total_attempts': 0
            },
            'by_qcm': [],
            'time_evolution': []
        })
    
    # Statistiques globales
    total_score = sum(result.score for result in qcm_results)
    avg_score = total_score / len(qcm_results)
    
    # Statistiques par QCM
    qcm_stats = {}
    for result in qcm_results:
        if result.qcm_id not in qcm_stats:
            qcm_stats[result.qcm_id] = {
                'qcm_id': result.qcm_id,
                'attempts': 0,
                'total_score': 0
            }
        
        qcm_stats[result.qcm_id]['attempts'] += 1
        qcm_stats[result.qcm_id]['total_score'] += result.score
    
    # Calculer les moyennes par QCM
    for qcm_id in qcm_stats:
        qcm_stats[qcm_id]['avg_score'] = qcm_stats[qcm_id]['total_score'] / qcm_stats[qcm_id]['attempts']
    
    # Évolution dans le temps (par semaine)
    time_evolution = []
    
    # Trier les résultats par date
    sorted_results = sorted(qcm_results, key=lambda x: x.created_at)
    
    # Regrouper par semaine
    weekly_stats = {}
    for result in sorted_results:
        # Obtenir le début de la semaine
        week_start = result.created_at.date() - timedelta(days=result.created_at.weekday())
        week_key = week_start.isoformat()
        
        if week_key not in weekly_stats:
            weekly_stats[week_key] = {
                'date': week_key,
                'total_score': 0,
                'count': 0
            }
        
        weekly_stats[week_key]['total_score'] += result.score
        weekly_stats[week_key]['count'] += 1
    
    # Calculer les moyennes par semaine
    for week_key in weekly_stats:
        weekly_stats[week_key]['avg_score'] = weekly_stats[week_key]['total_score'] / weekly_stats[week_key]['count']
        time_evolution.append({
            'date': weekly_stats[week_key]['date'],
            'avg_score': weekly_stats[week_key]['avg_score']
        })
    
    return jsonify({
        'global': {
            'avg_score': avg_score,
            'total_attempts': len(qcm_results)
        },
        'by_qcm': list(qcm_stats.values()),
        'time_evolution': time_evolution
    })

@student_performance_bp.route('/api/student/homework/stats/<int:student_id>')
@login_required
def get_homework_stats(student_id):
    """
    Récupère les statistiques des devoirs pour un élève donné
    """
    # Vérifier que l'utilisateur a le droit d'accéder à ces données
    if current_user.role != 'admin' and current_user.id != student_id:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Récupérer l'utilisateur
    student = User.query.get(student_id)
    if not student:
        return jsonify({'error': 'Élève non trouvé'}), 404
        
    # Récupérer les devoirs assignés à la classe ou au groupe de l'élève
    homeworks = []
    if student.class_id:
        class_homeworks = Homework.query.filter_by(class_id=student.class_id).all()
        homeworks.extend(class_homeworks)
    if student.group_id:
        group_homeworks = Homework.query.filter_by(group_id=student.group_id).all()
        homeworks.extend(group_homeworks)
    
    # Récupérer les complétions de devoirs pour cet élève
    completions = HomeworkCompletion.query.filter_by(student_id=student_id).all()
    completion_hw_ids = [c.homework_id for c in completions]
    
    if not homeworks:
        return jsonify({
            'global': {
                'avg_score': 0,
                'total_completed': 0,
                'total_late': 0
            },
            'by_subject': [],
            'time_evolution': []
        })
    
    # Récupérer les résultats de devoirs
    results = []
    for completion in completions:
        result = HomeworkResult.query.filter_by(completion_id=completion.id).first()
        if result:
            results.append(result)
    
    # Statistiques globales
    total_completed = len(completions)
    
    if results:
        total_score = sum(result.score for result in results if result.score is not None)
        scored_results = [result for result in results if result.score is not None]
        avg_score = total_score / len(scored_results) if scored_results else 0
    else:
        avg_score = 0
    
    total_late = sum(1 for result in results if result.is_late)
    
    # Créer un dictionnaire pour associer les devoirs à leurs complétions et résultats
    homework_dict = {hw.id: hw for hw in homeworks}
    completion_dict = {c.homework_id: c for c in completions}
    result_dict = {}
    for completion in completions:
        result = HomeworkResult.query.filter_by(completion_id=completion.id).first()
        if result:
            result_dict[completion.homework_id] = result
    
    # Statistiques par matière
    subject_stats = {}
    for hw_id, completion in completion_dict.items():
        hw = homework_dict.get(hw_id)
        result = result_dict.get(hw_id)
        
        if not hw or not result or result.score is None:
            continue
            
        subject = hw.subject or 'Non spécifiée'
        if subject not in subject_stats:
            subject_stats[subject] = {
                'subject': subject,
                'completed': 0,
                'total_score': 0
            }
        
        subject_stats[subject]['completed'] += 1
        subject_stats[subject]['total_score'] += result.score
    
    # Calculer les moyennes par matière
    for subject in subject_stats:
        subject_stats[subject]['avg_score'] = subject_stats[subject]['total_score'] / subject_stats[subject]['completed']
    
    # Évolution dans le temps (par mois)
    time_evolution = []
    
    # Préparer les données pour l'évolution dans le temps
    time_data = []
    for hw_id, completion in completion_dict.items():
        result = result_dict.get(hw_id)
        if result and result.score is not None:
            time_data.append({
                'date': completion.completed_at,
                'score': result.score
            })
    
    # Trier par date
    time_data.sort(key=lambda x: x['date'])
    
    # Regrouper par mois
    monthly_stats = {}
    for data in time_data:
        # Obtenir le début du mois
        month_key = data['date'].strftime('%Y-%m-01')
        
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {
                'date': month_key,
                'total_score': 0,
                'count': 0
            }
        
        monthly_stats[month_key]['total_score'] += data['score']
        monthly_stats[month_key]['count'] += 1
    
    # Calculer les moyennes par mois
    for month_key in monthly_stats:
        monthly_stats[month_key]['avg_score'] = monthly_stats[month_key]['total_score'] / monthly_stats[month_key]['count']
        time_evolution.append({
            'date': monthly_stats[month_key]['date'],
            'avg_score': monthly_stats[month_key]['avg_score']
        })
    
    return jsonify({
        'global': {
            'avg_score': avg_score,
            'total_completed': total_completed,
            'total_late': total_late
        },
        'by_subject': list(subject_stats.values()),
        'time_evolution': time_evolution
    })

@student_performance_bp.route('/api/student/qcm/history/<int:student_id>')
@login_required
def get_qcm_history(student_id):
    """
    Récupère l'historique des QCM pour un élève donné
    """
    # Vérifier que l'utilisateur a le droit d'accéder à ces données
    if current_user.role != 'admin' and current_user.id != student_id:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Récupérer tous les résultats de QCM pour cet élève, triés par date (les plus récents d'abord)
    qcm_results = QcmAttempt.query.filter_by(student_id=student_id).order_by(QcmAttempt.created_at.desc()).all()
    
    results = []
    for result in qcm_results:
        results.append({
            'id': result.id,
            'qcm_id': result.qcm_id,
            'score': result.score,
            'total_questions': result.total_questions,
            'correct_answers': result.correct_answers,
            'created_at': result.created_at.isoformat()
        })
    
    return jsonify({
        'results': results
    })

@student_performance_bp.route('/api/student/homework/history/<int:student_id>')
@login_required
def get_homework_history(student_id):
    """
    Récupère l'historique des devoirs pour un élève donné
    """
    # Vérifier que l'utilisateur a le droit d'accéder à ces données
    if current_user.role != 'admin' and current_user.id != student_id:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Récupérer l'utilisateur
    student = User.query.get(student_id)
    if not student:
        return jsonify({'error': 'Élève non trouvé'}), 404
        
    # Récupérer les devoirs assignés à la classe ou au groupe de l'élève
    homeworks = []
    if student.class_id:
        class_homeworks = Homework.query.filter_by(class_id=student.class_id).order_by(Homework.due_date.desc()).all()
        homeworks.extend(class_homeworks)
    if student.group_id:
        group_homeworks = Homework.query.filter_by(group_id=student.group_id).order_by(Homework.due_date.desc()).all()
        homeworks.extend(group_homeworks)
    
    # Récupérer les complétions de devoirs pour cet élève
    completions = HomeworkCompletion.query.filter_by(student_id=student_id).all()
    completion_dict = {c.homework_id: c for c in completions}
    
    # Récupérer les résultats de devoirs
    results_dict = {}
    for completion in completions:
        result = HomeworkResult.query.filter_by(completion_id=completion.id).first()
        if result:
            results_dict[completion.homework_id] = result
    
    results = []
    for hw in homeworks:
        completion = completion_dict.get(hw.id)
        result = results_dict.get(hw.id)
        
        status = "Non commencé"
        if completion:
            status = "Terminé"
        elif hw.due_date and hw.due_date < datetime.now().date():
            status = "En retard"
        else:
            status = "À faire"
        
        results.append({
            'id': hw.id,
            'title': hw.title,
            'subject': hw.subject,
            'due_date': hw.due_date.isoformat() if hw.due_date else None,
            'completed_at': completion.completed_at.isoformat() if completion else None,
            'status': status,
            'score': result.score if result else None,
            'is_late': result.is_late if result else False
        })
    
    return jsonify({
        'results': results
    })

@student_performance_bp.route('/api/student/metrics/<int:student_id>')
@login_required
def get_student_metrics(student_id):
    """
    Récupère les métriques de performance pour un élève donné
    """
    # Vérifier que l'utilisateur a le droit d'accéder à ces données
    if current_user.role != 'admin' and current_user.id != student_id:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Récupérer les moyennes des QCM par mois
    qcm_results = QcmAttempt.query.filter_by(student_id=student_id).all()
    
    # Regrouper par mois
    monthly_qcm_avg = {}
    for result in qcm_results:
        month_key = result.created_at.strftime('%Y-%m')
        
        if month_key not in monthly_qcm_avg:
            monthly_qcm_avg[month_key] = {
                'month': month_key,
                'total_score': 0,
                'count': 0
            }
        
        monthly_qcm_avg[month_key]['total_score'] += result.score
        monthly_qcm_avg[month_key]['count'] += 1
    
    # Calculer les moyennes par mois
    qcm_avg = []
    for month_key in monthly_qcm_avg:
        avg = monthly_qcm_avg[month_key]['total_score'] / monthly_qcm_avg[month_key]['count']
        qcm_avg.append({
            'month': month_key,
            'value': avg
        })
    
    # Trier par mois (les plus récents d'abord)
    qcm_avg.sort(key=lambda x: x['month'], reverse=True)
    
    return jsonify({
        'qcm_avg': qcm_avg
    })

@student_performance_bp.route('/api/student/recommendations/<int:student_id>')
@login_required
def get_student_recommendations(student_id):
    """
    Récupère les recommandations personnalisées pour un élève donné
    """
    # Vérifier que l'utilisateur a le droit d'accéder à ces données
    if current_user.role != 'admin' and current_user.id != student_id:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Récupérer les résultats de QCM pour cet élève
    qcm_results = QcmAttempt.query.filter_by(student_id=student_id).all()
    
    # Générer des recommandations basées sur les résultats
    recommendations = []
    
    # Identifier les QCM avec des scores faibles
    qcm_stats = {}
    for result in qcm_results:
        if result.qcm_id not in qcm_stats:
            qcm_stats[result.qcm_id] = []
        
        qcm_stats[result.qcm_id].append(result.score)
    
    # Pour chaque QCM, vérifier si le score moyen est faible
    for qcm_id, scores in qcm_stats.items():
        avg_score = sum(scores) / len(scores)
        
        if avg_score < 60:
            # Recommander de refaire ce QCM
            recommendations.append({
                'id': len(recommendations) + 1,
                'recommendation_type': 'qcm',
                'content_id': qcm_id,
                'reason': f'Votre score moyen pour ce QCM est de {avg_score:.1f}%. Refaites-le pour améliorer votre compréhension.',
                'priority': 4 if avg_score < 40 else 3
            })
    
    # Ajouter quelques recommandations génériques
    if len(recommendations) < 3:
        recommendations.append({
            'id': len(recommendations) + 1,
            'recommendation_type': 'resource',
            'content_id': 'subject:Algorithmique',
            'reason': 'Réviser les concepts fondamentaux d\'algorithmique pour améliorer vos performances.',
            'priority': 2
        })
        
        recommendations.append({
            'id': len(recommendations) + 1,
            'recommendation_type': 'exercise',
            'content_id': 'Exercice de tri',
            'reason': 'Pratiquer les algorithmes de tri pour renforcer vos compétences.',
            'priority': 2
        })
    
    return jsonify({
        'results': recommendations
    })

@student_performance_bp.route('/api/student/recommendations/mark_completed/<int:recommendation_id>', methods=['POST'])
@login_required
def mark_recommendation_completed(recommendation_id):
    """
    Marque une recommandation comme complétée
    """
    # Dans une implémentation réelle, nous stockerions les recommandations dans la base de données
    # et nous mettrions à jour leur statut. Pour cette démonstration, nous retournons simplement un succès.
    
    return jsonify({
        'success': True,
        'message': 'Recommandation marquée comme complétée'
    })

@student_performance_bp.route('/api/student/qcm/submit', methods=['POST'])
@login_required
def submit_qcm_result():
    """
    Enregistre un résultat de QCM
    """
    data = request.json
    
    # Vérifier que l'utilisateur a le droit d'accéder à ces données
    if current_user.role != 'admin' and current_user.id != data.get('student_id'):
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Créer un nouvel enregistrement de résultat QCM
    qcm_result = QcmAttempt(
        student_id=data.get('student_id'),
        qcm_id=data.get('qcm_id'),
        score=data.get('score'),
        total_questions=data.get('total_questions'),
        correct_answers=data.get('correct_answers'),
        time_spent=data.get('time_spent'),
        metadata=json.dumps(data.get('metadata', {}))
    )
    
    # Enregistrer dans la base de données
    from app import db
    db.session.add(qcm_result)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Résultat QCM enregistré avec succès',
        'result_id': qcm_result.id
    })
