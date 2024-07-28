"""
Adilet
Diego
Jaekyeong
Sandeep
"""

import tkinter as tk
from tkinter import messagebox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

class TemperatureGauge:
    def __init__(self, main):
        self.main = main
        self.main.title("Temperature Gauge")
        self.main.geometry("400x500")
        self.main.configure(bg='#f0f0f0')

        self.min_temp = 16  #can be modified to reflect lowest sensible temperature
        self.max_temp = 26  #can be modified to reflect highest sensible temperature
        self.current_temp = 18 #starting value

        self.gauge_starting_angle = 135
        self.gauge_ending_angle = 270
        self.create_widgets()

    def create_widgets(self):
        # define canvas for gauge
        self.canvas = tk.Canvas(self.main, width=300, height=300, bg='#f0f0f0', highlightthickness=0)
        self.canvas.pack(pady=20)

        # current temperature and textbox for entry
        self.temp_var = tk.StringVar(value=str(self.current_temp))
        self.temp_entry = tk.Entry(self.main, textvariable=self.temp_var, width=10, font=('Arial', 12))
        self.temp_entry.pack(pady=10)

        # update button
        update_button = tk.Button(self.main, text="Update", command=self.update_gauge)
        update_button.pack(pady=10)

        # for gauge
        self.draw_gauge()

    def draw_gauge(self):
        #refresh gauge
        self.canvas.delete("all")

        #create gauge bar using arc
        self.canvas.create_arc(10, 10, 290, 290, start=self.gauge_starting_angle, extent=self.gauge_ending_angle, outline="#ddd", width=20, style="arc")
        
        # use current temperature value to obtain an angle using mapping function
        angle = self.map_value_to_angle(self.current_temp)
        #create second arc on top of bar created above
        self.canvas.create_arc(10, 10, 290, 290, start=self.gauge_starting_angle, extent=angle-self.gauge_starting_angle, outline="#4CAF50", width=20, style="arc")
        
        # display current temperature value
        self.canvas.create_text(150, 150, text=f"{self.current_temp}°C", font=("Arial", 24, "bold"))
        
        # display minimum and maximum temperatures
        self.canvas.create_text(20, 40, text=f"{self.min_temp}°C", font=("Arial", 12))
        self.canvas.create_text(280, 40, text=f"{self.max_temp}°C", font=("Arial", 12))

    def map_value_to_angle(self, value):    #mapping function that returns an angular value for given temperature value
        return self.gauge_starting_angle + (self.gauge_ending_angle * (value - self.min_temp) / (self.max_temp - self.min_temp))
    
    def update_gauge(self):
        try:
            new_temp = float(self.temp_var.get())
            if self.min_temp <= new_temp <= self.max_temp:  #if within range
                self.current_temp = new_temp
                self.draw_gauge()   #update figure
            else:
                messagebox.showerror("Error", f"Temperature must be between {self.min_temp} and {self.max_temp}")   #display error message
                self.send_email_via_gmail(new_temp)
                self.send_email_via_ses(new_temp)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid temperature value") #display error message

    def send_email_via_gmail(self, value):
        sender_email = "networkinggroupnumber2@gmail.com"
        receiver_email = "amasalbekov12@gmail.com"
        password = "iglm mkcl xvxc urvb"

        message = MIMEMultipart("alternative")
        message["Subject"] = "Alert: Temperature Out of Range"
        message["From"] = sender_email
        message["To"] = receiver_email

        text = f"The temperature entered is {value}°C, which is outside the normal range of {self.min_temp}°C to {self.max_temp}°C."
        html = f"""\
        <html>
          <body>
            <h1>Alert: Temperature Out of Range</h1>
            <p>The temperature entered is {value}°C, which is outside the normal range of {self.min_temp}°C to {self.max_temp}°C.</p>
          </body>
        </html>
        """

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.close()
            print("Gmail email sent!")
        except Exception as e:
            print(f"Failed to send email via Gmail: {e}")

    def send_email_via_ses(self, value):
        ses = boto3.client('ses', region_name='us-east-1')
        source_email = "amasalbekov12@gmail.com"
        recipient_email = "amasalbekov12@gmail.com"
        subject = "Alert: Temperature Out of Range"
        body = f"The temperature entered is {value}°C, which is outside the normal range of {self.min_temp}°C to {self.max_temp}°C."

        BODY_TEXT = body
        BODY_HTML = f"""<html>
        <head></head>
        <body>
          <h1>{subject}</h1>
          <p>{body}</p>
        </body>
        </html>
        """            

        CHARSET = "UTF-8"

        try:
            response = ses.send_email(
                Destination={
                    'ToAddresses': [
                        recipient_email,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': subject,
                    },
                },
                Source=source_email,
            )
            print("Email sent! Message ID:", response['MessageId'])
        except NoCredentialsError:
            print("Credentials not available")
        except PartialCredentialsError:
            print("Incomplete credentials")

if __name__ == "__main__":
    root = tk.Tk()
    app = TemperatureGauge(root)
    root.mainloop()
