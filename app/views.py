from flask import render_template, flash, redirect, session, url_for, request, \
                  g, Markup, jsonify, json
from flask_login import login_user, logout_user, current_user, login_required
from flask_admin.base import MenuLink
from datetime import datetime
from app import app, db, lm, admin, hashids
from .models import *
from .forms import *
from .bracket import parentBracketMaker, userBracketMaker
from .admin import AdminModelView

admin.add_link(MenuLink(name='Back to Baby Brackets', url='/'))
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Bracket, db.session))
admin.add_view(AdminModelView(Names, db.session))
admin.add_view(AdminModelView(Matchups, db.session))

def redirect_dest(fallback):
    return request.args.get('next') or fallback

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
        form.referral.data = request.args.get('referral')
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
        flash('Thank you for signing up!','success')
        print form.referral.data
        print form.referral.data != ''
        if form.referral.data is not None and form.referral.data != '':
            return redirect(url_for('pool', refer_bracket_hash=form.referral.data))
        else:
            return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Route for Create Bracket Page"""
    form = CreateForm()

    if request.method == 'GET':
        return render_template('create.html', form=form)

    # validate form submission
    if form.validate_on_submit():
        name = request.form['name']
        b = Bracket(name=name, parent_id=g.user.id)
        db.session.add(b)
        db.session.commit()
        bracket_hash = hashids.encode(b.id)
        return redirect(url_for('setup',bracket_hash=bracket_hash))
    return render_template('create.html', form=form)


@app.route('/setup/<bracket_hash>', methods=['GET', 'POST'])
@login_required
def setup(bracket_hash):
    """Route for Setup Bracket Page"""
    bracket_id = hashids.decode(bracket_hash)[0]
    form = EditForm()

    if request.method == 'GET':
        b = Bracket.query.filter_by(id=bracket_id).first()
        return render_template('setup.html', form=form)

    # validate form submission
    if form.validate_on_submit():
        size = int(request.form['size'])

        parentBracketMaker(bracket_id, size, request.form, db)

        flash('Bracket Saved!','success')
        return redirect(url_for('invite', bracket_hash=bracket_hash))
    else:
        if form.errors:
            flash('All fields required','danger')
        return render_template('setup.html', form=form)


@app.route('/invite/<bracket_hash>')
@login_required
def invite(bracket_hash):
    """Route for Page to Invite Pool Participants"""
    return render_template('invite.html', bracket_hash=bracket_hash)


@app.route('/pool/<refer_bracket_hash>')
@login_required
def pool(refer_bracket_hash):
    """Route for Page to Enter Pool"""
    # if user logged in, redirect to login page
    if g.user.is_authenticated:
        refer_bracket_id = hashids.decode(refer_bracket_hash)[0]
        refer_bracket = Bracket.query.filter_by(id=refer_bracket_id).first()
        b = Bracket(name='%s (%s)' % (refer_bracket.name, g.user.user_name),
                    parent_id=refer_bracket.parent.id,
                    user_id=g.user.id, scoring_bracket_id=refer_bracket_id)
        db.session.add(b)
        db.session.commit()
        userBracketMaker(refer_bracket_id, b.id, db)
        bracket_hash = hashids.encode(b.id)
        return redirect(url_for('edit', bracket_hash=bracket_hash))
    else:
        return render_template('login.html')


@app.route('/edit/<bracket_hash>')
@login_required
def edit(bracket_hash):
    """Route for edit Bracket Page"""
    bracket_id = hashids.decode(bracket_hash)[0]

    b = Bracket.query.filter_by(id=bracket_id).first()
    parent_flag = b.parent == g.user

    round1 = Matchups.query.filter_by(bracket_id=bracket_id,rnd=1)\
             .order_by(Matchups.region).all()
    round2 = Matchups.query.filter_by(bracket_id=bracket_id,rnd=2)\
             .order_by(Matchups.region).all()
    round3 = Matchups.query.filter_by(bracket_id=bracket_id,rnd=3)\
             .order_by(Matchups.region).all()
    round4 = Matchups.query.filter_by(bracket_id=bracket_id,rnd=4)\
             .order_by(Matchups.region).all()
    return render_template('edit.html', round1=round1, round2=round2,
                           round3=round3, round4=round4,
                           bracket_hash=bracket_hash, parent_flag=parent_flag)


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


@app.route('/leaderboard/<bracket_hash>')
@login_required
def leaderboard(bracket_hash):
    """Route for Leaderboard Page"""
    bracket_id = hashids.decode(bracket_hash)[0]

    b = Bracket.query.filter_by(id=bracket_id).first()
    if b.scoring_bracket is None:
        pool = b.pool
    else:
        pool = b.scoring_bracket.pool
    return render_template('leaderboard.html', pool=pool)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route for Login Page"""
    # if user already logged in, redirect to main page
    if g.user is not None and g.user.is_authenticated:
        return redirect(redirect_dest(url_for('index')))

    form = LoginForm()

    if request.method == 'GET':
        nextarg = request.args.get('next')
        referral = nextarg.replace('/pool/','') if nextarg else None
        return render_template('login.html', form=form,
                               referral=referral)

    # validate form submission
    if form.validate_on_submit():
        user_name = request.form['user_name']
        password = request.form['password']
        # check if eid is in user db, add to db if not
        u = User.query.filter_by(user_name=user_name).first() #pylint: disable=invalid-name
        if u is None:
            flash('User name not found','danger')
            return redirect(url_for('login'))
        elif u.check_password(password):
            if u.login_ct is None:
                u.login_ct = 1
            else:
                u.login_ct += 1
            u.last_login = datetime.now()
            db.session.add(u)
            db.session.commit()
            login_user(u)
            return redirect(redirect_dest(url_for('index')))
        else:
            flash('User name or password incorrect','danger')
            return redirect(redirect_dest(url_for('login')))


    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
