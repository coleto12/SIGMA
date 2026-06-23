/**
 * Servicio de usuarios — corresponde a la app "usuarios" del backend,
 * para las entidades administrativas (Docente, Estudiante, JefeDepartamento)
 * que no son parte de la autenticación en sí (eso vive en servicioAutenticacion.js).
 */
import { peticionApi, obtenerAccessToken } from './clienteApi.js';

const URL_BASE_API = import.meta.env.VITE_URL_API;

export async function obtenerDocentes() {
  const datos = await peticionApi('/usuarios/docentes/');
  return datos.results ?? datos;
}

/**
 * Carga docentes vía CSV (CU02). Ver servicioAcademico.js para las
 * otras 3 cargas (Asignaturas, Plan de Estudio, Historial Académico) y
 * la explicación del patrón de manejo de errores fila por fila.
 */
export async function cargarDocentesCSV(archivo, reemplazar = false) {
  const formData = new FormData();
  formData.append('archivo', archivo);
  if (reemplazar) {
    formData.append('reemplazar', 'true');
  }

  const respuesta = await fetch(`${URL_BASE_API}/usuarios/cargar/docentes/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${obtenerAccessToken()}` },
    body: formData,
  });

  const cuerpo = await respuesta.json();
  if (!respuesta.ok) {
    if (Array.isArray(cuerpo.errores) && cuerpo.errores.length > 0) {
      const error = new Error(cuerpo.detail || 'El archivo contiene errores.');
      error.errores = cuerpo.errores;
      throw error;
    }
    throw new Error(cuerpo.detail || 'No se pudo procesar el archivo.');
  }
  return cuerpo;
}