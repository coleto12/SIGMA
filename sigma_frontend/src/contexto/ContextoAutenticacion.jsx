import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  iniciarSesion as iniciarSesionServicio,
  cerrarSesion as cerrarSesionServicio,
  obtenerUsuarioActual,
} from '../servicios/servicioAutenticacion.js';
import { obtenerAccessToken, limpiarTokens } from '../servicios/clienteApi.js';

/**
 * Contexto de autenticación: expone el usuario autenticado, su rol
 * (Estudiante, Jefe de Departamento, Administrador) y, si aplica, el id
 * de su registro Estudiante asociado (necesario para crear solicitudes
 * de matrícula, ya que el backend exige ese id, no el id del Usuario).
 */
const ContextoAutenticacion = createContext(null);

export function ProveedorAutenticacion({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [cargandoSesion, setCargandoSesion] = useState(true);

  useEffect(() => {
    async function restaurarSesion() {
      const token = obtenerAccessToken();
      if (!token) {
        setCargandoSesion(false);
        return;
      }
      try {
        const datosUsuario = await obtenerUsuarioActual();
        setUsuario(datosUsuario);
      } catch {
        limpiarTokens();
        setUsuario(null);
      } finally {
        setCargandoSesion(false);
      }
    }
    restaurarSesion();
  }, []);

  const iniciarSesion = useCallback(async (correo, password) => {
    const datos = await iniciarSesionServicio(correo, password);
    // Tras el login se consulta /usuarios/me/ para tener el objeto completo
    // (incluye estudiante_id), en lugar de construirlo a mano con lo que
    // devuelve /usuarios/login/ (que no incluye ese campo).
    const datosCompletos = await obtenerUsuarioActual();
    setUsuario(datosCompletos);
    return datosCompletos;
  }, []);

  const cerrarSesion = useCallback(async () => {
    await cerrarSesionServicio();
    setUsuario(null);
  }, []);

  const valor = {
    usuario,
    estaAutenticado: !!usuario,
    cargandoSesion,
    iniciarSesion,
    cerrarSesion,
  };

  return (
    <ContextoAutenticacion.Provider value={valor}>
      {children}
    </ContextoAutenticacion.Provider>
  );
}

export function useAutenticacion() {
  const contexto = useContext(ContextoAutenticacion);
  if (!contexto) {
    throw new Error('useAutenticacion debe usarse dentro de <ProveedorAutenticacion>');
  }
  return contexto;
}

export default ContextoAutenticacion;