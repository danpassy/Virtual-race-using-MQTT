import tkinter as tk
import paho.mqtt.client as mqtt
import json
from PIL import Image, ImageTk

class RaceScreen(tk.Frame):
    def __init__(self, master, player, uuid, car_index):
        super().__init__(master)
        self.master = master
        self.player = player
        self.uuid = uuid
        self.car_index = car_index
        self.other_player = None
        self.other_car_index = None

        self.configure(bg="#000000")  # Fond noir

        screen_width = self.master.winfo_screenwidth()
        target_width = int(screen_width * 0.8)
        self.offset_x = (screen_width - target_width) // 2

        self.bg_image = Image.open("assets/racefield.png").resize((target_width, 400), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(self, width=screen_width, height=400, highlightthickness=0, bg="#000000")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(self.offset_x, 0, anchor="nw", image=self.bg_photo)

        self.load_car_images()

        self.car_x = self.offset_x
        self.car_y = 300
        self.car_label = tk.Label(self.canvas, image=self.local_car_img, bg="gray")
        self.car_label.place(x=self.car_x, y=self.car_y)

        self.remote_x = self.offset_x
        self.remote_y = 100
        self.remote_label = tk.Label(self.canvas, text="⏳", font=("Helvetica", 24), bg="gray", fg="cyan")
        self.remote_label.place(x=self.remote_x, y=self.remote_y)

        self.winner_label = tk.Label(self, text="", font=("Helvetica", 20), bg="#000000", fg="gold")
        self.winner_label.place(x=screen_width // 2 - 100, y=20)

        self.step = 10
        self.victory_x = self.offset_x + target_width - 100

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("broker.hivemq.com", 1883, 60)
        self.client.loop_start()

        self.client.subscribe("race/commands")
        self.client.subscribe("race/registration")

        self.create_controls()

    def load_car_images(self):
        try:
            path = f"assets/cars/car{self.car_index}.png"
            car_img = Image.open(path).resize((70, 70), Image.Resampling.LANCZOS)
            self.local_car_img = ImageTk.PhotoImage(car_img)
        except Exception as e:
            print("Erreur chargement voiture locale :", e)
            self.local_car_img = None

    def load_remote_car(self, index):
        try:
            path = f"assets/cars/car{index}.png"
            car_img = Image.open(path).resize((70, 70), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(car_img)
        except Exception as e:
            print("Erreur chargement voiture distante :", e)
            return None

    def on_connect(self, client, userdata, flags, rc):
        print("Connecté au broker MQTT avec le code de résultat:", rc)

    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload.decode())
        print(f"[MQTT] Message reçu sur {msg.topic} : {data}")

        if msg.topic == "race/registration":
            if data["uuid"] != self.uuid:
                self.other_player = data["player"]
                self.other_car_index = data["car_index"]
                self.remote_car_img = self.load_remote_car(self.other_car_index)
                self.remote_label.configure(image=self.remote_car_img)
                self.remote_label.image = self.remote_car_img

        elif msg.topic == "race/commands":
            if data["uuid"] != self.uuid:
                self.remote_x += self.step
                self.remote_label.place(x=self.remote_x, y=self.remote_y)
                if self.remote_x >= self.victory_x:
                    self.declare_winner(self.other_player)

    def create_controls(self):
        self.master.bind("<Right>", self.move_car)

    def move_car(self, event):
        self.car_x += self.step
        self.car_label.place(x=self.car_x, y=self.car_y)
        self.client.publish("race/commands", json.dumps({"uuid": self.uuid}))

        if self.car_x >= self.victory_x:
            self.declare_winner(self.player)

    def declare_winner(self, winner):
        self.winner_label.config(text=f"🏁 {winner} wins! 🏁")
