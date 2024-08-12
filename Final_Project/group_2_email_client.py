import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

class EmailClient:
    def __init__(self, gmail_sender_email, gmail_password, ses_region='us-east-1'):
        self.gmail_sender_email = gmail_sender_email
        self.gmail_password = gmail_password
        self.ses = boto3.client('ses', region_name=ses_region)

    def send_email_via_gmail(self, receiver_email, subject, text, html):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.gmail_sender_email
        message["To"] = receiver_email

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(self.gmail_sender_email, self.gmail_password)
            server.sendmail(self.gmail_sender_email, receiver_email, message.as_string())
            server.close()
            print("Gmail email sent!")
        except Exception as e:
            print(f"Failed to send email via Gmail: {e}")

    def send_email_via_ses(self, source_email, recipient_email, subject, body):
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
            response = self.ses.send_email(
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

    def send_email(self, message):
        subject = "Alert: Notification"
        text = f"An important notification: {message}"
        html = f"""\
        <html>
          <body>
            <h1>Alert: Notification</h1>
            <p>{message}</p>
          </body>
        </html>
        """

        # Example usage of sending via Gmail
        self.send_email_via_gmail(
            receiver_email="amasalbekov12@gmail.com",
            subject=subject,
            text=text,
            html=html
        )

        # Example usage of sending via SES
        # self.send_email_via_ses(
        #     source_email="amasalbekov12@gmail.com",
        #     recipient_email="amasalbekov12@gmail.com",
        #     subject=subject,
        #     body=text
        # )
