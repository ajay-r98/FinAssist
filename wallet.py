from models import User
from datetime import datetime

def save_wallet_to_file(user_id, transactions):
    # Calculate total income, total expenses, and balance
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expenses = sum(t.amount for t in transactions if t.type == "expense")
    balance = total_income - total_expenses

    # Fetch the user's name from the database
    user = User.query.get(user_id)
    user_name = user.name if user else "Unknown User"

    # Define the filename based on the user ID
    filename = f"wallet_data_user_{user_id}.txt"
    file_path = f"./exports/{filename}"  # Save in an "exports" folder

    # Create the folder if it doesn't exist
    import os
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Prepare the text data
    wallet_summary = f"""
    User: {user_name} (ID: {user_id})
    -------------------------------------
    Total Income: {total_income:.2f}
    Total Expenses: {total_expenses:.2f}
    Balance: {balance:.2f}
    -------------------------------------

    Transactions:
    """
    transaction_details = "\n".join(
        f"{t.date.strftime('%Y-%m-%d')} - {t.type.capitalize()} - {t.category} - ${t.amount:.2f} - {t.description or 'N/A'}"
        for t in transactions
    )

    # Combine the summary and transactions
    wallet_data = wallet_summary + transaction_details

    # Write to the file (overwrites if it already exists)
    with open(file_path, "w") as file:
        file.write(wallet_data)

    print(f"Wallet data saved to {file_path}")
