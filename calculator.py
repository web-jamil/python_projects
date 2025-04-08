import tkinter as tk
from tkinter import messagebox
import math

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Calculator")
        self.root.geometry("400x600")
        
        # Initialize the expression and result
        self.expression = ""
        
        # Display frame
        self.display_frame = tk.Frame(self.root)
        self.display_frame.pack()
        
        # Entry widget to display the current expression
        self.result_var = tk.StringVar()
        self.result = tk.Entry(self.display_frame, textvar=self.result_var, font=("Arial", 24), bd=10, relief="sunken", justify="right")
        self.result.grid(row=0, column=0, columnspan=4)
        
        # Button layout
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()

        # Buttons for digits and basic operations
        self.create_buttons()

    def create_buttons(self):
        button_text = [
            ('7', '8', '9', '/'),
            ('4', '5', '6', '*'),
            ('1', '2', '3', '-'),
            ('0', '.', '=', '+'),
            ('sin', 'cos', 'tan', 'log'),
            ('sqrt', 'exp', 'pi', 'clear'),
        ]
        
        row = 0
        for buttons in button_text:
            col = 0
            for text in buttons:
                button = tk.Button(self.button_frame, text=text, font=("Arial", 18), width=6, height=2, command=lambda t=text: self.on_button_click(t))
                button.grid(row=row, column=col)
                col += 1
            row += 1

    def on_button_click(self, button_text):
        if button_text == "clear":
            self.expression = ""
            self.result_var.set(self.expression)
        elif button_text == "=":
            try:
                result = self.calculate_expression(self.expression)
                self.result_var.set(result)
                self.expression = str(result)
            except Exception as e:
                messagebox.showerror("Error", "Invalid expression")
                self.expression = ""
                self.result_var.set(self.expression)
        else:
            self.expression += str(button_text)
            self.result_var.set(self.expression)

    def calculate_expression(self, expr):
        # Replacing expressions for scientific functions
        expr = expr.replace("sin", "math.sin")
        expr = expr.replace("cos", "math.cos")
        expr = expr.replace("tan", "math.tan")
        expr = expr.replace("log", "math.log10")
        expr = expr.replace("sqrt", "math.sqrt")
        expr = expr.replace("exp", "math.exp")
        expr = expr.replace("pi", str(math.pi))

        # Evaluate the expression
        return eval(expr)

# Create the main window
root = tk.Tk()

# Initialize the calculator
calculator = Calculator(root)

# Run the main loop
root.mainloop()
