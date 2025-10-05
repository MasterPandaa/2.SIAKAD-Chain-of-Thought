from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from sqlalchemy import select

from ..extensions import db
from ..models import Teacher, User, RoleEnum
from ..utils.decorators import role_required
from .forms import TeacherForm

bp = Blueprint("teachers", __name__, url_prefix="/teachers")


@bp.route("/")
@login_required
@role_required("admin")
def index():
    teachers = db.session.execute(select(Teacher).order_by(Teacher.name)).scalars().all()
    return render_template("teachers/index.html", teachers=teachers)


@bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create():
    form = TeacherForm()
    if form.validate_on_submit():
        t = Teacher(
            nip=form.nip.data.strip(),
            name=form.name.data.strip(),
            phone=form.phone.data or None,
            address=form.address.data or None,
        )
        db.session.add(t)
        try:
            db.session.flush()
        except Exception:
            db.session.rollback()
            flash("Gagal menyimpan guru (kemungkinan NIP duplikat).", "danger")
            return render_template("teachers/form.html", form=form, title="Tambah Guru")
        if form.create_user.data and form.username.data and form.password.data:
            u = User(
                username=form.username.data.strip(),
                email=(form.email.data.strip() or None) if form.email.data else None,
                role=RoleEnum.teacher,
            )
            u.set_password(form.password.data)
            u.teacher_id = t.id
            db.session.add(u)
        db.session.commit()
        flash("Guru berhasil ditambahkan.", "success")
        return redirect(url_for("teachers.index"))
    return render_template("teachers/form.html", form=form, title="Tambah Guru")


@bp.route("/edit/<int:teacher_id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit(teacher_id):
    t = db.session.get(Teacher, teacher_id)
    if not t:
        flash("Guru tidak ditemukan.", "warning")
        return redirect(url_for("teachers.index"))
    form = TeacherForm(obj=t)
    if t.user:
        form.create_user.render_kw = {"disabled": True}
    if form.validate_on_submit():
        t.nip = form.nip.data.strip()
        t.name = form.name.data.strip()
        t.phone = form.phone.data or None
        t.address = form.address.data or None
        if form.create_user.data and not t.user and form.username.data and form.password.data:
            u = User(
                username=form.username.data.strip(),
                email=(form.email.data.strip() or None) if form.email.data else None,
                role=RoleEnum.teacher,
            )
            u.set_password(form.password.data)
            u.teacher_id = t.id
            db.session.add(u)
        db.session.commit()
        flash("Data guru diperbarui.", "success")
        return redirect(url_for("teachers.index"))
    return render_template("teachers/form.html", form=form, title="Edit Guru")


@bp.route("/delete/<int:teacher_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete(teacher_id):
    t = db.session.get(Teacher, teacher_id)
    if not t:
        flash("Guru tidak ditemukan.", "warning")
    else:
        db.session.delete(t)
        db.session.commit()
        flash("Guru dihapus.", "info")
    return redirect(url_for("teachers.index"))
