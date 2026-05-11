from flask import Flask, request, render_template, redirect
from flask_login import LoginManager, current_user, login_user, logout_user
import os
import sys
from dotenv import load_dotenv

# Ensure current directory is in path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///chess.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Simple form placeholder (replace with WTForms when ready)
    class FormPlaceholder:
        def hidden_tag(self):
            return ""
    
    @app.route("/")
    def index():
        return render_template("index.html", current_user=current_user, login_form=FormPlaceholder(), register_form=FormPlaceholder())
    
    @app.route("/play")
    def play():
        return render_template("chessboard.html", current_user=current_user)
    
    @app.route("/login", methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                return render_template("index.html", current_user=current_user, 
                                     login_form=FormPlaceholder(), register_form=FormPlaceholder(),
                                     error="Username and password are required.")
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect("/play")
            
            return render_template("index.html", current_user=current_user,
                                 login_form=FormPlaceholder(), register_form=FormPlaceholder(),
                                 error="Invalid username or password.")
        
        return render_template("index.html", current_user=current_user, login_form=FormPlaceholder(), register_form=FormPlaceholder())
    
    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not all([username, email, password, confirm_password]):
                return render_template("index.html", current_user=current_user,
                                     login_form=FormPlaceholder(), register_form=FormPlaceholder(),
                                     error="All fields are required.")
            
            if password != confirm_password:
                return render_template("index.html", current_user=current_user,
                                     login_form=FormPlaceholder(), register_form=FormPlaceholder(),
                                     error="Passwords do not match.")
            
            if User.query.filter_by(username=username).first():
                return render_template("index.html", current_user=current_user,
                                     login_form=FormPlaceholder(), register_form=FormPlaceholder(),
                                     error="Username already exists.")
            
            if User.query.filter_by(email=email).first():
                return render_template("index.html", current_user=current_user,
                                     login_form=FormPlaceholder(), register_form=FormPlaceholder(),
                                     error="Email already exists.")
            
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            return redirect("/play")
        
        return render_template("index.html", current_user=current_user, login_form=FormPlaceholder(), register_form=FormPlaceholder())
    
    @app.route("/logout")
    def logout():
        logout_user()
        return redirect("/")
    
    @app.route("/profile")
    def profile():
        return render_template("profile.html", current_user=current_user)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run()
