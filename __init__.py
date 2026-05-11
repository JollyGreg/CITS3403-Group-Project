from flask import Flask, request, render_template, redirect
from flask_login import LoginManager, current_user, UserMixin

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple form placeholder (replace with WTForms when ready)
class FormPlaceholder:
    def hidden_tag(self):
        return ""

# Placeholder user loader (replace with real user lookup when database is ready)
@login_manager.user_loader
def load_user(user_id):
    return None

@app.route("/")
def index():
    return render_template("index.html", current_user=current_user, login_form=FormPlaceholder(), register_form=FormPlaceholder())

@app.route("/play")
def play():
    return render_template("chessboard.html", current_user=current_user)

@app.route("/login", methods=['GET', 'POST'])
def login():
    # Placeholder - implement login logic
    return render_template("index.html", current_user=current_user, login_form=FormPlaceholder(), register_form=FormPlaceholder())

@app.route("/register", methods=['GET', 'POST'])
def register():
    # Placeholder - implement registration logic
    return render_template("index.html", current_user=current_user, login_form=FormPlaceholder(), register_form=FormPlaceholder())

@app.route("/logout")
def logout():
    # Placeholder - implement logout logic
    return redirect("/")

@app.route("/profile")
def profile():
    # Placeholder - implement profile page
    return render_template("profile.html", current_user=current_user)

if __name__ == '__main__':
    app.run()