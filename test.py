
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "esraaakg2@gmail.com"
receiver_email = "receiver_email@example.com"
password = "uvsf zamp filf nykh"  # 16 karakterlik uygulama şifresi

message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "Deneme Maili"

body = "Bu bir test mailidir."
message.attach(MIMEText(body, "plain"))

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Mail başarıyla gönderildi!")
except Exception as e:
    print("Mail gönderilirken hata oluştu:", e)

