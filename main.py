from flask import render_template, request, session, redirect, url_for
from app import app, db
from models import Character, Scenario, CharacterTemplate
from utils import generate_character, get_random_scenario, generate_character_from_template
import uuid

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    templates = CharacterTemplate.query.filter_by(session_id=session['session_id']).all()
    return render_template('index.html', templates=templates)

@app.route('/generate_character', methods=['POST'])
def generate_new_character():
    template_id = request.form.get('template_id')
    if template_id:
        template = CharacterTemplate.query.get_or_404(template_id)
        char_data = generate_character_from_template(template)
    else:
        char_data = generate_character()
    
    character = Character(
        session_id=session['session_id'],
        template_id=template_id,
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

@app.route('/create_template', methods=['GET', 'POST'])
def create_template():
    if request.method == 'POST':
        template = CharacterTemplate(
            session_id=session['session_id'],
            name=request.form['name'],
            description=request.form.get('description', ''),
            # Appearance options
            height_options=request.form.get('height_options', ''),
            hair_color_options=request.form.get('hair_color_options', ''),
            eye_color_options=request.form.get('eye_color_options', ''),
            style_preference_options=request.form.get('style_preference_options', ''),
            signature_items_options=request.form.get('signature_items_options', ''),
            # Background options
            childhood_story_templates=request.form.get('childhood_story_templates', ''),
            family_relations_templates=request.form.get('family_relations_templates', ''),
            life_goals_templates=request.form.get('life_goals_templates', ''),
            achievements_templates=request.form.get('achievements_templates', ''),
            # Personality options
            occupation_options=request.form.get('occupation_options', ''),
            communication_style_options=request.form.get('communication_style_options', ''),
            challenge_handling_options=request.form.get('challenge_handling_options', ''),
            hobbies_options=request.form.get('hobbies_options', ''),
            quirks_options=request.form.get('quirks_options', ''),
            # Costume options
            costume_options=request.form.get('costume_options', ''),
            accessories_options=request.form.get('accessories_options', ''),
            alternative_costumes_options=request.form.get('alternative_costumes_options', '')
        )
        db.session.add(template)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_template.html')

@app.route('/scenario')
def view_scenario():
    characters = Character.query.filter_by(session_id=session['session_id']).all()
    scenario = get_random_scenario()
    return render_template('scenario.html', characters=characters, scenario=scenario)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
