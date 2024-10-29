from flask import render_template, request, session, redirect, url_for
from app import app, db
from models import Character, Scenario
from utils import generate_character, get_random_scenario
import uuid

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/generate_character', methods=['POST'])
def generate_new_character():
    char_data = generate_character()
    character = Character(
        session_id=session['session_id'],
        **char_data
    )
    db.session.add(character)
    db.session.commit()
    return redirect(url_for('view_character', char_id=character.id))

@app.route('/character/<int:char_id>')
def view_character(char_id):
    character = Character.query.get_or_404(char_id)
    scenario = get_random_scenario()
    return render_template('character.html', character=character, scenario=scenario)

@app.route('/scenario')
def view_scenario():
    characters = Character.query.filter_by(session_id=session['session_id']).all()
    scenario = get_random_scenario()
    return render_template('scenario.html', characters=characters, scenario=scenario)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
