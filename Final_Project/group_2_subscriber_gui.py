import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import messagebox
import json
import threading
import queue

# GUI Application
class SubscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MQTT Subscriber")
        self.root.geometry("700x600")
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
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
        self.topic_label = tk.Label(self.root, text="Enter topic here:")
        self.topic_label.pack()
        self.topic_var = tk.StringVar()
        self.topic_entry = tk.Entry(self.root, width=10, textvariable=self.topic_var, font=('Arial', 12))
        self.topic_entry.pack()
        self.go_button = tk.Button(self.root, text="Subscribe", command=self.subscribe, width=10, bg="green",
                                   activebackground="white")
        self.go_button.pack(pady=10)
        self.stop_button = tk.Button(self.root, text="Unsubscribe", command=self.unsubscribe, width=10, bg="yellow", activebackground="white")
        self.stop_button.pack(pady=10)
        # Create a listbox to display received data
        self.data_listbox = tk.Listbox(self.root, width=50, height=10)
        self.data_listbox.pack(pady=10)

        #self.data_listbox.bind("<configure>", self.update_listbox)

        # Create frame for plotting data and labels
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        
        # Create a title label for the plot
        self.title_label = tk.Label(frame, text="Data Values Over Time", font=("Arial", 12, "bold"))
        self.title_label.pack()

        self.y_label = tk.Label(frame, text="Temperature", font=("Arial", 10))
        self.y_label.pack(side=tk.LEFT)

        self.x_label = tk.Label(frame, text="Packet ID", font=("Arial", 10))
        self.x_label.pack(side=tk.BOTTOM)
        # width = self.root.winfo_width()
        # height = self.root.winfo_height()
        # print(width, height)
        self.canvas = tk.Canvas(frame, width=500, height=300, bg='#FFEFFF')
        self.canvas.pack()    

    def start_mqtt(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.status_label.config(text="Connected to broker", fg="green")


    def on_disconnect(self,client, userdata, rc):
        self.status_label.config(text="Broker disconnected", fg="red")


    def subscribe(self):
        print(f"subscribing new topic:\t{str(self.topic_var.get())}")
        self.client.subscribe(str(self.topic_var.get()))

    def unsubscribe(self):
        self.client.unsubscribe((str(self.topic_var.get())))
        self.status_label.config(text=f"Unsubscribed from {str(self.topic_var.get())}", fg="green")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            self.queue.put(payload)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            self.data_listbox.insert(tk.END, f"====Error decoding JSON data")

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
            self.data_listbox.insert(tk.END, f"====Value {data} received. Possible transmission failure.")
            return
        for key in required_keys:
            if key not in data:
                self.handle_error(f"Data missing key: {key}")
                return
            
        try:
            current_temp = data['temperature']['current']
            packet_id = data['packet_id']

            min_temp = 16
            max_temp = 28

            if not (min_temp <= current_temp <= max_temp):
                self.data_listbox.insert(tk.END, f"==============ID: {packet_id}, Value: {current_temp} (out of range)")
                self.handle_error(f"Temperature out of range: {current_temp}")
                return


            self.data_list.append({'packet_id': data['packet_id'], 'value': current_temp})
            self.data_listbox.insert(tk.END, f"ID: {data['packet_id']}, Value: {current_temp}")
            if len(self.data_list) > 10:
                self.data_list.pop(0)
            self.update_plot()

        except KeyError as e:
            self.data_listbox.insert(tk.END, f"==============ID: {data.get('packet_id', 'N/A')}, Value: N/A (error)")
            self.handle_error(f"Data missing key: {e}")
        except Exception as e:
            self.data_listbox.insert(tk.END, f"==============ID: {data.get('packet_id', 'N/A')}, Value: N/A (error)")
            self.handle_error(f"Error processing data: {e}")

    def update_plot(self):
        self.canvas.delete("all")

        if not self.data_list:
            return

        max_height = 200
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
            self.canvas.create_text(x0+5, y0+5, text=values[i], fill="blue")

    def handle_error(self, message):
        messagebox.showwarning("Data Error", message)

# MQTT broker and port settings
BROKER = 'localhost'
PORT = 1883

# Run the GUI application
root = tk.Tk()
app = SubscriberApp(root)
root.mainloop()
