import tkinter as tk
import random
import threading
import time

class DynamicChartApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dynamic Display")
        self.geometry("600x400")
        self.configure(bg="#FFFFFF")

        # Header Frame with label, button and decorative lines
        header_frame = tk.Frame(self, bg="#FFEFFF")
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

        self.canvas = tk.Canvas(self, bg="#FFEFFF", width=580, height=250)
        self.canvas.pack(pady=10, padx=10)

        self.data_points = [random.randint(0, 100) for _ in range(25)]
        self.update_thread = threading.Thread(target=self.update_data_points_continuously)
        self.update_thread.daemon = True  # This will ensure the thread will be terminated when the main program exits
        self.thread_running = False

        # Draw the initial temperature label on the canvas
        self.canvas.create_text(10, 10, anchor='nw', text="Temperature", fill="black", font=("Arial", 12, "bold"), tags="label")

    def start_thread(self):
        try:
            if not self.thread_running:
                self.update_thread.start()
                self.thread_running = True
        except Exception as e:
            print(f"Error starting thread: {e}")

    def update_data_points_continuously(self):
        while True:
            try:
                self.data_points.pop(0)
                self.data_points.append(random.randint(0, 100))
                self.draw_chart()
                time.sleep(0.5)
            except Exception as e:
                print(f"Error updating data points: {e}")

    def draw_chart(self):
        try:
            self.canvas.delete("line")

            canvas_width = 580
            canvas_height = 250
            x_step = canvas_width / len(self.data_points)
            y_scale = (canvas_height - 20) / max(self.data_points)  # Scale down to leave some margin at the top

            for i in range(len(self.data_points) - 1):
                x0 = i * x_step
                y0 = canvas_height - (self.data_points[i] * y_scale)
                x1 = (i + 1) * x_step
                y1 = canvas_height - (self.data_points[i + 1] * y_scale)

                self.canvas.create_line(x0, y0, x1, y1, fill="red", width=2, tags="line")

            # Redraw the temperature label
            self.canvas.delete("label")
            self.canvas.create_text(10, 10, anchor='nw', text="Temperature", fill="black", font=("Arial", 12, "bold"), tags="label")
        except Exception as e:
            print(f"Error drawing chart: {e}")

if __name__ == "__main__":
    try:
        app = DynamicChartApp()
        app.mainloop()
    except Exception as e:
        print(f"Error running the application: {e}")
