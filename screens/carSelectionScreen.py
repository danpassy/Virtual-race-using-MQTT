
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import uuid
import json
import paho.mqtt.client as mqtt

class CarSelectionScreen(tk.Frame):
    def __init__(self, master, go_back_callback=None, go_continue_callback=None):
        super().__init__(master)
        self.master = master
        self.go_back_callback = go_back_callback
        self.go_continue_callback = go_continue_callback
        self.configure(bg="#1a1a1a")

        self.car_labels = []
        self.original_car_images = []
        self.selected_car_index = None
        self.uuid = str(uuid.uuid4())

        self.name_label = None
        self.name_entry = None
        self.role_var = tk.StringVar(value="Player1")

        self.continue_button = None
        self.back_button = None

        self.client = mqtt.Client()
        self.client.connect("broker.hivemq.com", 1883, 60)
        self.client.loop_start()

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
        title = tk.Label(self, text="Sélectionne ton joueur et ta voiture", fg="white", bg="#1a1a1a", font=("Helvetica", 20, "bold"))
        title.pack(pady=(20, 10))

        self.name_label = tk.Label(self, text="Ton pseudo :", fg="white", bg="#1a1a1a", font=("Helvetica", 14))
        self.name_label.pack()
        self.name_entry = tk.Entry(self, font=("Helvetica", 14), width=20)
        self.name_entry.pack(pady=(0, 10))

        role_frame = tk.Frame(self, bg="#1a1a1a")
        role_frame.pack()
        tk.Label(role_frame, text="Choisis ton rôle :", font=("Helvetica", 14), fg="white", bg="#1a1a1a").pack(side="left")
        self.role_menu = tk.OptionMenu(role_frame, self.role_var, "Player1", "Player2")
        self.role_menu.config(font=("Helvetica", 12))
        self.role_menu.pack(side="left", padx=10, pady=(0, 20))

        # Voitures
        self.cars_frame = tk.Frame(self, bg="#1a1a1a")
        self.cars_frame.pack(pady=10)
        for idx in range(6):
            label = tk.Label(self.cars_frame, bd=2, relief="flat", bg="#333333", cursor="hand2")
            label.bind("<Button-1>", lambda e, i=idx: self.select_car(i))
            label.grid(row=idx//3, column=idx%3, padx=15, pady=15)
            self.car_labels.append(label)

        # Boutons
        self.continue_button = tk.Button(self, text="🚀 Continuer", font=("Helvetica", 14, "bold"), command=self.continue_game, bg="#008CBA", fg="white")
        self.continue_button.pack(pady=(20, 10))

        self.back_button = tk.Button(self, text="⬅ Retour", font=("Helvetica", 12), command=self.go_back, bg="#444444", fg="white")
        self.back_button.pack()

    def redraw_layout(self, event=None):
        for idx, img in enumerate(self.original_car_images):
            if img:
                width = 120
                height = 70
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(resized)
                self.car_labels[idx].config(image=tk_image)
                self.car_labels[idx].image = tk_image

    def select_car(self, index):
        self.selected_car_index = index
        for idx, label in enumerate(self.car_labels):
            if idx == index:
                label.config(highlightthickness=4, highlightbackground="#FFD700")
            else:
                label.config(highlightthickness=0)

    def continue_game(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Attention", "Entre ton surnom.")
            return
        if self.selected_car_index is None:
            messagebox.showwarning("Attention", "Choisis une voiture.")
            return

        data = {
            "type": "register",
            "uuid": self.uuid,
            "player": self.role_var.get(),
            "name": name,
            "car": self.selected_car_index + 1
        }
        self.client.publish("race/registration", json.dumps(data))

        if self.go_continue_callback:
            self.go_continue_callback(
                player=self.role_var.get(),
                uuid=self.uuid,
                car_index=self.selected_car_index + 1
            )

    def go_back(self):
        if self.go_back_callback:
            self.go_back_callback()
