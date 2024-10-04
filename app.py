from auth import (
    create_connection,
    initialize_db,
    register_user,
    login_user,
    add_income,
    update_income,
    add_expense,
    update_expense,
    set_budget,
    check_budget,
    view_monthly_transactions,
    view_yearly_transactions,
    generate_report,
    delete_income,
    delete_expense,
    backup_data,
    restore_data
)
import getpass  # For masking the password input

def main():
    conn = create_connection()
    initialize_db(conn)

    while True:
        action = input("Do you want to (R)egister, (L)og in, or (Q)uit? ").strip().lower()

        if action == 'r':
            username = input("Enter a username to register: ")
            password = getpass.getpass("Enter a password: ")  # Masking password input
            register_message = register_user(conn, username, password)
            print(register_message)

        elif action == 'l':
            username = input("Enter your username: ")
            password = getpass.getpass("Enter your password: ")  # Masking password input
            user = login_user(conn, username, password)
            if user:
                user_id = user[0]
                print(f"Welcome {username}!")

                while True:
                    choice = input("Do you want to (A)dd income, (E)xpense, (U)pdate income/expense, (S)et budget, "
                                   "(C)heck budget, (V)iew transactions, (G)enerate report, (D)elete income/expense, "
                                   "(B)ackup data, (R)estore data, or (Q)uit? ").strip().lower()

                    if choice == 'a':
                        amount = float(input("Enter income amount: "))
                        category = input("Enter income category: ")
                        description = input("Enter income description: ")
                        date = input("Enter income date (YYYY-MM-DD): ")
                        add_income(conn, user_id, amount, category, description, date)
                        print("Income added successfully.")

                    elif choice == 'e':
                        amount = float(input("Enter expense amount: "))
                        category = input("Enter expense category: ")
                        description = input("Enter expense description: ")
                        date = input("Enter expense date (YYYY-MM-DD): ")
                        add_expense(conn, user_id, amount, category, description, date)
                        print("Expense added successfully.")

                    elif choice == 'u':
                        transaction_type = input("Do you want to update an (I)ncome or (E)xpense? ").strip().lower()
                        transaction_id = int(input("Enter the transaction ID to update: "))
                        amount = float(input("Enter the updated amount: "))
                        category = input("Enter the updated category: ")
                        description = input("Enter the updated description: ")
                        date = input("Enter the updated date (YYYY-MM-DD): ")
                        if transaction_type == 'i':
                            update_income(conn, transaction_id, user_id, amount, category, description, date)
                        else:
                            update_expense(conn, transaction_id, user_id, amount, category, description, date)
                        print("Transaction updated successfully.")

                    elif choice == 's':
                        category = input("Enter budget category: ")
                        budget_amount = float(input("Enter budget amount: "))
                        set_budget(conn, user_id, category, budget_amount)
                        print(f"Budget of {budget_amount} set for {category}.")

                    elif choice == 'c':
                        budget_info = check_budget(conn, user_id)
                        for category, budget_amount, total_expense, is_exceeded in budget_info:
                            status = "Exceeded" if is_exceeded else "Within Budget"
                            print(f"Category: {category}, Budget: {budget_amount}, Spent: {total_expense}, Status: {status}")

                    elif choice == 'v':
                        view_type = input("View (M)onthly or (Y)early transactions? ").strip().lower()
                        if view_type == 'm':
                            incomes, expenses = view_monthly_transactions(conn, user_id)
                        else:
                            incomes, expenses = view_yearly_transactions(conn, user_id)
                        print("Income Transactions:")
                        for income in incomes:
                            print(income)
                        print("Expense Transactions:")
                        for expense in expenses:
                            print(expense)

                    elif choice == 'g':
                        total_income, total_expense, savings = generate_report(conn, user_id)
                        print(f"Total Income: ${total_income:.2f}, Total Expenses: ${total_expense:.2f}, Savings: ${savings:.2f}")

                    elif choice == 'd':
                        transaction_type = input("Do you want to delete an (I)ncome or (E)xpense? ").strip().lower()
                        transaction_id = int(input("Enter the transaction ID to delete: "))
                        if transaction_type == 'i':
                            delete_income(conn, transaction_id)
                        else:
                            delete_expense(conn, transaction_id)
                        print("Transaction deleted successfully.")

                    elif choice == 'b':
                        backup_file = input("Enter the name of the backup file (e.g., backup.sql): ")
                        backup_data(conn, backup_file)
                        print("Data backup completed successfully.")

                    elif choice == 'r':
                        backup_file = input("Enter the name of the backup file to restore: ")
                        restore_data(conn, backup_file)
                        print("Data restored successfully.")

                    elif choice == 'q':
                        print("Goodbye!")
                        break

            else:
                print("Invalid username or password.")

        elif action == 'q':
            print("Exiting the program.")
            break

if __name__ == "__main__":
    main()
