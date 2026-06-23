import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAutenticacion } from '../../contexto/ContextoAutenticacion.jsx';
import './barra-lateral.css'; // Asegúrate de vincular sus estilos

function BarraLateral() {
  const location = useLocation();
  const { usuario } = useAutenticacion();
  const esJefe = usuario?.rol_nombre === 'Jefe de Departamento' || usuario?.rol_nombre === 'Administrador';

  // Estados para controlar qué submenús están abiertos de forma independiente
  const [openProg, setOpenProg] = useState(location.pathname.startsWith('/programacion-academica'));
  const [openFechas, setOpenFechas] = useState(location.pathname.startsWith('/fechas-y-requisitos'));
  const [openInfo, setOpenInfo] = useState(location.pathname.startsWith('/informacion-academica'));
  const [openSolicitudes, setOpenSolicitudes] = useState(location.pathname.startsWith('/solicitudes'));
  const [openMatriculas, setOpenMatriculas] = useState(location.pathname.startsWith('/matriculas'));

  return (
    <aside className="barra-lateral">
      
      {/* SECCIÓN SUPERIOR: IDENTIDAD INSTITUCIONAL */}
      <div className="barra-lateral__identidad">
        <div className="barra-lateral__universidad">
          <img 
            src="/escudo.jpg" 
            alt="Universidad de Cartagena" 
            className="barra-lateral__escudo"
            onError={(e) => { e.target.style.display = 'none'; }} // Evita romper si no encuentra la imagen aún
          />
          <div className="barra-lateral__universidad-texto">
            <p className="universidad-principal">Universidad</p>
            <p className="universidad-secundario">de Cartagena</p>
            <p className="universidad-fundacion">Fundada en 1827</p>
          </div>
        </div>

        <div className="barra-lateral__sigma-brand">
          <span className="material-icons-outlined logo-graduacion">school</span>
          <div className="barra-lateral__sigma-texto">
            <h1 className="sigma-titulo">SIGMA</h1>
            <p className="sigma-subtitulo">Sistema Integrado de Gestión de Matrícula Académica</p>
          </div>
        </div>
      </div>

      {/* MENÚ DE NAVEGACIÓN */}
      <nav className="barra-lateral__navegacion">
        
        {/* Inicio (ambos roles) */}
        <NavLink to="/" className={({ isActive }) => `enlace-directo ${isActive ? 'activo' : ''}`}>
          <span className="material-icons-outlined">home</span>
          <span>Inicio</span>
        </NavLink>

        {/* 1. Información Académica (solo Jefe/Admin: CU02, CU03) */}
        {esJefe && (
          <div className="barra-lateral__grupo">
            <div 
              className={`enlace-padre ${location.pathname.startsWith('/informacion-academica') ? 'activo' : ''}`}
              onClick={() => setOpenInfo(!openInfo)}
            >
              <div className="enlace-padre__izquierda">
                <span className="material-icons-outlined">description</span>
                <span>Información Académica</span>
              </div>
              <span className="material-icons-outlined flecha-menu">
                {openInfo ? 'expand_less' : 'expand_more'}
              </span>
            </div>
            {openInfo && (
              <ul className="barra-lateral__submenu">
                <li><NavLink to="/informacion-academica/carga">Carga de Información</NavLink></li>
                <li><NavLink to="/informacion-academica/consulta">Consultar Información</NavLink></li>
              </ul>
            )}
          </div>
        )}

        {/* 2. Programación Académica (solo Jefe/Admin: CU04-CU10) */}
        {esJefe && (
          <div className="barra-lateral__grupo">
            <div 
              className={`enlace-padre ${location.pathname.startsWith('/programacion-academica') ? 'activo' : ''}`}
              onClick={() => setOpenProg(!openProg)}
            >
              <div className="enlace-padre__izquierda">
                <span className="material-icons-outlined">calendar_view_day</span>
                <span>Programación Académica</span>
              </div>
              <span className="material-icons-outlined flecha-menu">
                {openProg ? 'expand_less' : 'expand_more'}
              </span>
            </div>
            {openProg && (
              <ul className="barra-lateral__submenu">
                <li><NavLink to="/programacion-academica/crear">Crear Programación</NavLink></li>
                <li><NavLink to="/programacion-academica/consultar">Consultar Programación</NavLink></li>
                <li><NavLink to="/programacion-academica/publicar">Publicar Programación</NavLink></li>
              </ul>
            )}
          </div>
        )}

        {/* 2.b. Oferta académica (solo Estudiante: consulta de grupos/horarios disponibles) */}
        {!esJefe && (
          <NavLink to="/programacion-academica/grupos" className={({ isActive }) => `enlace-directo ${isActive ? 'activo' : ''}`}>
            <span className="material-icons-outlined">calendar_view_day</span>
            <span>Oferta Académica</span>
          </NavLink>
        )}

        {/* 3. Fechas y Requisitos (solo Jefe/Admin: CU05) */}
        {esJefe && (
          <div className="barra-lateral__grupo">
            <div 
              className={`enlace-padre ${location.pathname.startsWith('/fechas-y-requisitos') ? 'activo' : ''}`}
              onClick={() => setOpenFechas(!openFechas)}
            >
              <div className="enlace-padre__izquierda">
                <span className="material-icons-outlined">date_range</span>
                <span>Fechas y Requisitos</span>
              </div>
              <span className="material-icons-outlined flecha-menu">
                {openFechas ? 'expand_less' : 'expand_more'}
              </span>
            </div>
            {openFechas && (
              <ul className="barra-lateral__submenu">
                <li><NavLink to="/fechas-y-requisitos/crear">Crear Fechas y Requisitos</NavLink></li>
                <li><NavLink to="/fechas-y-requisitos/consultar">Consultar Fechas y Requisitos</NavLink></li>
              </ul>
            )}
          </div>
        )}

        {/* 4. Solicitudes (contenido distinto según el rol) */}
        <div className="barra-lateral__grupo">
          <div 
            className={`enlace-padre ${location.pathname.startsWith('/solicitudes') ? 'activo' : ''}`}
            onClick={() => setOpenSolicitudes(!openSolicitudes)}
          >
            <div className="enlace-padre__izquierda">
              <span className="material-icons-outlined">assignment_turned_in</span>
              <span>Solicitudes</span>
            </div>
            <span className="material-icons-outlined flecha-menu">
              {openSolicitudes ? 'expand_less' : 'expand_more'}
            </span>
          </div>
          {openSolicitudes && (
            <ul className="barra-lateral__submenu">
              {esJefe ? (
                <>
                  <li><NavLink to="/solicitudes/consultar-solicitud">Consultar solicitud de matrícula</NavLink></li>
                </>
              ) : (
                <>
                  <li><NavLink to="/solicitudes/diligenciar-formulario">Realizar solicitud de matrícula</NavLink></li>
                  <li><NavLink to="/solicitudes/consultar-estado-solicitud">Consultar estado de solicitud</NavLink></li>
                </>
              )}
            </ul>
          )}
        </div>

        {/* 5. Matrículas (solo Estudiante: consulta y descarga su matrícula
            oficial en PDF una vez su solicitud fue aprobada, ver CU18) */}
        {!esJefe && (
          <div className="barra-lateral__grupo">
            <div
              className={`enlace-padre ${location.pathname.startsWith('/matriculas') ? 'activo' : ''}`}
              onClick={() => setOpenMatriculas(!openMatriculas)}
            >
              <div className="enlace-padre__izquierda">
                <span className="material-icons-outlined">badge</span>
                <span>Matrículas</span>
              </div>
              <span className="material-icons-outlined flecha-menu">
                {openMatriculas ? 'expand_less' : 'expand_more'}
              </span>
            </div>
            {openMatriculas && (
              <ul className="barra-lateral__submenu">
                <li><NavLink to="/matriculas">Consultar matrícula oficial</NavLink></li>
              </ul>
            )}
          </div>
        )}

        {/* SECCIÓN FINAL CON NOTIFICACIONES INTEGRADAS (ambos roles) */}
        <div className="barra-lateral__adicionales">
          <NavLink to="/notificaciones" className={({ isActive }) => `enlace-directo enlace-notificaciones ${isActive ? 'activo' : ''}`}>
            <div className="enlace-notificaciones__izquierda">
              <span className="material-icons-outlined">notifications</span>
              <span>Notificaciones</span>
            </div>
          </NavLink>
        </div>

      </nav>

      {/* Soporte (ambos roles) */}
      <div className="barra-lateral__ayuda">
        <NavLink to="/ayuda-soporte" className={({ isActive }) => `ayuda-link ${isActive ? 'activo' : ''}`}>
          <span className="material-icons-outlined">help_outline</span>
          <div className="ayuda-texto">
            <p className="p-pregunta">¿Necesitas ayuda?</p>
            <p className="p-sub">Centro de ayuda y soporte</p>
          </div>
        </NavLink>
      </div>
    </aside>
  );
}

export default BarraLateral;