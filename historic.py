import tkinter as tk
from tkinter import messagebox
import json
import os

def afficher_historique(parent):
    historique_file = "historique.json"
    
    if not os.path.exists(historique_file):
        messagebox.showinfo("Historique", "Aucune course enregistrée.", parent=parent)
        return

    try:
        with open(historique_file, "r", encoding="utf-8") as f:
            historique = json.load(f)
        if not isinstance(historique, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        messagebox.showerror("Erreur", "Fichier historique corrompu ou mal formé.", parent=parent)
        return

    fenetre = tk.Toplevel(parent)
    fenetre.title("Historique des courses")
    fenetre.geometry("400x400")
    fenetre.resizable(False, False)

    text_widget = tk.Text(fenetre, wrap="word", font=("Arial", 10), bg="black", fg="white")
    text_widget.pack(fill="both", expand=True, padx=10, pady=10)

    if not historique:
        text_widget.insert("end", "Aucune course enregistrée.")
    else:
        for course in reversed(historique[-10:]):
            date = course.get("date", "Date inconnue")
            carte = course.get("carte", "Carte inconnue")
            classement = course.get("classement", [])

            text_widget.insert("end", f"📅 {date}\n")
            text_widget.insert("end", f"🗺️ Carte : {carte}\n")
            for i, (joueur, score) in enumerate(classement, start=1):
                text_widget.insert("end", f"  {i}. {joueur} - {score}\n")
            text_widget.insert("end", "\n")

    text_widget.config(state="disabled")
