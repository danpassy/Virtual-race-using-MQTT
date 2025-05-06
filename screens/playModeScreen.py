import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class PlayModeScreen(tk.Frame):
    def destroy(self):
        self.master.unbind("<Configure>")
        super().destroy()
    def __init__(self, master, show_car_selection=None):
        super().__init__(master)
        self.master = master
        self.show_car_selection = show_car_selection
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

        tk.Button(
            button_frame,
            text="Joueur vs Joueur",
            font=("Helvetica", 16),
            command=self.launch_car_selection
        ).pack(pady=10)

        tk.Button(
            button_frame,
            text="Joueur vs IA",
            font=("Helvetica", 16),
            command=lambda: messagebox.showinfo("Joueur vs IA", "À implémenter")
        ).pack(pady=10)

        tk.Button(
            button_frame,
            text="⬅ Retour au Menu",
            font=("Helvetica", 14),
            command=lambda: self.master.show_frame("main")
        ).pack(pady=10)

    def resize_background(self, event):
        try:
            if hasattr(self, 'original_background') and self.background_label.winfo_exists():
                # ✅ Correction : redimensionnement sécurisé du fond sans duplication ni erreur de syntaxe
                resized_bg = self.original_background.resize((event.width, event.height), Image.Resampling.LANCZOS)
                self.background_img = ImageTk.PhotoImage(resized_bg)
                self.background_label.config(image=self.background_img)
        except tk.TclError as e:
            print(f"[⚠️ Resize annulé] {e}")
            print(f"[⚠️ Resize annulé] {e}")
            self.background_label.config(image=self.background_img)            
            self.background_img = ImageTk.PhotoImage(resized_bg)
            self.background_label.config(image=self.background_img)

    def launch_car_selection(self):
        if self.show_car_selection:
            print("[DEBUG] ➡️ Accès à l’écran de sélection de voiture.")
            self.show_car_selection()
        else:
            print("[ERREUR] show_car_selection callback manquant !")
