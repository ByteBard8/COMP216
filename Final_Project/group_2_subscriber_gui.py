import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import messagebox
import json
import threading
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import queue
from group_2_email_client import EmailClient

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

        # Initialize email client
        self.email_client = EmailClient(
            gmail_sender_email="networkinggroupnumber2@gmail.com",
            gmail_password="iglm mkcl xvxc urvb"
        )

        # Define acceptable temperature range
        self.min_temp = 16
        self.max_temp = 26

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
            error_message = f"Error decoding JSON: {e}"
            print(error_message)
            self.email_client.send_email(message=error_message)

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
            # Check for required keys in the data
            if 'temperature' not in data or 'current' not in data['temperature'] or 'packet_id' not in data:
                raise KeyError("Missing required data keys")

            current_temp = data['temperature']['current']

            # Check if the temperature is within the acceptable range
            if not (self.min_temp <= current_temp <= self.max_temp):
                raise ValueError(f"Temperature {current_temp}°C out of range ({self.min_temp}-{self.max_temp}°C)")

            self.data_list.append({'packet_id': data['packet_id'], 'value': current_temp})
            self.data_listbox.insert(tk.END, f"ID: {data['packet_id']}, Value: {current_temp}")
            self.update_plot()
        except KeyError as e:
            error_message = f"Data missing key: {str(e)}"
            self.handle_error(error_message)
            self.email_client.send_email(message=error_message)
        except ValueError as e:
            error_message = str(e)
            self.handle_error(error_message)
            self.email_client.send_email(message=error_message)

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
