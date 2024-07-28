import tkinter as tk
from group_2_data_generator import DataGenerator
from group_2_display_bar_email_service import TemperatureBar

class DisplayChar:
    def __init__(self, main):
        # initialize main window properties
        self.main = main
        self.main.title("Temperature Data")
        self.main.geometry("500x350")
        self.main.configure(bg='#f0f0f0')

        # Temperature range from TemperatureBar class
        self.min_temp = TemperatureBar.min_temp
        self.max_temp = TemperatureBar.max_temp
        
        # Generate initial temperature data from instance of DataGenerator class
        self.data_generator = DataGenerator()
        self.all_data = [self.data_generator.value for _ in range(20)]
        self.current_start = 0 # starting index for data range

        self.create_widgets() # Create UI elements
        self.draw_rectangles_and_lines() # Draw rectangles and lines graph
        
    def create_widgets(self):
        # Create and pack UI elements
        top_frame = tk.Frame(self.main, bg='#f0f0f0')
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        self.label = tk.Label(top_frame, text="Temperature range: ", bg='#f0f0f0')
        self.label.pack(side=tk.LEFT, padx=5)
        
        # Component to enter the starting index of the data range
        self.entry = tk.Entry(top_frame)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        # Button to update the displayed data range
        self.button = tk.Button(top_frame, text="Go", command=self.on_button_click, width=10)
        self.button.pack(side=tk.LEFT, padx=5)

        # Label to display the current data range
        self.range_label = tk.Label(self.main, text="Data range: 0 - 5", bg='#f0f0f0')
        self.range_label.pack(side=tk.TOP, fill=tk.X, padx=10)

        # Label to display error messages
        self.error_label = tk.Label(self.main, text="", fg="red", bg='#f0f0f0')
        self.error_label.pack(side=tk.TOP, fill=tk.X, padx=10)
        
    def draw_rectangles_and_lines(self):
        # Clear canvas if it already exists
        if hasattr(self, 'canvas'):
            self.canvas.destroy()

        # Create canvas for drawing rectangles and lines
        self.canvas = tk.Canvas(self.main, width=500, height=200, bg='#ffffff')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        bar_width = 60 # Width of each bar
        spacing = 10 # Spacing between bars
        max_height = 200 # Maximum height of the bars

        # Get the current data range
        current_data = self.all_data[self.current_start:self.current_start + 6]

        for i, value in enumerate(current_data):
            temp_value = max(self.min_temp, min(self.max_temp, value))
            height = ((temp_value - self.min_temp) / (self.max_temp - self.min_temp)) * max_height
            x1 = 50 + i * (bar_width + spacing)
            y1 = 180 - height
            x2 = x1 + bar_width
            y2 = 180

            # Draw the rectangle for the bar
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="green")

            # Draw the line connecting the bars
            if i > 0:
                prev_x = 50 + (i - 1) * (bar_width + spacing) + bar_width / 2
                prev_value = max(self.min_temp, min(self.max_temp, current_data[i - 1]))
                prev_y = 180 - ((prev_value - self.min_temp) / (self.max_temp - self.min_temp)) * max_height
                curr_x = x1 + bar_width / 2
                curr_y = y1

                self.canvas.create_line(prev_x, prev_y, curr_x, curr_y, fill="red", width=2)
        
    def on_button_click(self):
        # Handle button click event
        value = self.entry.get()
        try:
            # Convert the input to an integer and ensure it is within the valid range
            start_value = max(0, min(14, int(value)))
            self.error_label.config(text="")
        except ValueError:
            # If the input is not a valid integer, set the start value to 0
            start_value = 0
            self.error_label.config(text="Invalid input. Please enter a number between 0 and 14.")
        
        self.current_start = start_value
        range_text = f"Data range: {start_value} - {start_value + 5}"
        self.range_label.config(text=range_text)

        self.draw_rectangles_and_lines() # Redraw the rectangles and lines

if __name__ == "__main__":
    root = tk.Tk()
    app = DisplayChar(root)
    root.protocol("WM_DELETE_WINDOW", root.quit) # Handle window close event
    root.mainloop()