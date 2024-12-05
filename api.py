from flask import Blueprint, jsonify, request, session
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import Transaction, User
from flask_sqlalchemy import SQLAlchemy

api = Blueprint('api', __name__)

@api.route('/wallet', methods=['GET'])
@jwt_required()
def get_wallet_info():
    user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    data = [
        {
            'type': t.type,
            'category': t.category,
            'amount': t.amount,
            'description': t.description,
            'date': t.date.strftime('%Y-%m-%d')
        }
        for t in transactions
    ]

    return jsonify({'transactions': data}), 200
