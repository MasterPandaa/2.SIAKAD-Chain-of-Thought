-- MySQL 8+ schema for SIAKAD
CREATE TABLE IF NOT EXISTS classrooms (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nis VARCHAR(32) NOT NULL UNIQUE,
  name VARCHAR(128) NOT NULL,
  birth_date DATE NULL,
  address TEXT NULL,
  gender ENUM('M','F') NULL,
  parent_phone VARCHAR(32) NULL,
  classroom_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_students_classroom (classroom_id),
  CONSTRAINT fk_students_classroom FOREIGN KEY (classroom_id) REFERENCES classrooms(id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS teachers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nip VARCHAR(32) NOT NULL UNIQUE,
  name VARCHAR(128) NOT NULL,
  phone VARCHAR(32) NULL,
  address TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS subjects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(16) NOT NULL UNIQUE,
  name VARCHAR(128) NOT NULL,
  sks INT NOT NULL,
  teacher_id INT NULL,
  INDEX ix_subjects_teacher (teacher_id),
  CONSTRAINT fk_subjects_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS enrollments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  subject_id INT NOT NULL,
  CONSTRAINT uq_enrollment_student_subject UNIQUE (student_id, subject_id),
  INDEX ix_enrollments_student (student_id),
  INDEX ix_enrollments_subject (subject_id),
  CONSTRAINT fk_enrollments_student FOREIGN KEY (student_id) REFERENCES students(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_enrollments_subject FOREIGN KEY (subject_id) REFERENCES subjects(id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS grades (
  id INT AUTO_INCREMENT PRIMARY KEY,
  enrollment_id INT NOT NULL UNIQUE,
  tugas FLOAT NULL,
  uts FLOAT NULL,
  uas FLOAT NULL,
  nilai_akhir FLOAT NULL,
  CONSTRAINT fk_grades_enrollment FOREIGN KEY (enrollment_id) REFERENCES enrollments(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT ck_grade_tugas_range CHECK (tugas >= 0 AND tugas <= 100),
  CONSTRAINT ck_grade_uts_range CHECK (uts >= 0 AND uts <= 100),
  CONSTRAINT ck_grade_uas_range CHECK (uas >= 0 AND uas <= 100),
  CONSTRAINT ck_grade_final_range CHECK (nilai_akhir >= 0 AND nilai_akhir <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(64) NOT NULL UNIQUE,
  email VARCHAR(120) NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('admin','teacher','student') NOT NULL,
  teacher_id INT NULL UNIQUE,
  student_id INT NULL UNIQUE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  INDEX ix_users_role (role),
  CONSTRAINT fk_users_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fk_users_student FOREIGN KEY (student_id) REFERENCES students(id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
