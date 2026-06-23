/**
 * Servicio institucional — corresponde a la app "institucional" del backend
 * (Campus, Facultades, Niveles de Formación, Programas Académicos).
 */
import { peticionApi } from './clienteApi.js';

export async function obtenerProgramasAcademicos() {
  const datos = await peticionApi('/institucional/programas-academicos/');
  return datos.results ?? datos;
}

export async function obtenerFacultades() {
  const datos = await peticionApi('/institucional/facultades/');
  return datos.results ?? datos;
}