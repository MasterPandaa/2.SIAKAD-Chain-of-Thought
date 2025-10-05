# SIAKAD (Sistem Informasi Akademik) – Flask + MySQL

Proyek ini adalah implementasi SIAKAD sederhana menggunakan Flask, SQLAlchemy, dan MySQL.

## Fitur
- Manajemen Siswa (CRUD)
- Manajemen Guru (CRUD)
- Manajemen Kelas (CRUD)
- Manajemen Mata Pelajaran (CRUD)
- Manajemen Nilai
  - Input nilai (tugas/UTS/UAS)
  - Nilai akhir (rata-rata)
  - Transcript nilai siswa
  - Laporan nilai per kelas
- Sistem Login dengan 3 role: Admin, Guru, Siswa
- Dashboard statistik dan grafik rata-rata nilai per mata pelajaran

## Teknologi
- Python 3.10+
- Flask, Flask-Login, Flask-WTF, Flask-Migrate, Flask-Bcrypt
- SQLAlchemy ORM (mysql+pymysql)
- MySQL 8+
- Bootstrap 5, Chart.js

## Setup (Windows)
1. Siapkan database MySQL:
   - Buat database: `CREATE DATABASE siakad_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
2. Buat virtualenv dan install dependency:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Konfigurasi environment:
   - Salin `.env.example` menjadi `.env`, lalu isi kredensial database dan secret key.
4. Inisialisasi database (opsi 1 – schema.sql):
   - Import `schema.sql` ke database `siakad_db`.

   Opsi 2 – Flask-Migrate (opsional):
   ```powershell
   # Inisialisasi migrasi pertama kali
   set FLASK_APP=wsgi:app
   flask db init
   flask db migrate -m "init schema"
   flask db upgrade
   ```
5. Seed Admin (opsional, buat user admin awal):
   ```powershell
   set FLASK_APP=wsgi:app
   python seed.py
   ```
6. Menjalankan aplikasi (dev):
   ```powershell
   set FLASK_APP=wsgi:app
   flask run --debug
   ```
   atau
   ```powershell
   python run.py
   ```

## Konfigurasi
- Atur `SQLALCHEMY_DATABASE_URI` di `.env`:
  ```
  SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:password@localhost:3306/siakad_db
  ```

## Catatan Keamanan
- Simpan rahasia di `.env` (SECRET_KEY, DSN DB), jangan commit.
- Password disimpan dengan hashing bcrypt.
- CSRF enabled melalui Flask-WTF.

## Lisensi
MIT
