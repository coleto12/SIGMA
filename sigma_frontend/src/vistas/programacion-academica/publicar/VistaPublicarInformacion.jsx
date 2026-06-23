import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAutenticacion } from '../../../contexto/ContextoAutenticacion.jsx';
import { obtenerPeriodoAcademicoActivo, obtenerPlanVigente, obtenerAsignaturasDelPlan } from '../../../servicios/servicioAcademico.js';
import {
  obtenerProgramacionesAcademicas,
  obtenerGrupos,
  publicarProgramacionAcademica,
} from '../../../servicios/servicioProgramacion.js';
import { obtenerPeriodoMatriculaPublicado, obtenerRequisitosDocumentales } from '../../../servicios/servicioMatricula.js';
import './publicar-informacion.css';

function VistaPublicarInformacion() {
  const navegar = useNavigate();
  const { usuario } = useAutenticacion();

  const [periodoAcademico, setPeriodoAcademico] = useState(null);
  const [planEstudio, setPlanEstudio] = useState(null);
  const [filasPlan, setFilasPlan] = useState([]);
  const [programacionAcademica, setProgramacionAcademica] = useState(null);
  const [grupos, setGrupos] = useState([]);
  const [periodoMatricula, setPeriodoMatricula] = useState(null);
  const [requisitosDocumentales, setRequisitosDocumentales] = useState([]);

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');
  const [publicando, setPublicando] = useState(false);
  const [publicadoExitosamente, setPublicadoExitosamente] = useState(false);

  const cargarDatos = useCallback(async () => {
    setCargando(true);
    setError('');
    try {
      const periodo = await obtenerPeriodoAcademicoActivo();
      setPeriodoAcademico(periodo);
      if (!periodo) return;

      const [plan, programaciones, periodoMat] = await Promise.all([
        obtenerPlanVigente(usuario.programa_academico_id),
        obtenerProgramacionesAcademicas({ periodo_academico: periodo.id }),
        obtenerPeriodoMatriculaPublicado(),
      ]);

      setPlanEstudio(plan);
      setPeriodoMatricula(periodoMat);

      const programacion = programaciones[0] ?? null;
      setProgramacionAcademica(programacion);

      if (plan) {
        const filas = await obtenerAsignaturasDelPlan(plan.id);
        setFilasPlan(filas);
      }

      if (programacion) {
        const listaGrupos = await obtenerGrupos({ programacion_academica: programacion.id });
        setGrupos(listaGrupos);
      }

      if (periodoMat) {
        const requisitos = await obtenerRequisitosDocumentales(periodoMat.id);
        setRequisitosDocumentales(requisitos);
      }
    } catch {
      setError('No se pudo cargar la información de la programación académica.');
    } finally {
      setCargando(false);
    }
  }, [usuario]);

  useEffect(() => {
    cargarDatos();
  }, [cargarDatos]);

  // -----------------------------------------------------------------
  // Cálculo de la checklist de verificación, basado en datos REALES.
  // -----------------------------------------------------------------
  const totalAsignaturasPlan = filasPlan.length;
  const idsConGrupo = new Set(grupos.map((g) => g.asignatura));
  const asignaturasSinGrupo = filasPlan.filter((f) => !idsConGrupo.has(f.asignatura));
  const asignaturasCompletas = totalAsignaturasPlan - asignaturasSinGrupo.length;

  const totalGrupos = grupos.length;
  const totalDocentes = new Set(grupos.map((g) => g.docente)).size;

  const tieneFechasYRequisitos = !!periodoMatricula;
  const tieneRequisitosDocumentales = requisitosDocumentales.length > 0;
  const todasAsignaturasConGrupo = totalAsignaturasPlan > 0 && asignaturasSinGrupo.length === 0;
  const yaPublicada = programacionAcademica?.estado === 'publicada';

  const listaParaPublicar =
    !!programacionAcademica &&
    !yaPublicada &&
    todasAsignaturasConGrupo &&
    tieneFechasYRequisitos &&
    tieneRequisitosDocumentales;

  async function manejarPublicar() {
    if (!listaParaPublicar) return;
    const confirmado = window.confirm(
      'Una vez publicada, la programación no podrá ser modificada sin la intervención de un administrador. ¿Confirmas la publicación?'
    );
    if (!confirmado) return;

    setPublicando(true);
    setError('');
    try {
      const actualizada = await publicarProgramacionAcademica(programacionAcademica.id);
      setProgramacionAcademica(actualizada);
      setPublicadoExitosamente(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setPublicando(false);
    }
  }

  if (cargando) {
    return <p style={{ padding: '2rem' }}>Cargando información de la programación académica...</p>;
  }

  if (!periodoAcademico) {
    return (
      <div className="sigma-card-publicar" style={{ margin: '2rem' }}>
        <p>No hay un periodo académico activo en este momento.</p>
      </div>
    );
  }

  if (!programacionAcademica) {
    return (
      <div className="sigma-card-publicar" style={{ margin: '2rem' }}>
        <p>Todavía no has creado ninguna programación académica para este periodo.</p>
        <button type="button" className="btn-publish-now" onClick={() => navegar('/programacion-academica/crear')}>
          Ir a Crear Programación
        </button>
      </div>
    );
  }

  return (
    <div className="sigma-publicar-container">
      <div className="sigma-publicar-main">
        <header className="sigma-publicar-header">
          <h2>Publicar Programación Académica</h2>
          <p>Revise la información de la programación académica y publíquela para que esté disponible para los estudiantes.</p>
        </header>

        {error && (
          <div className="sigma-card-publicar" style={{ backgroundColor: '#fbe9e9' }}>
            <p style={{ color: '#c62828', margin: 0 }}>{error}</p>
          </div>
        )}

        {publicadoExitosamente && (
          <div className="sigma-card-publicar" style={{ backgroundColor: '#e6f4ea' }}>
            <p style={{ color: '#1e7d3c', margin: 0, fontWeight: 600 }}>
              ✓ La programación académica fue publicada exitosamente. Ya está disponible para los estudiantes.
            </p>
          </div>
        )}

        <section className="sigma-card-publicar">
          <h3 className="section-title">1. Resumen de la Programación</h3>
          <div className="resumen-prog-grid">
            <div>
              <p className="resumen-label">Periodo Académico:</p>
              <p className="resumen-value">{periodoAcademico.nombre}</p>
            </div>
            <div>
              <p className="resumen-label">Fecha de creación:</p>
              <p className="resumen-value">{new Date(programacionAcademica.created_at ?? Date.now()).toLocaleString('es-CO')}</p>
            </div>
            <div>
              <p className="resumen-label">Programa Académico:</p>
              <p className="resumen-value">{planEstudio?.nombre}</p>
            </div>
            <div>
              <p className="resumen-label">Estado actual:</p>
              <p className="resumen-value">{yaPublicada ? 'Publicada' : 'No publicada'}</p>
            </div>
          </div>
        </section>

        <section className="sigma-card-publicar">
          <h3 className="section-title">2. Resumen de Asignaturas Programadas</h3>

          <div className="metricas-publicar-grid">
            <div className="metrica-item border-blue">
              <span className="material-icons-outlined metrica-icon color-blue">menu_book</span>
              <div>
                <p className="metrica-title">Asignaturas</p>
                <p className="metrica-number">{asignaturasCompletas} / {totalAsignaturasPlan}</p>
                <p className="metrica-sub">Con al menos un grupo</p>
              </div>
            </div>
            <div className="metrica-item border-green">
              <span className="material-icons-outlined metrica-icon color-green">groups</span>
              <div>
                <p className="metrica-title">Grupos</p>
                <p className="metrica-number">{totalGrupos}</p>
                <p className="metrica-sub">Total creados</p>
              </div>
            </div>
            <div className="metrica-item border-orange">
              <span className="material-icons-outlined metrica-icon color-orange">person</span>
              <div>
                <p className="metrica-title">Docentes</p>
                <p className="metrica-number">{totalDocentes}</p>
                <p className="metrica-sub">Total asignados</p>
              </div>
            </div>
          </div>

          {asignaturasSinGrupo.length > 0 && (
            <>
              <h4 className="table-inner-title">Asignaturas sin grupo creado ({asignaturasSinGrupo.length})</h4>
              <div className="table-responsive">
                <table className="table-publicar">
                  <thead>
                    <tr>
                      <th>Asignatura</th>
                      <th>Código</th>
                      <th>Semestre</th>
                    </tr>
                  </thead>
                  <tbody>
                    {asignaturasSinGrupo.map((f) => (
                      <tr key={f.id}>
                        <td className="fw-semibold text-dark">{f.asignatura_nombre}</td>
                        <td className="font-mono text-muted">{f.asignatura_codigo}</td>
                        <td>{f.semestre}°</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </section>

        <footer className="action-bar-footer">
          <button type="button" className="btn-back" onClick={() => navegar('/programacion-academica/crear')}>
            <span className="material-icons-outlined">arrow_back</span> Volver a crear programación
          </button>
          <div className="right-actions">
            <button
              type="button"
              className="btn-publish-now"
              disabled={!listaParaPublicar || publicando}
              onClick={manejarPublicar}
            >
              {publicando ? 'Publicando...' : yaPublicada ? 'Ya publicada' : 'Publicar ahora'}
              <span className="material-icons-outlined">send</span>
            </button>
          </div>
        </footer>
      </div>

      <aside className="sigma-publicar-aside">
        <div className={`aside-card ${listaParaPublicar ? 'border-left-green' : 'border-left-amber'}`}>
          <p className="aside-label">Estado de publicación</p>
          <div className="status-row">
            <span className={listaParaPublicar ? 'dot-green' : 'dot-amber'}></span>
            <h4>{yaPublicada ? 'Publicada' : listaParaPublicar ? 'Lista para publicar' : 'Faltan requisitos'}</h4>
          </div>
          <p className="aside-desc-text">
            {yaPublicada
              ? 'Esta programación ya está publicada y visible para los estudiantes.'
              : listaParaPublicar
              ? 'La programación cumple todos los requisitos y está lista para ser publicada.'
              : 'Completa los puntos pendientes de la lista de verificación antes de publicar.'}
          </p>
        </div>

        <div className="aside-card">
          <h5 className="aside-block-title">Verificación previa</h5>
          <ul className="checklist-verify">
            <li>
              <span className={`material-icons-outlined ${todasAsignaturasConGrupo ? 'check-success' : 'check-pending'}`}>
                {todasAsignaturasConGrupo ? 'check_circle' : 'radio_button_unchecked'}
              </span>
              <span className="check-text">Asignaturas con grupo</span>
              <span className="check-count">{asignaturasCompletas} de {totalAsignaturasPlan}</span>
            </li>
            <li>
              <span className={`material-icons-outlined ${tieneFechasYRequisitos ? 'check-success' : 'check-pending'}`}>
                {tieneFechasYRequisitos ? 'check_circle' : 'radio_button_unchecked'}
              </span>
              <span className="check-text">Fechas del proceso de matrícula</span>
              <span className="check-badge-ok">{tieneFechasYRequisitos ? 'Configuradas' : 'Pendiente'}</span>
            </li>
            <li>
              <span className={`material-icons-outlined ${tieneRequisitosDocumentales ? 'check-success' : 'check-pending'}`}>
                {tieneRequisitosDocumentales ? 'check_circle' : 'radio_button_unchecked'}
              </span>
              <span className="check-text">Requisitos documentales</span>
              <span className="check-count">{requisitosDocumentales.length} documentos</span>
            </li>
          </ul>
        </div>

        <div className="aside-card alert-info-box">
          <div className="alert-title-row">
            <span className="material-icons-outlined">info</span>
            <strong>Información importante</strong>
          </div>
          <p className="alert-body-text">
            Una vez publicada, la programación será visible para los estudiantes y podrán iniciar su proceso de solicitud de matrícula.
          </p>
          <p className="alert-body-text-sub">
            No podrás realizar cambios mientras esté publicada, salvo intervención de un administrador.
          </p>
        </div>
      </aside>
    </div>
  );
}

export default VistaPublicarInformacion;