from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import select

from ..extensions import db
from ..models import Subject, Enrollment, Grade, Student, Classroom
from ..utils.decorators import role_required
from .forms import GradeInputForm, ReportFilterForm

bp = Blueprint("grades", __name__, url_prefix="/grades")


def _subjects_for_user():
    q = select(Subject).order_by(Subject.name)
    role = getattr(getattr(current_user, "role", None), "value", current_user.role)
    if role == "teacher" and current_user.teacher:
        q = q.where(Subject.teacher_id == current_user.teacher.id)
    return db.session.execute(q).scalars().all()


@bp.route("/subjects")
@login_required
@role_required("admin", "teacher")
def subjects():
    subjects = _subjects_for_user()
    return render_template("grades/subjects.html", subjects=subjects)


@bp.route("/subject/<int:subject_id>", methods=["GET", "POST"])
@login_required
@role_required("admin", "teacher")
def manage_subject(subject_id):
    subject = db.session.get(Subject, subject_id)
    if not subject:
        flash("Mata pelajaran tidak ditemukan.", "warning")
        return redirect(url_for("grades.subjects"))
    role = getattr(getattr(current_user, "role", None), "value", current_user.role)
    if role == "teacher":
        if not current_user.teacher or subject.teacher_id != current_user.teacher.id:
            flash("Anda tidak berhak mengelola mata pelajaran ini.", "danger")
            return redirect(url_for("grades.subjects"))

    class_id = request.args.get("classroom_id", type=int)
    classes = db.session.execute(select(Classroom).order_by(Classroom.name)).scalars().all()
    if not classes:
        flash("Belum ada data kelas. Tambahkan kelas terlebih dahulu.", "warning")
        return redirect(url_for("classes.create"))
    if class_id is None:
        class_id = classes[0].id
    classroom = db.session.get(Classroom, class_id)
    students = db.session.execute(
        select(Student).where(Student.classroom_id == class_id).order_by(Student.name)
    ).scalars().all()

    if request.method == "POST":
        form = GradeInputForm()
        if form.validate_on_submit():
            sid = int(form.student_id.data)
            siswa = db.session.get(Student, sid)
            if not siswa or siswa.classroom_id != class_id:
                flash("Siswa tidak valid.", "danger")
                return redirect(url_for("grades.manage_subject", subject_id=subject_id, classroom_id=class_id))
            enr = db.session.execute(
                select(Enrollment).where(Enrollment.student_id == sid, Enrollment.subject_id == subject_id)
            ).scalar_one_or_none()
            if not enr:
                enr = Enrollment(student_id=sid, subject_id=subject_id)
                db.session.add(enr)
                db.session.flush()
            grade = db.session.execute(
                select(Grade).where(Grade.enrollment_id == enr.id)
            ).scalar_one_or_none()
            if not grade:
                grade = Grade(enrollment_id=enr.id)
                db.session.add(grade)
            grade.tugas = form.tugas.data
            grade.uts = form.uts.data
            grade.uas = form.uas.data
            grade.recompute_final()
            db.session.commit()
            flash(f"Nilai untuk {siswa.name} disimpan.", "success")
            return redirect(url_for("grades.manage_subject", subject_id=subject_id, classroom_id=class_id))
        else:
            flash("Input nilai tidak valid.", "danger")

    forms = []
    for s in students:
        enr = db.session.execute(
            select(Enrollment).where(Enrollment.student_id == s.id, Enrollment.subject_id == subject_id)
        ).scalar_one_or_none()
        gr = None
        if enr:
            gr = db.session.execute(select(Grade).where(Grade.enrollment_id == enr.id)).scalar_one_or_none()
        f = GradeInputForm()
        f.student_id.data = str(s.id)
        f.tugas.data = gr.tugas if gr and gr.tugas is not None else None
        f.uts.data = gr.uts if gr and gr.uts is not None else None
        f.uas.data = gr.uas if gr and gr.uas is not None else None
        forms.append((s, gr, f))

    return render_template(
        "grades/manage_subject.html",
        subject=subject,
        classroom=classroom,
        classes=classes,
        forms=forms,
    )


@bp.route("/transcript")
@login_required
@role_required("student")
def transcript_me():
    student = current_user.student
    if not student:
        flash("Akun ini tidak terkait dengan data siswa.", "warning")
        return redirect(url_for("dashboard.index"))
    enrollments = db.session.execute(
        select(Enrollment).where(Enrollment.student_id == student.id)
    ).scalars().all()
    items = []
    for enr in enrollments:
        subject = db.session.get(Subject, enr.subject_id)
        grade = db.session.execute(select(Grade).where(Grade.enrollment_id == enr.id)).scalar_one_or_none()
        items.append((subject, grade))
    return render_template("grades/transcript.html", student=student, items=items)


@bp.route("/transcript/<int:student_id>")
@login_required
@role_required("admin")
def transcript_admin(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash("Siswa tidak ditemukan.", "warning")
        return redirect(url_for("students.index"))
    enrollments = db.session.execute(
        select(Enrollment).where(Enrollment.student_id == student.id)
    ).scalars().all()
    items = []
    for enr in enrollments:
        subject = db.session.get(Subject, enr.subject_id)
        grade = db.session.execute(select(Grade).where(Grade.enrollment_id == enr.id)).scalar_one_or_none()
        items.append((subject, grade))
    return render_template("grades/transcript.html", student=student, items=items)


@bp.route("/report", methods=["GET", "POST"])
@login_required
@role_required("admin", "teacher")
def report():
    form = ReportFilterForm()
    subs = _subjects_for_user()
    form.subject_id.choices = [(s.id, f"{s.code} - {s.name}") for s in subs]
    classes = db.session.execute(select(Classroom).order_by(Classroom.name)).scalars().all()
    form.classroom_id.choices = [(c.id, c.name) for c in classes]

    rows = None
    subject = None
    classroom = None
    if form.validate_on_submit():
        subject = db.session.get(Subject, form.subject_id.data)
        classroom = db.session.get(Classroom, form.classroom_id.data)
        students = db.session.execute(
            select(Student).where(Student.classroom_id == classroom.id).order_by(Student.name)
        ).scalars().all()
        rows = []
        for s in students:
            enr = db.session.execute(
                select(Enrollment).where(Enrollment.student_id == s.id, Enrollment.subject_id == subject.id)
            ).scalar_one_or_none()
            grade = None
            if enr:
                grade = db.session.execute(select(Grade).where(Grade.enrollment_id == enr.id)).scalar_one_or_none()
            rows.append((s, grade))
    return render_template("grades/report.html", form=form, rows=rows, subject=subject, classroom=classroom)
