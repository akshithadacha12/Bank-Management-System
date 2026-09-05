import sqlite3
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect("bank.db")
cursor = conn.cursor()

# Create accounts table
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    account_no INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    account_type TEXT NOT NULL,
    balance REAL DEFAULT 0
)
""")

# Create transactions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_no INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL
)
""")

conn.commit()


# Create new account
def create_account():
    print("\n--- Create Account ---")

    name = input("Enter account holder name: ")
    phone = input("Enter phone number: ")
    account_type = input("Enter account type (Savings/Current): ")

    try:
        initial_deposit = float(input("Enter initial deposit: ₹"))

        if initial_deposit < 0:
            print("Deposit cannot be negative.")
            return

    except ValueError:
        print("Invalid amount.")
        return

    cursor.execute("""
    INSERT INTO accounts (name, phone, account_type, balance)
    VALUES (?, ?, ?, ?)
    """, (name, phone, account_type, initial_deposit))

    account_no = cursor.lastrowid

    if initial_deposit > 0:
        cursor.execute("""
        INSERT INTO transactions
        (account_no, transaction_type, amount, date)
        VALUES (?, ?, ?, ?)
        """, (
            account_no,
            "Initial Deposit",
            initial_deposit,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    conn.commit()

    print("\nAccount created successfully!")
    print("Your Account Number:", account_no)


# View account
def view_account():
    print("\n--- View Account ---")

    try:
        account_no = int(input("Enter account number: "))
    except ValueError:
        print("Invalid account number.")
        return

    cursor.execute(
        "SELECT * FROM accounts WHERE account_no = ?",
        (account_no,)
    )

    account = cursor.fetchone()

    if account:
        print("\nAccount Details")
        print("-------------------------")
        print("Account Number :", account[0])
        print("Name           :", account[1])
        print("Phone          :", account[2])
        print("Account Type   :", account[3])
        print("Balance        : ₹", f"{account[4]:.2f}")
    else:
        print("Account not found.")


# Deposit money
def deposit():
    print("\n--- Deposit Money ---")

    try:
        account_no = int(input("Enter account number: "))
        amount = float(input("Enter deposit amount: ₹"))

        if amount <= 0:
            print("Amount must be greater than zero.")
            return

    except ValueError:
        print("Invalid input.")
        return

    cursor.execute(
        "SELECT balance FROM accounts WHERE account_no = ?",
        (account_no,)
    )

    account = cursor.fetchone()

    if not account:
        print("Account not found.")
        return

    new_balance = account[0] + amount

    cursor.execute("""
    UPDATE accounts
    SET balance = ?
    WHERE account_no = ?
    """, (new_balance, account_no))

    cursor.execute("""
    INSERT INTO transactions
    (account_no, transaction_type, amount, date)
    VALUES (?, ?, ?, ?)
    """, (
        account_no,
        "Deposit",
        amount,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()

    print("Money deposited successfully!")
    print("Current Balance: ₹", f"{new_balance:.2f}")


# Withdraw money
def withdraw():
    print("\n--- Withdraw Money ---")

    try:
        account_no = int(input("Enter account number: "))
        amount = float(input("Enter withdrawal amount: ₹"))

        if amount <= 0:
            print("Amount must be greater than zero.")
            return

    except ValueError:
        print("Invalid input.")
        return

    cursor.execute(
        "SELECT balance FROM accounts WHERE account_no = ?",
        (account_no,)
    )

    account = cursor.fetchone()

    if not account:
        print("Account not found.")
        return

    balance = account[0]

    if amount > balance:
        print("Insufficient balance.")
        return

    new_balance = balance - amount

    cursor.execute("""
    UPDATE accounts
    SET balance = ?
    WHERE account_no = ?
    """, (new_balance, account_no))

    cursor.execute("""
    INSERT INTO transactions
    (account_no, transaction_type, amount, date)
    VALUES (?, ?, ?, ?)
    """, (
        account_no,
        "Withdrawal",
        amount,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()

    print("Money withdrawn successfully!")
    print("Current Balance: ₹", f"{new_balance:.2f}")


# Transfer money
def transfer_money():
    print("\n--- Transfer Money ---")

    try:
        sender = int(input("Enter sender account number: "))
        receiver = int(input("Enter receiver account number: "))
        amount = float(input("Enter transfer amount: ₹"))

        if amount <= 0:
            print("Amount must be greater than zero.")
            return

        if sender == receiver:
            print("Sender and receiver cannot be the same.")
            return

    except ValueError:
        print("Invalid input.")
        return

    cursor.execute(
        "SELECT balance FROM accounts WHERE account_no = ?",
        (sender,)
    )
    sender_account = cursor.fetchone()

    cursor.execute(
        "SELECT balance FROM accounts WHERE account_no = ?",
        (receiver,)
    )
    receiver_account = cursor.fetchone()

    if not sender_account:
        print("Sender account not found.")
        return

    if not receiver_account:
        print("Receiver account not found.")
        return

    if amount > sender_account[0]:
        print("Insufficient balance.")
        return

    sender_balance = sender_account[0] - amount
    receiver_balance = receiver_account[0] + amount

    cursor.execute("""
    UPDATE accounts
    SET balance = ?
    WHERE account_no = ?
    """, (sender_balance, sender))

    cursor.execute("""
    UPDATE accounts
    SET balance = ?
    WHERE account_no = ?
    """, (receiver_balance, receiver))

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO transactions
    (account_no, transaction_type, amount, date)
    VALUES (?, ?, ?, ?)
    """, (sender, "Transfer Sent", amount, current_time))

    cursor.execute("""
    INSERT INTO transactions
    (account_no, transaction_type, amount, date)
    VALUES (?, ?, ?, ?)
    """, (receiver, "Transfer Received", amount, current_time))

    conn.commit()

    print("Money transferred successfully!")


# Transaction history
def transaction_history():
    print("\n--- Transaction History ---")

    try:
        account_no = int(input("Enter account number: "))
    except ValueError:
        print("Invalid account number.")
        return

    cursor.execute(
        "SELECT * FROM transactions WHERE account_no = ? ORDER BY id DESC",
        (account_no,)
    )

    transactions = cursor.fetchall()

    if not transactions:
        print("No transactions found.")
        return

    print("\nID | Type | Amount | Date")
    print("-" * 60)

    for transaction in transactions:
        print(
            transaction[0],
            "|",
            transaction[2],
            "| ₹",
            f"{transaction[3]:.2f}",
            "|",
            transaction[4]
        )


# Delete account
def delete_account():
    print("\n--- Delete Account ---")

    try:
        account_no = int(input("Enter account number: "))
    except ValueError:
        print("Invalid account number.")
        return

    cursor.execute(
        "SELECT * FROM accounts WHERE account_no = ?",
        (account_no,)
    )

    account = cursor.fetchone()

    if not account:
        print("Account not found.")
        return

    if account[4] != 0:
        print("Account cannot be deleted because balance is not zero.")
        return

    cursor.execute(
        "DELETE FROM transactions WHERE account_no = ?",
        (account_no,)
    )

    cursor.execute(
        "DELETE FROM accounts WHERE account_no = ?",
        (account_no,)
    )

    conn.commit()

    print("Account deleted successfully!")


# Main menu
def main():
    while True:

        print("\n")
        print("=" * 45)
        print("       BANK MANAGEMENT SYSTEM")
        print("=" * 45)

        print("1. Create Account")
        print("2. View Account")
        print("3. Deposit Money")
        print("4. Withdraw Money")
        print("5. Transfer Money")
        print("6. Transaction History")
        print("7. Delete Account")
        print("8. Exit")

        print("=" * 45)

        choice = input("Enter your choice: ")

        if choice == "1":
            create_account()

        elif choice == "2":
            view_account()

        elif choice == "3":
            deposit()

        elif choice == "4":
            withdraw()

        elif choice == "5":
            transfer_money()

        elif choice == "6":
            transaction_history()

        elif choice == "7":
            delete_account()

        elif choice == "8":
            print("Thank you for using Bank Management System!")
            break

        else:
            print("Invalid choice. Please try again.")


# Start program
if __name__ == "__main__":
    main()

# Close database
conn.close()