import numpy as np
import re
from sympy import symbols, sympify, lambdify, diff
import tkinter as tk
from tkinter import ttk

# Define the variable
x = symbols('x')

def preprocess_equation(equation):
    processed_equation = re.sub(r'\bx\^(\d+)', r'x**\1', equation)
    processed_equation = re.sub(r'(\d+)(x)\^(\d+)', r'\1*\2**\3', processed_equation)
    processed_equation = re.sub(r'(\d+)(x)(?![\^])', r'\1*\2', processed_equation)
    processed_equation = processed_equation.replace('^', '**')
    return processed_equation

def parse_equation(equation_str):
    equation_str = preprocess_equation(equation_str)
    try:
        f = sympify(equation_str)
    except Exception as e:
        raise ValueError(f"Error parsing the equation: {e}")
    f_lambda = lambdify(x, f, 'numpy')
    return f, f_lambda

def bisection_method(interval1, interval2, f_lambda):
    iteration_data = []
    iteration = 0
    while True:
        xl = interval1
        fxl = f_lambda(xl)

        xu = interval2
        fxu = f_lambda(xu)

        xm = (xl + xu) / 2
        fxm = f_lambda(xm)

        fxlxfxm = fxl * fxm
        iteration += 1
        iteration_data.append([iteration, xl, fxl, xm, fxm, xu, fxu, fxlxfxm])
        if abs(fxlxfxm) <= 0.0000004:
            return iteration_data, xm
        elif fxlxfxm > 0:
            interval1 = xm
        elif fxlxfxm < 0:
            interval2 = xm

def regula_falsi_method(interval1, interval2, f_lambda, tol):
    iteration_data = []
    iteration = 0
    while True:
        xl = interval1
        fxl = f_lambda(xl)

        xu = interval2
        fxu = f_lambda(xu)

        xm = xu - (fxu * (xl - xu)) / (fxl - fxu)
        fxm = f_lambda(xm)

        fxlxfxm = fxl * fxm
        iteration += 1
        iteration_data.append([iteration, xl, fxl, xm, fxm, xu, fxu, fxlxfxm])
        if abs(fxlxfxm) <= 0.0000004:
            return iteration_data, xm
        elif fxlxfxm > 0:
            interval1 = xm
        else:
            interval2 = xm

def fixed_point(f_lambda, f_prime_lambda, x0, tol):
    iteration_data = []
    iteration = 0
    g = lambda x: x - f_lambda(x) / f_prime_lambda(x)
    while True:
        x1 = g(x0)
        iteration += 1
        iteration_data.append([iteration, x0, g(x0), abs(x1 - x0)])
        if abs(x1 - x0) <= tol:
            return iteration_data, x1
        x0 = x1

def newton(f_lambda, f_prime_lambda, x0, tol):
    iteration_data = []
    iteration = 0
    while True:
        x1 = x0 - f_lambda(x0) / f_prime_lambda(x0)
        iteration += 1
        iteration_data.append([iteration, x0, f_lambda(x0), f_prime_lambda(x0), x1])
        if abs(x1 - x0) <= tol:
            return iteration_data, x1
        x0 = x1

def secant(f_lambda, x0, x1, tol):
    iteration_data = []
    iteration = 0
    while True:
        fx0 = f_lambda(x0)
        fx1 = f_lambda(x1)
        x2 = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
        iteration += 1
        iteration_data.append([iteration, x1, fx1, x0, fx0, x2])
        if abs(x2 - x1) <= tol:
            return iteration_data, x2
        x0, x1 = x1, x2

def show_results(method_name, iteration_data, root_value):
    root = tk.Tk()
    root.title(f"{method_name} Detailed Results")

    # Define column headings and columns based on the method
    columns = []
    headings = []
    
    if method_name == "Bisection Method":
        columns = ["k", "xl", "fxl", "xm", "fxm", "xu", "fxu", "fxl*fxm"]
        headings = ["k", "xl", "f(xl)", "xm", "f(xm)", "xu", "f(xu)", "f(xl)*f(xm)"]
    elif method_name == "Regula Falsi Method":
        columns = ["k", "xl", "fxl", "xm", "fxm", "xu", "fxu", "fxl*fxm"]
        headings = ["k", "xl", "f(xl)", "xm", "f(xm)", "xu", "f(xu)", "f(xl)*f(xm)"]
    elif method_name == "Fixed Point Method":
        columns = ["k", "xn", "g(xn)", "relative error"]
        headings = ["k", "xn", "g(xn)", "relative error"]
    elif method_name == "Newton-Raphson Method":
        columns = ["k", "xn", "F(xn)", "f'(xn)", "xn+1"]
        headings = ["k", "xn", "f(xn)", "f'(xn)", "xn+1"]
    elif method_name == "Secant Method":
        columns = ["k", "xn", "f(xn)", "xn-1", "f(xn-1)", "xn+1"]
        headings = ["k", "xn", "f(xn)", "xn-1", "f(xn-1)", "xn+1"]

    tree = ttk.Treeview(root, columns=columns, show='headings')
    
    # Define column headings
    for col, heading in zip(columns, headings):
        tree.heading(col, text=heading)
        tree.column(col, width=100, anchor='center')  # Adjust width as needed
    
    # Round values to 6 decimal places before inserting them
    rounded_data = [[round(value, 6) for value in row] for row in iteration_data]
    
    for row in rounded_data:
        tree.insert("", tk.END, values=row)
    
    # Show the root value rounded
    tk.Label(root, text=f"Root: {round(root_value, 6):.6f}").pack(pady=10)
    
    tree.pack(expand=True, fill='both')
    
    root.mainloop()



def main():
    print("Numerical Method (Finding Root)")
    print("A. Bisection Method")
    print("B. Regula Falsi Method")
    print("C. Fixed Point Method")
    print("D. Newton-Raphson Method")
    print("E. Secant Method\n")
    choice = input("Select your desired method (A-E): ").strip().upper()
    
    equation_str = input("Input a polynomial equation: ")
    try:
        f, f_lambda = parse_equation(equation_str)
    except ValueError as ve:
        print(ve)
        return

    f_prime_str = diff(f, x)
    f_prime_lambda = lambdify(x, f_prime_str, 'numpy')

    tol = 1e-6

    if choice == 'A':
        a = float(input("Input the lower bound (xl): "))
        b = float(input("Input the upper bound (xu): "))
        method_choice = input("Do you want to use the detailed bisection method (Y/N)? ").strip().upper()
        if method_choice == 'Y':
            iteration_data, root_value = bisection_method(a, b, f_lambda)
            show_results("Bisection Method", iteration_data, root_value)
        else:
            result = bisection_method(a, b, f_lambda)
            print(f"The root is: {result[1]}")
    elif choice == 'B':
        a = float(input("Input the lower bound (xl): "))
        b = float(input("Input the upper bound (xu): "))
        method_choice = input("Do you want to use the detailed regula falsi method (Y/N)? ").strip().upper()
        if method_choice == 'Y':
            iteration_data, root_value = regula_falsi_method(a, b, f_lambda, tol)
            show_results("Regula Falsi Method", iteration_data, root_value)
        else:
            result = regula_falsi_method(a, b, f_lambda, tol)
            print(f"The root is: {result[1]}")
    elif choice == 'C':
        x0 = float(input("Input the initial guess x_0: "))
        iteration_data, root_value = fixed_point(f_lambda, f_prime_lambda, x0, tol)
        show_results("Fixed Point Method", iteration_data, root_value)
    elif choice == 'D':
        x0 = float(input("Input the initial guess x_0: "))
        iteration_data, root_value = newton(f_lambda, f_prime_lambda, x0, tol)
        show_results("Newton-Raphson Method", iteration_data, root_value)
    elif choice == 'E':
        x0 = float(input("Input the initial guess (x_n): "))
        x1 = float(input("Input the (x_n-1): "))
        iteration_data, root_value = secant(f_lambda, x0, x1, tol)
        show_results("Secant Method", iteration_data, root_value)
    else:
        print("Invalid choice")
        return

if __name__ == "__main__":
    main()
