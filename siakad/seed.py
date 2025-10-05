from app import create_app
from app.extensions import db
from app.models import User, RoleEnum


def main():
    app = create_app()
    with app.app_context():
        # Create admin if not exists
        username = "admin"
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, role=RoleEnum.admin, email=None)
            user.set_password("admin123")
            db.session.add(user)
            db.session.commit()
            print("Admin user created: admin/admin123")
        else:
            print("Admin user already exists")


if __name__ == "__main__":
    main()
