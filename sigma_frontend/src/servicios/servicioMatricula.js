/**
 * Servicio de matrícula académica — corresponde a la app "matricula" del backend
 * (Matrículas Oficiales, Periodos de Matrícula, Requisitos Documentales, Solicitudes de Matrícula).
 *
 * Nota: el endpoint /matricula/solicitudes-matricula/ ya filtra automáticamente
 * por el lado del backend según el rol de quien consulta (un Estudiante solo
 * ve sus propias solicitudes; un Jefe/Administrador ve todas, y puede afinar
 * con los query params que el backend soporta: ?estado=, ?estudiante=,
 * ?periodo_matricula=).
 */
import { peticionApi } from './clienteApi.js';

// ---------------------------------------------------------------------
// Periodos de matrícula
// ---------------------------------------------------------------------
export async function obtenerPeriodosMatricula(filtroEstado) {
  const datos = await peticionApi('/matricula/periodos-matricula/');
  const lista = datos.results ?? datos;
  if (!filtroEstado) return lista;
  return lista.filter((p) => p.estado === filtroEstado);
}

export async function obtenerPeriodoMatriculaPublicado() {
  const publicados = await obtenerPeriodosMatricula('publicado');
  return publicados[0] ?? null;
}

/**
 * Obtiene el PeriodoMatricula (de cualquier estado) asociado a un
 * periodo académico específico, sin filtrar por estado. Útil para que
 * el Jefe vea/edite el que ya creó, esté publicado o no.
 */
export async function obtenerPeriodoMatriculaDelPeriodoAcademico(periodoAcademicoId) {
  const todos = await obtenerPeriodosMatricula();
  return todos.find((p) => p.periodo_academico === periodoAcademicoId) ?? null;
}

/**
 * Crea un PeriodoMatricula. El backend ya fuerza jefe_departamento
 * según el usuario autenticado (ver PeriodoMatriculaListCreateView.post).
 */
export function crearPeriodoMatricula({ periodoAcademicoId, fechaInicio, fechaFin }) {
  return peticionApi('/matricula/periodos-matricula/', {
    method: 'POST',
    body: {
      periodo_academico: periodoAcademicoId,
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
      estado: 'no_publicado',
    },
  });
}

export function actualizarPeriodoMatricula(periodoMatriculaId, { fechaInicio, fechaFin }) {
  return peticionApi(`/matricula/periodos-matricula/${periodoMatriculaId}/`, {
    method: 'PUT',
    body: { fecha_inicio: fechaInicio, fecha_fin: fechaFin },
  });
}

export function publicarPeriodoMatricula(periodoMatriculaId) {
  return peticionApi(`/matricula/periodos-matricula/${periodoMatriculaId}/`, {
    method: 'PUT',
    body: { estado: 'publicado' },
  });
}

/**
 * Reabre para edición un periodo de matrícula ya publicado. El backend
 * solo lo permite si la fecha_fin del periodo ya pasó (protege el
 * proceso de matrícula mientras todavía está activo).
 */
export function reabrirPeriodoMatricula(periodoMatriculaId) {
  return peticionApi(`/matricula/periodos-matricula/${periodoMatriculaId}/reabrir/`, {
    method: 'POST',
  });
}

// ---------------------------------------------------------------------
// Requisitos documentales
// ---------------------------------------------------------------------
export async function obtenerRequisitosDocumentales(periodoMatriculaId) {
  const query = periodoMatriculaId ? `?periodo_matricula=${periodoMatriculaId}` : '';
  const datos = await peticionApi(`/matricula/requisitos-documentales/${query}`);
  return datos.results ?? datos;
}

export function crearRequisitoDocumental({ periodoMatriculaId, nombre, descripcion, formato }) {
  return peticionApi('/matricula/requisitos-documentales/', {
    method: 'POST',
    body: { periodo_matricula: periodoMatriculaId, nombre, descripcion, formato },
  });
}

export function eliminarRequisitoDocumental(requisitoId) {
  return peticionApi(`/matricula/requisitos-documentales/${requisitoId}/`, { method: 'DELETE' });
}

// ---------------------------------------------------------------------
// Solicitudes de matrícula
// ---------------------------------------------------------------------
export async function obtenerSolicitudesMatricula(filtros = {}) {
  const params = new URLSearchParams(filtros).toString();
  const datos = await peticionApi(`/matricula/solicitudes-matricula/${params ? `?${params}` : ''}`);
  return datos.results ?? datos;
}

export async function obtenerMiSolicitudReciente() {
  const solicitudes = await obtenerSolicitudesMatricula();
  return solicitudes[0] ?? null;
}

export function obtenerSolicitudPorId(id) {
  return peticionApi(`/matricula/solicitudes-matricula/${id}/`);
}

export function crearSolicitud(estudianteId, periodoMatriculaId) {
  return peticionApi('/matricula/solicitudes-matricula/', {
    method: 'POST',
    body: { estudiante: estudianteId, periodo_matricula: periodoMatriculaId },
  });
}

export function eliminarSolicitud(id) {
  return peticionApi(`/matricula/solicitudes-matricula/${id}/`, { method: 'DELETE' });
}

/**
 * Aprueba una solicitud de matrícula. Si el estudiante ya tiene alguna
 * de las asignaturas aprobada en OTRO grupo dentro de este mismo
 * periodo (de un intento anterior), el backend responde 409 con
 * { requiere_confirmacion: true, reemplazos: [...] } en vez de
 * aprobar de una vez. En ese caso, se debe mostrar la advertencia al
 * Jefe y, si confirma, volver a llamar con confirmarReemplazos=true.
 */
export function aprobarSolicitud(solicitudId, confirmarReemplazos = false) {
  return peticionApi(`/matricula/solicitudes-matricula/${solicitudId}/aprobar/`, {
    method: 'POST',
    body: confirmarReemplazos ? { confirmar_reemplazos: true } : undefined,
  });
}

export function rechazarSolicitud(solicitudId, motivoRechazo) {
  return peticionApi(`/matricula/solicitudes-matricula/${solicitudId}/rechazar/`, {
    method: 'POST',
    body: { motivo_rechazo: motivoRechazo },
  });
}

/**
 * Confirma el envío formal de la solicitud (ver CU13 paso final). A
 * partir de este punto, el backend rechaza cualquier intento de
 * modificar las asignaturas seleccionadas o los documentos adjuntos
 * (ver CU19, CU20) hasta que el Jefe de Departamento la apruebe o
 * rechace.
 */
export function confirmarEnvioSolicitud(solicitudId) {
  return peticionApi(`/matricula/solicitudes-matricula/${solicitudId}/confirmar-envio/`, {
    method: 'POST',
  });
}

// ---------------------------------------------------------------------
// Asignaturas dentro de una solicitud
// ---------------------------------------------------------------------
export async function obtenerAsignaturasDeSolicitud(solicitudMatriculaId) {
  const datos = await peticionApi(`/matricula/solicitudes-asignatura/?solicitud_matricula=${solicitudMatriculaId}`);
  return datos.results ?? datos;
}

export function agregarAsignaturaASolicitud(solicitudMatriculaId, grupoId) {
  return peticionApi('/matricula/solicitudes-asignatura/', {
    method: 'POST',
    body: { solicitud_matricula: solicitudMatriculaId, grupo: grupoId },
  });
}

export function quitarAsignaturaDeSolicitud(solicitudAsignaturaId) {
  return peticionApi(`/matricula/solicitudes-asignatura/${solicitudAsignaturaId}/`, {
    method: 'DELETE',
  });
}

// ---------------------------------------------------------------------
// Documentos adjuntos
// ---------------------------------------------------------------------
export async function obtenerDocumentosDeSolicitud(solicitudMatriculaId) {
  const datos = await peticionApi(`/matricula/documentos-adjuntos/?solicitud_matricula=${solicitudMatriculaId}`);
  return datos.results ?? datos;
}

export async function subirDocumentoAdjunto({ solicitudMatriculaId, requisitoDocumentalId, archivo }) {
  const { obtenerAccessToken } = await import('./clienteApi.js');
  const URL_BASE_API = import.meta.env.VITE_URL_API;

  const formData = new FormData();
  formData.append('solicitud_matricula', solicitudMatriculaId);
  formData.append('requisito_documental', requisitoDocumentalId);
  formData.append('nombre_archivo', archivo.name);
  formData.append('archivo', archivo);

  const respuesta = await fetch(`${URL_BASE_API}/matricula/documentos-adjuntos/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${obtenerAccessToken()}` },
    body: formData,
  });

  const cuerpo = await respuesta.json();
  if (!respuesta.ok) {
    const mensaje = cuerpo.detail || Object.values(cuerpo)[0]?.[0] || 'No se pudo subir el documento.';
    throw new Error(mensaje);
  }
  return cuerpo;
}

// ---------------------------------------------------------------------
// Matrícula oficial
// ---------------------------------------------------------------------
export async function obtenerMiMatricula() {
  const datos = await peticionApi('/matricula/matriculas-oficiales/');
  const lista = datos.results ?? datos;
  return lista[0] ?? null;
}