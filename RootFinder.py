import numpy as np
import re
from sympy import symbols, sympify, lambdify, diff
import tkinter as tk
from tkinter import ttk, messagebox

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
    for widget in results_frame.winfo_children():
        widget.destroy()

    tk.Label(results_frame, text=f"Function f(x): {equation_str}", font=("Courier New", 12)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
    tk.Label(results_frame, text=f"Root: {round(root_value, 6):.6f}", font=("Courier New", 12)).grid(row=1, column=0, padx=10, pady=5, sticky='w')

    total_iterations = len(iteration_data)
    tk.Label(results_frame, text=f"Total Number of Iterations: {total_iterations}", font=("Courier New", 12)).grid(row=2, column=0, padx=10, pady=5, sticky='w')

    columns, headings = get_columns_and_headings(method_name)
    
    style = ttk.Style()
    style.configure("Custom.Treeview.Heading", font=("Courier New", 12), borderwidth=1, relief="solid")
    style.configure("Custom.Treeview", rowheight=25, borderwidth=1, relief="solid")
    
    tree = ttk.Treeview(results_frame, columns=columns, show='headings', style="Custom.Treeview")

    for col, heading in zip(columns, headings):
        tree.heading(col, text=heading)  # Removed style argument
        tree.column(col, width=100, anchor='center')

    rounded_data = [[round(value, 6) for value in row] for row in iteration_data]
    
    for row in rounded_data:
        tree.insert("", tk.END, values=row)
    
    tree.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

    try_again_button = tk.Button(results_frame, text="Try Again", command=try_again, font=("Courier New", 12))
    try_again_button.grid(row=4, column=0, padx=10, pady=10, sticky='e')

    results_frame.grid_rowconfigure(3, weight=1)
    results_frame.grid_columnconfigure(0, weight=1)

    window.geometry("1080x720")

def get_columns_and_headings(method_name):
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
    return columns, headings

def try_again():
    global window
    window.destroy()
    main()

def update_parameter_b_state(*args):
    method_name = method_combobox.get()
    if method_name in ['Fixed Point Method', 'Newton-Raphson Method']:
        param_b_entry.config(state='disabled')
    else:
        param_b_entry.config(state='normal')
    check_show_result_button_state()

def check_show_result_button_state():
    method_name = method_combobox.get()
    equation_filled = function_entry.get().strip() != ""
    param_a_filled = param_a_entry.get().strip() != ""
    param_b_filled = param_b_entry.get().strip() != ""

    if method_name == 'Bisection Method' and equation_filled and param_a_filled and param_b_filled:
        show_result_button.config(state='normal')
    elif method_name == 'Regula Falsi Method' and equation_filled and param_a_filled and param_b_filled:
        show_result_button.config(state='normal')
    elif method_name == 'Fixed Point Method' and equation_filled and param_a_filled:
        show_result_button.config(state='normal')
    elif method_name == 'Newton-Raphson Method' and equation_filled and param_a_filled:
        show_result_button.config(state='normal')
    elif method_name == 'Secant Method' and equation_filled and param_a_filled and param_b_filled:
        show_result_button.config(state='normal')
    else:
        show_result_button.config(state='disabled')

def process_input(method_name):
    global equation_str
    try:
        equation_str = function_entry.get()
        param_a = float(param_a_entry.get())
        param_b = float(param_b_entry.get()) if param_b_entry.get() else None
        tol = 0.0000004

        f, f_lambda = parse_equation(equation_str)
        f_prime = diff(f, x)
        f_prime_lambda = lambdify(x, f_prime, 'numpy')

        if method_name == "Bisection Method":
            iteration_data, root_value = bisection_method(param_a, param_b, f_lambda)
        elif method_name == "Regula Falsi Method":
            iteration_data, root_value = regula_falsi_method(param_a, param_b, f_lambda, tol)
        elif method_name == "Fixed Point Method":
            iteration_data, root_value = fixed_point(f_lambda, f_prime_lambda, param_a, tol)
        elif method_name == "Newton-Raphson Method":
            iteration_data, root_value = newton(f_lambda, f_prime_lambda, param_a, tol)
        elif method_name == "Secant Method":
            iteration_data, root_value = secant(f_lambda, param_a, param_b, tol)
        else:
            raise ValueError("Unknown method")

        show_results(method_name, iteration_data, root_value)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def main():
    global window, function_entry, method_combobox, param_a_entry, param_b_entry, show_result_button, results_frame

    window = tk.Tk()
    window.title("Numerical Methods to Find Roots of Equation")

    tk.Label(window, text="Function (in terms of x):", font=("Courier New", 12)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
    function_entry = tk.Entry(window, font=("Courier New", 12))
    function_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

    tk.Label(window, text="Method:", font=("Courier New", 12)).grid(row=1, column=0, padx=10, pady=5, sticky='w')
    method_combobox = ttk.Combobox(window, values=["Bisection Method", "Regula Falsi Method", "Fixed Point Method", "Newton-Raphson Method", "Secant Method"], font=("Courier New", 12), state="readonly")
    method_combobox.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
    method_combobox.bind("<<ComboboxSelected>>", update_parameter_b_state)

    tk.Label(window, text="Parameter A (or initial guess):", font=("Courier New", 12)).grid(row=2, column=0, padx=10, pady=5, sticky='w')
    param_a_entry = tk.Entry(window, font=("Courier New", 12))
    param_a_entry.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

    tk.Label(window, text="Parameter B (or second guess for Secant Method):", font=("Courier New", 12)).grid(row=3, column=0, padx=10, pady=5, sticky='w')
    param_b_entry = tk.Entry(window, font=("Courier New", 12))
    param_b_entry.grid(row=3, column=1, padx=10, pady=5, sticky='ew')

    show_result_button = tk.Button(window, text="Show Result", command=lambda: process_input(method_combobox.get()), font=("Courier New", 12), state='disabled')
    show_result_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    results_frame = tk.Frame(window)
    results_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

    window.grid_rowconfigure(5, weight=1)
    window.grid_columnconfigure(1, weight=1)

    function_entry.bind("<KeyRelease>", lambda event: check_show_result_button_state())
    param_a_entry.bind("<KeyRelease>", lambda event: check_show_result_button_state())
    param_b_entry.bind("<KeyRelease>", lambda event: check_show_result_button_state())

    window.mainloop()

if __name__ == "__main__":
    main()
