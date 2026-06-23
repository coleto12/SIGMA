import React, { useEffect, useState } from 'react';
import {
  obtenerMiSolicitudReciente,
  obtenerAsignaturasDeSolicitud,
  obtenerDocumentosDeSolicitud,
  obtenerMiMatricula,
} from '../../../servicios/servicioMatricula.js';
import './consultar-estado-solicitud.css';

const INFO_POR_ESTADO = {
  pendiente_revision: {
    etiqueta: 'En revisión',
    clase: 'badge-warning',
    icono: 'schedule',
    descripcion: 'Tu solicitud está siendo revisada por tu departamento académico.',
  },
  aprobada: {
    etiqueta: 'Aprobada',
    clase: 'badge-success',
    icono: 'check_circle',
    descripcion: 'Tu solicitud fue aprobada. Tu matrícula oficial ya debería estar disponible.',
  },
  rechazada: {
    etiqueta: 'Rechazada',
    clase: 'badge-danger',
    icono: 'cancel',
    descripcion: 'Tu solicitud fue rechazada. Revisa el motivo más abajo.',
  },
};

function VistaConsultarEstadoSolicitud() {
  const [solicitud, setSolicitud] = useState(null);
  const [asignaturas, setAsignaturas] = useState([]);
  const [documentos, setDocumentos] = useState([]);
  const [matricula, setMatricula] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function cargar() {
      try {
        const solicitudActual = await obtenerMiSolicitudReciente();
        setSolicitud(solicitudActual);

        if (solicitudActual) {
          const [listaAsignaturas, listaDocumentos] = await Promise.all([
            obtenerAsignaturasDeSolicitud(solicitudActual.id),
            obtenerDocumentosDeSolicitud(solicitudActual.id),
          ]);
          setAsignaturas(listaAsignaturas);
          setDocumentos(listaDocumentos);

          if (solicitudActual.estado === 'aprobada') {
            const miMatricula = await obtenerMiMatricula();
            setMatricula(miMatricula);
          }
        }
      } catch {
        setError('No se pudo cargar la información de tu solicitud.');
      } finally {
        setCargando(false);
      }
    }
    cargar();
  }, []);

  if (cargando) {
    return <p style={{ padding: '2rem' }}>Cargando estado de tu solicitud...</p>;
  }

  if (error) {
    return (
      <div className="instructions-box" style={{ backgroundColor: '#fbe9e9', margin: '2rem' }}>
        <p style={{ margin: 0, color: '#c62828' }}>{error}</p>
      </div>
    );
  }

  if (!solicitud) {
    return (
      <div className="sigma-solicitud-container">
        <div className="sigma-solicitud-main">
          <header className="sigma-solicitud-header">
            <h2>Consultar Estado de Solicitud</h2>
            <p className="margin-top-xs">Aún no tienes ninguna solicitud de matrícula registrada.</p>
          </header>
          <div className="instructions-box alert-blue-bg">
            <p className="text-blue" style={{ margin: 0 }}>
              Ve a "Realizar Solicitud de Matrícula" para crear tu primera solicitud del periodo vigente.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const info = INFO_POR_ESTADO[solicitud.estado] || INFO_POR_ESTADO.pendiente_revision;

  return (
    <div className="sigma-solicitud-container">
      {/* CUERPO PRINCIPAL */}
      <div className="sigma-solicitud-main">
        <header className="sigma-solicitud-header">
          <h2>Consultar Estado de Solicitud</h2>
          <p className="margin-top-xs">Consulta el estado actual y el detalle de tu solicitud de matrícula.</p>
        </header>

        {/* INFORMACIÓN DE LA SOLICITUD */}
        <section className="sigma-form-card">
          <div className="display-flex-align-center gap-sm margin-bottom-md">
            <span className="font-bold text-slate font-size-sm">Solicitud seleccionada</span>
            <span className="badge-id-solicitud">#{solicitud.id}</span>
          </div>

          <div className="grid-info-estudiante-solicitud">
            <div className="student-profile-block">
              <div className="student-avatar-mock">
                <span className="material-icons-outlined text-muted-dark">person</span>
              </div>
              <div className="student-meta-details">
                <strong className="text-slate font-size-sm">{solicitud.estudiante_nombre}</strong>
                <p className="student-subtext margin-top-xs"><strong>Código:</strong> {solicitud.estudiante_codigo}</p>
              </div>
            </div>

            <div className="display-flex-column gap-sm border-left-gray pl-24">
              <div>
                <span className="info-label">Número de intento</span>
                <p className="info-value-sm">{solicitud.num_intento}</p>
              </div>
              <div>
                <span className="info-label">Fecha de creación</span>
                <p className="info-value-sm">{new Date(solicitud.created_at).toLocaleString('es-CO')}</p>
              </div>
              <div>
                <span className="info-label">Última actualización</span>
                <p className="info-value-sm">{new Date(solicitud.updated_at).toLocaleString('es-CO')}</p>
              </div>
            </div>

            <div className="display-flex-column gap-sm border-left-gray pl-24">
              <div>
                <span className="info-label">Estado actual</span>
                <p className="margin-top-xs"><span className={`badge ${info.clase}`}>{info.etiqueta}</span></p>
              </div>
            </div>
          </div>
        </section>

        {/* PROGRESO REAL (3 estados posibles del backend) */}
        <section className="sigma-form-card">
          <h4 className="form-section-title font-bold margin-bottom-lg">Progreso de la solicitud</h4>

          <div className="stepper-horizontal-container">
            <div className="step-item step-completed">
              <div className="step-circle"><span className="material-icons-outlined">check</span></div>
              <strong className="step-name">1. Enviada</strong>
              <span className="step-date">{new Date(solicitud.created_at).toLocaleDateString('es-CO')}</span>
            </div>

            <div className={`step-line ${solicitud.estado !== 'pendiente_revision' ? 'line-active' : ''}`}></div>

            <div className={`step-item ${solicitud.estado === 'pendiente_revision' ? 'step-active' : 'step-completed'}`}>
              <div className="step-circle">
                <span className="material-icons-outlined">
                  {solicitud.estado === 'pendiente_revision' ? 'schedule' : 'check'}
                </span>
              </div>
              <strong className="step-name">2. En revisión</strong>
              <span className="step-date">
                {solicitud.estado === 'pendiente_revision' ? 'En curso' : 'Completado'}
              </span>
            </div>

            <div className={`step-line ${solicitud.estado === 'aprobada' ? 'line-active' : ''}`}></div>

            <div className={`step-item ${
              solicitud.estado === 'aprobada' ? 'step-completed'
              : solicitud.estado === 'rechazada' ? 'step-danger'
              : 'step-pending'
            }`}>
              <div className="step-circle">
                <span className="material-icons-outlined">
                  {solicitud.estado === 'aprobada' ? 'done_all' : solicitud.estado === 'rechazada' ? 'close' : 'assignment'}
                </span>
              </div>
              <strong className="step-name">3. {solicitud.estado === 'rechazada' ? 'Rechazada' : 'Matrícula generada'}</strong>
              <span className="step-date text-muted">
                {solicitud.estado === 'pendiente_revision' ? 'Pendiente' : 'Completado'}
              </span>
            </div>
          </div>

          <div className={`alert-amber-inner margin-top-lg`}>
            <span className={`material-icons-outlined font-size-md ${solicitud.estado === 'rechazada' ? 'text-danger' : 'text-warning'}`}>
              {info.icono}
            </span>
            <p className="margin-none font-size-xs text-slate">{info.descripcion}</p>
          </div>

          {solicitud.estado === 'rechazada' && solicitud.motivo_rechazo && (
            <div className="instructions-box margin-top-md" style={{ backgroundColor: '#fbe9e9' }}>
              <strong style={{ color: '#c62828', fontSize: '0.85rem' }}>Motivo del rechazo:</strong>
              <p style={{ margin: '0.25rem 0 0', color: '#c62828', fontSize: '0.85rem' }}>{solicitud.motivo_rechazo}</p>
            </div>
          )}

          {solicitud.estado === 'aprobada' && matricula && (
            <div className="instructions-box alert-blue-bg margin-top-md">
              <p className="text-blue" style={{ margin: 0 }}>
                Tu matrícula oficial está disponible.{' '}
                <a href={matricula.documento} target="_blank" rel="noopener noreferrer" style={{ fontWeight: 600 }}>
                  Descargar PDF
                </a>
              </p>
            </div>
          )}
        </section>

        {/* ASIGNATURAS SELECCIONADAS */}
        <section className="sigma-form-card no-padding">
          <div className="card-padding-title">
            <h4 className="form-section-title font-bold">Asignaturas seleccionadas ({asignaturas.length})</h4>
          </div>
          {asignaturas.length === 0 ? (
            <p className="px-24" style={{ paddingBottom: '1rem' }}>No has seleccionado ninguna asignatura todavía.</p>
          ) : (
            <table className="sigma-table">
              <thead>
                <tr>
                  <th>Asignatura</th>
                  <th>Código</th>
                  <th>Grupo</th>
                </tr>
              </thead>
              <tbody>
                {asignaturas.map((asig) => (
                  <tr key={asig.id}>
                    <td><strong>{asig.asignatura_nombre}</strong></td>
                    <td className="text-muted-dark">{asig.asignatura_codigo}</td>
                    <td>{asig.grupo_nombre}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </div>

      {/* PANEL LATERAL */}
      <aside className="sigma-solicitud-aside">
        <div className="aside-sol-card">
          <h5 className="aside-sol-title font-bold">Resumen del estado</h5>

          <div className="alert-inner-gray-large margin-top-sm">
            <span className={`material-icons-outlined font-size-lg ${solicitud.estado === 'rechazada' ? 'text-danger' : 'text-warning'}`}>
              {info.icono}
            </span>
            <div>
              <strong className="text-slate font-size-sm display-block">{info.etiqueta}</strong>
              <p className="margin-none text-muted-dark font-size-xs margin-top-xs line-height-md">
                {info.descripcion}
              </p>
            </div>
          </div>
        </div>

        <div className="aside-sol-card">
          <h5 className="aside-sol-title font-bold margin-bottom-md">Documentos adjuntos</h5>
          {documentos.length === 0 ? (
            <p className="font-size-xs text-muted-dark">Aún no has adjuntado documentos.</p>
          ) : (
            documentos.map((doc) => (
              <div key={doc.id} className="aside-meta-row margin-top-sm">
                <span className="info-label">{doc.requisito_nombre}</span>
                <span className="badge badge-success-outline">v{doc.version}</span>
              </div>
            ))
          )}
        </div>
      </aside>
    </div>
  );
}

export default VistaConsultarEstadoSolicitud;