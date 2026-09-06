from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def enviar_verificacion_email(user, token):
    url = f"{settings.SITE_URL}/core/verificar-email/{token}/"
    asunto = "Verifica tu cuenta — CafeteriaCerto"
    mensaje_texto = (
        f"Hola {user.first_name},\n\n"
        f"Gracias por registrarte en CafeteriaCerto.\n"
        f"Para activar tu cuenta haz clic en el siguiente enlace:\n\n"
        f"{url}\n\n"
        f"El enlace expira en 48 horas.\n\n"
        f"Si no creaste esta cuenta puedes ignorar este correo.\n\n"
        f"— Equipo CafeteriaCerto"
    )
    mensaje_html = render_to_string('emails/verificacion_email.html', {
        'nombre': user.first_name,
        'url': url,
        'site_url': settings.SITE_URL,
    })

    email = EmailMultiAlternatives(asunto, mensaje_texto, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.attach_alternative(mensaje_html, "text/html")
    email.send(fail_silently=False)


def enviar_contrasena_temporal(user, temp_password):
    login_url = f"{settings.SITE_URL}/core/signInUp/"
    asunto = "Tu contraseña temporal — CafeteriaCerto"
    mensaje_texto = (
        f"Hola {user.first_name},\n\n"
        f"Tu contraseña temporal es: {temp_password}\n\n"
        f"Por seguridad, cámbiala desde tus ajustes de cuenta después de iniciar sesión.\n\n"
        f"— Equipo CafeteriaCerto"
    )
    mensaje_html = render_to_string('emails/contrasena_temporal.html', {
        'nombre': user.first_name,
        'temp_password': temp_password,
        'login_url': login_url,
        'site_url': settings.SITE_URL,
    })

    email = EmailMultiAlternatives(asunto, mensaje_texto, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.attach_alternative(mensaje_html, "text/html")
    email.send(fail_silently=False)
