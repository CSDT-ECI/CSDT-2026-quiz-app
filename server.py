from datetime import datetime
from app import create_app
from app.modules.utils import generate_password
from flask_wtf.csrf import CSRFError
from flask import jsonify
import os

app = create_app(os.environ.get('FLASK_ENV','development'))

from app.db import db, quiz


def seed_data():
    """
    If there are no users, add a default admin.
    Login: username admin, password admin1 (change in dashboard).
    """
    cek = db.users.find_one({})
    if not cek:
        data = {
            'full_name': 'Admin Web',
            'username': 'admin',
            'password': generate_password('admin1'),
            'joined_at': datetime.utcnow(),
            'email': 'yourmail@gmail.com',
            'type': 1,
        }
        insert_data = db.users.insert_one(data)
        if insert_data.inserted_id:
            app.logger.info('new user added')


with app.app_context():
    seed_data()


@app.errorhandler(CSRFError)
def error_csrf(e):
    return jsonify(status='fail', errors='CSRF Error, please refresh the page')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
