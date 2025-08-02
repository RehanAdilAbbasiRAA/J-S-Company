from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
import aiosmtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class EmailDetails(BaseModel):
    recipient: EmailStr
    username: str
    company: str
    time: str
    interval: str
    department: str


@app.post("/send-email/")
async def send_email(details: EmailDetails):
    rendered_template = templates.get_template("J&S_hiring_template.html").render({
        "Customer": {"username": details.username},
        "account": {
            "company": details.company,
            "time": details.time,
            "interval": details.interval,
            "department": details.department
        }
    })

    message = EmailMessage()
    message["From"] = os.getenv("EMAIL_SENDER")
    message["To"] = details.recipient
    message["Subject"] = f"Internship Confirmation - {details.company}"
    message.set_content("This is an HTML email. Please view in an HTML-compatible client.")
    message.add_alternative(rendered_template, subtype="html")

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=os.getenv("EMAIL_SENDER"),
        password=os.getenv("EMAIL_PASSWORD")
    )

    return {"status": "Email sent successfully"}
