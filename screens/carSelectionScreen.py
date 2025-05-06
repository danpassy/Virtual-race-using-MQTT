import tkinter as tk
from PIL import Image, ImageTk

class CarSelectionScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.selected_car_index = None
        self.selected_role = None
        self.car_buttons = []

        self.configure(bg="black")

        title = tk.Label(self, text="Choisis ta voiture et ton rôle", font=("Helvetica", 20), fg="white", bg="black")
        title.pack(pady=20)

        self.role_var = tk.StringVar(value="player1")
        role_frame = tk.Frame(self, bg="black")
        role_frame.pack(pady=10)
        tk.Radiobutton(role_frame, text="Player 1", variable=self.role_var, value="player1", font=("Helvetica", 14), fg="white", bg="black", selectcolor="gray").pack(side="left", padx=10)
        tk.Radiobutton(role_frame, text="Player 2", variable=self.role_var, value="player2", font=("Helvetica", 14), fg="white", bg="black", selectcolor="gray").pack(side="left", padx=10)

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

        start_btn = tk.Button(self, text="Commencer la course", font=("Helvetica", 16), command=self.start_race)
        start_btn.pack(pady=30)

    def select_car(self, index):
        self.selected_car_index = index
        for i, btn in enumerate(self.car_buttons):
            btn.config(relief="sunken" if i == index else "raised")

    def start_race(self):
        if self.selected_car_index is not None:
            player_role = self.role_var.get()
            self.master.show_frame("race", player=player_role, car_index=self.selected_car_index)
        else:
            print("🚨 Choisis une voiture avant de démarrer !")
