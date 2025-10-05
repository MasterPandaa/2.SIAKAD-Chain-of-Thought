from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from sqlalchemy import select

from ..extensions import db
from ..models import Classroom
from ..utils.decorators import role_required
from .forms import ClassroomForm

bp = Blueprint("classes", __name__, url_prefix="/classes")


@bp.route("/")
@login_required
@role_required("admin")
def index():
    classes = db.session.execute(select(Classroom).order_by(Classroom.name)).scalars().all()
    return render_template("classes/index.html", classes=classes)


@bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create():
    form = ClassroomForm()
    if form.validate_on_submit():
        c = Classroom(name=form.name.data.strip())
        db.session.add(c)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Gagal menyimpan kelas (kemungkinan nama duplikat).", "danger")
            return render_template("classes/form.html", form=form, title="Tambah Kelas")
        flash("Kelas ditambahkan.", "success")
        return redirect(url_for("classes.index"))
    return render_template("classes/form.html", form=form, title="Tambah Kelas")


@bp.route("/edit/<int:class_id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit(class_id):
    c = db.session.get(Classroom, class_id)
    if not c:
        flash("Kelas tidak ditemukan.", "warning")
        return redirect(url_for("classes.index"))
    form = ClassroomForm(obj=c)
    if form.validate_on_submit():
        c.name = form.name.data.strip()
        db.session.commit()
        flash("Data kelas diperbarui.", "success")
        return redirect(url_for("classes.index"))
    return render_template("classes/form.html", form=form, title="Edit Kelas")


@bp.route("/delete/<int:class_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete(class_id):
    c = db.session.get(Classroom, class_id)
    if not c:
        flash("Kelas tidak ditemukan.", "warning")
    else:
        db.session.delete(c)
        db.session.commit()
        flash("Kelas dihapus.", "info")
    return redirect(url_for("classes.index"))
