from flask_wtf import FlaskForm
from wtforms import FloatField, HiddenField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class GradeInputForm(FlaskForm):
    student_id = HiddenField("Student ID")
    tugas = FloatField("Tugas", validators=[
                       Optional(), NumberRange(min=0, max=100)])
    uts = FloatField("UTS", validators=[
                     Optional(), NumberRange(min=0, max=100)])
    uas = FloatField("UAS", validators=[
                     Optional(), NumberRange(min=0, max=100)])
    submit = SubmitField("Simpan")


class ReportFilterForm(FlaskForm):
    subject_id = SelectField(
        "Mata Pelajaran", choices=[], coerce=int, validators=[DataRequired()]
    )
    classroom_id = SelectField(
        "Kelas", choices=[], coerce=int, validators=[DataRequired()]
    )
    submit = SubmitField("Tampilkan")
