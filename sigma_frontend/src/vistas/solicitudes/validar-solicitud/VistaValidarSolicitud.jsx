import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  obtenerSolicitudPorId,
  obtenerAsignaturasDeSolicitud,
  obtenerDocumentosDeSolicitud,
  aprobarSolicitud,
  rechazarSolicitud,
} from '../../../servicios/servicioMatricula.js';
import './validar-solicitud.css';

const ETIQUETAS_ESTADO = {
  pendiente_revision: { texto: 'En revisión', clase: 'badge-warning' },
  aprobada: { texto: 'Aprobada', clase: 'badge-success' },
  rechazada: { texto: 'Rechazada', clase: 'badge-danger' },
};

function VistaValidarSolicitud() {
  const { id } = useParams();
  const navegar = useNavigate();

  const [solicitud, setSolicitud] = useState(null);
  const [asignaturas, setAsignaturas] = useState([]);
  const [documentos, setDocumentos] = useState([]);

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');
  const [procesando, setProcesando] = useState(false);

  const [mostrarFormRechazo, setMostrarFormRechazo] = useState(false);
  const [motivoRechazo, setMotivoRechazo] = useState('');
  const [reemplazosPendientes, setReemplazosPendientes] = useState(null);

  useEffect(() => {
    async function cargar() {
      setCargando(true);
      setError('');
      try {
        const [sol, asigs, docs] = await Promise.all([
          obtenerSolicitudPorId(id),
          obtenerAsignaturasDeSolicitud(id),
          obtenerDocumentosDeSolicitud(id),
        ]);
        setSolicitud(sol);
        setAsignaturas(asigs);
        setDocumentos(docs);
      } catch {
        setError('No se pudo cargar la información de la solicitud.');
      } finally {
        setCargando(false);
      }
    }
    cargar();
  }, [id]);

  async function manejarAprobar(confirmarReemplazos = false) {
    if (!confirmarReemplazos) {
      const confirmado = window.confirm('¿Aprobar esta solicitud de matrícula? El estudiante quedará matriculado en las asignaturas seleccionadas.');
      if (!confirmado) return;
    }
    setError('');
    setProcesando(true);
    try {
      const actualizada = await aprobarSolicitud(id, confirmarReemplazos);
      setSolicitud(actualizada);
      setReemplazosPendientes(null);
    } catch (err) {
      if (err.status === 409 && err.cuerpo?.requiere_confirmacion) {
        setReemplazosPendientes(err.cuerpo.reemplazos);
      } else {
        setError(err.message);
      }
    } finally {
      setProcesando(false);
    }
  }

  async function manejarRechazar() {
    if (!motivoRechazo.trim()) {
      setError('Debes ingresar el motivo del rechazo.');
      return;
    }
    setError('');
    setProcesando(true);
    try {
      const actualizada = await rechazarSolicitud(id, motivoRechazo.trim());
      setSolicitud(actualizada);
      setMostrarFormRechazo(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setProcesando(false);
    }
  }

  if (cargando) {
    return <p style={{ padding: '2rem' }}>Cargando información de la solicitud...</p>;
  }

  if (!solicitud) {
    return (
      <div className="sigma-solicitud-container">
        <div className="sigma-solicitud-main">
          <p>No se encontró la solicitud solicitada.</p>
        </div>
      </div>
    );
  }

  const estadoInfo = ETIQUETAS_ESTADO[solicitud.estado] || { texto: solicitud.estado, clase: '' };
  const yaProcesada = solicitud.estado !== 'pendiente_revision';

  return (
    <div className="sigma-solicitud-container">
      <div className="sigma-solicitud-main">
        <header className="sigma-solicitud-header display-flex-space align-center">
          <div>
            <h2>Validar Solicitud de Matrícula</h2>
            <p className="margin-top-xs">Revisa la información de la solicitud antes de aprobar o rechazar.</p>
          </div>
          <button type="button" className="btn-aside-outline-blue width-auto px-16" onClick={() => navegar('/solicitudes/consultar-solicitud')}>
            <span className="material-icons-outlined">arrow_back</span> Volver a la lista
          </button>
        </header>

        {error && (
          <section className="sigma-form-card" style={{ backgroundColor: '#fbe9e9' }}>
            <p style={{ color: '#c62828', margin: 0 }}>{error}</p>
          </section>
        )}

        <section className="sigma-form-card">
          <h4 className="form-section-title font-bold margin-bottom-md">Información de la solicitud</h4>
          <div className="grid-info-validacion-solicitud">
            <div>
              <span className="info-label">ID Solicitud</span>
              <p className="info-value-sm font-bold text-blue-link">MATR-{solicitud.id}</p>
            </div>
            <div>
              <span className="info-label">Fecha de creación</span>
              <p className="info-value-sm">{new Date(solicitud.created_at).toLocaleString('es-CO')}</p>
            </div>
            <div>
              <span className="info-label">Intento número</span>
              <p className="info-value-sm">{solicitud.num_intento}</p>
            </div>
            <div>
              <span className="info-label">Estudiante</span>
              <p className="info-value-sm">{solicitud.estudiante_nombre} ({solicitud.estudiante_codigo})</p>
            </div>
            <div>
              <span className="info-label">Periodo</span>
              <p className="info-value-sm">{solicitud.periodo_matricula_nombre}</p>
            </div>
            <div>
              <span className="info-label">Estado actual</span>
              <p className="info-value-sm"><span className={`badge ${estadoInfo.clase}`}>{estadoInfo.texto}</span></p>
            </div>
          </div>
          {solicitud.estado === 'rechazada' && solicitud.motivo_rechazo && (
            <div className="alert-inner-gray margin-top-md" style={{ backgroundColor: '#fbe9e9' }}>
              <span className="material-icons-outlined" style={{ color: '#c62828' }}>info</span>
              <p style={{ color: '#c62828', margin: 0 }}><strong>Motivo del rechazo:</strong> {solicitud.motivo_rechazo}</p>
            </div>
          )}
        </section>

        <section className="sigma-form-card no-padding">
          <div className="card-padding-title">
            <h4 className="form-section-title font-bold">Asignaturas seleccionadas ({asignaturas.length})</h4>
          </div>
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
          <div className="table-pagination-footer px-24 py-12">
            <span>Total asignaturas: {asignaturas.length}</span>
          </div>
        </section>

        {reemplazosPendientes && (
          <section className="sigma-form-card" style={{ backgroundColor: '#fff8e1', borderColor: '#f0ad4e' }}>
            <h4 className="form-section-title font-bold" style={{ color: '#9a6700' }}>
              ⚠ Este estudiante ya tiene horario asignado en otras asignaturas
            </h4>
            <p style={{ fontSize: '0.85rem', color: '#9a6700', marginTop: '0.5rem' }}>
              Las siguientes asignaturas ya están aprobadas en un grupo distinto, dentro de este mismo periodo.
              Si confirmas, se liberará el cupo del grupo anterior y se ocupará el del nuevo.
            </p>
            <ul style={{ marginTop: '0.75rem', paddingLeft: '1.2rem' }}>
              {reemplazosPendientes.map((r, indice) => (
                <li key={indice} style={{ fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                  <strong>{r.asignatura_codigo} - {r.asignatura_nombre}:</strong>{' '}
                  Grupo {r.grupo_anterior} → Grupo {r.grupo_nuevo}
                </li>
              ))}
            </ul>
            <div className="display-flex-column gap-sm" style={{ marginTop: '0.75rem' }}>
              <button type="button" className="btn-aside-outline-blue" onClick={() => setReemplazosPendientes(null)} disabled={procesando}>
                Cancelar
              </button>
              <button type="button" className="btn-sol-aprobar-full" onClick={() => manejarAprobar(true)} disabled={procesando}>
                {procesando ? 'Procesando...' : 'Confirmar y reemplazar horario'}
              </button>
            </div>
          </section>
        )}

        {!yaProcesada && !reemplazosPendientes && (
          <section className="sigma-form-card grid-acciones-validacion">
            {mostrarFormRechazo ? (
              <>
                <div className="form-group margin-bottom-none" style={{ flex: 1 }}>
                  <label className="font-bold text-slate">Motivo del rechazo (obligatorio)</label>
                  <textarea
                    placeholder="Explica al estudiante por qué se rechaza la solicitud..."
                    rows="3"
                    value={motivoRechazo}
                    onChange={(e) => setMotivoRechazo(e.target.value)}
                  />
                </div>
                <div className="display-flex-column gap-sm justify-end">
                  <button type="button" className="btn-aside-outline-blue" onClick={() => setMostrarFormRechazo(false)} disabled={procesando}>
                    Cancelar
                  </button>
                  <button type="button" className="btn-sol-rechazar-full" onClick={manejarRechazar} disabled={procesando}>
                    {procesando ? 'Procesando...' : 'Confirmar rechazo'}
                  </button>
                </div>
              </>
            ) : (
              <>
                <p className="margin-bottom-none" style={{ color: '#64748b', fontSize: '0.85rem' }}>
                  Verifica cuidadosamente la información antes de tomar una decisión.
                </p>
                <div className="display-flex-column gap-sm justify-end">
                  <button type="button" className="btn-sol-rechazar-full" onClick={() => setMostrarFormRechazo(true)} disabled={procesando}>
                    <span className="material-icons-outlined font-size-md">cancel</span> Rechazar solicitud
                  </button>
                  <button type="button" className="btn-sol-aprobar-full" onClick={() => manejarAprobar(false)} disabled={procesando}>
                    <span className="material-icons-outlined font-size-md">check_circle</span> {procesando ? 'Procesando...' : 'Aprobar solicitud'}
                  </button>
                </div>
              </>
            )}
          </section>
        )}
      </div>

      <aside className="sigma-solicitud-aside">
        <div className="aside-sol-card">
          <h5 className="aside-sol-title font-bold">Documentos adjuntos</h5>
          {documentos.length === 0 ? (
            <p className="font-size-xs text-muted-dark margin-top-sm">No se han adjuntado documentos.</p>
          ) : (
            <ul style={{ marginTop: '0.5rem', paddingLeft: '1.2rem' }}>
              {documentos.map((doc) => (
                <li key={doc.id} style={{ fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                  <a href={doc.archivo} target="_blank" rel="noopener noreferrer">
                    {doc.requisito_nombre || doc.nombre_archivo}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="aside-sol-card alert-blue-bg border-none">
          <div className="alert-sol-title">
            <span className="material-icons-outlined text-blue">info</span>
            <strong className="text-blue font-size-sm">Información importante</strong>
          </div>
          <p className="font-size-xs text-blue margin-top-xs line-height-md">
            Al aprobar, se descuenta el cupo de cada grupo y se genera automáticamente la matrícula oficial en PDF.
          </p>
          <p className="font-size-xs text-blue margin-top-xs line-height-md">
            Al rechazar, debes indicar un motivo; el estudiante lo verá en su notificación.
          </p>
        </div>
      </aside>
    </div>
  );
}

export default VistaValidarSolicitud;