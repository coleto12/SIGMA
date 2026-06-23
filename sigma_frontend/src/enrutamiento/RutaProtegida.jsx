import { Navigate, Outlet } from 'react-router-dom';
import { useAutenticacion } from '../contexto/ContextoAutenticacion.jsx';

/**
 * Envuelve un grupo de rutas que requieren sesión activa.
 * - Mientras se restaura la sesión (al recargar la página), no decide
 *   nada todavía: evita un parpadeo donde redirige a login y luego
 *   "regresa" cuando la sesión sí existía.
 * - Si no hay sesión, redirige a /iniciar-sesion.
 * - Si se pasa `rolesPermitidos`, además verifica que el rol del usuario
 *   esté en esa lista; si no, redirige a la página de inicio.
 */
function RutaProtegida({ rolesPermitidos }) {
  const { estaAutenticado, cargandoSesion, usuario } = useAutenticacion();

  if (cargandoSesion) {
    return null; // o un spinner de carga, si se quiere más adelante
  }

  if (!estaAutenticado) {
    return <Navigate to="/iniciar-sesion" replace />;
  }

  if (rolesPermitidos && !rolesPermitidos.includes(usuario?.rol_nombre)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}

export default RutaProtegida;