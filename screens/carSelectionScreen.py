
import tkinter as tk
from PIL import Image, ImageTk
import os

class CarSelectionScreen(tk.Frame):
    def __init__(self, master, go_back_callback=None):
        super().__init__(master)
        self.master = master
        self.go_back_callback = go_back_callback
        self.configure(bg="#000000")

        # === Image de fond adaptative ===
        try:
            bg_path = "background01.png"
            self.original_bg = Image.open(bg_path)
            self.bg_photo = ImageTk.PhotoImage(self.original_bg)
            self.bg_label = tk.Label(self, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()
        except Exception as e:
            print(f"Erreur chargement fond : {e}")

        self.car_labels = []
        self.original_car_images = []
        self.selected_car_index = None

        self.name_label = None
        self.name_entry = None
        self.continue_button = None
        self.back_button = None

        self.load_images()
        self.create_widgets()
        self.bind("<Configure>", self.redraw_layout)

    def load_images(self):
        for i in range(1, 7):
            try:
                img = Image.open(f"assets/cars/car{i}.png")
                self.original_car_images.append(img)
            except Exception as e:
                print(f"Erreur chargement voiture {i} :", e)
                self.original_car_images.append(None)

    def create_widgets(self):
        self.name_label = tk.Label(self, text="Entre ton surnom :", fg="white", bg="#000000", font=("Helvetica", 16))
        self.name_label.pack(pady=(30, 5))
        self.name_entry = tk.Entry(self, font=("Helvetica", 16))
        self.name_entry.pack(pady=(0, 20))

        self.cars_frame = tk.Frame(self, bg="", highlightthickness=0)
        self.cars_frame.pack()

        for idx in range(6):
            label = tk.Label(self.cars_frame, bd=2, relief="flat", bg="#222222", cursor="hand2")
            label.bind("<Button-1>", lambda e, i=idx: self.select_car(i))
            label.pack(side="left", padx=20)
            self.car_labels.append(label)

        self.continue_button = tk.Button(self, text="Continuer", font=("Helvetica", 16), command=self.continue_game)
        self.continue_button.pack(pady=20)

        self.back_button = tk.Button(self, text="Retour", font=("Helvetica", 14), command=self.go_back)
        self.back_button.pack(pady=(0, 20))

    def redraw_layout(self, event=None):
        for idx, img in enumerate(self.original_car_images):
            if img:
                width = 100
                height = 60
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(resized)
                self.car_labels[idx].config(image=tk_image)
                self.car_labels[idx].image = tk_image

        # Resize background image to fit window
        if hasattr(self, 'original_bg') and event:
            resized_bg = self.original_bg.resize((event.width, event.height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized_bg)
            self.bg_label.configure(image=self.bg_photo)
            self.bg_label.image = self.bg_photo

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
        # Lancement de l'écran MQTT ici

    def go_back(self):
        if self.go_back_callback:
            self.go_back_callback()
