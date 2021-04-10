from flask import render_template, request, Blueprint, redirect, url_for, flash, session
from flask_login import login_user, current_user, logout_user, login_required
from portfolio_bjonathan import db
from portfolio_bjonathan.user_management.forms import *
from portfolio_bjonathan.models import User

user_management_portfolio = Blueprint('user_management_portfolio', __name__)

@user_management_portfolio.route('/login', methods = ['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()

        if user.check_password(form.password.data):
            login_user(user)

            next = request.args.get('next')

            if next == None or not next[0] == '/':
                next = url_for('app_management.main')

            return redirect(next)
        else:
            flash(u'Username or Password invalid.  Please try logging in again.', 'login_error')
    return render_template('user_management/login.html', form = form)


@user_management_portfolio.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():

    logout_user()

    return redirect(url_for('user_management_portfolio.login'))

@user_management_portfolio.route('/register', methods = ['GET', 'POST'])

def register():

    ### DISABLED FOR DEMO VERSION ###

    # form = RegistrationForm()

    # if form.validate_on_submit():
    #     user = User(username = form.username.data,
    #                 password = form.password.data)

    #     db.session.add(user)
    #     db.session.commit()

    #     return redirect(url_for('user_management.login'))

    return render_template('user_management/register.html', form = form)



