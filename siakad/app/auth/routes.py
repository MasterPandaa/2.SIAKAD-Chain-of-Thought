from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import db
from ..models import User
from .forms import LoginForm

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.is_active and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Login berhasil.", "success")
            next_url = request.args.get("next") or url_for("dashboard.index")
            return redirect(next_url)
        flash("Username atau password salah.", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Anda telah logout.", "info")
    return redirect(url_for("auth.login"))
