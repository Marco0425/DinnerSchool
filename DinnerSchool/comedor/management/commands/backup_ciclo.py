"""
Respaldo del ciclo escolar actual.

Uso:
    python manage.py backup_ciclo                    # solo genera el JSON
    python manage.py backup_ciclo --confirmar-reset  # respaldo + limpia tablas operacionales
    python manage.py backup_ciclo --reset-creditos   # también pone créditos en cero

El archivo de respaldo se guarda en backups/ciclo_<fecha>.json
"""
import os
import json
from datetime import date
from django.core import serializers
from django.core.management.base import BaseCommand
from django.db import transaction

from comedor.models import Pedido, Orden, CreditoDiario, Credito


class Command(BaseCommand):
    help = 'Genera respaldo del ciclo escolar y opcionalmente reinicia las tablas operacionales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar-reset',
            action='store_true',
            help='Después del respaldo, elimina Pedidos, Ordenes y CreditoDiario del ciclo actual',
        )
        parser.add_argument(
            '--reset-creditos',
            action='store_true',
            help='Pone todos los créditos (Credito.monto) en cero (usar con --confirmar-reset)',
        )

    def handle(self, *args, **options):
        hoy = date.today()
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        archivo = os.path.join(backup_dir, f'ciclo_{hoy.strftime("%Y%m%d_%H%M%S")}.json')

        # ── 1. Generar respaldo ──────────────────────────────────────────────
        self.stdout.write('Generando respaldo...')
        datos = {
            'fecha_respaldo': hoy.isoformat(),
            'pedidos': json.loads(serializers.serialize('json', Pedido.objects.all())),
            'ordenes': json.loads(serializers.serialize('json', Orden.objects.all())),
            'credito_diario': json.loads(serializers.serialize('json', CreditoDiario.objects.all())),
            'creditos': json.loads(serializers.serialize('json', Credito.objects.all())),
        }

        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2, default=str)

        totales = {
            'Pedidos': Pedido.objects.count(),
            'Ordenes': Orden.objects.count(),
            'CreditoDiario': CreditoDiario.objects.count(),
            'Creditos': Credito.objects.count(),
        }
        self.stdout.write(self.style.SUCCESS(f'Respaldo guardado en: {archivo}'))
        for modelo, n in totales.items():
            self.stdout.write(f'  {modelo}: {n} registros')

        if not options['confirmar_reset']:
            self.stdout.write(self.style.WARNING(
                '\nPara limpiar las tablas operacionales ejecuta con --confirmar-reset'
            ))
            return

        # ── 2. Limpiar tablas operacionales ────────────────────────────────
        self.stdout.write('\nLimpiando tablas operacionales...')
        with transaction.atomic():
            n_cd = CreditoDiario.objects.count()
            CreditoDiario.objects.all().delete()
            self.stdout.write(f'  CreditoDiario eliminados: {n_cd}')

            n_p = Pedido.objects.count()
            Pedido.objects.all().delete()
            self.stdout.write(f'  Pedidos eliminados: {n_p}')

            n_o = Orden.objects.count()
            Orden.objects.all().delete()
            self.stdout.write(f'  Órdenes eliminadas: {n_o}')

            if options['reset_creditos']:
                n_c = Credito.objects.update(monto=0)
                self.stdout.write(f'  Créditos puestos en cero: {n_c}')
            else:
                self.stdout.write(self.style.WARNING(
                    '  Créditos conservados. Agrega --reset-creditos para ponerlos en cero.'
                ))

        self.stdout.write(self.style.SUCCESS(
            '\n✓ Ciclo escolar listo para iniciar. El respaldo está en:\n' + archivo
        ))
