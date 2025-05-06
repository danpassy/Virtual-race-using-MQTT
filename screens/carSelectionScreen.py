import tkinter as tk
from PIL import Image, ImageTk
import paho.mqtt.client as mqtt
import json
import uuid

class CarSelectionScreen(tk.Frame):
    def __init__(self, master, go_back_callback=None, go_continue_callback=None):
        super().__init__(master)
        self.master = master
        self.go_back_callback = go_back_callback
        self.go_continue_callback = go_continue_callback
        self.selected_car_index = None
        self.selected_role = None
        self.car_buttons = []
        self.role_buttons = {}
        self.uuid = str(uuid.uuid4())[:8]
        self.room_id = "course123"

        self.configure(bg="black")

        title = tk.Label(self, text="Choisis ta voiture et ton rôle", font=("Helvetica", 20), fg="white", bg="black")
        title.pack(pady=20)

        self.role_var = tk.StringVar(value="player1")
        role_frame = tk.Frame(self, bg="black")
        role_frame.pack(pady=10)

        for role in ["player1", "player2"]:
            btn = tk.Radiobutton(role_frame, text=role.capitalize(), variable=self.role_var, value=role,
                                 font=("Helvetica", 14), fg="white", bg="black", selectcolor="gray")
            btn.pack(side="left", padx=10)
            self.role_buttons[role] = btn

        car_frame = tk.Frame(self, bg="black")
        car_frame.pack(pady=20)

        for i in range(6):
            try:
                path = f"assets/cars/car{i}.png"
                car_img = Image.open(path).resize((100, 100))
                photo = ImageTk.PhotoImage(car_img)
                btn = tk.Button(car_frame, image=photo, command=lambda idx=i: self.select_car(idx), bg="black", bd=2)
                btn.image = photo
                btn.grid(row=0, column=i, padx=10)
                self.car_buttons.append(btn)
            except Exception as e:
                print("Erreur chargement image voiture:", e)

        btn_frame = tk.Frame(self, bg="black")
        btn_frame.pack(pady=30)

        start_btn = tk.Button(btn_frame, text="Commencer la course", font=("Helvetica", 16), command=self.start_race)
        start_btn.pack(side="left", padx=20)

        if self.go_back_callback:
            back_btn = tk.Button(btn_frame, text="⬅ Retour", font=("Helvetica", 16), command=self.go_back_callback)
            back_btn.pack(side="left", padx=20)

        # MQTT setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("broker.hivemq.com", 1883, 60)
        self.client.loop_start()

        self.client.subscribe(f"race/{self.room_id}/player1/register")
        self.client.subscribe(f"race/{self.room_id}/player2/register")

    def select_car(self, index):
        self.selected_car_index = index
        for i, btn in enumerate(self.car_buttons):
            btn.config(relief="sunken" if i == index else "raised")

    def start_race(self):
        if self.selected_car_index is not None:
            player_role = self.role_var.get()
            topic = f"race/{self.room_id}/{player_role}/register"
            payload = {
                "uuid": self.uuid,
                "car_index": self.selected_car_index,
                "player": player_role
            }
            self.client.publish(topic, json.dumps(payload))
            print(f"[MQTT] ⬆️ PUB {topic}: {payload}")

            if self.go_continue_callback:
                self.go_continue_callback(player_role, self.selected_car_index)
        else:
            print("🚨 Choisis une voiture avant de démarrer !")

    def on_connect(self, client, userdata, flags, rc):
        print("[MQTT] ✅ Connecté avec code:", rc)

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            sender_uuid = data.get("uuid")
            topic = msg.topic

            if sender_uuid != self.uuid:
                if "player1" in topic:
                    self.role_buttons["player1"].config(state="disabled")
                    print(f"[MQTT] 📥 player1 déjà pris par uuid: {sender_uuid}")
                elif "player2" in topic:
                    self.role_buttons["player2"].config(state="disabled")
                    print(f"[MQTT] 📥 player2 déjà pris par uuid: {sender_uuid}")
        except Exception as e:
            print("[MQTT] ❌ Erreur réception message:", e)
