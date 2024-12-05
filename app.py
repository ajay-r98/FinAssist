from models import User, db, Transaction
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from collections import defaultdict
import subprocess
import os
import atexit
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_talisman import Talisman
from wallet import save_wallet_to_file

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'dev'  # Replace with a secure key for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = 'dev'  # Needed for session and flash messages
jwt = JWTManager(app)
Talisman(app, content_security_policy=None)

# Initialize the database
db.init_app(app)
with app.app_context():
    db.create_all()



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print(request.form)  # Print the entire form data for debugging
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("Username already taken. Please choose another one.", "error")
            return redirect(url_for('register'))

        # Hash the password before storing
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect(url_for('profile'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        password = request.form['password']

        # Fetch user from the database
        user = User.query.filter_by(username=username).first()

        if user:
            # Check the hashed password
            if check_password_hash(user.password, password):
                # Set session for user ID
                session['user_id'] = user.id

                # Generate access token for secure API communication
                access_token = create_access_token(identity=user.id)

                # Debugging: Print the token (for testing purposes; remove in production)
                print(f"Debug: Access Token - {access_token}")

                # Store token in the session if needed
                session['access_token'] = access_token

                # Redirect to the chat page
                flash("Login successful!", "success")
                return redirect(url_for('chat'))
            else:
                flash("Invalid password. Please try again.", "error")
        else:
            flash("User not found. Please register first.", "error")

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        if request.form['action'] == 'submit':
            user.name = request.form['name']
            user.age = request.form['age']
            user.email = request.form['email']
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('profile'))
        elif request.form['action'] == 'wallet':
            db.session.commit()
            return redirect(url_for('wallet'))
    return render_template('profile.html', user=user)

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        flash("Please log in to access the chat.", "error")
        return redirect(url_for('login'))
    return render_template('chat.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get('message')
    response = requests.post(
        "http://localhost:5005/webhooks/rest/webhook",
        json={"sender": "user", "message": user_input}
    )
    messages = response.json()
    bot_message = messages[0]["text"] if messages else "I'm not sure how to help with that."
    return jsonify({"response": bot_message})

@app.route('/wallet', methods=['GET', 'POST'])
def wallet():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    if request.method == 'POST':
        transaction_type = request.form['type']
        amount = request.form['amount']
        description = request.form.get('description', '')
        category = request.form.get('category') if transaction_type == 'expense' else "N/A"
        date_input = request.form.get('date', '')

        try:
            date = datetime.strptime(date_input, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format! Please use YYYY-MM-DD.", "error")
            return redirect(url_for('wallet'))

        transaction = Transaction(
            user_id=user_id,
            type=transaction_type,
            category=category,
            amount=float(amount),
            description=description,
            date=date
        )
        db.session.add(transaction)
        db.session.commit()
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        save_wallet_to_file(user_id, transactions)  # Save data to file

        flash("Transaction added successfully!", "success")
        return redirect(url_for('wallet'))

    transactions = Transaction.query.filter_by(user_id=user_id).all()
    monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0})
    category_totals = defaultdict(float)

    for t in transactions:
        month = t.date.strftime('%Y-%m')
        if t.type == 'income':
            monthly_data[month]['income'] += t.amount
        elif t.type == 'expense':
            monthly_data[month]['expense'] += t.amount
            category_totals[t.category] += t.amount

    months = sorted(monthly_data.keys())
    income_data = [monthly_data[month]['income'] for month in months]
    expense_data = [monthly_data[month]['expense'] for month in months]
    total_income = sum(income_data)
    total_expenses = sum(expense_data)

    return render_template(
        'wallet.html',
        transactions=transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=total_income - total_expenses,
        months=months,
        income_data=income_data,
        expense_data=expense_data,
        category_labels=list(category_totals.keys()),
        category_amounts=list(category_totals.values()),
        categories=['Groceries', 'Rent', 'Utilities', 'Transport', 'Dining', 'Shopping', 'Miscellaneous']
    )

@app.route('/another-page')
def another_page():
    return render_template('another_page.html')


if __name__ == "__main__":
    app.run(debug=True )
