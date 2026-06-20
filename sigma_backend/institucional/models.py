"""
Modelos del bloque Institucional.
Representa la estructura física y organizativa de la Universidad de Cartagena:
Campus, Facultad, NivelFormacion, ProgramaAcademico.

Es la base de la que dependen los demás bloques (usuarios, academico,
programacion, matricula), por eso se declara primero.
"""
from django.db import models


class Campus(models.Model):
    nombre = models.CharField(max_length=45, unique=True)
    direccion = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Campus'
        verbose_name_plural = 'Campus'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Facultad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    campus = models.ForeignKey(
        Campus,
        on_delete=models.PROTECT,
        related_name='facultades',
    )

    class Meta:
        verbose_name = 'Facultad'
        verbose_name_plural = 'Facultades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class NivelFormacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Nivel de Formación'
        verbose_name_plural = 'Niveles de Formación'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ProgramaAcademico(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    facultad = models.ForeignKey(
        Facultad,
        on_delete=models.PROTECT,
        related_name='programas_academicos',
    )
    nivel_formacion = models.ForeignKey(
        NivelFormacion,
        on_delete=models.PROTECT,
        related_name='programas_academicos',
    )

    class Meta:
        verbose_name = 'Programa Académico'
        verbose_name_plural = 'Programas Académicos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'
