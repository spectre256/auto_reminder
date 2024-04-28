import ssl
from smtplib import SMTP
from email.message import EmailMessage
from string import Template
from models import Student

class Emailer:
    config: dict
    smtp: SMTP

    def __init__(self, config):
        self.config = config
        self.smtp = SMTP(config["email_host"], int(config["email_port"]))
        context = ssl.create_default_context()
        self.smtp.starttls(context=context)

    def __del__(self):
        self.smtp.quit()

    def compose(self, template: Template, student: Student) -> EmailMessage:
        msg = EmailMessage()
        msg["Subject"] = config["subject"]
        msg["To"] = student.email if not config["test"] else self.config["email_address"]
        msg["From"] = self.config["email_address"]
        missing = "\n".join(map("    - {}".format, student.missing))
        msg.set_content(template.substitute(mapping=vars(student), missing=missing))
        return msg

    def send(self, template: Template, student: Student):
        msg = self.compose(template, student)
        self.smtp.send_message(msg)
