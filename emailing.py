import smtplib
import mimetypes
import glob
import os
from email.message import EmailMessage
from dotenv import load_dotenv

# Đọc thông tin bí mật từ file .env (file này đã được .gitignore bỏ qua)
load_dotenv()
PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SENDER = os.getenv("GMAIL_SENDER")
RECEIVER = os.getenv("GMAIL_RECEIVER")

# Hàm này CHỈ XÓA các ảnh nằm trong danh sách được chỉ định
def clean_folder(images_to_delete):
    for image in images_to_delete:
        if os.path.exists(image):
            os.remove(image)

def send_email(image_path, images_to_delete):
    print("send_email function started")
    email_message = EmailMessage()
    email_message["Subject"] = "New customer showed up!"
    email_message.set_content("Hey, we just saw a new customer!")

    with open(image_path, "rb") as file:
        content = file.read()
    mime_type, _ = mimetypes.guess_type(image_path)
    subtype = mime_type.split("/")[1] if mime_type else "png"
    email_message.add_attachment(content, maintype="image", subtype=subtype)

    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(SENDER, PASSWORD)
    gmail.sendmail(SENDER, RECEIVER, email_message.as_string())
    gmail.quit()
    print("send_email function ended")
    clean_folder(images_to_delete)

if __name__ == "__main__":
    send_email(image_path="images/55.png", images_to_delete=["images/55.png"])