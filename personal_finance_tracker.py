import json

class PersonalFinanceTracker:
    def __init__(self):
        self.budget = 0
        self.income = 0
        self.expenses = []
        self.categories = {}
        self.savings = 0
        self.total_expenses = 0
        self.total_income = 0
        self.points = 0
        self.goal = 0
        self.load_data()

    def load_data(self):
        """Load saved data from file"""
        try:
            with open("finance_data.json", "r") as f:
                data = json.load(f)
                self.budget = data['budget']
                self.income = data['income']
                self.categories = data['categories']
                self.savings = data['savings']
                self.total_expenses = data['total_expenses']
                self.total_income = data['total_income']
                self.points = data['points']
                self.goal = data['goal']
        except (FileNotFoundError, json.JSONDecodeError):
            print("No saved data found. Starting fresh.")
    
    def save_data(self):
        """Save data to file"""
        data = {
            'budget': self.budget,
            'income': self.income,
            'categories': self.categories,
            'savings': self.savings,
            'total_expenses': self.total_expenses,
            'total_income': self.total_income,
            'points': self.points,
            'goal': self.goal
        }
        with open("finance_data.json", "w") as f:
            json.dump(data, f, indent=4)
    
    def set_budget(self):
        """Set monthly budget"""
        while True:
            try:
                self.budget = float(input("Enter your monthly budget: $"))
                if self.budget <= 0:
                    print("Budget must be positive. Please try again.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def set_income(self):
        """Set monthly income"""
        while True:
            try:
                self.income = float(input("Enter your monthly income: $"))
                if self.income <= 0:
                    print("Income must be positive. Please try again.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def add_expense(self):
        """Add an expense"""
        while True:
            try:
                expense_name = input("Enter the name of the expense (e.g., Groceries): ").capitalize()
                expense_amount = float(input(f"Enter the amount for {expense_name}: $"))
                if expense_amount <= 0:
                    print("Expense amount must be positive. Please try again.")
                    continue
                self.categories[expense_name] = self.categories.get(expense_name, 0) + expense_amount
                self.expenses.append((expense_name, expense_amount))
                self.total_expenses += expense_amount
                self.savings = self.income - self.total_expenses
                print(f"{expense_name} expense of ${expense_amount} added.")
                self.update_points()
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def view_summary(self):
        """View a summary of the current financial status"""
        print("\n--- Financial Summary ---")
        print(f"Income: ${self.income:.2f}")
        print(f"Total Expenses: ${self.total_expenses:.2f}")
        print(f"Savings: ${self.savings:.2f}")
        print(f"Remaining Budget: ${self.budget - self.total_expenses:.2f}")
        print(f"Points: {self.points}")
        print("\nExpenses Breakdown:")
        for category, amount in self.categories.items():
            print(f"{category}: ${amount:.2f}")
        print("------------------------")

    def update_points(self):
        """Update points based on financial health"""
        if self.total_expenses <= self.budget:
            self.points += 10
        else:
            self.points -= 5

        if self.savings >= self.goal:
            self.points += 20
            print(f"Congratulations! You've met your savings goal of ${self.goal}!")
        elif self.savings < 0:
            self.points -= 10
            print("Warning: You are overspending. Consider reducing expenses.")

    def set_financial_goal(self):
        """Set savings goal"""
        while True:
            try:
                self.goal = float(input("Set a savings goal for the month: $"))
                if self.goal < 0:
                    print("Savings goal cannot be negative. Please try again.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def play(self):
        """Main game loop"""
        print("Welcome to the Personal Finance Tracker Game!")
        
        self.set_income()
        self.set_budget()
        self.set_financial_goal()

        while True:
            print("\nChoose an option:")
            print("1. Add an Expense")
            print("2. View Financial Summary")
            print("3. Exit")

            choice = input("Enter your choice (1-3): ")

            if choice == '1':
                self.add_expense()
            elif choice == '2':
                self.view_summary()
            elif choice == '3':
                self.save_data()
                print("Game saved. Exiting the game.")
                break
            else:
                print("Invalid choice. Please choose a valid option.")

if __name__ == "__main__":
    finance_tracker = PersonalFinanceTracker()
    finance_tracker.play()
