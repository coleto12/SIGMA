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

    filas = [['Código', 'Asignatura', 'Grupo', 'Docente', 'Horario']]
    dias_abreviados = {
        'lunes': 'Lun', 'martes': 'Mar', 'miercoles': 'Mié',
        'jueves': 'Jue', 'viernes': 'Vie', 'sabado': 'Sáb',
    }
    for sa in asignaturas_solicitadas:
        grupo = sa.grupo
        docente_nombre = f'{grupo.docente.primer_nombre} {grupo.docente.primer_apellido}'
        horarios_grupo = grupo.horarios.select_related('salon').all()
        if horarios_grupo:
            texto_horario = '<br/>'.join(
                f'{dias_abreviados.get(h.dia_semana, h.dia_semana)} '
                f'{h.hora_inicio.strftime("%H:%M")}-{h.hora_fin.strftime("%H:%M")} '
                f'({h.salon.nombre})'
                for h in horarios_grupo
            )
        else:
            texto_horario = 'Sin horario definido'
        filas.append([
            grupo.asignatura.codigo, grupo.asignatura.nombre, grupo.nombre,
            docente_nombre, Paragraph(texto_horario, styles['Normal']),
        ])

    tabla = Table(filas, colWidths=[2.3 * cm, 5.5 * cm, 1.8 * cm, 3.2 * cm, 3.7 * cm])
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

    # -------------------------------------------------------------
    # Cuadrícula de horario semanal (filas = bloques de hora, según
    # las horas de inicio/fin reales de los horarios de esta solicitud;
    # columnas = días). Cada celda muestra código + grupo + salón.
    # -------------------------------------------------------------
    todos_los_horarios = []
    for sa in asignaturas_solicitadas:
        for h in sa.grupo.horarios.select_related('salon').all():
            todos_los_horarios.append((sa.grupo, h))

    if todos_los_horarios:
        elementos.append(Paragraph('Horario semanal', styles['Heading3']))

        dias_columnas = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado']
        # Franjas únicas (inicio, fin) que aparecen en los horarios reales,
        # ordenadas cronológicamente - no se asume una duración fija de bloque.
        franjas = sorted({(h.hora_inicio, h.hora_fin) for _, h in todos_los_horarios})

        # Mapa (franja, dia) -> texto de la celda, para llenar la grilla.
        celda_por_franja_dia = {}
        for grupo, h in todos_los_horarios:
            clave = ((h.hora_inicio, h.hora_fin), h.dia_semana)
            texto_celda = f'{grupo.asignatura.codigo}-{grupo.nombre}<br/>{h.salon.nombre}'
            celda_por_franja_dia[clave] = texto_celda

        estilo_celda = styles['Normal'].clone('celda_horario')
        estilo_celda.fontSize = 7
        estilo_celda.leading = 8

        encabezado = ['Horario'] + [dias_abreviados.get(d, d).capitalize() for d in dias_columnas]
        filas_horario = [encabezado]
        for hora_inicio, hora_fin in franjas:
            fila = [f'{hora_inicio.strftime("%H:%M")}-{hora_fin.strftime("%H:%M")}']
            for dia in dias_columnas:
                texto_celda = celda_por_franja_dia.get(((hora_inicio, hora_fin), dia), '')
                fila.append(Paragraph(texto_celda, estilo_celda) if texto_celda else '')
            filas_horario.append(fila)

        ancho_col_hora = 2.2 * cm
        ancho_col_dia = (17.5 * cm - ancho_col_hora) / len(dias_columnas)
        tabla_horario = Table(
            filas_horario,
            colWidths=[ancho_col_hora] + [ancho_col_dia] * len(dias_columnas),
        )
        tabla_horario.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e8eef0')),
            ('FONTSIZE', (0, 1), (0, -1), 8),
        ]))
        elementos.append(tabla_horario)
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