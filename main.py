from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
import aiosmtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from typing import Optional

from fastapi.responses import JSONResponse

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



def _not_used_send_email_via_mailgun(user):
    import requests

    mailgun_domain = os.getenv("MAILGUN_DOMAIN", "sandbox.mailgun.fake.domain")
    mailgun_api_key = os.getenv("MAILGUN_API_KEY", "key-fakeapikey1234567890")
    sender_email = f"noreply@{mailgun_domain}"
    recipient_email = "example@client.com" or user

    subject = "Fake Mailgun Test"
    html_content = "<html><body><h1>This is a fake Mailgun email</h1></body></html>"

    # This code is NEVER executed - just shows the logic
    response = requests.post(
        f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
        auth=("api", mailgun_api_key),
        data={
            "from": sender_email,
            "to": recipient_email,
            "subject": subject,
            "html": html_content
        }
    )
    print("Fake Mailgun response (not actually sent):", response.status_code)



@app.post("/send-internship-confirmation/")
async def confirmation_internship_email(
    recipient: EmailStr = Form(...),
    username: str = Form(None),
    time: str = Form(None)
):
    # Fallback/default values
    applicant_name = username if username else "Dear Applicant"
    start_time = time if time else "Monday, 5th August 2025"
    company_name = "J&S Technologies"
    department = "General"
    interval = "Not Provided"

    # Render the HTML template with provided/default data
    rendered_template = templates.get_template("jss_hiring.html").render({
        "applicant_name": applicant_name,
        "account": {
            "company": company_name,
            "time": start_time,
            "interval": interval,
            "department": department
        }
    })

    # Email message setup
    message = EmailMessage()
    message["From"] = os.getenv("EMAIL_SENDER")
    message["To"] = recipient
    message["Subject"] = f"Internship Confirmation - {company_name}"
    message.set_content("This is an HTML email. Please view it in an HTML-compatible email client.")
    message.add_alternative(rendered_template, subtype="html")

    # Send email using aiosmtplib
    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=os.getenv("EMAIL_SENDER"),
        password=os.getenv("EMAIL_PASSWORD")
    )

    return {"status": "Internship confirmation email sent" , "success":True}


@app.post("/send-weekly-email/")
async def send_weekly_email(
    recipient: EmailStr = Form(...),
    username: str = Form(""),
    time: str = Form(""),
    tasks: Optional[str] = Form("")
):
    # Setup default values
    intern_name = username.strip() if username.strip() else "Intern"
    company_name = "J&S Technologies"
    start_date = "Monday, 4th August 2025"
    end_date = "Friday, 8th August 2025"

    # If custom time provided with comma
    if time and "," in time:
        parts = [p.strip() for p in time.split(",", 1)]
        if len(parts) == 2:
            start_date, end_date = parts

    # Task handling
    default_tasks = [
        "Completed onboarding process",
        "Set up development environment",
        "Reviewed company project guidelines",
        "Pushed first commit to repository",
        "Attended team stand-up meetings"
    ]
    task_list = [t.strip() for t in tasks.split(",")] if tasks and tasks.strip() else default_tasks

    # Render template
    rendered_template = templates.get_template("weekly_update.html").render({
        "intern_name": intern_name,
        "start_date": start_date,
        "end_date": end_date,
        "tasks": task_list
    })

    # Compose and send email
    message = EmailMessage()
    message["From"] = os.getenv("EMAIL_SENDER")
    message["To"] = recipient
    message["Subject"] = f"Weekly Internship Summary - {company_name}"
    message.set_content("This is an HTML email. Please view in a compatible email client.")
    message.add_alternative(rendered_template, subtype="html")

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=os.getenv("EMAIL_SENDER"),
        password=os.getenv("EMAIL_PASSWORD")
    )

    return JSONResponse(content={"status": "Weekly summary email sent" , "success":True})
