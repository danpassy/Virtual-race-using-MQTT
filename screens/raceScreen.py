import tkinter as tk
from PIL import Image, ImageTk
import paho.mqtt.client as mqtt

class RaceScreen(tk.Frame):
    def __init__(self, master, player_name, car_index):
        super().__init__(master)
        self.master = master
        self.player_name = player_name
        self.car_index = car_index  # 0 à 5

        self.configure(bg="#000000")
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.topic = "race/demo"
        self.positions = [0, 0]  # car1, car2

        self.load_images()
        self.create_widgets()
        self.client.connect("broker.hivemq.com", 1883, 60)
        self.client.loop_start()

    def load_images(self):
        try:
            car1_img = Image.open(f"cars/car{self.car_index+1}.png")
            car2_img = Image.open("cars/car6.png")  # Voiture adverse (temp)
            self.car1_photo = ImageTk.PhotoImage(car1_img.resize((100, 50)))
            self.car2_photo = ImageTk.PhotoImage(car2_img.resize((100, 50)))
        except Exception as e:
            print("Erreur chargement images :", e)

    def create_widgets(self):
        self.canvas = tk.Canvas(self, bg="#111111", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.car1 = self.canvas.create_image(0, 100, anchor="nw", image=self.car1_photo)
        self.car2 = self.canvas.create_image(0, 200, anchor="nw", image=self.car2_photo)

        self.advance_btn = tk.Button(self, text="Appuyer pour Avancer", font=("Helvetica", 16), command=self.advance)
        self.advance_btn.pack(pady=20)

    def advance(self):
        # Publier un message sur le topic MQTT
        self.client.publish(self.topic, f"{self.player_name}:advance")

    def on_connect(self, client, userdata, flags, rc):
        print("✅ Connecté au broker MQTT")
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        print("📩 Message reçu :", payload)

        if "advance" in payload:
            sender = payload.split(":")[0]
            if sender == self.player_name:
                self.positions[0] += 20  # voiture du joueur local
                self.canvas.coords(self.car1, self.positions[0], 100)
            else:
                self.positions[1] += 20  # autre voiture
                self.canvas.coords(self.car2, self.positions[1], 200)
