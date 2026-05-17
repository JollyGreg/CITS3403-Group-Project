import os
import sys
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit, join_room
from flask_migrate import Migrate

# Ensure the current directory is in the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User, Match, Game, Message
from forms import LoginForm, RegisterForm
from elo import record_match_with_elo

load_dotenv()

socketio = SocketIO()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Configuration - use environment variables with fallbacks
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-uwa-project')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///chess.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
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
        login_form = LoginForm()
        register_form = RegisterForm()
        # Top 5 users by ELO for the leaderboard
        top_users = User.query.order_by(User.elo_rating.desc()).limit(5).all()
        return render_template("index.html", 
                               current_user=current_user, 
                               login_form=login_form, 
                               register_form=register_form,
                               top_users=top_users)

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for('index'))
            flash("Invalid username or password.", "danger")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", "danger")
        #When the login fails, do not refresh the page. Instead, re-render the home page with the original data.
        register_form = RegisterForm()
        top_users = User.query.order_by(User.elo_rating.desc()).limit(5).all()
        return render_template("index.html", 
                               current_user=current_user, 
                               login_form=form, 
                               register_form=register_form,
                               top_users=top_users,
                               active_tab='login') #Keep the login page open

    @app.route("/register", methods=['POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash("Username already exists.", "danger")

                #If the username already exists, do not refresh the page.
                login_form = LoginForm()
                top_users = User.query.order_by(User.elo_rating.desc()).limit(5).all()
                return render_template("index.html", 
                                       current_user=current_user, 
                                       login_form=login_form, 
                                       register_form=form, 
                                       top_users=top_users, 
                                       active_tab='register') #Keep the registration page open
            
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Account created successfully!", "success")
            return redirect(url_for('index'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", "danger")
        #If the password is too weak and the verification fails, the page will not be refreshed either.
        login_form = LoginForm()
        top_users = User.query.order_by(User.elo_rating.desc()).limit(5).all()
        return render_template("index.html", 
                               current_user=current_user, 
                               login_form=login_form, 
                               register_form=form,
                               top_users=top_users,
                               active_tab='register')

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
        recent_matches = Match.query.filter(
            (Match.white_player_id == current_user.id) | 
            (Match.black_player_id == current_user.id)
        ).order_by(Match.date.desc()).limit(10).all()

        for match in recent_matches:
            if match.white_player_id == current_user.id:
                match.opponent_name = match.black_player.username if match.black_player else 'Unknown'
            else:
                match.opponent_name = match.white_player.username if match.white_player else 'Unknown'

        return render_template("profile.html", current_user=current_user, recent_matches=recent_matches)
        
    @app.route("/user/<username>")
    def user_profile(username):
        
        user = User.query.filter_by(username=username).first_or_404()
    
    
        recent_matches = Match.query.filter(
            (Match.white_player_id == user.id) | 
            (Match.black_player_id == user.id)
        ).order_by(Match.date.desc()).limit(10).all()

        for match in recent_matches:
            if match.white_player_id == user.id:
                match.opponent_name = match.black_player.username if match.black_player else 'Unknown'
            else:
                match.opponent_name = match.white_player.username if match.white_player else 'Unknown'

    
        return render_template("user_profile.html", profile_user=user, recent_matches=recent_matches)


        

    # --- Game API Routes ---

    @app.route('/api/game/create', methods=['POST'])
    @login_required
    def create_game():
        existing = Game.query.filter_by(player1_id=current_user.id, status='waiting').first()
        if existing:
            return jsonify({'success': True, 'game_id': existing.id, 'status': 'waiting'})
        
        game = Game(player1_id=current_user.id, status='waiting')
        db.session.add(game)
        db.session.commit()
        return jsonify({'success': True, 'game_id': game.id, 'status': 'waiting'})

    @app.route('/api/game/join', methods=['POST'])
    @login_required
    def join_game():
        game = Game.query.filter_by(status='waiting').filter(
            Game.player1_id != current_user.id
        ).first()
        
        if not game:
            return jsonify({'success': False, 'message': 'No games available'})
        
        game.player2_id = current_user.id
        game.status = 'active'
        db.session.commit()

        # Notify the waiting player via WebSocket
        socketio.emit('opponent_joined', {
            'game_id': game.id,
            'player1': game.player1.username,
            'player2': current_user.username,
            'current_turn': game.current_turn
        })
        return jsonify({'success': True, 'game_id': game.id, 'status': 'active'})

    @app.route('/api/game/<int:game_id>/state', methods=['GET'])
    @login_required
    def get_game_state(game_id):
        game = Game.query.get_or_404(game_id)
        
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
        
        if current_user.id not in [game.player1_id, game.player2_id]:
            return jsonify({'error': 'Not a player in this game'}), 403
        
        player_colour = 'white' if game.player1_id == current_user.id else 'black'
        if game.current_turn != player_colour:
            return jsonify({'success': False, 'message': 'Not your turn'})
        
        data = request.get_json()
        game.set_board(data['board_state'])
        game.current_turn = 'black' if game.current_turn == 'white' else 'white'
        db.session.commit()
        
        return jsonify({'success': True, 'current_turn': game.current_turn})

    @app.route('/api/game/<int:game_id>/messages', methods=['GET'])
    @login_required
    def get_messages(game_id):
        game = Game.query.get_or_404(game_id)
        
        if current_user.id not in [game.player1_id, game.player2_id]:
            return jsonify({'error': 'Not a player in this game'}), 403
        
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

        # Only players in this game can end it
        if current_user.id not in [game.player1_id, game.player2_id]:
            return jsonify({'error': 'Not a player in this game'}), 403

        # Ignore if already finished (prevents duplicate calls)
        if game.status == 'finished':
            return jsonify({'success': False, 'message': 'Game already finished'})

        data = request.get_json()
        # Expects: 'white_win' | 'black_win' | 'draw'
        result = data.get('result', 'draw')
        if result not in ('white_win', 'black_win', 'draw'):
            return jsonify({'success': False, 'message': f'Invalid result: {result}'}), 400

        white_player = User.query.get(game.player1_id)
        black_player = User.query.get(game.player2_id)

        if not white_player or not black_player:
            return jsonify({'success': False, 'message': 'Players not found'}), 404

        # Snapshot ELO BEFORE updating so the Match row records the delta correctly
        white_elo_before = white_player.elo_rating
        black_elo_before = black_player.elo_rating

        elo_changes = record_match_with_elo(white_player, black_player, result)

        # Persist match with full ELO history
        match = Match(
            white_player_id=game.player1_id,
            black_player_id=game.player2_id,
            result=result,
            mode='1v1 Quick Match',
            white_elo_before=white_elo_before,
            white_elo_after=white_player.elo_rating,
            black_elo_before=black_elo_before,
            black_elo_after=black_player.elo_rating,
        )
        db.session.add(match)

        # Mark the game as finished
        game.status = 'finished'
        db.session.commit()
        return jsonify({'success': True})

    # Player joins a socket room for their specific game, this ensures events are only sent to players in that game
    @socketio.on('join_game')
    def handle_join(data):
        game_id = data['game_id']
        join_room(f'game_{game_id}')

    # Handles a move from a player, saves board state to database then broadcasts the updated board to both players in the game room
    @socketio.on('make_move')
    def handle_move(data):
        game_id = data['game_id']
        game = Game.query.get(game_id)
        if not game:
            return
        game.set_board(data['board_state'])
        game.current_turn = 'black' if game.current_turn == 'white' else 'white'
        db.session.commit()
        emit('board_update', {
            'board_state': game.get_board(),
            'current_turn': game.current_turn,
            'player1': game.player1.username,
            'player2': game.player2.username if game.player2 else None
        }, room=f'game_{game_id}')

    # Handles a chat message and saves it to the database, then broadcasts it to both players in the game room
    @socketio.on('send_message')
    def handle_message(data):
        game_id = data['game_id']
        msg = Message(game_id=game_id, sender_id=data['sender_id'], content=data['content'])
        db.session.add(msg)
        db.session.commit()
        emit('new_message', {
            'sender': data['sender'],
            'content': data['content'],
            'timestamp': msg.timestamp.strftime('%H:%M')
        }, room=f'game_{game_id}')

    @socketio.on('draw_offer')
    def handle_draw_offer(data):
        game_id = data['game_id']
        # Broadcast to the room; the sender's client filters by username
        emit('draw_offered', {
            'from': data['from'],
            'game_id': game_id
        }, room=f'game_{game_id}')

    @socketio.on('draw_response')
    def handle_draw_response(data):
        game_id = data['game_id']
        emit('draw_responded', {
            'accepted': data['accepted'],
            'from': data['from']
        }, room=f'game_{game_id}')

    # Handles game over with ELO updates, records match history, then broadcasts game over message
    @socketio.on('end_game')
    def handle_end_game(data):
        game_id = data['game_id']
        game = Game.query.get(game_id)
        if not game or game.status == 'finished':
            return
        result = data.get('result', 'white_win')
        white_player = User.query.get(game.player1_id)
        black_player = User.query.get(game.player2_id)
        if not white_player or not black_player:
            return
        white_elo_before = white_player.elo_rating
        black_elo_before = black_player.elo_rating
        elo_changes = record_match_with_elo(white_player, black_player, result)
        match = Match(
            white_player_id=game.player1_id,
            black_player_id=game.player2_id,
            result=result,
            mode='1v1 Quick Match',
            white_elo_before=white_elo_before,
            white_elo_after=white_player.elo_rating,
            black_elo_before=black_elo_before,
            black_elo_after=black_player.elo_rating,
        )
        db.session.add(match)
        game.status = 'finished'
        db.session.commit()
        emit('game_over', {
            'message': f'{data.get("winner", "Someone")} wins!',
            'white_elo_change': elo_changes['white_change'],
            'black_elo_change': elo_changes['black_change']
        }, room=f'game_{game_id}')

    return app


app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)