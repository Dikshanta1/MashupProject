from flask import Flask, render_template, request
from mashup_logic import create_mashup
import re
import zipfile
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    singer = request.form["singer"]
    num_videos = int(request.form["videos"])
    duration = int(request.form["duration"])
    email = request.form["email"]

    if num_videos <= 10 or duration <= 20:
        return "Videos must be >10 and Duration must be >20 seconds."

    if not is_valid_email(email):
        return "Invalid Email Format."

    try:
        # Create mashup
        output_file = create_mashup(singer, num_videos, duration)

        # Zip file
        zip_name = "mashup.zip"
        with zipfile.ZipFile(zip_name, "w") as zipf:
            zipf.write(output_file)

        # Send email
        send_email(email, zip_name)

        return "Mashup created and sent to your email successfully!"

    except Exception as e:
        return f"Error occurred: {e}"

def send_email(receiver, attachment):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    msg = EmailMessage()
    msg["Subject"] = "Your Mashup File"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content("Please find attached your mashup file.")

    with open(attachment, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="zip",
            filename=attachment
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

if __name__ == "__main__":
    app.run(debug=True)
