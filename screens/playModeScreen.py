import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class PlayModeScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(bg="#000000")

        self.load_images()
        self.create_widgets()

        self.master.bind("<Configure>", self.resize_background)

    def load_images(self):
        try:
            self.original_background = Image.open("background01.png")
        except Exception as e:
            print(f"Erreur chargement fond : {e}")

    def create_widgets(self):
        self.background_label = tk.Label(self)
        self.background_label.place(relwidth=1, relheight=1)

        button_frame = tk.Frame(self, bg=None)
        button_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Button(button_frame, text="Joueur vs Joueur", command=lambda: self.master.show_frame("carselect")).pack(pady=10)
        tk.Button(button_frame, text="Joueur vs IA", command=lambda: messagebox.showinfo("Joueur vs IA", "À implémenter")).pack(pady=10)
        tk.Button(button_frame, text="Retour au Menu", command=lambda: self.master.show_frame("main")).pack(pady=10)

    def resize_background(self, event):
        if hasattr(self, 'original_background'):
            resized_bg = self.original_background.resize((event.width, event.height), Image.Resampling.LANCZOS)
            self.background_img = ImageTk.PhotoImage(resized_bg)
            self.background_label.config(image=self.background_img)
