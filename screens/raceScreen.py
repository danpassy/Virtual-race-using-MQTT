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
        self.other_player = "player2" if self.player == "player1" else "player1"
        self.other_car_index = None
        self.remote_ready = False
        self.local_ready = False
        self.game_over = False
        self.room_id = "course123"

        self.configure(bg="#000000")

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
        self.car_y = 80 if self.player == "player1" else 300
        self.car_label = tk.Label(self.canvas, image=self.local_car_img, bg="gray")
        self.car_label.place(x=self.car_x, y=self.car_y)

        self.remote_x = self.offset_x
        self.remote_y = 270 if self.player == "player1" else 125
        self.remote_label = tk.Label(self.canvas, text="⏳", font=("Helvetica", 24), bg="gray", fg="cyan")
        self.remote_label.place(x=self.remote_x, y=self.remote_y)

        self.waiting_label = tk.Label(self, text="🕒 En attente de l'autre joueur...", font=("Helvetica", 20), bg="black", fg="white")
        self.waiting_label.place(relx=0.5, rely=0.5, anchor="center")
        self.waiting_label.lift()

        self.winner_label = tk.Label(self, text="", font=("Helvetica", 20), bg="#000000", fg="gold")
        self.winner_label.place(x=screen_width // 2 - 100, y=20)

        self.step = 10
        self.victory_x = self.offset_x + target_width - 100

        self.countdown_label = tk.Label(self, text="", font=("Helvetica", 40), fg="white", bg="black")
        self.countdown_label.place(relx=0.5, rely=0.4, anchor="center")
        self.countdown_label.lower()

        self.timer_label = tk.Label(self, text="⏱ 0.00s", font=("Helvetica", 18), fg="white", bg="black")
        self.timer_label.place(relx=0.85, rely=0.05, anchor="center")
        self.timer_label.lift()

        self.start_time = None
        self.timer_running = False
        self.end_frame = None

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("broker.hivemq.com", 1883, 60)
        self.client.loop_start()

        self.client.subscribe(f"race/{self.room_id}/{self.other_player}/move")
        self.client.subscribe(f"race/{self.room_id}/{self.other_player}/win")
        self.client.subscribe(f"race/{self.room_id}/{self.other_player}/register")
        self.client.subscribe(f"race/{self.room_id}/broadcast")

        self.create_controls()
        self.publish_register()

    def load_car_images(self):
        try:
            path = f"assets/cars/car{self.car_index}.png"
            car_img = Image.open(path).resize((70, 70), Image.Resampling.LANCZOS)
            self.local_car_img = ImageTk.PhotoImage(car_img)
        except Exception as e:
            print("Erreur chargement voiture locale :", e)
            self.local_car_img = None

    def create_controls(self):
        self.master.bind("<Right>", self.move_car)

    def check_start_conditions(self):
        if self.remote_ready and self.local_ready:
            self.waiting_label.destroy()
            self.start_countdown()

    def start_countdown(self, count=3):
        if not self.remote_ready or not self.local_ready:
            print("[⛔] Tentative de démarrer le compte à rebours avant que les deux joueurs ne soient prêts.")
            return

        if count > 0:
            self.countdown_label.config(text=str(count))
            print(f"[MQTT] 🕒 Compte à rebours: {count}")
            self.after(1000, self.start_countdown, count - 1)
        else:
            self.countdown_label.config(text="GO!")
            print("[MQTT] 🚀 Départ de la course !")
            self.send_json(f"race/{self.room_id}/broadcast", {
                "type": "start",
                "message": "La course commence !"
            })
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

    def move_car(self, event):
        if self.game_over or not self.timer_running:
            return

        self.car_x += self.step
        self.update_position()
        move_topic = f"race/{self.room_id}/{self.player}/move"
        self.send_json(move_topic, {"uuid": self.uuid, "direction": "right"})

        if self.car_x >= self.victory_x:
            self.declare_winner(self.player)

    def update_position(self):
        self.car_label.place(x=self.car_x, y=self.car_y)
        self.remote_label.place(x=self.remote_x, y=self.remote_y)

    def publish_register(self):
        topic = f"race/{self.room_id}/{self.player}/register"
        payload = {"uuid": self.uuid, "player": self.player, "car_index": self.car_index}
        self.send_json(topic, payload)
        self.local_ready = True
        self.check_start_conditions()

    def on_connect(self, client, userdata, flags, rc):
        print("[MQTT] ✅ Connecté avec code:", rc)

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            print(f"[MQTT] 📩 RECV {msg.topic}: {json.dumps(data)}")

            if msg.topic.endswith("/register"):
                if data["player"] == self.other_player:
                    self.remote_ready = True
                    self.other_car_index = data.get("car_index")
                    remote_img = self.load_car_images_by_index(self.other_car_index)
                    if remote_img:
                        self.remote_label.config(image=remote_img, text="")
                        self.remote_label.image = remote_img
                    self.check_start_conditions()

            elif msg.topic.endswith("/move"):
                self.remote_x += self.step
                self.update_position()

            elif msg.topic.endswith("/win"):
                self.declare_winner(data.get("player", "Autre joueur"))

            elif msg.topic.endswith("/broadcast"):
                print(f"[MQTT] 📣 Message broadcast : {data.get('message')}")

        except Exception as e:
            print("❌ Erreur réception MQTT:", e)

    def load_car_images_by_index(self, index):
        try:
            path = f"assets/cars/car{index}.png"
            car_img = Image.open(path).resize((70, 70), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(car_img)
        except Exception as e:
            print("Erreur chargement voiture distante :", e)
            return None

    def declare_winner(self, winner):
        self.winner_label.config(text=f"🏁 {winner} wins! 🏁")
        self.game_over = True
        self.timer_running = False

        topic = f"race/{self.room_id}/{self.player}/win"
        payload = {"uuid": self.uuid, "player": self.player, "time": f"{time.time() - self.start_time:.2f}"}
        self.send_json(topic, payload)

        self.send_json(f"race/{self.room_id}/broadcast", {
            "type": "info",
            "message": f"{winner} a terminé la course."
        })

        self.show_end_buttons()
        self.save_race_history()

    def show_end_buttons(self):
        if self.end_frame:
            self.end_frame.destroy()

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

        if self.end_frame:
            self.end_frame.destroy()
            self.end_frame = None

        self.car_x = self.offset_x
        self.car_y = 80 if self.player == "player1" else 300
        self.remote_x = self.offset_x
        self.remote_y = 270 if self.player == "player1" else 125

        self.car_label.place(x=self.car_x, y=self.car_y)
        self.remote_label.place(x=self.remote_x, y=self.remote_y)

        self.timer_label.config(text="⏱ 0.00s")
        self.countdown_label = tk.Label(self, text="", font=("Helvetica", 40), fg="white", bg="black")
        self.countdown_label.place(relx=0.5, rely=0.4, anchor="center")
        self.countdown_label.lift()

        self.waiting_label = tk.Label(self, text="🕒 En attente de l'autre joueur...", font=("Helvetica", 20), bg="black", fg="white")
        self.waiting_label.place(relx=0.5, rely=0.5, anchor="center")
        self.waiting_label.lift()

        self.remote_ready = False
        self.local_ready = False

        self.publish_register()

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
            "carte": "Désert",
            "classement": classement
        })

        with open(historique_file, "w", encoding="utf-8") as f:
            json.dump(historique, f, ensure_ascii=False, indent=2)

    def send_json(self, topic, data):
        try:
            self.client.publish(topic, json.dumps(data))
            print(f"[MQTT] ⬆️ PUB {topic}: {data}")
        except Exception as e:
            print("❌ Erreur envoi JSON :", e)
