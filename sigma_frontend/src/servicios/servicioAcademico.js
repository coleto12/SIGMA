/**
 * Servicio de información académica — corresponde a la app "academico" del backend
 * (Asignaturas, Historiales Académicos, Periodos Académicos, Planes de Estudio, Prerrequisitos).
 */
import { peticionApi, obtenerAccessToken } from './clienteApi.js';

const URL_BASE_API = import.meta.env.VITE_URL_API;

/**
 * Lista los periodos académicos. Si se pasa filtroEstado ('activo' | 'cerrado'),
 * filtra en el cliente (el backend no expone ?estado= en este endpoint).
 */
export async function obtenerPeriodosAcademicos(filtroEstado) {
  const datos = await peticionApi('/academico/periodos-academicos/');
  const lista = datos.results ?? datos;
  if (!filtroEstado) return lista;
  return lista.filter((p) => p.estado === filtroEstado);
}

/**
 * Obtiene el periodo académico actualmente activo (el primero con estado 'activo').
 * Devuelve null si no hay ninguno.
 */
export async function obtenerPeriodoAcademicoActivo() {
  const activos = await obtenerPeriodosAcademicos('activo');
  return activos[0] ?? null;
}

/**
 * Obtiene el plan de estudios VIGENTE de un programa académico.
 * Devuelve null si el programa no tiene ningún plan vigente todavía.
 */
export async function obtenerPlanVigente(programaAcademicoId) {
  const datos = await peticionApi(
    `/academico/planes-estudio/?programa_academico=${programaAcademicoId}&estado=vigente`
  );
  const lista = datos.results ?? datos;
  return lista[0] ?? null;
}

/**
 * Lista las asignaturas de un plan de estudio, agrupables por semestre.
 * @param {number} planEstudioId
 */
export async function obtenerAsignaturasDelPlan(planEstudioId) {
  const datos = await peticionApi(`/academico/plan-asignaturas/?plan_estudio=${planEstudioId}`);
  return datos.results ?? datos;
}

/**
 * Devuelve la lista de números de semestre disponibles en un plan
 * (sin duplicados, ordenados), a partir de sus PlanEstudioAsignatura.
 */
export async function obtenerSemestresDelPlan(planEstudioId) {
  const filas = await obtenerAsignaturasDelPlan(planEstudioId);
  const semestres = [...new Set(filas.map((f) => f.semestre))];
  return semestres.sort((a, b) => a - b);
}

export async function obtenerAsignaturas() {
  const datos = await peticionApi('/academico/asignaturas/');
  return datos.results ?? datos;
}

/** Lista los prerrequisitos de una asignatura específica (o todos si no se pasa id). */
export async function obtenerPrerrequisitos(asignaturaId) {
  const query = asignaturaId ? `?asignatura=${asignaturaId}` : '';
  const datos = await peticionApi(`/academico/prerrequisitos/${query}`);
  return datos.results ?? datos;
}

/**
 * Lista el historial académico visible para el usuario autenticado.
 * El backend ya filtra: un Estudiante solo ve el suyo; un Jefe de
 * Departamento solo ve el de estudiantes de su propio programa; un
 * Administrador ve todo.
 */
export async function obtenerHistorialAcademico(filtros = {}) {
  const params = new URLSearchParams(filtros).toString();
  const datos = await peticionApi(`/academico/historial-academico/${params ? `?${params}` : ''}`);
  return datos.results ?? datos;
}

// ---------------------------------------------------------------------
// Carga de Información Académica vía CSV (CU02)
// Estas 3 funciones suben un archivo (multipart/form-data), por eso no
// usan peticionApi() directamente (que solo serializa JSON) sino que
// hacen el fetch manualmente, igual patrón que subirDocumentoAdjunto()
// en servicioMatricula.js.
// ---------------------------------------------------------------------

async function _subirCsv(ruta, archivo, reemplazar = false) {
  const formData = new FormData();
  formData.append('archivo', archivo);
  if (reemplazar) {
    formData.append('reemplazar', 'true');
  }

  const respuesta = await fetch(`${URL_BASE_API}${ruta}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${obtenerAccessToken()}` },
    body: formData,
  });

  const cuerpo = await respuesta.json();
  if (!respuesta.ok) {
    // Si el backend devolvió una lista de errores fila por fila
    // (ver carga_csv.py), se incluyen en el mensaje para mostrarlos
    // todos de una vez, no solo el genérico.
    if (Array.isArray(cuerpo.errores) && cuerpo.errores.length > 0) {
      const error = new Error(cuerpo.detail || 'El archivo contiene errores.');
      error.errores = cuerpo.errores;
      throw error;
    }
    throw new Error(cuerpo.detail || 'No se pudo procesar el archivo.');
  }
  return cuerpo;
}

export function cargarAsignaturasCSV(archivo) {
  // Las asignaturas son un catálogo compartido entre todos los programas;
  // nunca admite "reemplazar todo" (sería destructivo para otras carreras).
  return _subirCsv('/academico/cargar/asignaturas/', archivo, false);
}

export function cargarPlanEstudioCSV(archivo, reemplazar = false) {
  return _subirCsv('/academico/cargar/plan-estudio/', archivo, reemplazar);
}

export function cargarHistorialAcademicoCSV(archivo, reemplazar = false) {
  return _subirCsv('/academico/cargar/historial-academico/', archivo, reemplazar);
}