"""
Utilidad para generar el documento oficial de matrícula en PDF.

Genera un PDF simple (texto + tabla) con los datos de la solicitud
aprobada: estudiante, periodo, asignaturas matriculadas y horarios.
No usa todavía la plantilla de identidad institucional de la
Universidad de Cartagena (logos/colores) - eso queda como mejora futura.
"""
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet
from django.core.files.base import ContentFile


def generar_pdf_matricula_oficial(solicitud_matricula):
    """
    Construye el PDF de matrícula oficial para una SolicitudMatricula
    ya aprobada, y devuelve un ContentFile listo para asignar al
    campo FileField de MatriculaOficial.documento.
    """
    estudiante = solicitud_matricula.estudiante
    asignaturas_solicitadas = solicitud_matricula.asignaturas_solicitadas.select_related(
        'grupo', 'grupo__asignatura', 'grupo__docente'
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph('Universidad de Cartagena', styles['Title']))
    elementos.append(Paragraph('Matrícula Académica Oficial', styles['Heading2']))
    elementos.append(Spacer(1, 0.5 * cm))

    datos_estudiante = (
        f'<b>Estudiante:</b> {estudiante.nombre_completo}<br/>'
        f'<b>Código:</b> {estudiante.codigo}<br/>'
        f'<b>Programa académico:</b> {estudiante.programa_academico.nombre}<br/>'
        f'<b>Periodo:</b> {solicitud_matricula.periodo_matricula.periodo_academico.nombre}<br/>'
        f'<b>Número de intento:</b> {solicitud_matricula.num_intento}'
    )
    elementos.append(Paragraph(datos_estudiante, styles['Normal']))
    elementos.append(Spacer(1, 0.7 * cm))

    elementos.append(Paragraph('Asignaturas matriculadas', styles['Heading3']))

    filas = [['Código', 'Asignatura', 'Grupo', 'Docente']]
    for sa in asignaturas_solicitadas:
        grupo = sa.grupo
        docente_nombre = f'{grupo.docente.primer_nombre} {grupo.docente.primer_apellido}'
        filas.append([grupo.asignatura.codigo, grupo.asignatura.nombre, grupo.nombre, docente_nombre])

    tabla = Table(filas, colWidths=[3 * cm, 7 * cm, 2.5 * cm, 4 * cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
    ]))
    elementos.append(tabla)
    elementos.append(Spacer(1, 1 * cm))

    pie = (
        f'Documento generado automáticamente por SIGMA el '
        f'{solicitud_matricula.updated_at.strftime("%Y-%m-%d %H:%M")}.'
    )
    elementos.append(Paragraph(pie, styles['Italic']))

    doc.build(elementos)
    buffer.seek(0)

    nombre_archivo = f'matricula_{estudiante.codigo}_{solicitud_matricula.pk}.pdf'
    return ContentFile(buffer.read(), name=nombre_archivo)