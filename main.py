import tkinter as tk
from screens.mainScreen import MainScreen
from screens.playModeScreen import PlayModeScreen
from screens.carSelectionScreen import CarSelectionScreen
from screens.raceScreen import RaceScreen
import uuid

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Virtual Race")
        self.geometry("1200x700")
        self.frames = {}
        self.current_frame = None

        self.show_frame("main")

    def show_frame(self, name, **kwargs):
        if self.current_frame:
            self.current_frame.destroy()

        if name == "main":
            frame = MainScreen(self)

        elif name == "playmode":
            frame = PlayModeScreen(self, show_car_selection=self.show_car_selection)

        elif name == "car":
            frame = CarSelectionScreen(
                self,
                go_back_callback=lambda: self.show_frame("playmode"),
                go_continue_callback=self.show_race_screen
            )

        elif name == "race":
            player = kwargs.get("player")
            car_index = kwargs.get("car_index")
            user_uuid = str(uuid.uuid4())[:8]
            frame = RaceScreen(self, player, user_uuid, car_index)

        else:
            frame = tk.Frame(self)  # fallback empty frame

        self.current_frame = frame
        self.current_frame.pack(fill="both", expand=True)

    def show_car_selection(self):
        self.show_frame("car")

    def show_race_screen(self, player, car_index):
        self.show_frame("race", player=player, car_index=car_index)

if __name__ == "__main__":
    app = App()
    app.mainloop()