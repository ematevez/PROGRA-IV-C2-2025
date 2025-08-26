from django.template import context
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


def send_account_activation_email(name, email, subject, description):
    # context = {"name": name, "email": email, "description": description}
    content = f"Hello {name},\n{description}.\nThank you."
    email_subject = subject
    email_body = render_to_string(
        "email_message.html",
        {
            "content": "{}".format(content),
            "image_url": None
        },
    )

    email = EmailMessage(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [
            email,
        ],
    )
    return email.send(fail_silently=False)
