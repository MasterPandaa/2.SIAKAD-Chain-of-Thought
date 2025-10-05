from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ClassroomForm(FlaskForm):
    name = StringField("Nama Kelas", validators=[DataRequired(), Length(max=64)])
    submit = SubmitField("Simpan")
