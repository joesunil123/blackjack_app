from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from datetime import datetime
from turbo_flask import Turbo
import sqlite3
import os
import processing as proc
from flask_socketio import SocketIO, emit
from eventlet import wsgi
import eventlet

eventlet.monkey_patch()
app = Flask(__name__)
turbo = Turbo(app)
app.config['SECRET_KEY'] = 'your secret key' # should be a long random string: generate one
socketio = SocketIO(app, async_mode='eventlet')
game_state = proc.GameState()

# Pre-game pages
# Application entry page
@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html')

# Intermediate page to clear the database
@app.route('/clear_and_home')
def clear_and_home():
    return redirect(url_for("index"))

# Page where game settings are inputted
@app.route('/game_settings', methods=('GET', 'POST'))
def game_settings():
    if request.method == 'POST':
        counting_technique = request.form.get('counting-technique')
        betting_strategy = request.form.get('betting-strategy')
        player_pos = request.form.get('player-position', type=int)
        num_shoes = request.form.get('num-shoes', type=int)
        unit_bet = request.form.get('unit-bet', type=int)

        #TODO: Add Num shoes field to this page
        game_state.start(counting_technique=counting_technique, betting_strategy=betting_strategy, player_pos=player_pos, num_shoes=num_shoes, unit_bet=unit_bet)

        return redirect(url_for('pre_round'))
    return render_template('game_settings.html')

# Information page
@app.route('/info')
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
def curr_game():
    # Extract data from game state
    winnings_history = list(game_state.get_winnings())
    rounds = [f"{i+1}" for i in range(len(winnings_history))]
    curr_bet = game_state.get_current_bet()
    player_hands = game_state.get_player_hands()
    optimal_actions, dealer_hand, count = game_state.get_processed_play()

    optimal_play = []
    for i in range(len(optimal_actions)):
        optimal_play.append({"id": i+1, "action": optimal_actions[i]})

    return render_template(
        "curr_game.html",
        current_winnings=winnings_history[-1],
        winnings_history=winnings_history,
        rounds=rounds,
        curr_bet=curr_bet,
        dealer=dealer_hand,
        player_hands=player_hands,
        optimal_play=optimal_play,
        count=count
    )

@app.route("/handle_hand_result", methods=["POST"])
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
    # global game_state
    print("Received hands", data)
    parsed_data = game_state.process_data(data)
    print("Parsed: ", parsed_data)
    game_state.update_hands(parsed_data)
    player_hands = game_state.get_player_hands()
    optimal_actions, dealer_hand, count = game_state.get_processed_play()

    optimal_play = []
    for i in range(len(optimal_actions)):
        optimal_play.append({"id": i+1, "action": optimal_actions[i]})

    html = render_template('partials/_player_toggle_info.html', player_hands=player_hands, optimal_play=optimal_play, dealer=dealer_hand, count=count)
    print(html)
    turbo.push(turbo.replace(html, target='player-toggle-info'))


if __name__ == "__main__":
    socketio.run(app, port=5050, debug=True)
        
        