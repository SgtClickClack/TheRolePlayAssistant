from flask import render_template, request, session, redirect, url_for, flash
from app import app, db
from models import Character, Scenario, CharacterTemplate, Achievement, ScenarioCompletion
from utils import generate_character as create_character_data, get_random_scenario, generate_character_from_template
import uuid
from datetime import datetime

ACHIEVEMENTS = [
    {
        "name": "Adventurer Novice",
        "description": "Complete your first scenario",
        "icon": "bi-stars",
        "scenarios_required": 1,
        "points_required": 100
    },
    {
        "name": "Seasoned Explorer",
        "description": "Complete 5 scenarios",
        "icon": "bi-trophy",
        "scenarios_required": 5,
        "points_required": 500
    },
    {
        "name": "Master Storyteller",
        "description": "Earn 1000 points from completed scenarios",
        "icon": "bi-book",
        "scenarios_required": 0,
        "points_required": 1000
    }
]

def init_session():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        # Create achievements for new session
        for achievement_data in ACHIEVEMENTS:
            achievement = Achievement(
                session_id=session['session_id'],
                **achievement_data
            )
            db.session.add(achievement)
        db.session.commit()

@app.route('/')
def index():
    init_session()
    templates = CharacterTemplate.query.filter_by(session_id=session['session_id']).all()
    return render_template('index.html', templates=templates)

@app.route('/generate_character', methods=['POST'])
def create_new_character():
    try:
        init_session()
        template_id = request.form.get('template_id')
        if template_id:
            template = CharacterTemplate.query.get_or_404(template_id)
            char_data = generate_character_from_template(template)
        else:
            char_data = create_character_data()
        
        character = Character(
            session_id=session['session_id'],
            template_id=template_id,
            **char_data
        )
        db.session.add(character)
        db.session.commit()
        return redirect(url_for('view_character', char_id=character.id))
    except Exception as e:
        app.logger.error(f"Error generating character: {str(e)}")
        flash("An error occurred while generating your character. Please try again.", "error")
        return redirect(url_for('index'))

@app.route('/character/<int:char_id>')
def view_character(char_id):
    init_session()
    character = Character.query.get_or_404(char_id)
    scenario = get_random_scenario()
    return render_template('character.html', character=character, scenario=scenario)

@app.route('/create_template', methods=['GET', 'POST'])
def create_template():
    init_session()
    if request.method == 'POST':
        try:
            template = CharacterTemplate(
                session_id=session['session_id'],
                name=request.form['name'],
                description=request.form.get('description', ''),
                height_options=request.form.get('height_options', ''),
                hair_color_options=request.form.get('hair_color_options', ''),
                eye_color_options=request.form.get('eye_color_options', ''),
                style_preference_options=request.form.get('style_preference_options', ''),
                signature_items_options=request.form.get('signature_items_options', ''),
                childhood_story_templates=request.form.get('childhood_story_templates', ''),
                family_relations_templates=request.form.get('family_relations_templates', ''),
                life_goals_templates=request.form.get('life_goals_templates', ''),
                achievements_templates=request.form.get('achievements_templates', ''),
                occupation_options=request.form.get('occupation_options', ''),
                communication_style_options=request.form.get('communication_style_options', ''),
                challenge_handling_options=request.form.get('challenge_handling_options', ''),
                hobbies_options=request.form.get('hobbies_options', ''),
                quirks_options=request.form.get('quirks_options', ''),
                costume_options=request.form.get('costume_options', ''),
                accessories_options=request.form.get('accessories_options', ''),
                alternative_costumes_options=request.form.get('alternative_costumes_options', '')
            )
            db.session.add(template)
            db.session.commit()
            flash('Template created successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            app.logger.error(f"Error creating template: {str(e)}")
            flash("An error occurred while creating the template. Please try again.", "error")
            return redirect(url_for('create_template'))
    return render_template('create_template.html')

@app.route('/scenario')
def view_scenario():
    init_session()
    characters = Character.query.filter_by(session_id=session['session_id']).all()
    scenario = get_random_scenario()
    
    # Create scenario if it doesn't exist
    db_scenario = Scenario.query.filter_by(
        title=scenario['title'],
        description=scenario['description']
    ).first()
    
    if not db_scenario:
        db_scenario = Scenario(
            title=scenario['title'],
            description=scenario['description'],
            setting=scenario['setting'],
            challenge=scenario['challenge'],
            goal=scenario['goal'],
            points=100  # Default points for completing scenario
        )
        db.session.add(db_scenario)
        db.session.commit()
    
    # Get completion status
    completion = ScenarioCompletion.query.filter_by(
        session_id=session['session_id'],
        scenario_id=db_scenario.id
    ).first()
    
    # Get achievements and total points
    achievements = Achievement.query.filter_by(session_id=session['session_id']).all()
    total_points = db.session.query(db.func.sum(ScenarioCompletion.points_earned))\
        .filter_by(session_id=session['session_id']).scalar() or 0
    
    return render_template('scenario.html', 
                         characters=characters, 
                         scenario=db_scenario,
                         is_completed=bool(completion),
                         completion=completion,
                         achievements=achievements,
                         total_points=total_points)

@app.route('/complete_scenario/<int:scenario_id>', methods=['POST'])
def complete_scenario(scenario_id):
    init_session()
    scenario = Scenario.query.get_or_404(scenario_id)
    
    # Check if already completed
    existing_completion = ScenarioCompletion.query.filter_by(
        session_id=session['session_id'],
        scenario_id=scenario_id
    ).first()
    
    if existing_completion:
        flash('Scenario already completed!', 'warning')
        return redirect(url_for('view_scenario'))
    
    # Record completion
    completion = ScenarioCompletion(
        session_id=session['session_id'],
        scenario_id=scenario_id,
        points_earned=scenario.points
    )
    db.session.add(completion)
    
    # Update achievements
    total_completions = ScenarioCompletion.query.filter_by(
        session_id=session['session_id']
    ).count() + 1
    
    total_points = db.session.query(db.func.sum(ScenarioCompletion.points_earned))\
        .filter_by(session_id=session['session_id']).scalar() or 0
    total_points += scenario.points
    
    # Check and unlock achievements
    achievements = Achievement.query.filter_by(
        session_id=session['session_id'],
        unlocked_at=None
    ).all()
    
    for achievement in achievements:
        if (achievement.scenarios_required > 0 and total_completions >= achievement.scenarios_required) or \
           (achievement.points_required > 0 and total_points >= achievement.points_required):
            achievement.unlocked_at = datetime.utcnow()
            flash(f'Achievement Unlocked: {achievement.name}!', 'success')
    
    db.session.commit()
    flash('Scenario completed successfully!', 'success')
    return redirect(url_for('view_scenario'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
