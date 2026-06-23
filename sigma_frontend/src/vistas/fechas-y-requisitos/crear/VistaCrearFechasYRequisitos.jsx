import React, { useEffect, useState, useCallback } from 'react';
import { useAutenticacion } from '../../../contexto/ContextoAutenticacion.jsx';
import { obtenerPeriodoAcademicoActivo } from '../../../servicios/servicioAcademico.js';
import {
  obtenerPeriodoMatriculaDelPeriodoAcademico,
  crearPeriodoMatricula,
  actualizarPeriodoMatricula,
  publicarPeriodoMatricula,
  reabrirPeriodoMatricula,
  obtenerRequisitosDocumentales,
  crearRequisitoDocumental,
  eliminarRequisitoDocumental,
} from '../../../servicios/servicioMatricula.js';
import './crear-fechas-y-requisitos.css';

const FORMATOS = ['PDF', 'JPG', 'PDF/JPG'];

function VistaFechasYRequisitos() {
  const { usuario } = useAutenticacion();

  const [periodoAcademico, setPeriodoAcademico] = useState(null);
  const [periodoMatricula, setPeriodoMatricula] = useState(null);
  const [requisitos, setRequisitos] = useState([]);

  const [fechaInicio, setFechaInicio] = useState('');
  const [fechaFin, setFechaFin] = useState('');

  const [formRequisito, setFormRequisito] = useState({ nombre: '', descripcion: '', formato: 'PDF' });

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');
  const [exito, setExito] = useState('');
  const [guardandoFechas, setGuardandoFechas] = useState(false);
  const [guardandoRequisito, setGuardandoRequisito] = useState(false);
  const [eliminandoId, setEliminandoId] = useState(null);
  const [publicando, setPublicando] = useState(false);

  const cargarDatos = useCallback(async () => {
    setCargando(true);
    setError('');
    try {
      const periodo = await obtenerPeriodoAcademicoActivo();
      setPeriodoAcademico(periodo);
      if (!periodo) return;

      const periodoMat = await obtenerPeriodoMatriculaDelPeriodoAcademico(periodo.id);
      setPeriodoMatricula(periodoMat);

      if (periodoMat) {
        setFechaInicio(periodoMat.fecha_inicio);
        setFechaFin(periodoMat.fecha_fin);
        const listaRequisitos = await obtenerRequisitosDocumentales(periodoMat.id);
        setRequisitos(listaRequisitos);
      }
    } catch {
      setError('No se pudo cargar la información de fechas y requisitos.');
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    cargarDatos();
  }, [cargarDatos]);

  async function manejarGuardarFechas() {
    if (!fechaInicio || !fechaFin) {
      setError('Completa ambas fechas antes de guardar.');
      return;
    }
    if (fechaInicio > fechaFin) {
      setError('La fecha de inicio debe ser anterior a la fecha de fin.');
      return;
    }
    setError('');
    setExito('');
    setGuardandoFechas(true);
    try {
      if (periodoMatricula) {
        const actualizado = await actualizarPeriodoMatricula(periodoMatricula.id, { fechaInicio, fechaFin });
        setPeriodoMatricula(actualizado);
      } else {
        const nuevo = await crearPeriodoMatricula({
          periodoAcademicoId: periodoAcademico.id,
          fechaInicio,
          fechaFin,
        });
        setPeriodoMatricula(nuevo);
      }
      setExito('Las fechas del proceso de matrícula se guardaron correctamente.');
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardandoFechas(false);
    }
  }

  async function manejarAgregarRequisito() {
    if (!periodoMatricula) {
      setError('Primero guarda las fechas del proceso de matrícula.');
      return;
    }
    if (!formRequisito.nombre.trim()) {
      setError('El nombre del documento requerido es obligatorio.');
      return;
    }
    setError('');
    setGuardandoRequisito(true);
    try {
      const nuevo = await crearRequisitoDocumental({
        periodoMatriculaId: periodoMatricula.id,
        nombre: formRequisito.nombre,
        descripcion: formRequisito.descripcion,
        formato: formRequisito.formato,
      });
      setRequisitos((previo) => [...previo, nuevo]);
      setFormRequisito({ nombre: '', descripcion: '', formato: 'PDF' });
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardandoRequisito(false);
    }
  }

  async function manejarEliminarRequisito(requisitoId) {
    const confirmado = window.confirm('¿Eliminar este requisito documental?');
    if (!confirmado) return;
    setError('');
    setEliminandoId(requisitoId);
    try {
      await eliminarRequisitoDocumental(requisitoId);
      setRequisitos((previo) => previo.filter((r) => r.id !== requisitoId));
    } catch (err) {
      setError(err.message);
    } finally {
      setEliminandoId(null);
    }
  }

  async function manejarPublicar() {
    if (!periodoMatricula || requisitos.length === 0) {
      setError('Debes guardar las fechas y al menos un requisito documental antes de publicar.');
      return;
    }
    const confirmado = window.confirm('¿Publicar las fechas y requisitos? Quedarán visibles para los estudiantes.');
    if (!confirmado) return;
    setError('');
    setPublicando(true);
    try {
      const actualizado = await publicarPeriodoMatricula(periodoMatricula.id);
      setPeriodoMatricula(actualizado);
      setExito('Las fechas y requisitos fueron publicados exitosamente.');
    } catch (err) {
      setError(err.message);
    } finally {
      setPublicando(false);
    }
  }

  async function manejarReabrir() {
    const confirmado = window.confirm(
      '¿Reabrir este periodo de matrícula para edición? Los estudiantes ya no podrán enviar nuevas solicitudes hasta que vuelvas a publicarlo con una nueva fecha límite.'
    );
    if (!confirmado) return;
    setError('');
    setExito('');
    setPublicando(true);
    try {
      const actualizado = await reabrirPeriodoMatricula(periodoMatricula.id);
      setPeriodoMatricula(actualizado);
      setExito('El periodo de matrícula fue reabierto. Ya puedes modificar las fechas y los requisitos.');
    } catch (err) {
      setError(err.message);
    } finally {
      setPublicando(false);
    }
  }

  if (cargando) {
    return <p style={{ padding: '2rem' }}>Cargando información del periodo de matrícula...</p>;
  }

  if (!periodoAcademico) {
    return (
      <div className="sigma-card" style={{ margin: '2rem' }}>
        <p>No hay un periodo académico activo en este momento.</p>
      </div>
    );
  }

  const yaPublicado = periodoMatricula?.estado === 'publicado';
  const fechaFinYaPaso = periodoMatricula?.fecha_fin
    ? new Date(periodoMatricula.fecha_fin) < new Date(new Date().toDateString())
    : false;
  const sePuedeReabrir = yaPublicado && fechaFinYaPaso;

  return (
    <div className="sigma-container">
      <div className="sigma-main-content">
        <header className="sigma-view-header">
          <h2>Crear Fechas y Requisitos</h2>
          <p>Establezca las fechas límite y los documentos requeridos para el proceso de matrícula académica.</p>
        </header>

        <div className="sigma-alert sigma-alert-warning">
          <span className="material-icons-outlined">info</span>
          <p>La información configurada será visible para los estudiantes una vez se publique este periodo de matrícula.</p>
        </div>

        {error && (
          <div className="sigma-alert" style={{ backgroundColor: '#fbe9e9' }}>
            <p style={{ color: '#c62828', margin: 0 }}>{error}</p>
          </div>
        )}
        {exito && (
          <div className="sigma-alert" style={{ backgroundColor: '#e6f4ea' }}>
            <p style={{ color: '#1e7d3c', margin: 0 }}>{exito}</p>
          </div>
        )}

        <section className="sigma-card sigma-form-section">
          <div className="sigma-section-title">
            <span className="material-icons-outlined text-gold">calendar_today</span>
            <h3>1. Definir Fechas del Proceso</h3>
          </div>
          <p className="sigma-section-subtitle">
            Configure las fechas del proceso de matrícula para el período {periodoAcademico.nombre}.
          </p>

          <div className="sigma-dates-grid">
            <div className="sigma-date-column">
              <div className="sigma-form-group">
                <label>Fecha de inicio de solicitudes</label>
                <input
                  type="date"
                  value={fechaInicio}
                  onChange={(e) => setFechaInicio(e.target.value)}
                  disabled={yaPublicado}
                />
              </div>
            </div>
            <div className="sigma-date-column">
              <div className="sigma-form-group">
                <label>Fecha límite de solicitudes</label>
                <input
                  type="date"
                  value={fechaFin}
                  onChange={(e) => setFechaFin(e.target.value)}
                  disabled={yaPublicado}
                />
              </div>
            </div>
          </div>

          {!yaPublicado && (
            <div className="sigma-footer-actions" style={{ marginTop: '1rem', borderTop: 'none', paddingTop: 0 }}>
              <button type="button" className="btn-primary" disabled={guardandoFechas} onClick={manejarGuardarFechas}>
                {guardandoFechas ? 'Guardando...' : periodoMatricula ? 'Actualizar fechas' : 'Guardar fechas'}
              </button>
            </div>
          )}
        </section>

        <section className="sigma-card sigma-table-section">
          <div className="sigma-table-header-row">
            <div className="sigma-section-title">
              <span className="material-icons-outlined text-gold">folder</span>
              <h3>2. Definir Requisitos Documentales</h3>
            </div>
          </div>
          <p className="sigma-section-subtitle mb-4">
            Agregue los documentos que los estudiantes deben adjuntar al realizar su solicitud.
          </p>

          <div className="sigma-table-responsive">
            <table className="sigma-custom-table">
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>#</th>
                  <th>Documento requerido</th>
                  <th>Descripción</th>
                  <th>Formato permitido</th>
                  <th style={{ textAlign: 'center' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {requisitos.map((req, index) => (
                  <tr key={req.id}>
                    <td>{index + 1}</td>
                    <td className="fw-medium">{req.nombre}</td>
                    <td className="text-muted">{req.descripcion}</td>
                    <td>{req.formato}</td>
                    <td className="text-center">
                      {!yaPublicado && (
                        <button
                          className="btn-action-delete"
                          title="Eliminar"
                          disabled={eliminandoId === req.id}
                          onClick={() => manejarEliminarRequisito(req.id)}
                        >
                          <span className="material-icons-outlined">delete_outline</span>
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {!yaPublicado && (
            <div className="sigma-form-group" style={{ marginTop: '1rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'flex-end' }}>
              <input
                type="text"
                placeholder="Nombre del documento (ej. Certificado de notas)"
                value={formRequisito.nombre}
                onChange={(e) => setFormRequisito((p) => ({ ...p, nombre: e.target.value }))}
              />
              <input
                type="text"
                placeholder="Descripción"
                value={formRequisito.descripcion}
                onChange={(e) => setFormRequisito((p) => ({ ...p, descripcion: e.target.value }))}
                style={{ flex: 1, minWidth: '200px' }}
              />
              <select
                value={formRequisito.formato}
                onChange={(e) => setFormRequisito((p) => ({ ...p, formato: e.target.value }))}
              >
                {FORMATOS.map((f) => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
              <button type="button" className="sigma-btn-text" disabled={guardandoRequisito} onClick={manejarAgregarRequisito}>
                <span className="material-icons-outlined">add</span> {guardandoRequisito ? 'Guardando...' : 'Agregar requisito'}
              </button>
            </div>
          )}

          <div className="sigma-alert sigma-alert-info mt-4">
            <span className="material-icons-outlined">info</span>
            <p>Los formatos permitidos son: <strong>PDF y JPG</strong>. Asegúrese de que los documentos sean legibles.</p>
          </div>
        </section>

        <div className="sigma-footer-actions">
          <span></span>
          <div className="sigma-footer-right">
            {sePuedeReabrir && (
              <button
                className="btn-aside-outline-blue"
                disabled={publicando}
                onClick={manejarReabrir}
                style={{ marginRight: '0.5rem' }}
              >
                {publicando ? 'Reabriendo...' : 'Reabrir para editar'}
              </button>
            )}
            <button
              className="btn-primary"
              disabled={yaPublicado || publicando || !periodoMatricula || requisitos.length === 0}
              onClick={manejarPublicar}
            >
              {publicando ? 'Publicando...' : yaPublicado ? 'Ya publicado' : 'Publicar fechas y requisitos'}
              <span className="material-icons-outlined">arrow_forward</span>
            </button>
          </div>
        </div>
      </div>

      <aside className="sigma-summary-panel">
        <div className="summary-card">
          <div className="summary-card-row">
            <div className="summary-icon-box">
              <span className="material-icons-outlined">calendar_today</span>
            </div>
            <div>
              <span className="summary-label">Resumen del Período</span>
              <h4 className="summary-main-title">{periodoAcademico.nombre}</h4>
              <p className="summary-sub">{periodoAcademico.fecha_inicio} a {periodoAcademico.fecha_fin}</p>
              <span className="badge-status-creation">
                {yaPublicado ? 'Publicado' : periodoMatricula ? 'En creación' : 'Sin configurar'}
              </span>
            </div>
          </div>
        </div>

        <div className="summary-card">
          <h5 className="summary-block-title">Resumen de fechas</h5>
          <ul className="summary-timeline">
            <li>
              <span className="material-icons-outlined timeline-icon">calendar_month</span>
              <div>
                <strong>Inicio solicitudes</strong>
                <p>{fechaInicio || '—'}</p>
              </div>
            </li>
            <li>
              <span className="material-icons-outlined timeline-icon">calendar_month</span>
              <div>
                <strong>Límite solicitudes</strong>
                <p>{fechaFin || '—'}</p>
              </div>
            </li>
          </ul>
        </div>

        <div className="summary-card alert-summary-blue">
          <div className="summary-card-row align-start">
            <span className="material-icons-outlined text-blue mr-2">info</span>
            <div>
              <strong className="text-blue">Importante</strong>
              <p className="mt-1 text-muted fs-sm">
                Una vez publicado, no podrás modificar las fechas ni los requisitos documentales.
              </p>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}

export default VistaFechasYRequisitos;