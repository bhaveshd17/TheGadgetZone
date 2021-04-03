from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags


def sendMail(request, email):
    # template = render_to_string('authentication/emailT.html', {'username':request.user.username})
    content = {'username': request.user.username}
    template = get_template('authentication/emailT.html').render(content)

    email = EmailMessage(
        'Welcome To The Gadget Zone',
        template,
        settings.EMAIL_HOST_USER,
        [email],
    )

    email.fail_silently = False
    email.content_subtype = 'html'
    email.send()
    # return send_mail(
    #    subject,
    #    message,
    #    settings.EMAIL_HOST_USER,
    #    [email],
    #    fail_silently=False,
    # html_content = render_to_string("emailT.html"),
    # )