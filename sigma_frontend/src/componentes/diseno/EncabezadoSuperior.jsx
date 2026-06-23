import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAutenticacion } from '../../contexto/ContextoAutenticacion.jsx';
import { obtenerNotificaciones } from '../../servicios/servicioNotificaciones.js';
// import './EncabezadoSuperior.css'; 

/**
 * Encabezado superior unificado para SIGMA.
 * Muestra el menú hamburguesa, el título dinámico de la vista actual,
 * los accesos de ayuda/notificaciones y los datos del usuario autenticado,
 * con un menú desplegable para cerrar sesión.
 */
function EncabezadoSuperior({ titulo = "SIGMA" }) {
  const navegar = useNavigate();
  const { usuario, cerrarSesion } = useAutenticacion();
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [noLeidas, setNoLeidas] = useState(0);
  const referenciaMenu = useRef(null);

  // Carga el conteo real de notificaciones no leídas del usuario al
  // montar el componente. No se actualiza en tiempo real (sin polling
  // ni websockets), pero refleja el estado correcto en cada navegación
  // que vuelva a montar el layout principal.
  useEffect(() => {
    obtenerNotificaciones(true)
      .then((lista) => setNoLeidas(lista.length))
      .catch(() => setNoLeidas(0));
  }, []);

  // Cierra el menú desplegable si se hace click fuera de él.
  useEffect(() => {
    function manejarClickFuera(evento) {
      if (referenciaMenu.current && !referenciaMenu.current.contains(evento.target)) {
        setMenuAbierto(false);
      }
    }
    document.addEventListener('mousedown', manejarClickFuera);
    return () => document.removeEventListener('mousedown', manejarClickFuera);
  }, []);

  async function manejarCerrarSesion() {
    setMenuAbierto(false);
    await cerrarSesion();
    navegar('/iniciar-sesion');
  }

  // El backend solo expone "correo" (no nombre completo) en /usuarios/me/,
  // así que se usa como respaldo visual mientras no haya un nombre disponible.
  const nombreMostrado = usuario?.correo || 'Usuario';
  const rolMostrado = usuario?.rol_nombre || '';

  return (
    <header className="encabezado-superior">
      {/* LADO IZQUIERDO: Menú hamburguesa y Título Dinámico */}
      <div className="encabezado-superior__izquierda">
        <button className="encabezado-superior__menu-btn" type="button" aria-label="Abrir menú lateral">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
        <h1 className="encabezado-superior__titulo">{titulo}</h1>
      </div>

      {/* LADO DERECHO: Acciones, Notificaciones y Perfil */}
      <div className="encabezado-superior__acciones">
        {/* Contenedor de Notificaciones con su indicador numérico (Badge) */}
        <div className="encabezado-superior__notificaciones-wrapper">
          <button
            className="encabezado-superior__icono"
            type="button"
            aria-label="Notificaciones"
            onClick={() => navegar('/notificaciones')}
          >
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
          </button>
          {noLeidas > 0 && (
            <span className="encabezado-superior__badge">{noLeidas > 9 ? '9+' : noLeidas}</span>
          )}
        </div>

        {/* Ícono de Ayuda */}
        <button className="encabezado-superior__icono" type="button" aria-label="Centro de ayuda">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        </button>

        {/* Perfil del Usuario Autenticado */}
        <div className="encabezado-superior__usuario-wrapper" ref={referenciaMenu}>
          <div
            className="encabezado-superior__usuario"
            onClick={() => setMenuAbierto((v) => !v)}
            role="button"
            tabIndex={0}
            aria-expanded={menuAbierto}
            aria-haspopup="true"
          >
            <div className="encabezado-superior__avatar-wrapper">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5-4-8-4z"/>
              </svg>
            </div>
            <div className="encabezado-superior__info">
              <p className="encabezado-superior__nombre">{nombreMostrado}</p>
              <p className="encabezado-superior__rol">{rolMostrado}</p>
            </div>
            {/* Flecha indicadora de menú desplegable */}
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" className="encabezado-superior__flecha">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>

          {menuAbierto && (
            <div className="encabezado-superior__menu-desplegable" role="menu">
              <button
                type="button"
                className="encabezado-superior__opcion-menu"
                role="menuitem"
                onClick={manejarCerrarSesion}
              >
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                  <polyline points="16 17 21 12 16 7"></polyline>
                  <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>
                Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default EncabezadoSuperior;