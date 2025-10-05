from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class SubjectForm(FlaskForm):
    code = StringField("Kode", validators=[DataRequired(), Length(max=16)])
    name = StringField("Nama", validators=[DataRequired(), Length(max=128)])
    sks = IntegerField("SKS", validators=[DataRequired(), NumberRange(min=1, max=10)])
    teacher_id = SelectField("Guru Pengampu", choices=[], coerce=int, validators=[Optional()])
    submit = SubmitField("Simpan")
