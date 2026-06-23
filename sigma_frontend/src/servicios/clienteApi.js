/**
 * Cliente base de conexión con la API del backend (SIGMA_BACKEND).
 *
 * Responsabilidades:
 * - Construir la URL completa a partir de VITE_URL_API + la ruta relativa.
 * - Adjuntar automáticamente el header Authorization: Bearer <access> en
 *   cada petición, si hay sesión activa.
 * - Si el backend responde 401 (access token vencido), intenta refrescar
 *   el token automáticamente con el refresh token guardado, y reintenta
 *   la petición original UNA vez. Si el refresh también falla, limpia la
 *   sesión y redirige a /iniciar-sesion.
 * - Parsea JSON automáticamente y lanza errores legibles con el mensaje
 *   que devuelve DRF (p.ej. "detail" o "non_field_errors").
 */

const URL_BASE_API = import.meta.env.VITE_URL_API;

const CLAVE_ACCESS_TOKEN = 'sigma_access_token';
const CLAVE_REFRESH_TOKEN = 'sigma_refresh_token';

export function obtenerAccessToken() {
  return localStorage.getItem(CLAVE_ACCESS_TOKEN);
}

export function obtenerRefreshToken() {
  return localStorage.getItem(CLAVE_REFRESH_TOKEN);
}

export function guardarTokens({ access, refresh }) {
  if (access) localStorage.setItem(CLAVE_ACCESS_TOKEN, access);
  if (refresh) localStorage.setItem(CLAVE_REFRESH_TOKEN, refresh);
}

export function limpiarTokens() {
  localStorage.removeItem(CLAVE_ACCESS_TOKEN);
  localStorage.removeItem(CLAVE_REFRESH_TOKEN);
}

/**
 * Extrae un mensaje de error legible de la respuesta de DRF.
 * DRF puede devolver el error en distintas formas:
 *   {"detail": "..."}                  -> permisos, autenticación
 *   {"non_field_errors": ["..."]}      -> validaciones de serializer
 *   {"campo": ["mensaje 1", "..."]}    -> validación de un campo específico
 */
function extraerMensajeError(cuerpoError) {
  if (!cuerpoError || typeof cuerpoError !== 'object') {
    return 'Ocurrió un error inesperado. Intenta de nuevo.';
  }
  if (cuerpoError.detail) {
    return cuerpoError.detail;
  }
  if (Array.isArray(cuerpoError.non_field_errors) && cuerpoError.non_field_errors.length > 0) {
    return cuerpoError.non_field_errors[0];
  }
  const primeraClave = Object.keys(cuerpoError)[0];
  if (primeraClave && Array.isArray(cuerpoError[primeraClave])) {
    return cuerpoError[primeraClave][0];
  }
  return 'Ocurrió un error inesperado. Intenta de nuevo.';
}

/**
 * Intenta refrescar el access token usando el refresh token guardado.
 * Devuelve true si lo logró (y ya guardó el nuevo access token), false
 * si no (refresh inválido o expirado).
 */
async function intentarRefrescarToken() {
  const refresh = obtenerRefreshToken();
  if (!refresh) return false;

  try {
    const respuesta = await fetch(`${URL_BASE_API}/usuarios/login/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (!respuesta.ok) return false;

    const datos = await respuesta.json();
    guardarTokens({ access: datos.access, refresh: datos.refresh });
    return true;
  } catch {
    return false;
  }
}

/**
 * Petición principal de la app. Uso:
 *   peticionApi('/usuarios/me/')
 *   peticionApi('/matricula/solicitudes-matricula/', { method: 'POST', body: {...} })
 *
 * @param {string} ruta - ruta relativa, ej. '/usuarios/login/'
 * @param {object} opciones - { method, body, sinAuth }
 *   sinAuth: true evita adjuntar el token (útil para login).
 */
export async function peticionApi(ruta, opciones = {}) {
  const { method = 'GET', body, sinAuth = false, ...resto } = opciones;

  const construirHeaders = () => {
    const headers = { 'Content-Type': 'application/json' };
    if (!sinAuth) {
      const token = obtenerAccessToken();
      if (token) headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  };

  const ejecutar = async () => {
    return fetch(`${URL_BASE_API}${ruta}`, {
      method,
      headers: construirHeaders(),
      body: body !== undefined ? JSON.stringify(body) : undefined,
      ...resto,
    });
  };

  let respuesta = await ejecutar();

  // Si el access token venció (401) y no es la petición de login/refresh,
  // intentamos refrescar una sola vez y reintentar la petición original.
  if (respuesta.status === 401 && !sinAuth) {
    const refrescoExitoso = await intentarRefrescarToken();
    if (refrescoExitoso) {
      respuesta = await ejecutar();
    } else {
      limpiarTokens();
      window.location.href = '/iniciar-sesion';
      throw new Error('Tu sesión expiró. Por favor inicia sesión de nuevo.');
    }
  }

  // Sin contenido (204) — no hay body que parsear.
  if (respuesta.status === 204) {
    return null;
  }

  const contentType = respuesta.headers.get('content-type') || '';
  const cuerpo = contentType.includes('application/json')
    ? await respuesta.json()
    : await respuesta.text();

  if (!respuesta.ok) {
    const error = new Error(extraerMensajeError(cuerpo));
    error.status = respuesta.status;
    error.cuerpo = cuerpo;
    throw error;
  }

  return cuerpo;
}

export default URL_BASE_API;