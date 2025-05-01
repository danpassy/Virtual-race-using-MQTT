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

        # Charger tous les écrans au démarrage
        self.frames = {
            "main": MainScreen(self),
            "playmode": PlayModeScreen(self),
            "carselect": CarSelectionScreen(self)
        }

        self.current_frame = None
        self.show_frame("main")

    def show_frame(self, name):
        if self.current_frame:
            self.current_frame.pack_forget()

        frame = self.frames[name]
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

if __name__ == "__main__":
    app = App()
    app.mainloop()
