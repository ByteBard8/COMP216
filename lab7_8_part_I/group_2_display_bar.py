"""
Adilet
Diego
Jaekyeong
Sandeep
"""
import tkinter as tk
from tkinter import messagebox

class TemperatureBar:
    def __init__(self, main):
        self.main = main
        self.main.title("Vertical Temperature Bar")
        self.main.geometry("300x500")
        self.main.configure(bg='#f0f0f0')

        self.min_temp = 16  #can be modified to reflect lowest sensible temperature
        self.max_temp = 26  #can be modified to reflect highest sensible temperature
        self.current_temp = 18 #starting value

        self.x_max = 60
        self.y_max = 340
        self.create_widgets()

    def create_widgets(self):
        # define canvas for bar
        self.canvas = tk.Canvas(self.main, width=100, height=360, bg='#f0f0f0', highlightthickness=0)
        self.canvas.pack(pady=20)

        # current temperature and textbox for entry
        self.temp_var = tk.StringVar(value=str(self.current_temp))
        self.temp_entry = tk.Entry(self.main, textvariable=self.temp_var, width=10, font=('Arial', 12))
        self.temp_entry.pack(pady=10)

        # update button
        update_button = tk.Button(self.main, text="Update", command=self.update_bar)
        update_button.pack(pady=10)

        #call function to draw line bar
        self.draw_bar()

    def draw_bar(self):
        #refresh canvas
        self.canvas.delete("all")
        
        # create background bar using rectangle
        self.canvas.create_rectangle(40, 20, self.x_max, self.y_max, fill="#ddd", outline="")
        
        # get a height using mapping function based on current temperature
        bar_height = self.map_value_to_height(self.current_temp)

        # Draw temperature on top of background bar with gradient fill
        for i in range(int(bar_height)):
            y = self.y_max - i
            color = self.get_gradient_color(i / bar_height)
            self.canvas.create_line(40, y, self.x_max, y, fill=color)
        
        # display current temperature
        self.canvas.create_text(50, 350, text=f"{self.current_temp}°C", font=("Arial", 12, "bold"))
        

        # Draw tick marks on the bar
        for temp in range(self.min_temp, self.max_temp + 1):
            y = self.y_max - self.map_value_to_height(temp)
            self.canvas.create_line(self.x_max, y, self.x_max + 5, y, fill="black")
            if temp % 2 == 0:  # Label every even temperature
                self.canvas.create_text(75, y, text=str(temp), font=("Arial", 8), anchor="w")

    def map_value_to_height(self, value):   #map from value to bar height
        return 320 * (value - self.min_temp) / (self.max_temp - self.min_temp)

    def get_gradient_color(self, ratio):
        r = int(255 * ratio)
        b = int(255 * (1 - ratio))
        return f'#{r:02x}00{b:02x}'

    def update_bar(self):
        try:
            new_temp = float(self.temp_var.get())
            if self.min_temp <= new_temp <= self.max_temp:  #if within range
                self.current_temp = new_temp
                self.draw_bar() #update figure
            else:
                messagebox.showerror("Error", f"Temperature must be between {self.min_temp} and {self.max_temp}")   #display error message
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")    #display error message

if __name__ == "__main__":
    root = tk.Tk()
    app = TemperatureBar(root)
    root.mainloop()