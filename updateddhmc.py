import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
import numpy as np
import sympy as sp

class DHMatrixCalculator:
    def __init__(self, master):
        self.master = master
        self.master.title("DH Matrix Calculator")

        self.num_joints_label = tk.Label(master, text="Number of Joints:")
        self.num_joints_label.grid(row=0, column=0)
        self.num_joints_entry = tk.Entry(master)
        self.num_joints_entry.grid(row=0, column=1)

        self.var_or_num_label = tk.Label(master, text="Parameter Type:")
        self.var_or_num_label.grid(row=1, column=0)
        self.var_or_num_var = tk.StringVar()
        self.var_or_num_var.set("Numeric")
        self.var_or_num_menu = tk.OptionMenu(master, self.var_or_num_var, "Numeric", "Symbolic")
        self.var_or_num_menu.grid(row=1, column=1)

        self.calculate_button = tk.Button(master, text="Calculate DH Matrix", command=self.calculate_dh_matrix)
        self.calculate_button.grid(row=2, column=0, columnspan=2)

        # Add a Treeview widget for the DH parameters table
        self.dh_parameters_tree = ttk.Treeview(master, columns=("Alpha", "A", "D", "Theta"), show="headings")
        self.dh_parameters_tree.heading("Alpha", text="Alpha")
        self.dh_parameters_tree.heading("A", text="A")
        self.dh_parameters_tree.heading("D", text="D")
        self.dh_parameters_tree.heading("Theta", text="Theta")
        self.dh_parameters_tree.grid(row=3, column=0, columnspan=2)

        self.result_text = tk.Text(master, height=15, width=70)
        self.result_text.grid(row=4, column=0, columnspan=2)

    def calculate_dh_matrix(self):
        try:
            num_joints = int(self.num_joints_entry.get())
        except ValueError:
            self.show_error("Please enter a valid number of joints.")
            return

        dh_parameters = []

        # Clear existing entries in the treeview
        for item in self.dh_parameters_tree.get_children():
            self.dh_parameters_tree.delete(item)

        for i in range(num_joints):
            alpha = self.get_input(f"Enter alpha for Joint {i + 1}: ")
            a = self.get_input(f"Enter a for Joint {i + 1}: ")
            d = self.get_input(f"Enter d for Joint {i + 1}: ")
            theta = self.get_input(f"Enter theta for Joint {i + 1}: ")

            dh_parameters.append([alpha, a, d, theta])

            # Insert the DH parameters into the treeview
            self.dh_parameters_tree.insert("", "end", values=(alpha, a, d, theta))

        parameter_type = self.var_or_num_var.get()

        if parameter_type == "Numeric":
            intermediate_matrices = self.calculate_numeric_dh_matrices(dh_parameters)
        elif parameter_type == "Symbolic":
            intermediate_matrices = self.calculate_symbolic_dh_matrices(dh_parameters)
        else:
            self.show_error("Invalid parameter type selected.")
            return

        self.display_result("Intermediate Matrices:\n")
        for i, matrix in enumerate(intermediate_matrices):
            matrix_text = f"DH Matrix for Joint {i + 1}:\n{self.format_matrix(matrix)}\n\n"
            self.display_result(matrix_text)

        final_matrix = self.calculate_final_dh_matrix(intermediate_matrices, parameter_type)

        result_text = f"Final DH Matrix:\n\n{self.format_matrix(final_matrix)}"
        self.display_result(result_text)

    def get_input(self, prompt):
        input_value = simpledialog.askstring("Input", prompt)
        try:
            # Try converting the input to a float for numeric mode
            return float(input_value)
        except ValueError:
            # If conversion fails, assume it's a symbolic expression for symbolic mode
            return sp.symbols(input_value)

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def display_result(self, result_text):
        self.result_text.insert(tk.END, result_text)
        self.result_text.insert(tk.END, "\n")

    def calculate_numeric_dh_matrices(self, dh_parameters):
        intermediate_matrices = []  # Store intermediate matrices for each joint

        for params in dh_parameters:
            alpha, a, d, theta = params
            alpha_rad = np.deg2rad(alpha)
            theta_rad = np.deg2rad(theta)

            dh_matrix = np.array([
                [np.cos(theta_rad), -np.sin(theta_rad) * np.cos(alpha_rad), np.sin(theta_rad) * np.sin(alpha_rad), a * np.cos(theta_rad)],
                [np.sin(theta_rad), np.cos(theta_rad) * np.cos(alpha_rad), -np.cos(theta_rad) * np.sin(alpha_rad), a * np.sin(theta_rad)],
                [0, np.sin(alpha_rad), np.cos(alpha_rad), d],
                [0, 0, 0, 1]
            ])
            intermediate_matrices.append(dh_matrix)

        return intermediate_matrices

    def calculate_symbolic_dh_matrices(self, dh_parameters):
        intermediate_matrices = []  # Store intermediate matrices for each joint

        for params in dh_parameters:
            alpha, a, d, theta = params
            if isinstance(alpha, sp.Expr):
                alpha_rad = alpha
            else:
                alpha_rad = sp.rad(alpha)

            if isinstance(theta, sp.Expr):
                theta_rad = theta
            else:
                theta_rad = sp.rad(theta)

            dh_matrix = sp.Matrix([
                [sp.cos(theta_rad), -sp.sin(theta_rad) * sp.cos(alpha_rad), sp.sin(theta_rad) * sp.sin(alpha_rad),
                 a * sp.cos(theta_rad)],
                [sp.sin(theta_rad), sp.cos(alpha_rad) * sp.cos(theta_rad), -sp.sin(alpha_rad) * sp.cos(theta_rad),
                 a * sp.sin(theta_rad)],
                [0, sp.sin(alpha_rad), sp.cos(alpha_rad), d],
                [0, 0, 0, 1]
            ])
            intermediate_matrices.append(dh_matrix)

        return intermediate_matrices

    def calculate_final_dh_matrix(self, intermediate_matrices, parameter_type):
        if parameter_type == "Numeric":
            final_matrix = np.identity(4)
            for matrix in intermediate_matrices:
                final_matrix = final_matrix @ matrix
            final_matrix = np.round(final_matrix).astype(int)  # Round and convert to integers
        elif parameter_type == "Symbolic":
            final_matrix = sp.eye(4)
            for matrix in intermediate_matrices:
                final_matrix = final_matrix * matrix
            final_matrix = sp.simplify(final_matrix)  # Simplify the symbolic expression
        else:
            self.show_error("Invalid parameter type selected.")
            return

        return final_matrix

    def format_matrix(self, matrix):
        # Format the matrix for display
        formatted_matrix = '['
        for row in matrix.tolist():
            formatted_row = '['
            for element in row:
                if isinstance(element, sp.Expr):
                    simplified_element = sp.simplify(element)
                    if simplified_element.is_integer:
                        formatted_row += f'{int(simplified_element)} '
                    else:
                        formatted_row += f'{sp.N(simplified_element, 4)} '
                elif isinstance(element, sp.Basic):
                    formatted_row += f'{sp.simplify(element)} '
                else:
                    formatted_row += f'{int(element)} '
            formatted_row = formatted_row.rstrip() + ']\n '
            formatted_matrix += formatted_row
        formatted_matrix += ']'
        return formatted_matrix

def main():
    root = tk.Tk()
    app = DHMatrixCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()

