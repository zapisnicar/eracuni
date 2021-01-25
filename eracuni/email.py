import smtplib
import ssl


def send_email(message):
    ssl_port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "sender@gmail.com"
    receiver_email = "receiver@gmail.com"
    email_password = "your_password"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, ssl_port, context=context) as server:
        try:
            server.login(sender_email, email_password)
            res = server.sendmail(sender_email, receiver_email, message)
            print('email sent!')
        except:
            print("could not login or send the mail.")
