from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp


class StudentForm(FlaskForm):
    nis = StringField("NIS", validators=[DataRequired(), Length(max=32)])
    name = StringField("Nama", validators=[DataRequired(), Length(max=128)])
    birth_date = DateField("Tanggal Lahir", validators=[Optional()], format="%Y-%m-%d")
    address = TextAreaField("Alamat", validators=[Optional(), Length(max=1000)])
    gender = SelectField("Jenis Kelamin", choices=[("", "- Pilih -"), ("M", "Laki-laki"), ("F", "Perempuan")], validators=[Optional()])
    parent_phone = StringField("No. Telp Orang Tua", validators=[Optional(), Length(max=32), Regexp(r"^[0-9+\\-]*$")])
    classroom_id = SelectField("Kelas", choices=[], coerce=int, validators=[Optional()])

    create_user = BooleanField("Buat akun siswa?")
    username = StringField("Username", validators=[Optional(), Length(max=64)])
    email = StringField("Email", validators=[Optional(), Length(max=120)])
    password = PasswordField("Password", validators=[Optional(), Length(min=6, max=128)])

    submit = SubmitField("Simpan")
