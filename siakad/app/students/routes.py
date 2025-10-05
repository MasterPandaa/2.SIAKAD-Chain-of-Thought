from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from sqlalchemy import select

from ..extensions import db
from ..models import Student, Classroom, User, RoleEnum
from ..utils.decorators import role_required
from .forms import StudentForm

bp = Blueprint("students", __name__, url_prefix="/students")


@bp.route("/")
@login_required
@role_required("admin")
def index():
    students = db.session.execute(select(Student).order_by(Student.name)).scalars().all()
    return render_template("students/index.html", students=students)


def _populate_class_choices(form: StudentForm):
    classes = db.session.execute(select(Classroom).order_by(Classroom.name)).scalars().all()
    form.classroom_id.choices = [(-1, "- Tidak ada -")] + [(c.id, c.name) for c in classes]


@bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create():
    form = StudentForm()
    _populate_class_choices(form)
    if form.validate_on_submit():
        classroom_id = form.classroom_id.data if form.classroom_id.data != -1 else None
        s = Student(
            nis=form.nis.data.strip(),
            name=form.name.data.strip(),
            birth_date=form.birth_date.data,
            address=form.address.data or None,
            gender=form.gender.data or None,
            parent_phone=form.parent_phone.data or None,
            classroom_id=classroom_id,
        )
        db.session.add(s)
        try:
            db.session.flush()
        except Exception:
            db.session.rollback()
            flash("Gagal menyimpan siswa (kemungkinan NIS duplikat).", "danger")
            return render_template("students/form.html", form=form, title="Tambah Siswa")
        if form.create_user.data and form.username.data and form.password.data:
            u = User(
                username=form.username.data.strip(),
                email=(form.email.data.strip() or None) if form.email.data else None,
                role=RoleEnum.student,
            )
            u.set_password(form.password.data)
            u.student_id = s.id
            db.session.add(u)
        db.session.commit()
        flash("Siswa berhasil ditambahkan.", "success")
        return redirect(url_for("students.index"))
    return render_template("students/form.html", form=form, title="Tambah Siswa")


@bp.route("/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit(student_id):
    s = db.session.get(Student, student_id)
    if not s:
        flash("Siswa tidak ditemukan.", "warning")
        return redirect(url_for("students.index"))
    form = StudentForm(obj=s)
    _populate_class_choices(form)
    form.classroom_id.data = s.classroom_id or -1
    if s.user:
        form.create_user.render_kw = {"disabled": True}
    if form.validate_on_submit():
        s.nis = form.nis.data.strip()
        s.name = form.name.data.strip()
        s.birth_date = form.birth_date.data
        s.address = form.address.data or None
        s.gender = form.gender.data or None
        s.parent_phone = form.parent_phone.data or None
        s.classroom_id = form.classroom_id.data if form.classroom_id.data != -1 else None
        if form.create_user.data and not s.user and form.username.data and form.password.data:
            u = User(
                username=form.username.data.strip(),
                email=(form.email.data.strip() or None) if form.email.data else None,
                role=RoleEnum.student,
            )
            u.set_password(form.password.data)
            u.student_id = s.id
            db.session.add(u)
        db.session.commit()
        flash("Data siswa diperbarui.", "success")
        return redirect(url_for("students.index"))
    return render_template("students/form.html", form=form, title="Edit Siswa")


@bp.route("/delete/<int:student_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete(student_id):
    s = db.session.get(Student, student_id)
    if not s:
        flash("Siswa tidak ditemukan.", "warning")
    else:
        db.session.delete(s)
        db.session.commit()
        flash("Siswa dihapus.", "info")
    return redirect(url_for("students.index"))


@bp.route("/view/<int:student_id>")
@login_required
@role_required("admin")
def view(student_id):
    s = db.session.get(Student, student_id)
    if not s:
        flash("Siswa tidak ditemukan.", "warning")
        return redirect(url_for("students.index"))
    return render_template("students/view.html", student=s)
