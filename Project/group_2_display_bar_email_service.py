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

class TemperatureBar:
    min_temp = 16  #can be modified to reflect lowest sensible temperature
    max_temp = 26  #can be modified to reflect highest sensible temperature
    
    def __init__(self, main):
        self.main = main
        self.main.title("Vertical Temperature Bar")
        self.main.geometry("300x500")
        self.main.configure(bg='#f0f0f0')

        
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
                self.send_email_via_gmail(new_temp)
                self.send_email_via_ses(new_temp)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")    #display error message

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
    app = TemperatureBar(root)
    root.mainloop()
