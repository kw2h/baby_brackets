from flask import render_template, flash, redirect, session, url_for, request, \
                  g, Markup, jsonify, json
from flask_login import login_user, logout_user, current_user, login_required
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from app import app, db, lm, admin
from config import ADMINS
from .models import *
from .forms import *
from .bracket import bracketMaker

class AdminModelView(ModelView):
    def is_accessible(self):
        """Return True if user is logged in and an administrator"""
        return g.user is not None and g.user.is_authenticated and g.user.id in ADMINS

    def inaccessible_callback(self, name, **kwargs):
        """Redirect to login page if user doesn't have access"""
        return redirect(url_for('login', next=request.url))

admin.add_view(AdminModelView(User, db.session))

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.now()
        db.session.add(g.user)
        db.session.commit()


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Route for Register Page"""
    # if user already logged in, redirect to main page
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()

    if request.method == 'GET':
        return render_template('register.html', form=form)

    # validate form submission
    if form.validate_on_submit():
        user_name = request.form['user_name']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        u = User(user_name, password, first_name,
                 last_name, email, 1, datetime.now())
        db.session.add(u)
        db.session.commit()
        login_user(u)
        flash('Thank you for signing up!')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Route for Create Bracket Page"""
    # if user not logged in, redirect to login page
    if not g.user.is_authenticated:
        flash('Please login to continue')
        return redirect(url_for('login'))

    form = CreateForm()

    if request.method == 'GET':
        return render_template('create.html', form=form)

    # validate form submission
    if form.validate_on_submit():
        name = request.form['name']
        b = Bracket(name=name, parent_id=g.user.id)
        db.session.add(b)
        db.session.commit()
        return redirect(url_for('setup',bracket_id=b.id))
    return render_template('create.html', form=form)


@app.route('/setup/<int:bracket_id>', methods=['GET', 'POST'])
@login_required
def setup(bracket_id):
    """Route for Setup Bracket Page"""
    # if user not logged in, redirect to login page
    if not g.user.is_authenticated:
        flash('Please login to continue')
        return redirect(url_for('login'))

    form = EditForm()

    if request.method == 'GET':
        b = Bracket.query.filter_by(id=bracket_id).first()
        return render_template('setup.html', form=form)

    # validate form submission
    if form.validate_on_submit():
        size = int(request.form['size'])

        bracketMaker(bracket_id, size, request.form, db)

        flash('Bracket Saved!')
        return redirect(url_for('edit', bracket_id=bracket_id))
    return render_template('setup.html', form=form)


@app.route('/edit/<int:bracket_id>')
@login_required
def edit(bracket_id):
    """Route for View Bracket Page"""
    # if user not logged in, redirect to login page
    if not g.user.is_authenticated:
        flash('Please login to continue')
        return redirect(url_for('login'))

    #b = Bracket.query.filter_by(id=bracket_id).first()

    round1 = Matchups.query.filter_by(bracket_id=bracket_id,rnd=1)\
             .order_by(Matchups.region).all()
    round2 = Matchups.query.filter_by(bracket_id=bracket_id,rnd=2)\
             .order_by(Matchups.region).all()
    round3 = Matchups.query.filter_by(bracket_id=bracket_id,rnd=3)\
             .order_by(Matchups.region).all()
    round4 = Matchups.query.filter_by(bracket_id=bracket_id,rnd=4)\
             .order_by(Matchups.region).all()
    return render_template('edit.html', round1=round1, round2=round2,
                           round3=round3, round4=round4, bracket_id=bracket_id)

@app.route('/api/edit', methods=['POST'])
@login_required
def APIedit():
    """API Route to Edit Bracket"""
    bracket_id = int(request.form['bracket_id'])
    match_id = int(request.form['match_id'])
    winner_id = int(request.form['winner_id'])
    next_id = int(request.form['next_id'])
    next_Top_Or_Bottom = int(request.form['next_Top_Or_Bottom'])
    m = Matchups.query.filter_by(bracket_id=bracket_id).filter_by(match_id=match_id).first()
    m.winner_id = winner_id
    n = Matchups.query.filter_by(bracket_id=bracket_id).filter_by(match_id=next_id).first()
    if next_Top_Or_Bottom == 1:
        n.name1_id = winner_id
    else:
        n.name2_id = winner_id
    db.session.add(m)
    db.session.add(n)
    db.session.commit()
    return jsonify('')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route for Login Page"""
    # if user already logged in, redirect to main page
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', form=form)

    # validate form submission
    if form.validate_on_submit():
        user_name = request.form['user_name']
        password = request.form['password']
        # check if eid is in user db, add to db if not
        u = User.query.filter_by(user_name=user_name).first() #pylint: disable=invalid-name
        if u is None:
            flash('User name not found')
            return redirect(url_for('login'))
        elif u.check_password(password):
            u.login_ct += 1
            u.last_login = datetime.now()
            db.session.add(u)
            db.session.commit()
            login_user(u)
            return redirect(url_for('index'))
        else:
            flash('User name or password incorrect')
            return redirect(url_for('login'))


    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
