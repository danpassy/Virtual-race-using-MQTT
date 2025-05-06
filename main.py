
import tkinter as tk
from screens.mainScreen import MainScreen
from screens.playModeScreen import PlayModeScreen
from screens.carSelectionScreen import CarSelectionScreen
from screens.raceScreen import RaceScreen

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Race Button")
        self.geometry("600x700")
        self.configure(bg="#000000")
        self.resizable(True, True)

        self.frames = {
            "main": MainScreen(self),
            "playmode": PlayModeScreen(self)
        }

        self.current_frame = None
        self.show_frame("main")

    def show_frame(self, name):
        if self.current_frame:
            self.current_frame.pack_forget()
        frame = self.frames[name]
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

    def show_car_selection(self):
        frame = CarSelectionScreen(self,
            go_back_callback=lambda: self.show_frame("playmode"),
            go_continue_callback=self.show_race_screen
        )
        self.frames["carselect"] = frame
        self.show_frame("carselect")

    def show_race_screen(self, player, uuid, car_index):
        if "race" in self.frames:
            try:
                self.frames["race"].client.loop_stop()  # 🛑 Arrête proprement MQTT
                self.frames["race"].client.disconnect()
                self.frames["race"].destroy()
                del self.frames["race"]
            except Exception as e:
                print("Erreur lors du nettoyage de l'ancienne RaceScreen:", e)

        frame = RaceScreen(self, player, uuid, car_index)
        self.frames["race"] = frame
        self.show_frame("race")




if __name__ == "__main__":
    app = App()
    app.frames["playmode"].start_button.config(command=app.show_car_selection)
    app.mainloop()
