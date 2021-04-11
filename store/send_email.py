from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags


def sendMail(request, email, mailFor, msg, subject):
    content = {'mailFor':mailFor}

    if msg == 'AddPAndWelcome':
         template = get_template('authentication/emailT.html').render(content)
    else:
         template = get_template('authentication/emailT1.html').render(content)
    
    if not subject:
        subject = 'Welcome to The Gadgets Zone'

    email = EmailMessage(
        subject,
        template,
        settings.EMAIL_HOST_USER,
        email,
    )

    email.fail_silently = False
    email.content_subtype = 'html'
    email.send()


def otpMail(request, email, username, user_otp):
    email = EmailMessage(
        'Please Verify Your Email ID',
        f"Hello {username},\n Your OTP is {user_otp} \n Please Verify",
        settings.EMAIL_HOST_USER,
        [email],
    )

    email.fail_silently = False
    email.content_subtype = 'html'
    email.send()
