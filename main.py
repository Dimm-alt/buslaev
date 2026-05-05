import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.expenses = self.load_data()
        self.setup_ui()

    def setup_ui(self):
        
        tk.Label(self.root, text="Сумма:").grid(row=0, column=0)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Категория:").grid(row=1, column=0)
        self.category_var = tk.StringVar()
        categories = ["Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"]
        ttk.Combobox(self.root, textvariable=self.category_var,
                   values=categories).grid(row=1, column=1)

        tk.Label(self.root, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0)
        self.date_entry = tk.Entry(self.root)
        self.date_entry.grid(row=2, column=1)

     
        tk.Button(self.root, text="Добавить расход",
                 command=self.add_expense).grid(row=3, column=0, columnspan=2)


      
        self.tree = ttk.Treeview(self.root, columns=("Сумма", "Категория", "Дата"),
                               show="headings")
        for col in ("Сумма", "Категория", "Дата"):
            self.tree.heading(col, text=col)
        self.tree.grid(row=4, column=0, columnspan=2)

        
        tk.Label(self.root, text="Фильтр категории:").grid(row=5, column=0)
        self.filter_var = tk.StringVar(value="Все")
        ttk.Combobox(self.root, textvariable=self.filter_var,
                   values=["Все"] + categories).grid(row=5, column=1)

        tk.Label(self.root, text="С даты (ГГГГ-ММ-ДД):").grid(row=6, column=0)
        self.start_entry = tk.Entry(self.root)
        self.start_entry.grid(row=6, column=1)

        tk.Label(self.root, text="По дату (ГГГГ-ММ-ДД):").grid(row=7, column=0)
        self.end_entry = tk.Entry(self.root)
        self.end_entry.grid(row=7, column=1)

        tk.Button(self.root, text="Применить фильтры",
                 command=self.apply_filters).grid(row=8, column=0)
        tk.Button(self.root, text="Показать сумму",
                 command=self.calculate_sum).grid(row=8, column=1)

        self.sum_label = tk.Label(self.root, text="Общая сумма: 0")
        self.sum_label.grid(row=9, column=0, columnspan=2)

        self.update_table()

    def validate_input(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма")
            return False

        try:
            datetime.strptime(self.date_entry.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты")
            return False

        if not self.category_var.get():
            messagebox.showerror("Ошибка", "Выберите категорию")
            return False
        return True

    def add_expense(self):
        if not self.validate_input():
            return

        self.expenses.append({
            "amount": float(self.amount_entry.get()),
            "category": self.category_var.get(),
            "date": self.date_entry.get()
        })
        self.save_data()
        self.update_table()
        self.clear_inputs()

    def clear_inputs(self):
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.category_var.set("")

    def save_data(self):
        with open("expenses.json", "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)

    def load_data(self):
        try:
            with open("expenses.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for expense in self.expenses:
            self.tree.insert("", "end", values=(
                expense["amount"], expense["category"], expense["date"]
            ))

    def apply_filters(self):
        filtered = self.expenses
        category = self.filter_var.get()
        if category != "Все":
            filtered = [e for e in filtered if e["category"] == category]

        start = self.start_entry.get()
        end = self.end_entry.get()

        if start:
            try:
                start_date = datetime.strptime(start, "%Y-%m-%d")
                filtered = [e for e in filtered
                           if datetime.strptime(e["date"], "%Y-%m-%d") >= start_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверная начальная дата")
                return

        if end:
            try:
                end_date = datetime.strptime(end, "%Y-%m-%d")
                filtered = [e for e in filtered
                   if datetime.strptime(e["date"], "%Y-%m-%d") <= end_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверная конечная дата")
                return

        for item in self.tree.get_children():
            self.tree.delete(item)
        for expense in filtered:
            self.tree.insert("", "end", values=(
                expense["amount"], expense["category"], expense["date"]
            ))

    def calculate_sum(self):
        filtered = self.expenses
        category = self.filter_var.get()
        if category != "Все":
            filtered = [e for e in filtered if e["category"] == category]

        start = self.start_entry.get()
        end = self.end_entry.get()

        if start or end:
            temp_filter = filtered
            if start:
                try:
                    start_date = datetime.strptime(start, "%Y-%m-%d")
                    temp_filter = [e for e in temp_filter
                        if datetime.strptime(e["date"], "%Y-%m-%d") >= start_date]
                except ValueError: pass
            if end:
                try:
                    end_date = datetime.strptime(end, "%Y-%m-%d")
                    temp_filter = [e for e in temp_filter
                       if datetime.strptime(e["date"], "%Y-%m-%d") <= end_date]
                except ValueError: pass
            filtered = temp_filter

        total = sum(e["amount"] for e in filtered)
        self.sum_label.config(text=f"Общая сумма: {total}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
