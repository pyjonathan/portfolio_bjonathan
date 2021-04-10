from flask import render_template, request, Blueprint, redirect, url_for, flash, session
from flask_login import login_user, current_user, logout_user, login_required
from portfolio_bjonathan import db


app_management = Blueprint('app_management', __name__)

@app_management.route('/app_management')
@login_required
def main():

    return render_template('app_management/main.html')
