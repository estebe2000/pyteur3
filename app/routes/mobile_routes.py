from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app, send_file, flash
from flask_login import current_user

mobile_bp = Blueprint('mobile', __name__, url_prefix='/mobile')

@mobile_bp.route('/')
def index():
    return render_template('mobile/index.html')
