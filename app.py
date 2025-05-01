import eventlet
from eventlet import wsgi
eventlet.monkey_patch()

import os
import processing as proc
import time

from flask import Flask, render_template, request, url_for, flash, redirect, jsonify, session
from datetime import datetime
from turbo_flask import Turbo
from flask_socketio import SocketIO, emit

from functools import wraps

app = Flask(__name__)
turbo = Turbo(app)
app.config['SECRET_KEY'] = 'your secret key' # should be a long random string: generate one
DEVICE_PASSWORD = "18500-lohiththegoat"

# Lock

# Wrappers
def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped_view

# Game Start wrapper
def start_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get('game_start'):
            return redirect(url_for('game_settings'))
        return view_func(*args, **kwargs)
    return wrapped_view

socketio = SocketIO(app, async_mode='eventlet', manage_session=False)
game_state = proc.GameState()

# Pre-game pages
# Application entry page
@app.route('/', methods=('GET', 'POST'))
def login():
    session.clear()
    if request.method == 'POST':
        if request.form['password'] == DEVICE_PASSWORD:
            session['authenticated'] = True

            return redirect(url_for("warning"))
        else:
            flash("Incorrect password")
    return render_template('login.html')

@app.route('/warning', methods=('GET', 'POST'))
@login_required
def warning():
    if request.method == 'POST':
        return redirect(url_for("game_settings"))
    
    return render_template('warning.html')

# Intermediate page to clear the game state
@app.route('/clear_and_home')
def clear_and_home():
    session.clear()
    return redirect(url_for("login"))

# Page where game settings are inputted
@app.route('/game_settings', methods=('GET', 'POST'))
@login_required
def game_settings():
    if request.method == 'POST':
        counting_technique = request.form.get('counting-technique')
        betting_strategy = request.form.get('betting-strategy')
        player_pos = request.form.get('player-position', type=int)
        num_shoes = request.form.get('num-shoes', type=int)
        unit_bet = request.form.get('unit-bet', type=int)
        game_state.start(counting_technique=counting_technique, betting_strategy=betting_strategy, player_pos=player_pos, num_shoes=num_shoes, unit_bet=unit_bet)
        session['game_start'] = True

        return redirect(url_for('pre_round'))
    return render_template('game_settings.html')

# Information page
@app.route('/info')
@login_required
def info():
    # This is the information page with a specific page
    topic = request.args.get('topic')

    if not topic:
        content = "No information available"
    
    path = f"./info_text/{topic}.txt"

    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "Invalid request"

    return render_template('info.html',topic = topic,content=content)

# Game pages
# Page before the start of a round
@app.route('/pre_round', methods=('GET', 'POST'))
@login_required
@start_required
def pre_round():
    if request.method == 'POST':
        bet_amount = request.form.get('bet-amount', type=int)
        game_state.place_bet(bet_amount)
        return redirect(url_for("curr_game"))
    
    # Extract data from game state
    winnings_history = list(game_state.get_winnings())
    rounds = [f"{i+1}" for i in range(len(winnings_history))]
    optimal_bet = game_state.get_optimal_bet()
    betting_strategy = game_state.get_betting_mode()

    return render_template(
        "pre_round.html",
        current_winnings=winnings_history[-1],
        winnings_history=winnings_history,
        rounds=rounds,
        optimal_bet=optimal_bet,
        betting_strategy=betting_strategy
    )

@app.route('/curr_game', methods=('GET', 'POST'))
@login_required
@start_required
def curr_game():
    # Extract data from game state
    winnings_history = list(game_state.get_winnings())
    rounds = [f"{i+1}" for i in range(len(winnings_history))]
    curr_bet = game_state.get_current_bet()
    player_hands = game_state.get_player_hands()
    optimal_actions, count = game_state.get_processed_play()

    optimal_play = []
    for i in range(len(optimal_actions)):
        optimal_play.append({"id": i+1, "action": optimal_actions[i]})

    return render_template(
        "curr_game.html",
        current_winnings=winnings_history[-1],
        winnings_history=winnings_history,
        rounds=rounds,
        curr_bet=curr_bet,
        player_hands=player_hands,
        optimal_play=optimal_play,
        count=count
    )

@app.route("/handle_hand_result", methods=["POST"])
@login_required
@start_required
def handle_hand_result():
    hand_id = request.form.get("hand_id", type=int)
    outcome = request.form.get('result')

    if outcome == 'win':
        outcome = proc.Outcome.WIN
    elif outcome == 'push':
        outcome = proc.Outcome.PUSH
    elif outcome == 'lose':
        outcome = proc.Outcome.LOSE
    elif outcome == "double":
        outcome = proc.Outcome.DOUBLE
    else:
        outcome = proc.Outcome.BJ

    if game_state.hand_outcome(outcome, hand_id-1):
        return redirect(url_for("pre_round"))

    return redirect(url_for("curr_game"))

# Communication with ML model

@socketio.on('card_data')
def handle_card_data(data):
    if not game_state.round_start:
        return

    # Check if bet has been made if not toss result
    parsed_data = game_state.process_data(data)
    if not game_state.update_hands(parsed_data):
        return

    player_hands = game_state.get_player_hands()
    optimal_actions, count = game_state.get_processed_play()

    optimal_play = []
    for i in range(len(optimal_actions)):
        optimal_play.append({"id": i+1, "action": optimal_actions[i]})
    print("PUSHING")
    html = render_template('partials/_player_toggle_info.html', player_hands=player_hands, optimal_play=optimal_play, count=count)
    turbo.push(turbo.replace(html, target='player-toggle-info'))


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5050, debug=True)
        
        