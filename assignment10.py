import tkinter as tk
import threading
import time

from Project.group_2_data_generator import DataGenerator


class DynamicChartApp:
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.main.title("Dynamic Display")
        self.main.geometry("600x400")
        self.main.configure(bg="#FFFFFF")

        # Header Frame with label, button and decorative lines
        header_frame = tk.Frame(self.main, bg="#FFEFFF")
        header_frame.pack(side=tk.TOP, fill=tk.X)

        self.label_decor_left = tk.Label(header_frame, text="==========================", bg="#ECEDEC")
        self.label_decor_left.grid(row=0, column=0, sticky="e")

        self.go_button = tk.Button(header_frame, text="Go", command=self.start_thread, width=10, bg="white", activebackground="white")  # Wider button with white background
        self.go_button.grid(row=0, column=1, padx=10)

        self.label_decor_right = tk.Label(header_frame, text="==========================", bg="#ECEDEC")
        self.label_decor_right.grid(row=0, column=2, sticky="w")

        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        header_frame.grid_columnconfigure(2, weight=1)

        self.canvas = tk.Canvas(self.main, bg="#FFEFFF", width=580, height=250)
        self.canvas.pack(pady=10, padx=10)
        #data generator class to get our dataset
        self.data_generator = DataGenerator()
        self.current_start = self.data_generator.min_value  # starting index for data range
        self.data_points = [self.data_generator.value for _ in range(20)] #generate values and return data points
        #define a new thread and assign a function
        self.update_thread = threading.Thread(target=self.update_data_points_continuously)
        self.update_thread.daemon = True  # This will ensure the thread will be terminated when the main program exits
        self.thread_running = False
        # Draw the initial temperature label on the canvas
        self.canvas.create_text(0, 0, anchor='nw', text="Temperature", fill="black", font=("Arial", 12, "bold"), tags="label")

    def start_thread(self): #function to start thread
        try:
            if not self.thread_running:
                self.update_thread.start()
                self.thread_running = True
        except Exception as e:
            print(f"Error starting thread: {e}")

    def update_data_points_continuously(self):  #removes first point generates a new data point and appends to list of dataset. Runs with 0.5s interval
        while True:
            try:
                self.data_points.pop(0)
                self.data_points.append(self.data_generator.value)
                self.draw_chart()
                time.sleep(0.5)
            except Exception as e:
                print(f"Error updating data points: {e}")

    def draw_chart(self):   #main function to draw the line graph
        try:
            # Clear canvas if it already exists
            if hasattr(self, 'canvas'):
                self.canvas.destroy()
            self.canvas = tk.Canvas(self.main, width=500, height=200, bg='#FFEFFF') #define fresh canvas
            self.canvas.pack(fill=tk.BOTH, expand=True)
            canvas_width = 580
            canvas_height = 280
            #get attributes from data points needed for data scaling
            x_step = (canvas_width / len(self.data_points))
            y_min = min(self.data_points)
            y_max = max(self.data_points)

            for i in range(len(self.data_points) - 1):
                x0 = i * x_step
                y0 = ((self.data_points[i] - y_min) / (y_max - y_min)) * canvas_height
                x1 = (i + 1) * x_step
                y1 = ((self.data_points[i+1] - y_min) / (y_max - y_min)) * canvas_height
                self.canvas.create_line(x0, y0, x1, y1, fill="red", width=2, tags="line")   #draw line based on calculated point
            # Redraw the temperature label
            self.canvas.delete("label")
            self.canvas.create_text(0, 0, anchor='nw', text="Temperature", fill="black", font=("Arial", 12, "bold"), tags="label")
        except Exception as e:
            print(f"Error drawing chart: {e}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = DynamicChartApp(root)
        root.protocol("WM_DELETE_WINDOW", root.quit)
        root.mainloop()
    except Exception as e:
        print(f"Error running the application: {e}")
