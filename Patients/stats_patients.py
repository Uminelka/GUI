import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import Optional
import json
import os
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class Patient:
    fio: str
    age: int
    sex: str
    height: float
    weight: float
    bmi: float


DB_FILE = "patients.json"


class PatientForm(tk.Toplevel):
    def __init__(self, master, on_save, patient: Optional[Patient] = None):
        super().__init__(master)
        self.title("Пациент")
        self.geometry("300x350")
        self.on_save = on_save

        self.e_fio = self._make_input("ФИО")
        self.e_age = self._make_input("Возраст")
        self.c_sex = self._make_combo("Пол", ["М", "Ж"])
        self.e_height = self._make_input("Рост (см)")
        self.e_weight = self._make_input("Вес (кг)")

        if patient:
            self.e_fio.insert(0, patient.fio)
            self.e_age.insert(0, str(patient.age))
            self.c_sex.set(patient.sex)
            self.e_height.insert(0, str(patient.height)) 
            self.e_weight.insert(0, str(patient.weight)) 

        tk.Button(self, text="Сохранить", bg="lightgreen", command=self.save).pack(pady=10)

    def _make_input(self, label):
        tk.Label(self, text=label).pack()
        entry = tk.Entry(self)
        entry.pack()
        return entry

    def _make_combo(self, label, values):
        tk.Label(self, text=label).pack()
        box = ttk.Combobox(self, values=values, state="readonly")
        box.pack()
        box.current(0)
        return box

    def save(self):
        try:
            fio = self.e_fio.get().strip()
            if not fio or any(ch.isdigit() for ch in fio):
                raise ValueError("Некорректное ФИО")

            age = int(self.e_age.get())
            height = float(self.e_height.get())
            weight = float(self.e_weight.get())

            if age <= 0 or age > 150:
                raise ValueError("Неверный возраст")
            if height < 30 or height > 300:
                raise ValueError("Неверный рост")
            if weight < 2 or weight > 500:
                raise ValueError("Неверный вес")

            bmi = round(weight / ((height / 100) ** 2), 2)

            new_patient = Patient(fio, age, self.c_sex.get(), height, weight, bmi)
            self.on_save(new_patient)
            self.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


class PatientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт пациентов")
        self.root.geometry("900x600")

        self.patients: list[Patient] = []
        self.load()

        self.sheet = ttk.Treeview(root, columns=("fio", "age", "sex", "h", "w", "bmi"),
                                  show="headings")
        for col in self.sheet["columns"]:
            self.sheet.heading(col, text=col)
            self.sheet.column(col, width=140)
        self.sheet.pack(fill="both", expand=True)

        panel = tk.Frame(root)
        panel.pack(fill="x", pady=10)

        tk.Button(panel, text="Добавить", command=self.add).pack(side="left", padx=5)
        tk.Button(panel, text="Редактировать", command=self.edit).pack(side="left", padx=5)
        tk.Button(panel, text="Статистика", command=self.stats).pack(side="right", padx=5)

        self.refresh()

    def load(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self.patients = [Patient(**p) for p in raw]
            except:
                self.patients = []

    def save(self):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump([p.__dict__ for p in self.patients], f, ensure_ascii=False, indent=4)

    def refresh(self):
        for row in self.sheet.get_children():
            self.sheet.delete(row)

        for p in self.patients:
            self.sheet.insert("", "end",
                              values=(str(p.fio), str(p.age), str(p.sex), 
                                      str(p.height), str(p.weight), str(p.bmi)))

    def add(self):
        def callback(new_patient):
            self.patients.append(new_patient)
            self.save()
            self.refresh()

        PatientForm(self.root, callback, None) 

    def edit(self):
        selected = self.sheet.selection()
        if not selected:
            return

        idx = self.sheet.index(selected[0])
        old_patient = self.patients[idx]

        def callback(updated):
            self.patients[idx] = updated
            self.save()
            self.refresh()

        PatientForm(self.root, callback, old_patient)

    def stats(self):
        if not self.patients:
            messagebox.showinfo("Нет данных", "Пациентов нет")
            return

        ages = [p.age for p in self.patients]
        sexes = [p.sex for p in self.patients]
        bmis = [p.bmi for p in self.patients]

        ages_array = np.array(ages)
        sexes_array = np.array(sexes)
        bmis_array = np.array(bmis)

        plt.figure(figsize=(12, 8))

        # График 1: Распределение пациентов по полу
        plt.subplot(2, 2, 1)
        plt.title("Распределение пациентов по полу")
        plt.xlabel("Пол")
        plt.ylabel("Количество")
        
        male_count = np.sum(sexes_array == "М")
        female_count = np.sum(sexes_array == "Ж")
        
        plt.bar(["Мужчины", "Женщины"], [male_count, female_count], color=["blue", "pink"])
        plt.grid(True, axis='y')

        # График 2: Распределение возраста пациентов
        plt.subplot(2, 2, 2)
        plt.title("Распределение возраста пациентов")
        plt.xlabel("Возраст")
        plt.ylabel("Количество")
        plt.hist(ages_array, bins=10, color="orange", edgecolor="black")
        plt.grid(True)

        # График 3: Распределение ИМТ пациентов
        plt.subplot(2, 2, 3)
        plt.title("Распределение ИМТ пациентов")
        plt.xlabel("ИМТ")
        plt.ylabel("Количество")
        plt.hist(bmis_array, bins=10, color="green", edgecolor="black")
        plt.grid(True)

        # График 4: Зависимость ИМТ от возраста
        plt.subplot(2, 2, 4)
        plt.title("Зависимость ИМТ от возраста")
        plt.xlabel("Возраст")
        plt.ylabel("ИМТ")
        plt.scatter(ages_array, bmis_array, color="red")
        plt.grid(True)

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    PatientApp(root)
    root.mainloop()
