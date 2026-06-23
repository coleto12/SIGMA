/**
 * Servicio de programación académica — corresponde a la app "programacion" del backend
 * (Grupos, Horarios de Grupo, Programaciones Académicas, Salones).
 */
import { peticionApi } from './clienteApi.js';

/**
 * Lista los grupos visibles para el usuario autenticado.
 * El backend ya filtra: un Estudiante solo ve grupos de programaciones
 * académicas publicadas; Jefe/Administrador ven todo.
 * @param {object} [filtros] - { programacion_academica, asignatura }
 */
export async function obtenerGrupos(filtros = {}) {
  const params = new URLSearchParams(filtros).toString();
  const datos = await peticionApi(`/programacion/grupos/${params ? `?${params}` : ''}`);
  return datos.results ?? datos;
}

export function crearGrupo({ nombre, cupoMaximo, programacionAcademicaId, asignaturaId, docenteId }) {
  return peticionApi('/programacion/grupos/', {
    method: 'POST',
    body: {
      nombre,
      cupo_maximo: cupoMaximo,
      cupo_disponible: cupoMaximo,
      programacion_academica: programacionAcademicaId,
      asignatura: asignaturaId,
      docente: docenteId,
    },
  });
}

export function eliminarGrupo(grupoId) {
  return peticionApi(`/programacion/grupos/${grupoId}/`, { method: 'DELETE' });
}

/**
 * Edita un grupo existente (CU09 - Modificar Programación Académica).
 * El backend rechaza el cambio si la programación ya está publicada,
 * y registra el cambio en el log de auditoría.
 */
export function editarGrupo(grupoId, { nombre, cupoMaximo, docenteId }) {
  const body = {};
  if (nombre !== undefined) body.nombre = nombre;
  if (cupoMaximo !== undefined) body.cupo_maximo = cupoMaximo;
  if (docenteId !== undefined) body.docente = docenteId;
  return peticionApi(`/programacion/grupos/${grupoId}/`, { method: 'PUT', body });
}

/** Lista los horarios de un grupo específico (o todos si no se pasa id). */
export async function obtenerHorarios(grupoId) {
  const query = grupoId ? `?grupo=${grupoId}` : '';
  const datos = await peticionApi(`/programacion/horarios/${query}`);
  return datos.results ?? datos;
}

/**
 * Crea un bloque de horario para un grupo. El backend valida que no se
 * cruce con otro horario del mismo docente ni del mismo salón.
 * @param {object} datos - { grupoId, diaSemana, horaInicio, horaFin, salonId }
 *   diaSemana: 'lunes' | 'martes' | 'miercoles' | 'jueves' | 'viernes' | 'sabado'
 *   horaInicio, horaFin: strings 'HH:MM' (formato 24h)
 */
export function crearHorario({ grupoId, diaSemana, horaInicio, horaFin, salonId }) {
  return peticionApi('/programacion/horarios/', {
    method: 'POST',
    body: {
      grupo: grupoId,
      dia_semana: diaSemana,
      hora_inicio: horaInicio,
      hora_fin: horaFin,
      salon: salonId,
    },
  });
}

export function eliminarHorario(horarioId) {
  return peticionApi(`/programacion/horarios/${horarioId}/`, { method: 'DELETE' });
}

/**
 * Edita un bloque de horario existente (CU09). El backend valida que
 * no se generen conflictos de horario con el nuevo día/hora/salón, y
 * rechaza el cambio si la programación ya está publicada.
 */
export function editarHorario(horarioId, { diaSemana, horaInicio, horaFin, salonId }) {
  const body = {};
  if (diaSemana !== undefined) body.dia_semana = diaSemana;
  if (horaInicio !== undefined) body.hora_inicio = horaInicio;
  if (horaFin !== undefined) body.hora_fin = horaFin;
  if (salonId !== undefined) body.salon = salonId;
  return peticionApi(`/programacion/horarios/${horarioId}/`, { method: 'PUT', body });
}

export async function obtenerSalones() {
  const datos = await peticionApi('/programacion/salones/');
  return datos.results ?? datos;
}

/**
 * Lista las programaciones académicas visibles. Para el Jefe/Admin
 * incluye también las no publicadas; un Estudiante solo ve publicadas
 * (filtro que ya aplica el backend).
 * @param {object} [filtros] - { periodo_academico, programa_academico }
 */
export async function obtenerProgramacionesAcademicas(filtros = {}) {
  const params = new URLSearchParams(filtros).toString();
  const datos = await peticionApi(`/programacion/programaciones-academicas/${params ? `?${params}` : ''}`);
  return datos.results ?? datos;
}

/**
 * Crea una ProgramacionAcademica. El backend ya fuerza programa_academico
 * y jefe_departamento según el usuario autenticado (ver
 * ProgramacionAcademicaListCreateView.post), así que aquí solo se envía
 * el periodo_academico; el resto del body es ignorado/sobrescrito por
 * el servidor si el usuario es Jefe de Departamento.
 */
export function crearProgramacionAcademica(periodoAcademicoId) {
  return peticionApi('/programacion/programaciones-academicas/', {
    method: 'POST',
    body: { periodo_academico: periodoAcademicoId, estado: 'no_publicada' },
  });
}

export function publicarProgramacionAcademica(programacionAcademicaId) {
  return peticionApi(`/programacion/programaciones-academicas/${programacionAcademicaId}/publicar/`, {
    method: 'POST',
  });
}