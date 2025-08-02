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

    return {"status": "Internship confirmation email sent"}


@app.post("/send-weekly-email/")
async def send_weekly_email(
    recipient: EmailStr = Form(...),
    username: str = Form(""),
    time: str = Form(""),
    tasks: Optional[str] = Form("")
):
    # Default values
    intern_name = username.strip() if username.strip() else "Intern"
    start_date = "Monday, 4th August 2025"
    end_date = "Friday, 8th August 2025"
    company_name = "J&S Technologies"

    # Override if custom time string provided (basic assumption: "Start to End")
    if time and "to" in time:
        time_parts = [part.strip() for part in time.split("to")]
        if len(time_parts) == 2:
            start_date, end_date = time_parts

    # Tasks
    default_tasks = [
        "Completed onboarding process",
        "Set up development environment",
        "Reviewed company project guidelines",
        "Pushed first commit to repository",
        "Attended team stand-up meetings"
    ]
    task_list = [t.strip() for t in tasks.split(",")] if tasks.strip() else default_tasks

    # Render email
    rendered_template = templates.get_template("weekly_update.html").render({
        "intern_name": intern_name,
        "start_date": start_date,
        "end_date": end_date,
        "tasks": task_list
    })

    # Send email
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

    return JSONResponse(content={"status": "Weekly summary email sent"})