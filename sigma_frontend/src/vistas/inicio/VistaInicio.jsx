import React, { useEffect, useState } from 'react';
import { useAutenticacion } from '../../contexto/ContextoAutenticacion.jsx';
import Tarjeta from '../../componentes/comunes/Tarjeta.jsx';
import { obtenerPeriodoAcademicoActivo } from '../../servicios/servicioAcademico.js';
import { obtenerMiSolicitudReciente, obtenerSolicitudesMatricula } from '../../servicios/servicioMatricula.js';
import { obtenerNotificaciones } from '../../servicios/servicioNotificaciones.js';
import './inicio.css';

const ETIQUETAS_ESTADO_SOLICITUD = {
  pendiente_revision: 'En revisión por departamento',
  aprobada: 'Aprobada',
  rechazada: 'Rechazada',
};

/**
 * Vista de inicio / dashboard general tras autenticarse.
 * El contenido varía según el rol del usuario:
 * - Estudiante: ve su propia solicitud, periodo activo, notificaciones.
 * - Jefe de Departamento: ve solicitudes pendientes de revisión.
 */
function VistaInicio() {
  const { usuario } = useAutenticacion();
  const esJefe = usuario?.rol_nombre === 'Jefe de Departamento' || usuario?.rol_nombre === 'Administrador';

  return (
    <div className="vista-inicio">
      <header className="inicio-welcome-banner">
        <div className="welcome-banner-content">
          <h1>¡Hola, {usuario?.correo}!</h1>
          <p>Bienvenido al Sistema Integrado de Gestión de Matrícula Académica (SIGMA).</p>
        </div>
        <div className="welcome-banner-illustration">
          <span className="material-icons-outlined">school</span>
        </div>
      </header>

      {esJefe ? <ResumenJefeDepartamento /> : <ResumenEstudiante />}
    </div>
  );
}

function ResumenEstudiante() {
  const [periodo, setPeriodo] = useState(null);
  const [solicitud, setSolicitud] = useState(null);
  const [notificacionesNoLeidas, setNotificacionesNoLeidas] = useState(0);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    async function cargarResumen() {
      try {
        const [periodoActivo, solicitudReciente, notificaciones] = await Promise.all([
          obtenerPeriodoAcademicoActivo(),
          obtenerMiSolicitudReciente(),
          obtenerNotificaciones(true),
        ]);
        setPeriodo(periodoActivo);
        setSolicitud(solicitudReciente);
        setNotificacionesNoLeidas(notificaciones.length);
      } catch {
        // Si algo falla, el dashboard simplemente muestra los valores por defecto.
      } finally {
        setCargando(false);
      }
    }
    cargarResumen();
  }, []);

  const etiquetaSolicitud = solicitud
    ? ETIQUETAS_ESTADO_SOLICITUD[solicitud.estado] || solicitud.estado
    : 'Sin solicitudes activas';

  return (
    <>
      <h3 className="inicio-section-title">Resumen de tu estado</h3>
      <div className="vista-inicio__tarjetas grid-dashboard-cards">

        <Tarjeta titulo="Periodo académico activo">
          <div className="card-custom-body">
            <span className="material-icons-outlined icon-metric text-blue">calendar_today</span>
            <div className="metric-content">
              <span className="metric-value">{cargando ? '...' : (periodo?.nombre || 'No definido')}</span>
              <span className="metric-sub">
                {periodo ? `${periodo.fecha_inicio} a ${periodo.fecha_fin}` : 'Sin periodo activo'}
              </span>
            </div>
          </div>
        </Tarjeta>

        <Tarjeta titulo="Solicitud de matrícula">
          <div className="card-custom-body">
            <span className="material-icons-outlined icon-metric text-amber">assignment_late</span>
            <div className="metric-content">
              <span className="metric-value">{cargando ? '...' : (solicitud ? `#${solicitud.id}` : '—')}</span>
              <span className="metric-sub">{cargando ? 'Cargando...' : etiquetaSolicitud}</span>
            </div>
          </div>
        </Tarjeta>

        <Tarjeta titulo="Notificaciones nuevas">
          <div className="card-custom-body">
            <span className="material-icons-outlined icon-metric text-slate">notifications_active</span>
            <div className="metric-content">
              <span className="metric-value">{cargando ? '...' : notificacionesNoLeidas}</span>
              <span className="metric-sub">{notificacionesNoLeidas > 0 ? 'Tienes novedades' : 'Todo al día por hoy'}</span>
            </div>
          </div>
        </Tarjeta>

      </div>

      <div className="inicio-dashboard-grid margin-top-xl">
        <section className="dashboard-block-card">
          <h4 className="block-card-title">Enlaces rápidos frecuentes</h4>
          <div className="grid-quick-actions">
            <a href="/solicitudes/consultar-estado-solicitud" className="quick-action-item">
              <span className="material-icons-outlined text-blue">search</span>
              <div>
                <strong>Consultar estado</strong>
                <p>Mira el avance de tu matrícula</p>
              </div>
            </a>
            <a href="/solicitudes/diligenciar-formulario" className="quick-action-item">
              <span className="material-icons-outlined text-success">add_circle_outline</span>
              <div>
                <strong>Nueva solicitud</strong>
                <p>Crea un nuevo borrador de carga</p>
              </div>
            </a>
            <a href="/programacion-academica/grupos" className="quick-action-item">
              <span className="material-icons-outlined text-purple">schedule</span>
              <div>
                <strong>Horarios de asignaturas</strong>
                <p>Consulta la oferta del periodo</p>
              </div>
            </a>
          </div>
        </section>
      </div>
    </>
  );
}

function ResumenJefeDepartamento() {
  const [pendientes, setPendientes] = useState([]);
  const [notificacionesNoLeidas, setNotificacionesNoLeidas] = useState(0);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    async function cargarResumen() {
      try {
        const [solicitudesPendientes, notificaciones] = await Promise.all([
          obtenerSolicitudesMatricula({ estado: 'pendiente_revision' }),
          obtenerNotificaciones(true),
        ]);
        setPendientes(solicitudesPendientes);
        setNotificacionesNoLeidas(notificaciones.length);
      } catch {
        // Igual que en el dashboard de Estudiante: se deja en blanco si falla.
      } finally {
        setCargando(false);
      }
    }
    cargarResumen();
  }, []);

  return (
    <>
      <h3 className="inicio-section-title">Resumen operativo</h3>
      <div className="vista-inicio__tarjetas grid-dashboard-cards">

        <Tarjeta titulo="Solicitudes pendientes de revisión">
          <div className="card-custom-body">
            <span className="material-icons-outlined icon-metric text-amber">pending_actions</span>
            <div className="metric-content">
              <span className="metric-value">{cargando ? '...' : pendientes.length}</span>
              <span className="metric-sub">Esperando aprobación o rechazo</span>
            </div>
          </div>
        </Tarjeta>

        <Tarjeta titulo="Notificaciones nuevas">
          <div className="card-custom-body">
            <span className="material-icons-outlined icon-metric text-slate">notifications_active</span>
            <div className="metric-content">
              <span className="metric-value">{cargando ? '...' : notificacionesNoLeidas}</span>
              <span className="metric-sub">{notificacionesNoLeidas > 0 ? 'Tienes novedades' : 'Todo al día por hoy'}</span>
            </div>
          </div>
        </Tarjeta>

      </div>

      <div className="inicio-dashboard-grid margin-top-xl">
        <section className="dashboard-block-card">
          <h4 className="block-card-title">Enlaces rápidos frecuentes</h4>
          <div className="grid-quick-actions">
            <a href="/solicitudes/consultar-solicitud" className="quick-action-item">
              <span className="material-icons-outlined text-blue">fact_check</span>
              <div>
                <strong>Validar solicitudes</strong>
                <p>Revisa las solicitudes pendientes</p>
              </div>
            </a>
            <a href="/programacion-academica/crear" className="quick-action-item">
              <span className="material-icons-outlined text-success">edit_calendar</span>
              <div>
                <strong>Crear programación</strong>
                <p>Define la oferta académica del periodo</p>
              </div>
            </a>
            <a href="/fechas-y-requisitos/crear" className="quick-action-item">
              <span className="material-icons-outlined text-purple">event_available</span>
              <div>
                <strong>Fechas y requisitos</strong>
                <p>Configura el calendario de matrícula</p>
              </div>
            </a>
          </div>
        </section>
      </div>
    </>
  );
}

export default VistaInicio;