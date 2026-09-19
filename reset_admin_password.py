
from getpass import getpass

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User


app = create_app()

with app.app_context():
    user = User.query.filter_by(username="admin").first()

    if not user:
        print("ERROR: Super Admin user 'admin' was not found.")
        raise SystemExit(1)

    print(f"Account found: {user.username}")
    print(f"Role: {user.role}")

    new_password = getpass("Enter new password: ")
    confirm_password = getpass("Confirm new password: ")

    if not new_password:
        print("ERROR: Password cannot be empty.")
        raise SystemExit(1)

    if new_password != confirm_password:
        print("ERROR: Passwords do not match.")
        raise SystemExit(1)

    if len(new_password) < 8:
        print("ERROR: Password must contain at least 8 characters.")
        raise SystemExit(1)

    if hasattr(user, "set_password"):
        user.set_password(new_password)
    elif hasattr(user, "password_hash"):
        user.password_hash = generate_password_hash(new_password)
    elif hasattr(user, "password"):
        user.password = generate_password_hash(new_password)
    else:
        print("ERROR: Could not find the password field or method.")
        raise SystemExit(1)

    db.session.commit()

    print("SUCCESS: Super Admin password updated successfully.")