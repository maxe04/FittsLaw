import tkinter as tk
from tkinter import ttk
import pandas as pd
import random as rnd
import time
import math

class FittsLaw(ttk.Frame):
    def __init__(self, root):

        super().__init__()
        self.root = root
        self.grid(column = 0, row = 0)
        self.root.title("Fitts' Law")

        self.canvas = tk.Canvas(self, bg="pink", height=900, width=1500)
        self.canvas.grid(column = 0, row = 0)

        #Tags erstellen für die beiden Kreise um die jeweiligen Klicks zu registrieren
        self.canvas.tag_bind("o", "<Button-1>", self.click)
        self.canvas.tag_bind("g", "<Button-1>", self.click)

        #Ein Set erstellen um zu schauen ob schon beide Kreise jeweils einmal geklickt wurden
        self.clicked_circles = set()

        #Breiten, Distanzen, Durchläufe festlegen
        self.widths = [30, 60, 90]
        self.distances = [300, 600, 900]
        self.width_index = 0
        self.distance_index = 0
        self.rep_count = 0
        self.max_reps = 3

        #Liste wo nach jedem Durchlauf die Daten gespeichert werden
        self.results = []

        #Start timer definieren
        self.start_time = None

        #Das Programm kickstarten
        self.spawn_circles()

    #Die beiden Kreise zeichnen
    def draw_circles(self):

        #Breite und Distanz variabel bestimmen je nach Durchlauf
        width = self.widths[self.width_index]
        distance = self.distances[self.distance_index]

        #Nützliche größen
        radius = int(width/2)
         #Margin: Kreise sollten nicht außerhalb des Bildschrims spawnen
        margin = 100 + width
        canvas_width = 1500
        canvas_height = 900

        #Random X und Y Punkt für den orangenen Kreis bestimmen
        x = rnd.randint(margin, canvas_width - margin)
        y = rnd.randint(margin, canvas_height - margin)

        #Anhand des bestimmten Punktes die Koordinaten des zu zeichnenden orangenen Kreises bestimmen
        x0 = x - radius
        y0 = y - radius
        x1 = x + radius
        y1 = y + radius

        #Random Winkel im unit circle um den orangenen Kreis bestimmen
        angle = rnd.uniform(0, 2 * math.pi)
        dx = math.cos(angle) * distance
        dy = math.sin(angle) * distance

        #Kreis 1 erstellen (Orange)
        c1 = self.canvas.create_oval(
            x0, y0,
            x1, y1,
            fill="orange", tags=("o",)
        )

        #Kreis 2 erstellen (Grün)
        c2 = self.canvas.create_oval(
            x0 + dx, y0 + dy,
            x1 + dx, y1 + dy,
            fill="green", tags=("g",)
        )

        #Falls der grüne Kreis offscreen spawned, dann nochmal neu spawnen, solange bis beide Kreise onscreen sind
        if not self.is_circle_in_bounds(self.canvas.coords(c2),canvas_width,canvas_height, margin):
            self.canvas.delete("all")
            self.draw_circles()


    #Was passiert wenn man auf die Kreise klickt
    def click(self, event):
        #Gucken welcher Kreis geklickt wurde
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)

        #Geklickten Kreis dem Set hinzufügen
        self.clicked_circles.add(tags[0])

        #Nachdem der erste Kreis geklickt wurde, timer starten
        if len(self.clicked_circles) == 1:
            self.start_time = time.time()

        #Was passiert wenn beide Kreise geklickt wurden
        if "o" in self.clicked_circles and "g" in self.clicked_circles:

            #Daten des Durchlaufs sichern, nützlich für zu erstellende CSV Datei
            width = self.widths[self.width_index]
            distance = self.distances[self.distance_index]
            index_of_difficulty = round(math.log2(1 +(distance / width)), 2)
            time_elapsed = round(time.time() - self.start_time, 2)
            self.results.append([width, distance, index_of_difficulty, time_elapsed])

            #Durchlauf-index erhöhen und alle Kreise löschen
            self.rep_count += 1
            self.canvas.delete("all")
            self.clicked_circles.clear()

            #Programmlogik
            if self.rep_count >= self.max_reps:
                self.rep_count = 0
                self.distance_index +=1

                if self.distance_index >= len(self.distances):
                    self.distance_index = 0
                    self.width_index +=1

                    if self.width_index >= len(self.widths):
                        self.save_results()

    #Kreise iterativ spawnen, falls canvas leer ist und Experiment nicht schon fertig gelaufen ist
    def spawn_circles(self):
        if not self.canvas.find_all() and self.width_index < len(self.widths):
            self.draw_circles()
        self.root.after(100, self.spawn_circles)

    #Daten des Experiments in CSV speichern
    def save_results(self):
        df = pd.DataFrame(self.results, columns=["Width", "Distance", "Index Of Difficulty", "Time"])
        df.to_csv("fitts_law_results.csv", index = False)

    #Funktion um zu schauen ob der grüne Kreis offscreen spawned, bzw ob er innerhalb der der vorgegebenen margin spawned
    def is_circle_in_bounds(self, coords, canvas_width, canvas_height, margin):
        x0, y0, x1, y1 = coords
        if x1 > 0 + margin and x1 < canvas_width - margin and y1 > 0 + margin and y1 < canvas_height - margin:
            return True
        else:
            return False

#Main
if __name__ == "__main__":
    app_root = tk.Tk()
    app = FittsLaw(app_root)
    app_root.mainloop()

