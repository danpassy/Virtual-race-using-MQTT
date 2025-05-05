import tkinter as tk
from tkinter import messagebox
import json
import os

def afficher_historique(parent):
    historique_file = "historique.json"
    if not os.path.exists(historique_file):
        messagebox.showinfo("Historique", "Aucune course enregistrée.", parent=parent)
        return

    with open(historique_file, "r") as f:
        historique = json.load(f)

    fenetre = tk.Toplevel(parent)
    fenetre.title("Historique des courses")
    fenetre.geometry("400x400")
    fenetre.resizable(False, False)

    text_widget = tk.Text(fenetre, wrap="word", font=("Arial", 10))
    text_widget.pack(fill="both", expand=True, padx=10, pady=10)

    for course in reversed(historique[-10:]):  # Dernières 10 courses
        text_widget.insert("end", f"📅 {course['date']}\n")
        text_widget.insert("end", f"🗺️ Carte : {course['carte']}\n")
        for i, (joueur, score) in enumerate(course['classement'], start=1):
            text_widget.insert("end", f"  {i}. {joueur} - {score} points\n")
        text_widget.insert("end", "\n")

    text_widget.config(state="disabled")  # Lecture seule
