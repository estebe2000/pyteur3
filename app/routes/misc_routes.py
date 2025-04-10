from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db, csrf
from app.models import TodoList, TodoListAssignment, TodoItem, User, Group, SchoolClass

misc_bp = Blueprint('misc', __name__)

# TODO routes
@misc_bp.route('/todo', methods=['GET'])
@login_required
def todo():
    my_lists = TodoList.query.filter_by(owner_id=current_user.id).all()

    shared_lists = (
        TodoList.query.join(TodoListAssignment)
        .filter(TodoListAssignment.user_id == current_user.id)
        .all()
    )

    return render_template('todo.html', my_lists=my_lists, shared_lists=shared_lists)

@misc_bp.route('/todo/add_list', methods=['POST'])
@login_required
def add_todo_list():
    title = request.form.get('title')
    if title:
        new_list = TodoList(title=title, owner_id=current_user.id)
        db.session.add(new_list)
        db.session.commit()
        flash('Liste créée')

    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/rename_list/<int:list_id>', methods=['POST'])
@login_required
def rename_todo_list(list_id):
    todo_list = TodoList.query.get_or_404(list_id)
    if todo_list.owner_id != current_user.id:
        return "Accès non autorisé", 403

    title = request.form.get('title')
    if title:
        todo_list.title = title
        db.session.commit()
        flash('Liste renommée')

    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/delete_list/<int:list_id>', methods=['POST'])
@login_required
def delete_todo_list(list_id):
    todo_list = TodoList.query.get_or_404(list_id)
    if todo_list.owner_id != current_user.id:
        return "Accès non autorisé", 403

    db.session.delete(todo_list)
    db.session.commit()
    flash('Liste supprimée')

    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/add_item/<int:list_id>', methods=['POST'])
@login_required
def add_todo_item(list_id):
    todo_list = TodoList.query.get_or_404(list_id)

    if todo_list.owner_id != current_user.id and not any(
        assign.user_id == current_user.id for assign in todo_list.assignments
    ):
        return "Accès non autorisé", 403

    content = request.form.get('content')
    if content:
        item = TodoItem(content=content, list_id=list_id)
        db.session.add(item)
        db.session.commit()
        flash('Tâche ajoutée')

    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/toggle_item/<int:item_id>', methods=['POST'])
@login_required
def toggle_todo_item(item_id):
    item = TodoItem.query.get_or_404(item_id)
    todo_list = item.list

    if todo_list.owner_id != current_user.id and not any(
        assign.user_id == current_user.id for assign in todo_list.assignments
    ):
        return "Accès non autorisé", 403

    item.done = not item.done
    db.session.commit()
    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_todo_item(item_id):
    item = TodoItem.query.get_or_404(item_id)
    todo_list = item.list

    if todo_list.owner_id != current_user.id and not any(
        assign.user_id == current_user.id for assign in todo_list.assignments
    ):
        return "Accès non autorisé", 403

    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/edit_item/<int:item_id>', methods=['POST'])
@login_required
def edit_todo_item(item_id):
    item = TodoItem.query.get_or_404(item_id)
    todo_list = item.list

    if todo_list.owner_id != current_user.id and not any(
        assign.user_id == current_user.id for assign in todo_list.assignments
    ):
        return "Accès non autorisé", 403

    content = request.form.get('content')
    if content:
        item.content = content
        db.session.commit()

    return redirect(url_for('misc.todo'))

# Classes & groupes routes
@misc_bp.route('/classes', methods=['GET', 'POST'])
@login_required
def classes():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'class':
            nom = request.form.get('nom')
            niveau = request.form.get('niveau')
            if nom and niveau:
                new_class = SchoolClass(nom=nom, niveau=niveau)
                db.session.add(new_class)
                db.session.commit()
                flash('Classe créée avec succès')
            else:
                flash('Veuillez remplir tous les champs')
        elif form_type == 'group':
            nom = request.form.get('group_nom')
            class_id = request.form.get('class_id')
            if nom and class_id:
                new_group = Group(nom=nom, class_id=class_id)
                db.session.add(new_group)
                db.session.commit()
                flash('Groupe créé avec succès')
            else:
                flash('Veuillez remplir tous les champs')
        elif form_type == 'add_student_to_group':
            user_id = request.form.get('user_id')
            group_id = request.form.get('group_id')
            if user_id and group_id:
                user = User.query.get(user_id)
                user.group_id = group_id
                db.session.commit()
                flash('Élève ajouté au groupe')
            else:
                flash('Veuillez sélectionner un élève')
        return redirect(url_for('misc.classes', class_id=request.args.get('class_id'), group_id=request.args.get('group_id')))

    class_id = request.args.get('class_id', type=int)
    group_id = request.args.get('group_id', type=int)
    classes = SchoolClass.query.all()
    selected_class = None
    groups = []
    selected_group = None
    group_students = []
    unassigned_students = []
    if class_id:
        selected_class = SchoolClass.query.get(class_id)
        if selected_class:
            groups = Group.query.filter_by(class_id=class_id).all()
            if group_id:
                selected_group = Group.query.get(group_id)
                if selected_group:
                    group_students = selected_group.users
            unassigned_students = User.query.filter_by(group_id=None, role='eleve').all()
    return render_template('classes.html',
                           classes=classes,
                           selected_class=selected_class,
                           groups=groups,
                           selected_group=selected_group,
                           group_students=group_students,
                           unassigned_students=unassigned_students)

@misc_bp.route('/groups/remove_student/<int:user_id>', methods=['POST'])
@login_required
def remove_student_from_group(user_id):
    user = User.query.get_or_404(user_id)
    group = user.group
    user.group_id = None
    db.session.commit()
    flash('Élève retiré du groupe')
    return redirect(url_for('misc.classes', class_id=group.class_id, group_id=group.id))

@misc_bp.route('/classes/delete/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    school_class = SchoolClass.query.get_or_404(class_id)
    for group in school_class.groups:
        db.session.delete(group)
    db.session.delete(school_class)
    db.session.commit()
    flash('Classe supprimée avec succès')
    return redirect(url_for('misc.classes'))

@misc_bp.route('/groups/delete/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    class_id = group.class_id
    db.session.delete(group)
    db.session.commit()
    flash('Groupe supprimé avec succès')
    return redirect(url_for('misc.classes', class_id=class_id))

@misc_bp.route('/classes/edit/<int:class_id>', methods=['POST'])
@login_required
def edit_class(class_id):
    school_class = SchoolClass.query.get_or_404(class_id)
    nom = request.form.get('nom')
    niveau = request.form.get('niveau')
    if nom and niveau:
        school_class.nom = nom
        school_class.niveau = niveau
        db.session.commit()
        flash('Classe modifiée avec succès')
    else:
        flash('Veuillez remplir tous les champs')
    return redirect(url_for('misc.classes', class_id=class_id))

@misc_bp.route('/groups/edit/<int:group_id>', methods=['POST'])
@login_required
def edit_group(group_id):
    group = Group.query.get_or_404(group_id)
    nom = request.form.get('nom')
    if nom:
        group.nom = nom
        db.session.commit()
        flash('Groupe modifié avec succès')
    else:
        flash('Veuillez remplir le nom')
    return redirect(url_for('misc.classes', class_id=group.class_id))
