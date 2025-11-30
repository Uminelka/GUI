import tkinter as tk
from tkinter import messagebox
import math


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Простой Калькулятор")
        self.root.geometry("300x400")

        vcmd = (root.register(self.validate_input), "%S", "%P")

        self.entry = tk.Entry(
            root,
            font=("Arial", 20),
            justify="right",
            validate="key",
            validatecommand=vcmd,
        )
        self.entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="we")

        buttons = [
            ("7", 1, 0),
            ("8", 1, 1),
            ("9", 1, 2),
            ("/", 1, 3),
            ("4", 2, 0),
            ("5", 2, 1),
            ("6", 2, 2),
            ("*", 2, 3),
            ("1", 3, 0),
            ("2", 3, 1),
            ("3", 3, 2),
            ("-", 3, 3),
            ("0", 4, 0),
            (".", 4, 1),
            ("+", 4, 2),
        ]

        for text, row, col in buttons:
            tk.Button(
                root,
                text=text,
                font=("Arial", 15),
                command=lambda t=text: self.click(t),
            ).grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

        tk.Button(
            root, text="=", font=("Arial", 15), bg="lightblue", command=self.calculate
        ).grid(row=4, column=3, sticky="nsew", padx=2, pady=2)
        tk.Button(
            root, text="C", font=("Arial", 15), bg="red", fg="white", command=self.clear
        ).grid(row=5, column=0, columnspan=2, sticky="nsew", padx=2, pady=2)
        tk.Button(root, text="√", font=("Arial", 15), command=self.sqrt).grid(
            row=5, column=2, columnspan=2, sticky="nsew", padx=2, pady=2
        )

        for i in range(4):
            root.grid_columnconfigure(i, weight=1)
        for i in range(6):
            root.grid_rowconfigure(i, weight=1)

    def validate_input(self, char, new_value):
        allowed = "0123456789.+-*/"
        if new_value == "":
            return True
        return all(c in allowed for c in new_value)

    def click(self, value):
        self.entry.insert(tk.END, value)

    def clear(self):
        self.entry.delete(0, tk.END)

    def calculate(self):
        expression = self.entry.get()
        try:
            result = eval(expression)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(result))
        except ZeroDivisionError:
            messagebox.showerror("Ошибка", "На ноль делить нельзя!")
            self.clear()
        except Exception:
            messagebox.showerror("Ошибка", "Некорректное выражение")
            self.clear()

    def sqrt(self):
        try:
            value = float(self.entry.get())
            if value < 0:
                messagebox.showerror("Ошибка", "Корень из отрицательного числа!")
                return
            result = math.sqrt(value)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(result))
        except:
            messagebox.showerror("Ошибка", "Введите число")


if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()
