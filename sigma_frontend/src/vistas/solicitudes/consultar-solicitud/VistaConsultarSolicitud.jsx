import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { obtenerSolicitudesMatricula } from '../../../servicios/servicioMatricula.js';
import './consultar-solicitud.css';

const ETIQUETAS_ESTADO = {
  pendiente_revision: { texto: 'En revisión', clase: 'badge-warning' },
  aprobada: { texto: 'Aprobada', clase: 'badge-success' },
  rechazada: { texto: 'Rechazada', clase: 'badge-danger' },
};

function VistaConsultarSolicitud() {
  const navegar = useNavigate();
  const [solicitudes, setSolicitudes] = useState([]);
  const [filtroEstado, setFiltroEstado] = useState('pendiente_revision');
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function cargar() {
      setCargando(true);
      setError('');
      try {
        const filtros = filtroEstado === 'todos' ? {} : { estado: filtroEstado };
        const lista = await obtenerSolicitudesMatricula(filtros);
        setSolicitudes(lista);
      } catch {
        setError('No se pudieron cargar las solicitudes de matrícula.');
      } finally {
        setCargando(false);
      }
    }
    cargar();
  }, [filtroEstado]);

  const totalPendientes = solicitudes.filter((s) => s.estado === 'pendiente_revision').length;
  const totalAprobadas = solicitudes.filter((s) => s.estado === 'aprobada').length;
  const totalRechazadas = solicitudes.filter((s) => s.estado === 'rechazada').length;

  return (
    <div className="sigma-solicitud-container">
      <div className="sigma-solicitud-main">
        <header className="sigma-solicitud-header">
          <h2>Consultar Solicitudes de Matrícula</h2>
          <p>Consulta las solicitudes de matrícula enviadas por los estudiantes de tu programa.</p>
        </header>

        <section className="sigma-form-card grid-filtros-consulta">
          <div className="form-group">
            <label>Estado</label>
            <select value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}>
              <option value="pendiente_revision">En revisión</option>
              <option value="aprobada">Aprobadas</option>
              <option value="rechazada">Rechazadas</option>
              <option value="todos">Todos los estados</option>
            </select>
          </div>
        </section>

        {error && (
          <section className="sigma-form-card" style={{ backgroundColor: '#fbe9e9' }}>
            <p style={{ color: '#c62828', margin: 0 }}>{error}</p>
          </section>
        )}

        <section className="sigma-form-card no-padding">
          <div className="card-padding-title">
            <h4 className="form-section-title font-bold">Solicitudes</h4>
          </div>

          {cargando ? (
            <p style={{ padding: '1rem' }}>Cargando solicitudes...</p>
          ) : solicitudes.length === 0 ? (
            <p style={{ padding: '1rem' }}>No hay solicitudes con este filtro.</p>
          ) : (
            <table className="sigma-table">
              <thead>
                <tr>
                  <th>ID Solicitud</th>
                  <th>Estudiante</th>
                  <th>Periodo</th>
                  <th>Fecha de creación</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {solicitudes.map((sol) => {
                  const estadoInfo = ETIQUETAS_ESTADO[sol.estado] || { texto: sol.estado, clase: '' };
                  return (
                    <tr key={sol.id}>
                      <td className="font-medium text-blue-link">MATR-{sol.id}</td>
                      <td>{sol.estudiante_nombre || sol.estudiante}</td>
                      <td>{sol.periodo_matricula_nombre || sol.periodo_matricula}</td>
                      <td>{new Date(sol.created_at).toLocaleString('es-CO')}</td>
                      <td><span className={`badge ${estadoInfo.clase}`}>{estadoInfo.texto}</span></td>
                      <td>
                        <button
                          type="button"
                          className="btn-table-action text-blue-btn"
                          onClick={() => navegar(`/solicitudes/validar-solicitud/${sol.id}`)}
                        >
                          <span className="material-icons-outlined">visibility</span> Ver
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}

          <div className="table-pagination-footer px-24 py-12">
            <span>Mostrando {solicitudes.length} solicitudes</span>
          </div>
        </section>
      </div>

      <aside className="sigma-solicitud-aside">
        <div className="aside-sol-card">
          <h5 className="aside-sol-title font-bold">Resumen</h5>
          <div className="resumen-list margin-top-sm">
            <div className="resumen-row font-medium"><span>Total solicitudes</span><strong>{solicitudes.length}</strong></div>
            <div className="resumen-row font-size-sm"><span className="display-flex-align-center gap-xs"><span className="dot-legend bg-warning"></span> En revisión</span><strong>{totalPendientes}</strong></div>
            <div className="resumen-row font-size-sm"><span className="display-flex-align-center gap-xs"><span className="dot-legend bg-success"></span> Aprobadas</span><strong>{totalAprobadas}</strong></div>
            <div className="resumen-row font-size-sm"><span className="display-flex-align-center gap-xs"><span className="dot-legend bg-danger"></span> Rechazadas</span><strong>{totalRechazadas}</strong></div>
          </div>
        </div>

        <div className="aside-sol-card alert-orange-bg">
          <div className="alert-sol-title">
            <span className="material-icons-outlined text-orange">help_outline</span>
            <strong className="text-orange">Recordatorio</strong>
          </div>
          <p className="font-size-xs text-orange margin-top-xs">
            Las solicitudes "En revisión" requieren tu validación. Haz clic en "Ver" para revisar el detalle y aprobar o rechazar.
          </p>
        </div>
      </aside>
    </div>
  );
}

export default VistaConsultarSolicitud;