import os
import sys
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from dotenv import load_dotenv

# Ensure the current directory is in the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User, Match
from forms import LoginForm, RegisterForm

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    
    # Configuration - use environment variables with fallbacks
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-uwa-project')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///chess.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Routes ---

    @app.route("/")
    def index():
        # Initialize forms to be rendered in the index.html modal
        login_form = LoginForm()
        register_form = RegisterForm()
        return render_template("index.html", 
                               current_user=current_user, 
                               login_form=login_form, 
                               register_form=register_form)

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        # validate_on_submit handles CSRF token check and form validation
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for('play'))
            flash("Invalid username or password.", "danger")
        return redirect(url_for('index'))

    @app.route("/register", methods=['POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            # Check if username already exists
            if User.query.filter_by(username=form.username.data).first():
                flash("Username already exists.", "danger")
                return redirect(url_for('index'))
            
            # Create new user and hash password
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            
            # Log the user in immediately after registration
            login_user(user)
            return redirect(url_for('play'))
        return redirect(url_for('index'))

    @app.route("/play")
    @login_required
    def play():
        return render_template("chessboard.html", current_user=current_user)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route("/profile")
    @login_required
    def profile():
        # TODO: Query recent matches from the database to pass to the template
        # recent_matches = Match.query.filter_by(...) 
        return render_template("profile.html", current_user=current_user)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)