"""
Modelos del bloque Usuarios.
Representa: Rol, Usuario, Estudiante, JefeDepartamento, Docente.

Decisión de diseño (ver notas del proyecto): Rol se modela como tabla aparte
en lugar de un ENUM simple en Usuario, para permitir escalar a nuevos roles
(p.ej. Administrador) sin alterar el esquema.

Decisión de diseño (autenticación): Usuario es el AUTH_USER_MODEL real de
Django (hereda de AbstractBaseUser + PermissionsMixin). Esto permite usar
el hashing de contraseñas nativo de Django y la integración directa con
djangorestframework-simplejwt, en lugar de reimplementar esa lógica a mano.
El campo de login es 'correo' (no 'username').
"""
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from institucional.models import ProgramaAcademico


class Rol(models.Model):
    nombre = models.CharField(max_length=45, unique=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    """Manager personalizado: crea usuarios identificados por correo, no username."""

    def create_user(self, correo, password=None, rol=None, **extra_fields):
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        correo = self.normalize_email(correo)
        usuario = self.model(correo=correo, rol=rol, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador')
        extra_fields.setdefault('rol', rol_admin)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True')

        return self.create_user(correo, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    correo = models.EmailField(max_length=150, unique=True)
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name='usuarios',
        null=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = []  # 'rol' se pide aparte al crear superusuario por consola

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['correo']

    def __str__(self):
        return self.correo


class Estudiante(models.Model):
    primer_nombre = models.CharField(max_length=45)
    segundo_nombre = models.CharField(max_length=45, null=True, blank=True)
    primer_apellido = models.CharField(max_length=45)
    segundo_apellido = models.CharField(max_length=45, null=True, blank=True)
    telefono = models.CharField(max_length=45)
    codigo = models.CharField(max_length=25, unique=True)
    semestre_actual = models.PositiveIntegerField()
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.PROTECT,
        related_name='estudiante',
    )
    programa_academico = models.ForeignKey(
        ProgramaAcademico,
        on_delete=models.PROTECT,
        related_name='estudiantes',
    )

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        ordering = ['primer_apellido', 'primer_nombre']

    def __str__(self):
        return f'{self.codigo} - {self.primer_nombre} {self.primer_apellido}'

    @property
    def nombre_completo(self):
        partes = [self.primer_nombre, self.segundo_nombre, self.primer_apellido, self.segundo_apellido]
        return ' '.join(p for p in partes if p)


class JefeDepartamento(models.Model):
    primer_nombre = models.CharField(max_length=45)
    segundo_nombre = models.CharField(max_length=45, null=True, blank=True)
    primer_apellido = models.CharField(max_length=45)
    segundo_apellido = models.CharField(max_length=45, null=True, blank=True)
    codigo = models.CharField(max_length=25, unique=True)
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.PROTECT,
        related_name='jefe_departamento',
    )
    # Relación 1 a 1: cada Programa Académico tiene un único Jefe de Departamento.
    programa_academico = models.OneToOneField(
        ProgramaAcademico,
        on_delete=models.PROTECT,
        related_name='jefe_departamento',
    )

    class Meta:
        verbose_name = 'Jefe de Departamento'
        verbose_name_plural = 'Jefes de Departamento'
        ordering = ['primer_apellido', 'primer_nombre']

    def __str__(self):
        return f'{self.codigo} - {self.primer_nombre} {self.primer_apellido}'

    @property
    def nombre_completo(self):
        partes = [self.primer_nombre, self.segundo_nombre, self.primer_apellido, self.segundo_apellido]
        return ' '.join(p for p in partes if p)


class Docente(models.Model):
    primer_nombre = models.CharField(max_length=45)
    segundo_nombre = models.CharField(max_length=45, null=True, blank=True)
    primer_apellido = models.CharField(max_length=45)
    segundo_apellido = models.CharField(max_length=45, null=True, blank=True)
    codigo = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(max_length=150, unique=True)
    programa_academico = models.ForeignKey(
        ProgramaAcademico,
        on_delete=models.PROTECT,
        related_name='docentes',
    )

    class Meta:
        verbose_name = 'Docente'
        verbose_name_plural = 'Docentes'
        ordering = ['primer_apellido', 'primer_nombre']

    def __str__(self):
        return f'{self.codigo} - {self.primer_nombre} {self.primer_apellido}'