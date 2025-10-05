from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from ..extensions import db
from ..models import Enrollment, Grade, Student, Subject, Teacher

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    total_students = db.session.scalar(db.select(func.count(Student.id)))
    total_teachers = db.session.scalar(db.select(func.count(Teacher.id)))
    total_subjects = db.session.scalar(db.select(func.count(Subject.id)))

    averages = db.session.execute(
        db.select(Subject.name, func.avg(Grade.nilai_akhir))
        .join(Enrollment, Enrollment.subject_id == Subject.id, isouter=True)
        .join(Grade, Grade.enrollment_id == Enrollment.id, isouter=True)
        .group_by(Subject.id, Subject.name)
        .order_by(Subject.name)
    ).all()

    labels = [row[0] for row in averages]
    data = [float(row[1]) if row[1] is not None else 0.0 for row in averages]

    return render_template(
        "dashboard/index.html",
        total_students=total_students,
        total_teachers=total_teachers,
        total_subjects=total_subjects,
        chart_labels=labels,
        chart_data=data,
    )
