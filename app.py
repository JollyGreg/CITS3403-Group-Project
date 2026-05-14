import os
import sys
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from dotenv import load_dotenv

# Ensure the current directory is in the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User, Match, Game, Message
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
        # Query top 5 users by wins for the leaderboard
        top_users = User.query.order_by(User.wins.desc()).limit(5).all()
        return render_template("index.html", 
                               current_user=current_user, 
                               login_form=login_form, 
                               register_form=register_form,
                               top_users=top_users)

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        # validate_on_submit handles CSRF token check and form validation
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for('index'))
            flash("Invalid username or password.", "danger")
        else:
            # Flash validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", "danger")
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
            flash("Account created successfully!", "success")
            return redirect(url_for('index'))
        else:
            # Flash validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", "danger")
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
        # Query recent matches where the current user was either white or black player
        recent_matches = Match.query.filter(
            (Match.white_player_id == current_user.id) | 
            (Match.black_player_id == current_user.id)
        ).order_by(Match.date.desc()).limit(10).all()

        # Add opponent name to each match for display
        for match in recent_matches:
            if match.white_player_id == current_user.id:
                match.opponent_name = match.black_player.username if match.black_player else 'Unknown'
            else:
                match.opponent_name = match.white_player.username if match.white_player else 'Unknown'

        return render_template("profile.html", current_user=current_user, recent_matches=recent_matches)

    # Game API Routes 

    @app.route('/api/game/create', methods=['POST'])
    @login_required
    def create_game():
        # Check if player already has a waiting game
        existing = Game.query.filter_by(player1_id=current_user.id, status='waiting').first()
        if existing:
            return jsonify({'success': True, 'game_id': existing.id, 'status': 'waiting'})
        
        # Create a new game and wait for opponent
        game = Game(player1_id=current_user.id, status='waiting')
        db.session.add(game)
        db.session.commit()
        return jsonify({'success': True, 'game_id': game.id, 'status': 'waiting'})

    @app.route('/api/game/join', methods=['POST'])
    @login_required
    def join_game():
        # Find a waiting game that the current user didn't create
        game = Game.query.filter_by(status='waiting').filter(
            Game.player1_id != current_user.id
        ).first()
        
        if not game:
            return jsonify({'success': False, 'message': 'No games available'})
        
        # Join the game as player 2
        game.player2_id = current_user.id
        game.status = 'active'
        db.session.commit()
        return jsonify({'success': True, 'game_id': game.id, 'status': 'active'})

    @app.route('/api/game/<int:game_id>/state', methods=['GET'])
    @login_required
    def get_game_state(game_id):
        game = Game.query.get_or_404(game_id)
        
        # Only players in this game can see state
        if current_user.id not in [game.player1_id, game.player2_id]:
            return jsonify({'error': 'Not a player in this game'}), 403
        
        return jsonify({
            'game_id': game.id,
            'status': game.status,
            'current_turn': game.current_turn,
            'board_state': game.get_board(),
            'player1': game.player1.username,
            'player2': game.player2.username if game.player2 else None,
            'your_colour': 'white' if game.player1_id == current_user.id else 'black'
        })

    @app.route('/api/game/<int:game_id>/move', methods=['POST'])
    @login_required
    def make_move(game_id):
        game = Game.query.get_or_404(game_id)
        
        # Verify player is in this game
        if current_user.id not in [game.player1_id, game.player2_id]:
            return jsonify({'error': 'Not a player in this game'}), 403
        
        # Verify it is this player's turn
        player_colour = 'white' if game.player1_id == current_user.id else 'black'
        if game.current_turn != player_colour:
            return jsonify({'success': False, 'message': 'Not your turn'})
        
        data = request.get_json()
        
        # Save the new board state
        game.set_board(data['board_state'])
        
        # Switch turns
        game.current_turn = 'black' if game.current_turn == 'white' else 'white'
        db.session.commit()
        
        return jsonify({'success': True, 'current_turn': game.current_turn})

    @app.route('/api/game/<int:game_id>/messages', methods=['GET'])
    @login_required
    def get_messages(game_id):
        game = Game.query.get_or_404(game_id)
        
        # Only players in this game can see messages
        if current_user.id not in [game.player1_id, game.player2_id]:
            return jsonify({'error': 'Not a player in this game'}), 403
        
        # Fetch messages for this specific game
        messages = Message.query.filter_by(game_id=game_id).order_by(Message.timestamp.asc()).all()
        return jsonify([{
            'sender': m.sender.username,
            'content': m.content,
            'timestamp': m.timestamp.strftime('%H:%M')
        } for m in messages])

    @app.route('/api/game/<int:game_id>/message', methods=['POST'])
    @login_required
    def send_message(game_id):
        game = Game.query.get_or_404(game_id)
        
        # Only players in this game can send messages
        if current_user.id not in [game.player1_id, game.player2_id]:
            return jsonify({'error': 'Not a player in this game'}), 403
        
        data = request.get_json()
        msg = Message(game_id=game_id, sender_id=current_user.id, content=data['content'])
        db.session.add(msg)
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/api/game/<int:game_id>/end', methods=['POST'])
    @login_required
    def end_game(game_id):
        game = Game.query.get_or_404(game_id)
        
        # Mark game as finished
        game.status = 'finished'

        # Update winner's stats
        winner_id = game.player1_id if game.current_turn == 'black' else game.player2_id
        winner = User.query.get(winner_id)
        if winner:
            winner.wins += 1
            winner.matches_played += 1
    
        # Update loser's stats
        loser_id = game.player2_id if winner_id == game.player1_id else game.player1_id
        loser = User.query.get(loser_id)
        if loser:
            loser.matches_played += 1

        db.session.commit()
        return jsonify({'success': True})

    @app.route('/api/messages', methods=['GET'])
    @login_required
    def get_messages():
        # Fetch the 50 most recent messages ordered by time
        messages = Message.query.order_by(Message.timestamp.asc()).limit(50).all()
        return jsonify([{
            'sender': m.sender.username,
            'content': m.content,
            'timestamp': m.timestamp.strftime('%H:%M')
        } for m in messages])

    @app.route('/api/messages', methods=['POST'])
    @login_required
    def send_message():
        # Save a new message from the current user to the database
        data = request.get_json()
        msg = Message(sender_id=current_user.id, content=data['content'])
        db.session.add(msg)
        db.session.commit()
        return jsonify({'success': True})

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)