from django.core.mail import send_mail
from django.conf import settings


def enviar_verificacion_email(user, token):
    url = f"{settings.SITE_URL}/core/verificar-email/{token}/"
    asunto = "Verifica tu cuenta — CafeteriaCerto"
    mensaje = (
        f"Hola {user.first_name},\n\n"
        f"Gracias por registrarte en CafeteriaCerto.\n"
        f"Para activar tu cuenta haz clic en el siguiente enlace:\n\n"
        f"{url}\n\n"
        f"El enlace expira en 48 horas.\n\n"
        f"Si no creaste esta cuenta puedes ignorar este correo.\n\n"
        f"— Equipo CafeteriaCerto"
    )
    send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)


def enviar_contrasena_temporal(user, temp_password):
    asunto = "Tu contraseña temporal — CafeteriaCerto"
    mensaje = (
        f"Hola {user.first_name},\n\n"
        f"Tu contraseña temporal es: {temp_password}\n\n"
        f"Por seguridad, cámbiala desde tus ajustes de cuenta después de iniciar sesión.\n\n"
        f"— Equipo CafeteriaCerto"
    )
    send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
