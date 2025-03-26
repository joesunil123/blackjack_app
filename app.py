from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import datetime
import sqlite3
import os
import processing.py
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key' # should be a long random string: generate one
socketio = SocketIO(app)

game_state = processing.GameState()

# Actual app stuff
@app.route('/')
def index():
    # This is the base screen showing begin
    return render_template('index.html')

@app.route('/clear_and_home')
def clear_and_home():

    # TODO: Might want to make it so that this is only run once instead of everytime we reload the page
    conn = get_db_connection()
    with open("./db/schemas.sql") as file:
        conn.executescript(file.read())
    
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route('/game_settings', methods=('GET', 'POST'))
def game_settings():
    if request.method == 'POST':
        return redirect(url_for('curr_game'))
    return render_template('game_settings.html')

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

@app.route('/curr_game', methods=('GET', 'POST'))
def curr_game():
    if request.method == 'POST':
        # delete from database
        pass

    return render_template('curr_game.html')


# Communication with ML model

# @socketio.on('card_data')
# def handle_card_data(data):
#     # global game_state
#     pass

##### Helper functions


def get_db_connection():
    conn = sqlite3.connect('./db/data.db')
    conn.row_factory = sqlite3.Row
    return conn


# Old stuff
# @app.route('/create', methods=('GET', 'POST'))
# def create():
#     if request.method == 'POST':
#         team_info = request.form['team-info']
#         match_results = request.form['match-results']

#         if not team_info:
#             flash('Team info is required!')
#         elif not match_results:
#             flash('Match results are required!')
#         else:
#             conn = get_db_connection()

#             # First perform for the the team details
#             all_details, valid_input = enter_details(team_info, conn)
#             if all_details == None:
#                 if valid_input == 0:
#                     flash('Malformed request!')
#                 elif valid_input == 1:
#                     flash('Invalid datetime format on one or more lines')
#                 elif valid_input == 2:
#                     flash('Invalid group on one or more teams')
#                 elif valid_input == 3:
#                     flash('Contains an already registered team OR group is too large')

#             else:
#                 for details in all_details:
#                     conn.execute('INSERT INTO team_details (name, reg, group) VALUES (?, ?, ?)',
#                                  (details[0], details[1], int(details[2])))

#             match_details, valid_input = enter_matches()
#             print("submitted form")
            
#             # conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
#             #              (title, content))
#             # conn.commit()
#             # conn.close()
#             # return redirect(url_for('index'))
#             pass

#     return render_template('create.html')

# @app.route('/edit', methods=('GET', 'POST'))
# def edit():
#     curr_info = {"team-info" : "string with curr team info", "match-results":"string with curr match results"}
    
#     if request.method == 'POST':
#         team_info = request.form['team-info']
#         match_results = request.form['match-results']

#         if not team_info:
#             flash('Team info is required!')
#         elif not match_results:
#             flash('Match results are required!')
#         else:
#             print("submitted form")
#             # process and add to databse here!!
#             pass

#     return render_template('edit.html', curr_info=curr_info)
        
        