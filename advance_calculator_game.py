import math
import cmath

class AdvancedCalculator:
    def __init__(self):
        self.history = []  # Stores previous calculations
        self.memory = 0  # Stores the memory value

    # Function to evaluate expressions with basic and scientific operations
    def evaluate_expression(self, expression):
        try:
            # Handle functions like sin, cos, etc.
            expression = expression.replace("sin", "math.sin")
            expression = expression.replace("cos", "math.cos")
            expression = expression.replace("tan", "math.tan")
            expression = expression.replace("log", "math.log10")
            expression = expression.replace("sqrt", "math.sqrt")
            expression = expression.replace("exp", "math.exp")
            expression = expression.replace("pi", str(math.pi))
            expression = expression.replace("e", str(math.e))
            
            # Handle complex numbers
            if 'j' in expression:
                expression = expression.replace("j", "1j")

            result = eval(expression)  # Evaluate the mathematical expression
            self.history.append(f"{expression} = {result}")  # Save to history
            return result
        except Exception as e:
            return f"Error: {e}"

    # Function to clear the memory
    def clear_memory(self):
        self.memory = 0
        return "Memory Cleared!"

    # Function to store a value in memory
    def store_to_memory(self, value):
        self.memory = value
        return f"Stored {value} in memory."

    # Function to recall the value from memory
    def recall_memory(self):
        return f"Memory: {self.memory}"

    # Function to display the history
    def show_history(self):
        if not self.history:
            return "No history available."
        return "\n".join(self.history)

# Main interface to interact with the calculator
def main():
    calc = AdvancedCalculator()
    print("Advanced Calculator")
    print("Type 'exit' to quit.")
    
    while True:
        print("\nOptions:")
        print("1. Enter an expression (e.g., 2+2, sin(30), log(10), etc.)")
        print("2. View History")
        print("3. Memory Operations (Store, Recall, Clear)")
        print("4. Exit")
        
        option = input("Choose an option: ")
        
        if option == "1":
            expression = input("Enter the expression: ")
            if expression.lower() == "exit":
                break
            result = calc.evaluate_expression(expression)
            print(f"Result: {result}")
        
        elif option == "2":
            print("History:")
            print(calc.show_history())
        
        elif option == "3":
            memory_option = input("Memory Operations:\n1. Store value\n2. Recall value\n3. Clear memory\nChoose option: ")
            if memory_option == "1":
                value = float(input("Enter value to store in memory: "))
                print(calc.store_to_memory(value))
            elif memory_option == "2":
                print(calc.recall_memory())
            elif memory_option == "3":
                print(calc.clear_memory())
            else:
                print("Invalid option!")
        
        elif option == "4":
            print("Exiting...")
            break
        else:
            print("Invalid option! Please choose again.")

if __name__ == "__main__":
    main()




import math
import cmath
import sympy as sp

class AdvancedCalculator:
    def __init__(self):
        self.history = []  # Stores previous calculations
        self.memory = 0  # Stores the memory value

    # Function to evaluate expressions with basic and scientific operations
    def evaluate_expression(self, expression):
        try:
            # Handle functions like sin, cos, etc.
            expression = expression.replace("sin", "math.sin")
            expression = expression.replace("cos", "math.cos")
            expression = expression.replace("tan", "math.tan")
            expression = expression.replace("log", "math.log10")
            expression = expression.replace("sqrt", "math.sqrt")
            expression = expression.replace("exp", "math.exp")
            expression = expression.replace("pi", str(math.pi))
            expression = expression.replace("e", str(math.e))
            
            # Handle complex numbers
            if 'j' in expression:
                expression = expression.replace("j", "1j")

            # Evaluate the expression
            result = eval(expression)  # Evaluate the mathematical expression
            self.history.append(f"{expression} = {result}")  # Save to history
            return result
        except Exception as e:
            return f"Error: {e}"

    # Function for symbolic differentiation
    def differentiate(self, expression):
        try:
            # Use SymPy to parse and differentiate the expression
            x = sp.symbols('x')
            expr = sp.sympify(expression)
            derivative = sp.diff(expr, x)
            self.history.append(f"diff({expression}) = {derivative}")
            return derivative
        except Exception as e:
            return f"Error: {e}"

    # Function for symbolic integration
    def integrate(self, expression):
        try:
            # Use SymPy to parse and integrate the expression
            x = sp.symbols('x')
            expr = sp.sympify(expression)
            integral = sp.integrate(expr, x)
            self.history.append(f"integrate({expression}) = {integral}")
            return integral
        except Exception as e:
            return f"Error: {e}"

    # Function to clear the memory
    def clear_memory(self):
        self.memory = 0
        return "Memory Cleared!"

    # Function to store a value in memory
    def store_to_memory(self, value):
        self.memory = value
        return f"Stored {value} in memory."

    # Function to recall the value from memory
    def recall_memory(self):
        return f"Memory: {self.memory}"

    # Function to display the history
    def show_history(self):
        if not self.history:
            return "No history available."
        return "\n".join(self.history)


# Main interface to interact with the calculator
def main():
    calc = AdvancedCalculator()
    print("Advanced Calculator with Differentiation & Integration")
    print("Type 'exit' to quit.")
    
    while True:
        print("\nOptions:")
        print("1. Enter an expression (e.g., 2+2, sin(30), log(10), etc.)")
        print("2. View History")
        print("3. Memory Operations (Store, Recall, Clear)")
        print("4. Differentiation (e.g., diff(x**2 + 3*x))")
        print("5. Integration (e.g., integrate(x**2 + 3*x))")
        print("6. Exit")
        
        option = input("Choose an option: ")
        
        if option == "1":
            expression = input("Enter the expression: ")
            if expression.lower() == "exit":
                break
            result = calc.evaluate_expression(expression)
            print(f"Result: {result}")
        
        elif option == "2":
            print("History:")
            print(calc.show_history())
        
        elif option == "3":
            memory_option = input("Memory Operations:\n1. Store value\n2. Recall value\n3. Clear memory\nChoose option: ")
            if memory_option == "1":
                value = float(input("Enter value to store in memory: "))
                print(calc.store_to_memory(value))
            elif memory_option == "2":
                print(calc.recall_memory())
            elif memory_option == "3":
                print(calc.clear_memory())
            else:
                print("Invalid option!")
        
        elif option == "4":
            expression = input("Enter the expression to differentiate: ")
            result = calc.differentiate(expression)
            print(f"Result: {result}")
        
        elif option == "5":
            expression = input("Enter the expression to integrate: ")
            result = calc.integrate(expression)
            print(f"Result: {result}")
        
        elif option == "6":
            print("Exiting...")
            break
        else:
            print("Invalid option! Please choose again.")

if __name__ == "__main__":
    main()
