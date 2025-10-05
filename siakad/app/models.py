from __future__ import annotations

import enum
from datetime import date, datetime

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import bcrypt, db


class RoleEnum(enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


class Classroom(db.Model):
    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        db.String(64), unique=True, nullable=False)

    students: Mapped[list[Student]] = relationship(
        "Student", back_populates="classroom"
    )

    def __repr__(self) -> str:
        return f"<Classroom {self.name}>"


class Student(db.Model):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    nis: Mapped[str] = mapped_column(
        db.String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(128), nullable=False)
    birth_date: Mapped[date | None]
    address: Mapped[str | None] = mapped_column(db.Text())
    gender: Mapped[str | None] = mapped_column(
        db.Enum("M", "F", name="gender_enum"))
    parent_phone: Mapped[str | None] = mapped_column(db.String(32))
    classroom_id: Mapped[int | None] = mapped_column(
        ForeignKey("classrooms.id"), index=True
    )

    classroom: Mapped[Classroom | None] = relationship(
        "Classroom", back_populates="students"
    )
    enrollments: Mapped[list[Enrollment]] = relationship(
        "Enrollment", back_populates="student", cascade="all, delete-orphan"
    )
    user: Mapped[User | None] = relationship(
        "User", back_populates="student", uselist=False
    )

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Student {self.nis} {self.name}>"


class Teacher(db.Model):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    nip: Mapped[str] = mapped_column(
        db.String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(128), nullable=False)
    phone: Mapped[str | None] = mapped_column(db.String(32))
    address: Mapped[str | None] = mapped_column(db.Text())

    subjects: Mapped[list[Subject]] = relationship(
        "Subject", back_populates="teacher")
    user: Mapped[User | None] = relationship(
        "User", back_populates="teacher", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Teacher {self.nip} {self.name}>"


class Subject(db.Model):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(
        db.String(16), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(128), nullable=False)
    sks: Mapped[int] = mapped_column(db.Integer, nullable=False)
    teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id"), index=True
    )

    teacher: Mapped[Teacher | None] = relationship(
        "Teacher", back_populates="subjects")
    enrollments: Mapped[list[Enrollment]] = relationship(
        "Enrollment", back_populates="subject", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Subject {self.code} {self.name}>"


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "subject_id", name="uq_enrollment_student_subject"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), nullable=False, index=True
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"), nullable=False, index=True
    )

    student: Mapped[Student] = relationship(
        "Student", back_populates="enrollments")
    subject: Mapped[Subject] = relationship(
        "Subject", back_populates="enrollments")
    grade: Mapped[Grade | None] = relationship(
        "Grade",
        back_populates="enrollment",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Enrollment s:{self.student_id} sub:{self.subject_id}>"


class Grade(db.Model):
    __tablename__ = "grades"
    __table_args__ = (
        CheckConstraint("tugas >= 0 AND tugas <= 100",
                        name="ck_grade_tugas_range"),
        CheckConstraint("uts >= 0 AND uts <= 100", name="ck_grade_uts_range"),
        CheckConstraint("uas >= 0 AND uas <= 100", name="ck_grade_uas_range"),
        CheckConstraint(
            "nilai_akhir >= 0 AND nilai_akhir <= 100", name="ck_grade_final_range"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("enrollments.id"), unique=True, nullable=False
    )

    tugas: Mapped[float | None] = mapped_column(db.Float)
    uts: Mapped[float | None] = mapped_column(db.Float)
    uas: Mapped[float | None] = mapped_column(db.Float)
    nilai_akhir: Mapped[float | None] = mapped_column(db.Float)

    enrollment: Mapped[Enrollment] = relationship(
        "Enrollment", back_populates="grade")

    def recompute_final(self):
        parts = [p for p in [self.tugas, self.uts, self.uas] if p is not None]
        self.nilai_akhir = round(sum(parts) / len(parts), 2) if parts else None

    def __repr__(self) -> str:
        return f"<Grade enr:{self.enrollment_id} final:{self.nilai_akhir}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        db.String(64), unique=True, nullable=False, index=True
    )
    email: Mapped[str | None] = mapped_column(db.String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        db.Enum(RoleEnum), nullable=False, index=True)

    teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id"), unique=True
    )
    student_id: Mapped[int | None] = mapped_column(
        ForeignKey("students.id"), unique=True
    )
    is_active: Mapped[bool] = mapped_column(
        db.Boolean, default=True, nullable=False)

    teacher: Mapped[Teacher | None] = relationship(
        "Teacher", back_populates="user")
    student: Mapped[Student | None] = relationship(
        "Student", back_populates="user")

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode()

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_id(self):  # Flask-Login
        return str(self.id)

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"


# Helpful indexes
Index("ix_students_classroom", Student.classroom_id)
Index("ix_subjects_teacher", Subject.teacher_id)
