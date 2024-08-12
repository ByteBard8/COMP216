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
        self.root.title("Temperature Monitor Dashboard")
        self.root.geometry("700x600")
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.create_widgets()
        self.min_temp = 16
        self.max_temp = 28
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
        self.status_label = tk.Label(self.root, text="Temperature Monitor Dashboard", fg="indigo", font=('Arial', 20))
        self.status_label.pack(pady=10)
        self.status_label = tk.Label(self.root, text="Connecting to broker...", fg="blue", font=('Arial', 14))
        self.status_label.pack(pady=10)
        self.topic_label = tk.Label(self.root, text="Enter topic here:")
        self.topic_label.pack()
        self.topic_var = tk.StringVar()
        self.topic_entry = tk.Entry(self.root, width=10, textvariable=self.topic_var, font=('Arial', 12))
        self.topic_entry.pack()
        self.go_button = tk.Button(self.root, text="Subscribe", command=self.subscribe, width=10, bg="green",
                                   activebackground="white")
        self.go_button.pack(pady=40)
        self.stop_button = tk.Button(self.root, text="Unsubscribe", command=self.unsubscribe, width=10, bg="yellow", activebackground="white")
        self.stop_button.pack(pady=40)

        # Create a figure for data visualization
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.plot = self.figure.add_subplot(1, 1, 1)

        # Create frame for plotting data and labels
        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        # Create a title label for the plot
        self.title_label = tk.Label(frame, text="Data Values Over Time", font=("Arial", 12, "bold"))
        self.title_label.pack()

        self.y_label = tk.Label(frame, text="°C", font=("Arial", 10))
        self.y_label.pack(side=tk.LEFT)

        self.x_label = tk.Label(frame, text="Pkt ID", font=("Arial", 10))
        self.x_label.pack(side=tk.BOTTOM)

        self.canvas = tk.Canvas(frame, width=500, height=300, bg='#FFEFFF')
        self.canvas.pack()

        # Create a listbox to display received data
        self.data_listbox = tk.Listbox(self.root, width=500, height=10)
        self.data_listbox.pack(padx=20, pady=20, side=tk.BOTTOM )

    def start_mqtt(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.status_label.config(text="Connected to broker", fg="blue")


    def on_disconnect(self,client, userdata, rc):
        self.status_label.config(text="Broker disconnected", fg="red")


    def subscribe(self):
        print(f"subscribing new topic:\t{str(self.topic_var.get())}")
        self.client.subscribe(str(self.topic_var.get()))
        self.status_label.config(text=f"Subscribed to {str(self.topic_var.get())}", fg="green")

    def unsubscribe(self):
        self.client.unsubscribe((str(self.topic_var.get())))
        self.status_label.config(text=f"Unsubscribed from {str(self.topic_var.get())}", fg="green")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            self.queue.put(payload)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            self.data_listbox.insert(0, f"====Error decoding JSON data")

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
        required_keys = ['packet_id', 'temperature']
        if isinstance(data, int):
            self.data_listbox.insert(0, f"====Value {data} received. Possible transmission failure.")
            return
        for key in required_keys:
            if key not in data:
                self.handle_error(f"Data missing key: {key}")
                return
            
        try:
            # Check for required keys in the data
            if 'temperature' not in data or 'current' not in data['temperature'] or 'packet_id' not in data:
                raise KeyError("Missing required data keys")

            current_temp = data['temperature']['current']
            packet_id = data['packet_id']


            if not (self.min_temp <= current_temp <= self.max_temp):
                self.data_listbox.insert(0, f"==============ID: {packet_id}, Value: {current_temp} (out of range)")
                self.handle_error(f"Temperature out of range: {current_temp}")
                return

            # Check if the temperature is within the acceptable range
            if not (self.min_temp <= current_temp <= self.max_temp):
                raise ValueError(f"Temperature {current_temp}°C out of range ({self.min_temp}-{self.max_temp}°C)")

            self.data_list.append({'packet_id': data['packet_id'], 'value': current_temp})
            self.data_listbox.insert(0, f"ID: {data['packet_id']}, Value: {current_temp}. Message={data}")
            if len(self.data_list) > 10:
                self.data_list.pop(0)
            self.update_plot()

        except KeyError as e:
            self.data_listbox.insert(0, f"==============ID: {data.get('packet_id', 'N/A')}, Value: N/A (error)")
            self.handle_error(f"Data missing key: {e}")
        except Exception as e:
            self.data_listbox.insert(0, f"==============ID: {data.get('packet_id', 'N/A')}, Value: N/A (error)")
            self.handle_error(f"Error processing data: {e}")

    def update_plot(self):
        self.canvas.delete("all")

        if not self.data_list:
            return

        max_height = 250
        max_width = 500
        padding = 10

        # Calculate the range of packet IDs and temperature values
        packet_ids = [data['packet_id'] for data in self.data_list]
        values = [data['value'] for data in self.data_list]

        if len(packet_ids) == 1:
            return

        min_packet_id, max_packet_id = min(packet_ids), max(packet_ids)
        min_value, max_value = min(values), max(values)

        # Normalize the data for plotting
        def normalize(value, min_value, max_value, canvas_size):
            if max_value == min_value:
                return canvas_size / 2
            return padding + (value - min_value) / (max_value - min_value) * (canvas_size - 2 * padding)

        # Draw the plot
        for i in range(len(packet_ids) - 1):
            x0 = normalize(packet_ids[i], min_packet_id, max_packet_id, max_width)
            y0 = max_height - normalize(values[i], min_value, max_value, max_height)
            x1 = normalize(packet_ids[i + 1], min_packet_id, max_packet_id, max_width)
            y1 = max_height - normalize(values[i + 1], min_value, max_value, max_height)

            self.canvas.create_line(x0, y0, x1, y1, fill="red")
            self.canvas.create_oval(x0 - 2, y0 - 2, x0 + 2, y0 + 2, fill="blue")
            self.canvas.create_text(x0+10, y0+10, text=values[i], fill="blue")

    def handle_error(self, message):
        messagebox.showwarning("Data Error", message)
        self.email_client.send_email(message)

# MQTT broker and port settings
BROKER = 'localhost'
PORT = 1883

# Run the GUI application
root = tk.Tk()
app = SubscriberApp(root)
root.mainloop()
