/**
 * Servicio de notificaciones — corresponde a la app "notificaciones" del
 * backend. Cada usuario ve únicamente sus propias notificaciones (el
 * backend ya filtra por el usuario autenticado, sin excepción de rol).
 */
import { peticionApi } from './clienteApi.js';

/**
 * Lista las notificaciones del usuario autenticado.
 * @param {boolean} [soloNoLeidas] - si se pasa true/false, filtra por
 *   ese estado de lectura; si se omite, trae TODAS (leídas y no leídas).
 */
export async function obtenerNotificaciones(soloNoLeidas) {
  const params = soloNoLeidas === undefined ? '' : `?leida=${soloNoLeidas ? 'false' : 'true'}`;
  const datos = await peticionApi(`/notificaciones/${params}`);
  return datos.results ?? datos;
}

export function marcarNotificacionLeida(notificacionId) {
  return peticionApi(`/notificaciones/${notificacionId}/`, {
    method: 'PUT',
    body: { leida: true },
  });
}

export function eliminarNotificacion(notificacionId) {
  return peticionApi(`/notificaciones/${notificacionId}/`, { method: 'DELETE' });
}

export function marcarTodasLeidas() {
  return peticionApi('/notificaciones/marcar-todas-leidas/', { method: 'POST' });
}