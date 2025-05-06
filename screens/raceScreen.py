import tkinter as tk
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import time
import os
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
        self.game_over = False
        self.max_distance = 500

        self.configure(bg="#000000")

        self.load_car_images()

        self.car_label = tk.Label(self, image=self.local_car_img, bg="#000000")
        self.car_label.place(x=50, y=300)

        self.remote_label = tk.Label(self, text="⏳", font=("Helvetica", 24), bg="#000000", fg="cyan")
        self.remote_label.place(x=50, y=100)

        self.winner_label = tk.Label(self, text="", font=("Helvetica", 20), bg="#000000", fg="gold")
        self.winner_label.pack(pady=10)

        self.car_x = 50
        self.car_y = 300
        self.remote_x = 50
        self.remote_y = 100
        self.step = 10

        # Timer
        # Timer
        self.countdown_label = tk.Label(self, text="", font=("Helvetica", 40), fg="white", bg="black")
        self.countdown_label.place(relx=0.5, rely=0.4, anchor="center")
        self.countdown_label.lift()  # ← force au premier plan

        self.timer_label = tk.Label(self, text="⏱ 0.00s", font=("Helvetica", 18), fg="white", bg="black")
        self.timer_label.place(relx=0.85, rely=0.05, anchor="center")
        self.timer_label.lift()  # ← force au premier plan


        self.start_time = None
        self.timer_running = False

        # MQTT
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("broker.hivemq.com", 1883, 60)
        self.client.loop_start()

        self.client.subscribe("race/commands")
        self.client.subscribe("race/registration")

        self.create_controls()
        self.end_frame = None

        # Démarre le compte à rebours
        self.start_countdown()

    def load_car_images(self):
        try:
            path = f"assets/cars/car{self.car_index}.png"
            car_img = Image.open(path).resize((70, 70), Image.Resampling.LANCZOS)
            self.local_car_img = ImageTk.PhotoImage(car_img)
        except Exception as e:
            print("Erreur chargement voiture locale :", e)
            self.local_car_img = None

    def create_controls(self):
        controls_frame = tk.Frame(self, bg="#000000")
        controls_frame.place(x=10, rely=1.0, anchor="sw")

        up_btn = tk.Button(controls_frame, text="▲", font=("Helvetica", 16), command=lambda: self.move("up"))
        left_btn = tk.Button(controls_frame, text="◀", font=("Helvetica", 16), command=lambda: self.move("left"))
        right_btn = tk.Button(controls_frame, text="▶", font=("Helvetica", 16), command=lambda: self.move("right"))
        down_btn = tk.Button(controls_frame, text="▼", font=("Helvetica", 16), command=lambda: self.move("down"))

        up_btn.grid(row=0, column=1, padx=10, pady=5)
        left_btn.grid(row=1, column=0, padx=10, pady=5)
        down_btn.grid(row=1, column=1, padx=10, pady=5)
        right_btn.grid(row=1, column=2, padx=10, pady=5)

    def start_countdown(self, count=3):
        if count > 0:
            self.countdown_label.config(text=str(count))
            self.after(1000, self.start_countdown, count - 1)
        else:
            self.countdown_label.config(text="GO!")
            self.after(1000, self.countdown_label.destroy)
            self.start_timer()

    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running and not self.game_over:
            elapsed = time.time() - self.start_time
            self.timer_label.config(text=f"⏱ {elapsed:.2f}s")
            self.after(100, self.update_timer)

    def move(self, direction):
        if self.game_over or not self.timer_running:
            return

        if direction == "up":
            self.car_y -= self.step
        elif direction == "down":
            self.car_y += self.step
        elif direction == "left":
            self.car_x -= self.step
        elif direction == "right":
            self.car_x += self.step

        self.update_position()

        if self.car_x >= self.max_distance:
            self.game_over = True
            self.timer_running = False
            self.winner_label.config(text=f"🏁 {self.player} a gagné !")
            self.send_json("race/commands", {"event": "win", "player": self.player})
            self.show_end_buttons()
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

            elif payload.get("uuid") == self.uuid or self.game_over:
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
                self.game_over = True
                self.timer_running = False
                self.winner_label.config(text=f"🏁 {payload['player']} a gagné !")
                self.show_end_buttons()

        except Exception as e:
            print("❌ Erreur traitement message :", e)

    def send_json(self, topic, data):
        try:
            self.client.publish(topic, json.dumps(data))
        except Exception as e:
            print("❌ Erreur envoi JSON :", e)

    def show_end_buttons(self):
        if not self.game_over:
            return
        
        self.save_race_history()

        if self.end_frame:
            self.end_frame.lift()
        else:
            self.end_frame = tk.Frame(self, bg="#000000")
            self.end_frame.place(relx=0.5, rely=0.7, anchor="center")
        
            replay_btn = tk.Button(self.end_frame, text="🔁 Rejouer", command=self.rejouer)
            menu_btn = tk.Button(self.end_frame, text="🏠 Menu", command=lambda: self.master.show_frame("main"))
            quit_btn = tk.Button(self.end_frame, text="❌ Quitter", command=self.master.destroy)

            replay_btn.pack(pady=5)
            menu_btn.pack(pady=5)
            quit_btn.pack(pady=5)

    def rejouer(self):
        self.game_over = False
        self.timer_running = False
        self.winner_label.config(text="")

        # ✅ Détruire les boutons de fin s'ils existent
        if self.end_frame:
            self.end_frame.destroy()
            self.end_frame = None

        self.car_x = 50
        self.car_y = 300
        self.remote_x = 50
        self.remote_y = 100

        self.car_label.place(x=self.car_x, y=self.car_y)
        self.remote_label.place(x=self.remote_x, y=self.remote_y)

        self.timer_label.config(text="⏱ 0.00s")
        self.countdown_label = tk.Label(self, text="", font=("Helvetica", 40), fg="white", bg="black")
        self.countdown_label.place(relx=0.5, rely=0.4, anchor="center")
        self.countdown_label.lift()

        self.start_countdown()


    def save_race_history(self):
        historique_file = "historique.json"
        if os.path.exists(historique_file):
            try:
                with open(historique_file, "r", encoding="utf-8") as f:
                    historique = json.load(f)
                if not isinstance(historique, list):
                    historique = []
            except:
                historique = []
        else:
            historique = []

        classement = []
        if self.player:
            temps = time.time() - self.start_time if self.start_time else 0
        classement.append((self.player, f"{temps:.2f}s"))
        if self.other_player:
            classement.append((self.other_player, "Perdu"))

        historique.append({
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "carte": "Désert",  # tu peux changer selon ta logique
            "classement": classement
        })

        with open(historique_file, "w", encoding="utf-8") as f:
            json.dump(historique, f, ensure_ascii=False, indent=2)

    def load_remote_car(self, car_index):
        try:
            path = f"assets/cars/car{car_index}.png"
            car_img = Image.open(path).resize((70, 70), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(car_img)
        except Exception as e:
            print("Erreur chargement voiture distante :", e)
            return None
