from app import create_app
from app.extensions import socketio, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Создаём дефолтного администратора, если его нет
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                full_name="Администратор",
                role="admin",
            )
            admin.set_password("admin")
            db.session.add(admin)
            db.session.commit()
            print("Создан пользователь admin/admin")

    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
