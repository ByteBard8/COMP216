import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import messagebox
import json
import threading
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import queue

# GUI Application
class SubscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MQTT Subscriber")
        self.root.geometry("600x400")

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.create_widgets()

        # Queue for thread-safe communication between MQTT callback and Tkinter GUI
        self.queue = queue.Queue()

        # List to store received data for plotting
        self.data_list = []

        # Start MQTT client in a separate thread
        threading.Thread(target=self.start_mqtt, daemon=True).start()

        # Periodically process the queue
        self.process_queue()

    def create_widgets(self):
        # Create a label for connection status
        self.status_label = tk.Label(self.root, text="Connecting to broker...", fg="blue")
        self.status_label.pack(pady=10)

        # Create a listbox to display received data
        self.data_listbox = tk.Listbox(self.root, width=50, height=10)
        self.data_listbox.pack(pady=10)

        # Create a figure for data visualization
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.plot = self.figure.add_subplot(1, 1, 1)

        # Create a canvas to display the figure
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().pack()

    def start_mqtt(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.subscribe(TOPIC)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.status_label.config(text="Connected to broker", fg="green")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            self.queue.put(payload)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)

    def process_queue(self):
        try:
            while not self.queue.empty():
                data = self.queue.get_nowait()
                self.process_data(data)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)  # Schedule the next queue processing

    def process_data(self, data):
        try:
            current_temp = data['temperature']['current']
            self.data_list.append({'packet_id': data['packet_id'], 'value': current_temp})
            self.data_listbox.insert(tk.END, f"ID: {data['packet_id']}, Value: {current_temp}")
            self.update_plot()
        except KeyError as e:
            self.handle_error(f"Data missing key: {str(e)}")

    def update_plot(self):
        self.plot.clear()
        packet_ids = [d['packet_id'] for d in self.data_list]
        values = [d['value'] for d in self.data_list]
        self.plot.plot(packet_ids, values, marker='o', linestyle='-')
        self.plot.set_title("Data Values Over Time")
        self.plot.set_xlabel("Packet ID")
        self.plot.set_ylabel("Temperature Value")
        self.canvas.draw()

    def handle_error(self, message):
        messagebox.showwarning("Data Error", message)

# MQTT broker and port settings
BROKER = 'localhost'
PORT = 1883
TOPIC = 'data/temp'

# Run the GUI application
root = tk.Tk()
app = SubscriberApp(root)
root.mainloop()
