from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Crea los grupos de usuarios requeridos por la aplicación'

    def handle(self, *args, **options):
        grupos = [(1, 'Tutor'), (2, 'Alumno'), (3, 'Empleado'), (4, 'Profesor')]
        for pk, name in grupos:
            g, created = Group.objects.get_or_create(id=pk, defaults={'name': name})
            if not created and g.name != name:
                g.name = name
                g.save()
            self.stdout.write(f'  {pk}: {name} ({"creado" if created else "ya existe"})')
        self.stdout.write(self.style.SUCCESS('Grupos listos.'))
