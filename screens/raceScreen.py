
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

        self.configure(bg="#000000")

        self.load_car_images()

        self.car_label = tk.Label(self, image=self.local_car_img, bg="#000000")
        self.car_label.place(x=250, y=300)

        self.remote_label = tk.Label(self, text="⏳", font=("Helvetica", 24), bg="#000000", fg="cyan")
        self.remote_label.place(x=250, y=100)

        self.winner_label = tk.Label(self, text="", font=("Helvetica", 20), bg="#000000", fg="gold")
        self.winner_label.pack(pady=10)

        self.car_x = 250
        self.car_y = 300
        self.remote_x = 250
        self.remote_y = 100
        self.step = 10
        self.victory_x = 500

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

    def create_controls(self):
        controls_frame = tk.Frame(self, bg="#000000")
        controls_frame.pack(pady=20)

        up_btn = tk.Button(controls_frame, text="▲", font=("Helvetica", 16), command=lambda: self.move("up"))
        left_btn = tk.Button(controls_frame, text="◀", font=("Helvetica", 16), command=lambda: self.move("left"))
        right_btn = tk.Button(controls_frame, text="▶", font=("Helvetica", 16), command=lambda: self.move("right"))
        down_btn = tk.Button(controls_frame, text="▼", font=("Helvetica", 16), command=lambda: self.move("down"))

        up_btn.grid(row=0, column=1, padx=10, pady=5)
        left_btn.grid(row=1, column=0, padx=10, pady=5)
        down_btn.grid(row=1, column=1, padx=10, pady=5)
        right_btn.grid(row=1, column=2, padx=10, pady=5)

    def move(self, direction):
        if direction == "up":
            self.car_y -= self.step
        elif direction == "down":
            self.car_y += self.step
        elif direction == "left":
            self.car_x -= self.step
        elif direction == "right":
            self.car_x += self.step

        self.update_position()

        if self.car_x >= self.victory_x:
            self.winner_label.config(text=f"{self.player} a gagné !")
            self.send_json("race/commands", {"event": "win", "player": self.player})
        else:
            self.send_json("race/commands", {
                "action": direction,
                "player": self.player,
                "uuid": self.uuid
            })

    def update_position(self):
        self.car_label.place(x=self.car_x, y=self.car_y)
        self.remote_label.place(x=self.remote_x, y=self.remote_y)

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT connecté avec le code :", rc)

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            print(f"📩 Message [{msg.topic}] :", json.dumps(payload, indent=2))

            if payload.get("type") == "register":
                if payload.get("uuid") != self.uuid and not self.other_player:
                    self.other_player = payload.get("player")
                    self.other_car_index = payload.get("car")
                    remote_car_img = self.load_remote_car(self.other_car_index)
                    if remote_car_img:
                        self.remote_label.config(image=remote_car_img, text="")
                        self.remote_label.image = remote_car_img
                    print("👤 Adversaire détecté :", self.other_player)

            elif payload.get("uuid") == self.uuid:
                return

            if "action" in payload:
                direction = payload["action"]
                if direction == "up":
                    self.remote_y -= self.step
                elif direction == "down":
                    self.remote_y += self.step
                elif direction == "left":
                    self.remote_x -= self.step
                elif direction == "right":
                    self.remote_x += self.step
                self.update_position()

            elif "event" in payload and payload["event"] == "win":
                self.winner_label.config(text=f"{payload['player']} a gagné !")

        except Exception as e:
            print("❌ Erreur traitement message :", e)

    def send_json(self, topic, data):
        try:
            self.client.publish(topic, json.dumps(data))
        except Exception as e:
            print("❌ Erreur envoi JSON :", e)
