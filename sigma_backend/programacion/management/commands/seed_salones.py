"""
Comando de management para poblar 81 salones de prueba (A101-C309).

Uso:
    python manage.py seed_salones

Es idempotente: usa bulk_create con ignore_conflicts=True. No depende
de que 'nombre' sea único a nivel de base de datos (Salon no tiene esa
restricción), así que antes de insertar se filtran los nombres que ya
existan en el campus, para no duplicar si se corre más de una vez.

Distribución: 3 edificios (A, B, C) x 3 pisos (1, 2, 3) x 9 salones
por piso (01-09) = 81 salones en total.
Capacidad: varía según el piso, simulando aulas más grandes en pisos
intermedios y laboratorios/salas pequeñas en el piso 1.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from institucional.models import Campus
from programacion.models import Salon


class Command(BaseCommand):
    help = 'Crea 81 salones de prueba (A101 a C309).'

    @transaction.atomic
    def handle(self, *args, **options):
        campus, _ = Campus.objects.get_or_create(
            nombre='Piedra de Bolívar',
            defaults={'direccion': 'Cartagena de Indias'},
        )

        edificios = ['A', 'B', 'C']
        pisos = [1, 2, 3]
        salones_por_piso = range(1, 10)  # 01 a 09

        nombres_a_crear = []
        for edificio in edificios:
            for piso in pisos:
                for numero in salones_por_piso:
                    nombre = f'{edificio}{piso}{numero:02d}'
                    nombres_a_crear.append(nombre)

        # Evita duplicar si el comando ya se corrió antes.
        existentes = set(
            Salon.objects.filter(campus=campus, nombre__in=nombres_a_crear)
            .values_list('nombre', flat=True)
        )

        nuevos_salones = []
        for nombre in nombres_a_crear:
            if nombre in existentes:
                continue
            piso = int(nombre[1])
            # Piso 1: salas pequeñas/laboratorios (20-25); piso 2: aulas
            # estándar (30-35); piso 3: auditorios/aulas grandes (40-50).
            if piso == 1:
                capacidad = 22
            elif piso == 2:
                capacidad = 32
            else:
                capacidad = 45
            nuevos_salones.append(Salon(nombre=nombre, capacidad=capacidad, campus=campus))

        Salon.objects.bulk_create(nuevos_salones, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('\n=== Salones de prueba creados exitosamente ==='))
        self.stdout.write(f'Salones nuevos creados: {len(nuevos_salones)}')
        self.stdout.write(f'Total de salones en el campus "{campus.nombre}": {Salon.objects.filter(campus=campus).count()}')