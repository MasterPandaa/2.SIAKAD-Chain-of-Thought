from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class TeacherForm(FlaskForm):
    nip = StringField("NIP", validators=[DataRequired(), Length(max=32)])
    name = StringField("Nama", validators=[DataRequired(), Length(max=128)])
    phone = StringField("No. Telp", validators=[Optional(), Length(max=32)])
    address = TextAreaField("Alamat", validators=[
                            Optional(), Length(max=1000)])

    create_user = BooleanField("Buat akun guru?")
    username = StringField("Username", validators=[Optional(), Length(max=64)])
    email = StringField("Email", validators=[Optional(), Length(max=120)])
    password = PasswordField(
        "Password", validators=[Optional(), Length(min=6, max=128)]
    )

    submit = SubmitField("Simpan")
