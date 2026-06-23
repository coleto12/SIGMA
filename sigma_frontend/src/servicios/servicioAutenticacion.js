/**
 * Servicio de autenticación — corresponde a la app "usuarios" del backend.
 */
import { peticionApi, guardarTokens, limpiarTokens, obtenerRefreshToken } from './clienteApi.js';

/**
 * Inicia sesión contra POST /usuarios/login/.
 * El backend espera {correo, password} y devuelve
 * {access, refresh, rol, correo, usuario_id}.
 *
 * @returns {Promise<{access: string, refresh: string, rol: string, correo: string, usuario_id: number}>}
 */
export async function iniciarSesion(correo, password) {
  const datos = await peticionApi('/usuarios/login/', {
    method: 'POST',
    body: { correo, password },
    sinAuth: true,
  });
  guardarTokens({ access: datos.access, refresh: datos.refresh });
  return datos;
}

/**
 * Cierra sesión: invalida el refresh token en el backend (blacklist) y
 * limpia los tokens guardados localmente. Si la petición al backend
 * falla (p.ej. sin conexión), igual se limpia la sesión local.
 */
export async function cerrarSesion() {
  const refresh = obtenerRefreshToken();
  try {
    if (refresh) {
      await peticionApi('/usuarios/logout/', {
        method: 'POST',
        body: { refresh },
      });
    }
  } finally {
    limpiarTokens();
  }
}

/**
 * Obtiene los datos del usuario actualmente autenticado.
 * GET /usuarios/me/ -> {id, correo, rol, rol_nombre, is_active}
 */
export function obtenerUsuarioActual() {
  return peticionApi('/usuarios/me/');
}

/**
 * Solicita el envío del enlace de recuperación de contraseña al correo
 * indicado. El backend SIEMPRE responde con el mismo mensaje genérico
 * (exista o no una cuenta con ese correo), por seguridad.
 */
export function solicitarRecuperacionContrasena(correo) {
  return peticionApi('/usuarios/recuperar-contrasena/', {
    method: 'POST',
    body: { correo },
    sinAuth: true,
  });
}

/**
 * Confirma el restablecimiento de contraseña usando el uid/token que
 * llegaron en el enlace del correo.
 */
export function restablecerContrasena({ uid, token, nuevaContrasena }) {
  return peticionApi('/usuarios/restablecer-contrasena/', {
    method: 'POST',
    body: { uid, token, nueva_contrasena: nuevaContrasena },
    sinAuth: true,
  });
}