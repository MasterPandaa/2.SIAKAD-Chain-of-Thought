from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import select

from ..extensions import db
from ..models import Subject, Teacher
from ..utils.decorators import role_required
from .forms import SubjectForm

bp = Blueprint("subjects", __name__, url_prefix="/subjects")


def _teacher_choices():
    teachers = db.session.execute(select(Teacher).order_by(Teacher.name)).scalars().all()
    return [(-1, "- Tidak ada -")] + [(t.id, t.name) for t in teachers]


@bp.route("/")
@login_required
@role_required("admin", "teacher")
def index():
    q = select(Subject).order_by(Subject.name)
    role = getattr(getattr(current_user, "role", None), "value", current_user.role)
    if role == "teacher" and current_user.teacher:
        q = q.where(Subject.teacher_id == current_user.teacher.id)
    subjects = db.session.execute(q).scalars().all()
    return render_template("subjects/index.html", subjects=subjects)


@bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create():
    form = SubjectForm()
    form.teacher_id.choices = _teacher_choices()
    if form.validate_on_submit():
        teacher_id = form.teacher_id.data if form.teacher_id.data != -1 else None
        s = Subject(code=form.code.data.strip(), name=form.name.data.strip(), sks=form.sks.data, teacher_id=teacher_id)
        db.session.add(s)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Gagal menyimpan mata pelajaran (kemungkinan kode duplikat).", "danger")
            return render_template("subjects/form.html", form=form, title="Tambah Mata Pelajaran")
        flash("Mata pelajaran ditambahkan.", "success")
        return redirect(url_for("subjects.index"))
    return render_template("subjects/form.html", form=form, title="Tambah Mata Pelajaran")


@bp.route("/edit/<int:subject_id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit(subject_id):
    s = db.session.get(Subject, subject_id)
    if not s:
        flash("Mata pelajaran tidak ditemukan.", "warning")
        return redirect(url_for("subjects.index"))
    form = SubjectForm(obj=s)
    form.teacher_id.choices = _teacher_choices()
    form.teacher_id.data = s.teacher_id or -1
    if form.validate_on_submit():
        s.code = form.code.data.strip()
        s.name = form.name.data.strip()
        s.sks = form.sks.data
        s.teacher_id = form.teacher_id.data if form.teacher_id.data != -1 else None
        db.session.commit()
        flash("Data mata pelajaran diperbarui.", "success")
        return redirect(url_for("subjects.index"))
    return render_template("subjects/form.html", form=form, title="Edit Mata Pelajaran")


@bp.route("/delete/<int:subject_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete(subject_id):
    s = db.session.get(Subject, subject_id)
    if not s:
        flash("Mata pelajaran tidak ditemukan.", "warning")
    else:
        db.session.delete(s)
        db.session.commit()
        flash("Mata pelajaran dihapus.", "info")
    return redirect(url_for("subjects.index"))
