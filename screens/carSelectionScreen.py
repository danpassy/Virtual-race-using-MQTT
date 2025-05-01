import tkinter as tk
from PIL import Image, ImageTk
import os

class CarSelectionScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(bg="#000000")

        self.car_images = []
        self.car_labels = []
        self.selected_car_index = None

        self.load_images()
        self.create_widgets()
        self.bind("<Configure>", self.redraw_layout)

    def load_images(self):
        self.original_car_images = []
        for i in range(1, 7):
            try:
                img = Image.open(f"assets/cars/car{i}.png")  # 📁 les images doivent être dans cars/car1.png ... car6.png
                self.original_car_images.append(img)
            except Exception as e:
                print(f"Erreur chargement voiture {i} :", e)
                self.original_car_images.append(None)

    def create_widgets(self):
        # Pseudo joueur
        self.name_label = tk.Label(self, text="Entre ton surnom :", fg="white", bg="#000000", font=("Helvetica", 16))
        self.name_label.pack(pady=(30, 5))
        self.name_entry = tk.Entry(self, font=("Helvetica", 16))
        self.name_entry.pack(pady=(0, 20))

        # Grille de voitures
        self.cars_frame = tk.Frame(self, bg="#000000")
        self.cars_frame.pack(expand=True, fill="both", padx=20, pady=20)

        for idx in range(6):
            label = tk.Label(self.cars_frame, bd=2, relief="flat", bg="#222222", cursor="hand2")
            label.bind("<Button-1>", lambda e, i=idx: self.select_car(i))
            self.car_labels.append(label)
            label.grid(row=idx // 3, column=idx % 3, padx=10, pady=10, sticky="nsew")

        for i in range(2):  # 2 lignes
            self.cars_frame.grid_rowconfigure(i, weight=1)
        for j in range(3):  # 3 colonnes
            self.cars_frame.grid_columnconfigure(j, weight=1)

        # Bouton continuer
        self.continue_button = tk.Button(self, text="Continuer", font=("Helvetica", 16), command=self.continue_game)
        self.continue_button.pack(pady=20)

    def redraw_layout(self, event=None):
        # Redimensionnement des images
        for idx, img in enumerate(self.original_car_images):
            if img:
                width = int(self.cars_frame.winfo_width() / 3.5)
                height = int(self.cars_frame.winfo_height() / 2.5)
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(resized)
                self.car_labels[idx].config(image=tk_image)
                self.car_labels[idx].image = tk_image

    def select_car(self, index):
        self.selected_car_index = index
        for idx, label in enumerate(self.car_labels):
            label.config(highlightthickness=4 if idx == index else 0, highlightbackground="#FFD700")

    def continue_game(self):
        name = self.name_entry.get().strip()
        if not name:
            tk.messagebox.showwarning("Attention", "Entre ton surnom.")
            return
        if self.selected_car_index is None:
            tk.messagebox.showwarning("Attention", "Choisis une voiture.")
            return

        print(f"Joueur : {name} | Voiture : {self.selected_car_index + 1}")
        # Ici tu appelleras le screen MQTT avec les infos sélectionnées
