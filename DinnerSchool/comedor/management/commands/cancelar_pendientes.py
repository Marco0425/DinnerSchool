"""
Cancela y reembolsa las Ordenes de HOY que se quedaron en "Pendiente"
(status=0) sin que la cocina las haya avanzado en el kanban.

Pensado para correr vía cron una vez al día (ej. 7:30pm, antes de que
reabra el registro de pedidos a las 8pm) — así el día no se cierra con
pedidos fantasma que nadie va a preparar y el tutor/profesor recupera
su crédito automáticamente.

Uso:
    python manage.py cancelar_pendientes
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from comedor.models import Orden, Credito
from comedor.views import cancelar_orden_completa


class Command(BaseCommand):
    help = 'Cancela y reembolsa las órdenes de hoy que siguen en estado Pendiente'

    def handle(self, *args, **options):
        hoy = timezone.localtime().date()
        ordenes_pendientes = Orden.objects.filter(status=0, fecha=hoy)

        total = ordenes_pendientes.count()
        if total == 0:
            self.stdout.write(f'No hay órdenes pendientes del {hoy} por cancelar.')
            return

        canceladas = 0
        for orden in ordenes_pendientes:
            try:
                with transaction.atomic():
                    total_reembolso, _ = cancelar_orden_completa(orden)
                canceladas += 1
                self.stdout.write(
                    f'Orden #{orden.id} cancelada — reembolso: ${total_reembolso}'
                )
            except Credito.DoesNotExist:
                self.stderr.write(
                    f'Orden #{orden.id}: no se encontró crédito asociado, se omite.'
                )
            except Exception as e:
                self.stderr.write(f'Orden #{orden.id}: error al cancelar — {e}')

        self.stdout.write(self.style.SUCCESS(
            f'Listo: {canceladas}/{total} órdenes pendientes del {hoy} canceladas y reembolsadas.'
        ))
