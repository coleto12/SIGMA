import React, { useEffect, useState, useCallback } from 'react';
import { useAutenticacion } from '../../../contexto/ContextoAutenticacion.jsx';
import { obtenerPeriodoAcademicoActivo, obtenerPlanVigente, obtenerAsignaturasDelPlan } from '../../../servicios/servicioAcademico.js';
import { obtenerProgramacionesAcademicas, obtenerGrupos, obtenerHorarios } from '../../../servicios/servicioProgramacion.js';
import './consultar-programacion.css';

const ETIQUETAS_DIA = {
  lunes: 'Lun', martes: 'Mar', miercoles: 'Mié', miércoles: 'Mié',
  jueves: 'Jue', viernes: 'Vie', sabado: 'Sáb', sábado: 'Sáb',
};

function ConsultarProgramacion() {
  const { usuario } = useAutenticacion();

  const [periodoAcademico, setPeriodoAcademico] = useState(null);
  const [planEstudio, setPlanEstudio] = useState(null);
  const [filasPlan, setFilasPlan] = useState([]);
  const [programacionAcademica, setProgramacionAcademica] = useState(null);
  const [grupos, setGrupos] = useState([]);
  const [horariosPorGrupo, setHorariosPorGrupo] = useState({});

  const [semestreSeleccionado, setSemestreSeleccionado] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  const cargarDatos = useCallback(async () => {
    setCargando(true);
    setError('');
    try {
      const periodo = await obtenerPeriodoAcademicoActivo();
      setPeriodoAcademico(periodo);
      if (!periodo) return;

      const plan = await obtenerPlanVigente(usuario.programa_academico_id);
      setPlanEstudio(plan);

      const programaciones = await obtenerProgramacionesAcademicas({ periodo_academico: periodo.id });
      const programacion = programaciones[0] ?? null;
      setProgramacionAcademica(programacion);

      if (plan) {
        const filas = await obtenerAsignaturasDelPlan(plan.id);
        setFilasPlan(filas);
        if (!semestreSeleccionado && filas.length > 0) {
          setSemestreSeleccionado(filas[0].semestre);
        }
      }

      if (programacion) {
        const listaGrupos = await obtenerGrupos({ programacion_academica: programacion.id });
        setGrupos(listaGrupos);

        const horariosTraidos = await Promise.all(
          listaGrupos.map((g) => obtenerHorarios(g.id).then((h) => [g.id, h]))
        );
        setHorariosPorGrupo(Object.fromEntries(horariosTraidos));
      }
    } catch {
      setError('No se pudo cargar la programación académica.');
    } finally {
      setCargando(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usuario]);

  useEffect(() => {
    cargarDatos();
  }, [cargarDatos]);

  const semestresDisponibles = [...new Set(filasPlan.map((f) => f.semestre))].sort((a, b) => a - b);
  const asignaturasDelSemestre = filasPlan.filter((f) => f.semestre === semestreSeleccionado);

  function formatearHorario(grupoId) {
    const horarios = horariosPorGrupo[grupoId] || [];
    if (horarios.length === 0) return 'Sin horario definido';
    return horarios
      .map((h) => `${ETIQUETAS_DIA[h.dia_semana] || h.dia_semana} ${h.hora_inicio}-${h.hora_fin}`)
      .join(', ');
  }

  function gruposDeAsignatura(asignaturaId) {
    return grupos.filter((g) => g.asignatura === asignaturaId);
  }

  const totalGrupos = grupos.length;
  const totalDocentes = new Set(grupos.map((g) => g.docente)).size;

  if (cargando) {
    return <p style={{ padding: '2rem' }}>Cargando programación académica...</p>;
  }

  if (error) {
    return (
      <div className="sigma-card" style={{ margin: '2rem', backgroundColor: '#fbe9e9' }}>
        <p style={{ color: '#c62828', margin: 0 }}>{error}</p>
      </div>
    );
  }

  if (!periodoAcademico) {
    return (
      <div className="sigma-card" style={{ margin: '2rem' }}>
        <p>No hay un periodo académico activo en este momento.</p>
      </div>
    );
  }

  if (!planEstudio) {
    return (
      <div className="sigma-card" style={{ margin: '2rem' }}>
        <p>Tu programa académico aún no tiene un plan de estudios vigente registrado.</p>
      </div>
    );
  }

  return (
    <div className="sigma-consultar-container">
      <div className="sigma-consultar-main">
        <header className="sigma-consultar-header">
          <h2>Consultar Programación Académica</h2>
          <p>Visualice la programación académica creada para el periodo vigente.</p>
        </header>

        <section className="sigma-card sigma-filtros-section">
          <div className="sigma-filtros-grid">
            <div className="sigma-filter-group">
              <label>Periodo Académico</label>
              <select value={periodoAcademico.id} disabled>
                <option value={periodoAcademico.id}>{periodoAcademico.nombre}</option>
              </select>
            </div>
            <div className="sigma-filter-group">
              <label>Plan de estudios</label>
              <select value={planEstudio.id} disabled>
                <option value={planEstudio.id}>{planEstudio.nombre}</option>
              </select>
            </div>
            <div className="sigma-filter-group">
              <label>Semestre</label>
              <select
                value={semestreSeleccionado ?? ''}
                onChange={(e) => setSemestreSeleccionado(Number(e.target.value))}
              >
                {semestresDisponibles.map((s) => (
                  <option key={s} value={s}>{s}° Semestre</option>
                ))}
              </select>
            </div>
          </div>
        </section>

        <section className="sigma-metricas-row">
          <div className="metric-card">
            <div className="metric-icon-box blue-bg">
              <span className="material-icons-outlined">menu_book</span>
            </div>
            <div className="metric-info">
              <span className="metric-label">Asignaturas</span>
              <h3>{asignaturasDelSemestre.length}</h3>
              <p>Del semestre seleccionado</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon-box green-bg">
              <span className="material-icons-outlined">groups</span>
            </div>
            <div className="metric-info">
              <span className="metric-label">Grupos creados</span>
              <h3>{totalGrupos}</h3>
              <p>Total en la programación</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon-box orange-bg">
              <span className="material-icons-outlined">person</span>
            </div>
            <div className="metric-info">
              <span className="metric-label">Docentes asignados</span>
              <h3>{totalDocentes}</h3>
              <p>Distintos en la programación</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon-box purple-bg">
              <span className="material-icons-outlined">{programacionAcademica?.estado === 'publicada' ? 'public' : 'edit_note'}</span>
            </div>
            <div className="metric-info">
              <span className="metric-label">Estado</span>
              <h3 style={{ fontSize: '1.1rem' }}>
                {programacionAcademica ? (programacionAcademica.estado === 'publicada' ? 'Publicada' : 'En creación') : 'Sin crear'}
              </h3>
            </div>
          </div>
        </section>

        <section className="sigma-card sigma-tabla-container">
          <div className="sigma-tabla-top-bar">
            <h4>Programación Académica - {semestreSeleccionado}° Semestre</h4>
          </div>

          <div className="sigma-table-responsive">
            <table className="sigma-programacion-table">
              <thead>
                <tr>
                  <th>Asignatura</th>
                  <th>Código</th>
                  <th>Créditos</th>
                  <th>Grupos</th>
                  <th>Docente(s)</th>
                  <th>Horario(s)</th>
                  <th>Cupo</th>
                </tr>
              </thead>
              <tbody>
                {asignaturasDelSemestre.map((fila) => {
                  const gruposAsig = gruposDeAsignatura(fila.asignatura);
                  return (
                    <tr key={fila.id}>
                      <td className="fw-semibold">
                        <div>{fila.asignatura_nombre}</div>
                        <span className={`badge-asig-status ${gruposAsig.length > 0 ? 'activa' : 'inactiva'}`}>
                          {gruposAsig.length > 0 ? 'Programada' : 'Sin grupos'}
                        </span>
                      </td>
                      <td className="text-dark-mono">{fila.asignatura_codigo}</td>
                      <td>{fila.creditos}</td>
                      <td>{gruposAsig.length}</td>
                      <td className="text-muted-details">
                        {gruposAsig.length === 0
                          ? '—'
                          : gruposAsig.map((g) => `${g.nombre}: ${g.docente_nombre}`).join(' / ')}
                      </td>
                      <td>
                        {gruposAsig.length === 0
                          ? '—'
                          : gruposAsig.map((g) => (
                              <span key={g.id} className="badge-horario" style={{ display: 'block', marginBottom: '2px' }}>
                                {g.nombre}: {formatearHorario(g.id)}
                              </span>
                            ))}
                      </td>
                      <td className="text-dark-mono">
                        {gruposAsig.length === 0
                          ? '—'
                          : gruposAsig.map((g) => `${g.cupo_disponible}/${g.cupo_maximo}`).join(', ')}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <aside className="sigma-consultar-aside">
        <div className="aside-summary-card">
          <div className="aside-summary-row">
            <div className="aside-icon-calendar">
              <span className="material-icons-outlined">calendar_today</span>
            </div>
            <div>
              <span className="aside-card-label">Periodo Académico</span>
              <h4>{periodoAcademico.nombre}</h4>
              <span className="badge-aside-vigente">Activo</span>
            </div>
          </div>
          <p className="aside-card-date mt-3">{periodoAcademico.fecha_inicio} a {periodoAcademico.fecha_fin}</p>
        </div>

        <div className="aside-summary-card">
          <h5 className="aside-block-title">Leyenda</h5>
          <ul className="aside-leyenda-list">
            <li>
              <span className="badge-asig-status activa inline-badge">Programada</span>
              <p>Asignatura con al menos un grupo creado</p>
            </li>
            <li>
              <span className="badge-asig-status inactiva inline-badge">Sin grupos</span>
              <p>Asignatura del plan sin grupos creados aún</p>
            </li>
          </ul>
        </div>

        <div className="aside-summary-card info-blue-bg">
          <div className="info-title-row">
            <span className="material-icons-outlined text-blue">info</span>
            <strong className="text-blue">Información</strong>
          </div>
          <p className="info-card-text">
            Esta es la programación que verán los estudiantes una vez sea publicada por el departamento.
          </p>
        </div>
      </aside>
    </div>
  );
}

export default ConsultarProgramacion;