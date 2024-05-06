from auto_reminder.models import Student
from aiosmtplib import SMTP
from email.message import EmailMessage
from string import Template


class Emailer:
    """
    Emails students about their missing assignments. It is a simple wrapper
    around an aiosmtplib.SMTP object that provides templating and async sending
    """
    config: dict
    smtp: SMTP

    def __init__(self, config):
        self.config = config
        self.smtp = SMTP()

    async def __aenter__(self):
        await self.smtp.connect(
            hostname=self.config["email_host"],
            port=int(self.config["email_port"]),
            username=self.config["email_address"],
            password=self.config["email_password"],
            use_tls=True,
        )

        return self


    async def __aexit__(self, *_):
        await self.smtp.quit()


    def compose(self, template: Template, student: Student) -> EmailMessage:
        """
        Creates an email message from the given template and student information

        :param template: The email message template to use
        :param student: The student to send the email to
        :return: The formatted email message
        """
        msg = EmailMessage()
        msg["Subject"] = self.config["subject"]
        msg["To"] = student.email if not bool(self.config["test"]) else self.config["email_address"]
        msg["From"] = self.config["email_address"]
        missing = "\n".join(map("    - {}".format, student.missing))
        msg.set_content(template.substitute(name=student.name, missing=missing))
        return msg


    async def send(self, template: Template, student: Student):
        """
        Composes and sends an email to a student about their missing assignments

        :param template: The email message template to use
        :param student: The student to send the email to
        """
        msg = self.compose(template, student)
        await self.smtp.send_message(msg)
