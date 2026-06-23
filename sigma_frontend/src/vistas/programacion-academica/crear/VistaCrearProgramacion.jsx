import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAutenticacion } from '../../../contexto/ContextoAutenticacion.jsx';
import { obtenerPeriodoAcademicoActivo } from '../../../servicios/servicioAcademico.js';
import {
  obtenerPlanVigente,
  obtenerAsignaturasDelPlan,
} from '../../../servicios/servicioAcademico.js';
import {
  obtenerProgramacionesAcademicas,
  crearProgramacionAcademica,
  crearGrupo,
  editarGrupo,
  eliminarGrupo,
  obtenerGrupos,
  crearHorario,
  editarHorario,
  eliminarHorario,
  obtenerHorarios,
  obtenerSalones,
} from '../../../servicios/servicioProgramacion.js';
import { obtenerDocentes } from '../../../servicios/servicioUsuarios.js';
import './CrearProgramacion.css';

const DIAS_SEMANA = [
  { valor: 'lunes', etiqueta: 'Lunes' },
  { valor: 'martes', etiqueta: 'Martes' },
  { valor: 'miercoles', etiqueta: 'Miércoles' },
  { valor: 'jueves', etiqueta: 'Jueves' },
  { valor: 'viernes', etiqueta: 'Viernes' },
  { valor: 'sabado', etiqueta: 'Sábado' },
];

// ==========================================
// SUB-COMPONENTE: una fila de grupo ya creado, con su gestión de horarios
// ==========================================
function FilaGrupoConHorarios({ grupo, docentes, salones, onEliminarGrupo, eliminandoGrupo, onGrupoActualizado }) {
  const [horarios, setHorarios] = useState([]);
  const [cargandoHorarios, setCargandoHorarios] = useState(true);
  const [formHorario, setFormHorario] = useState({ diaSemana: '', horaInicio: '', horaFin: '', salonId: '' });
  const [guardandoHorario, setGuardandoHorario] = useState(false);
  const [eliminandoHorarioId, setEliminandoHorarioId] = useState(null);
  const [error, setError] = useState('');

  // --- Edición del grupo (docente / cupo) ---
  const [editandoGrupo, setEditandoGrupo] = useState(false);
  const [formGrupoEdicion, setFormGrupoEdicion] = useState({ cupoMaximo: grupo.cupo_maximo, docenteId: grupo.docente });
  const [guardandoGrupo, setGuardandoGrupo] = useState(false);

  // --- Edición de un bloque de horario (cuál id se está editando) ---
  const [horarioEditandoId, setHorarioEditandoId] = useState(null);
  const [formHorarioEdicion, setFormHorarioEdicion] = useState({ diaSemana: '', horaInicio: '', horaFin: '', salonId: '' });
  const [guardandoEdicionHorario, setGuardandoEdicionHorario] = useState(false);

  const cargarHorarios = useCallback(async () => {
    setCargandoHorarios(true);
    try {
      const lista = await obtenerHorarios(grupo.id);
      setHorarios(lista);
    } catch {
      setError('No se pudieron cargar los horarios de este grupo.');
    } finally {
      setCargandoHorarios(false);
    }
  }, [grupo.id]);

  useEffect(() => {
    cargarHorarios();
  }, [cargarHorarios]);

  async function manejarAgregarHorario() {
    if (!formHorario.diaSemana || !formHorario.horaInicio || !formHorario.horaFin || !formHorario.salonId) {
      setError('Completa día, hora de inicio, hora de fin y salón.');
      return;
    }
    setError('');
    setGuardandoHorario(true);
    try {
      const nuevo = await crearHorario({
        grupoId: grupo.id,
        diaSemana: formHorario.diaSemana,
        horaInicio: formHorario.horaInicio,
        horaFin: formHorario.horaFin,
        salonId: Number(formHorario.salonId),
      });
      setHorarios((previo) => [...previo, nuevo]);
      setFormHorario({ diaSemana: '', horaInicio: '', horaFin: '', salonId: '' });
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardandoHorario(false);
    }
  }

  async function manejarEliminarHorario(horarioId) {
    setError('');
    setEliminandoHorarioId(horarioId);
    try {
      await eliminarHorario(horarioId);
      setHorarios((previo) => previo.filter((h) => h.id !== horarioId));
    } catch (err) {
      setError(err.message);
    } finally {
      setEliminandoHorarioId(null);
    }
  }

  function manejarIniciarEdicionGrupo() {
    setFormGrupoEdicion({ cupoMaximo: grupo.cupo_maximo, docenteId: grupo.docente });
    setEditandoGrupo(true);
  }

  async function manejarGuardarEdicionGrupo() {
    setError('');
    setGuardandoGrupo(true);
    try {
      const actualizado = await editarGrupo(grupo.id, {
        cupoMaximo: Number(formGrupoEdicion.cupoMaximo),
        docenteId: Number(formGrupoEdicion.docenteId),
      });
      onGrupoActualizado(actualizado);
      setEditandoGrupo(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardandoGrupo(false);
    }
  }

  function manejarIniciarEdicionHorario(horario) {
    setFormHorarioEdicion({
      diaSemana: horario.dia_semana,
      horaInicio: horario.hora_inicio,
      horaFin: horario.hora_fin,
      salonId: horario.salon,
    });
    setHorarioEditandoId(horario.id);
  }

  async function manejarGuardarEdicionHorario(horarioId) {
    setError('');
    setGuardandoEdicionHorario(true);
    try {
      const actualizado = await editarHorario(horarioId, {
        diaSemana: formHorarioEdicion.diaSemana,
        horaInicio: formHorarioEdicion.horaInicio,
        horaFin: formHorarioEdicion.horaFin,
        salonId: Number(formHorarioEdicion.salonId),
      });
      setHorarios((previo) => previo.map((h) => (h.id === horarioId ? actualizado : h)));
      setHorarioEditandoId(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardandoEdicionHorario(false);
    }
  }

  return (
    <div className="programacion__grupo-detalle" style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.75rem 1rem', marginBottom: '0.75rem' }}>
      <div className="programacion__row-header-meta" style={{ justifyContent: 'space-between', display: 'flex', alignItems: 'center' }}>
        {editandoGrupo ? (
          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <strong>Grupo {grupo.nombre}</strong>
            <select
              value={formGrupoEdicion.docenteId}
              onChange={(e) => setFormGrupoEdicion((p) => ({ ...p, docenteId: e.target.value }))}
              className="programacion__select-tabla"
            >
              {docentes.map((d) => (
                <option key={d.id} value={d.id}>{d.primer_nombre} {d.primer_apellido}</option>
              ))}
            </select>
            <input
              type="number"
              value={formGrupoEdicion.cupoMaximo}
              onChange={(e) => setFormGrupoEdicion((p) => ({ ...p, cupoMaximo: e.target.value }))}
              className="programacion__input-tabla"
              style={{ width: '80px' }}
            />
            <button type="button" className="programacion__btn-agregar-grupo" disabled={guardandoGrupo} onClick={manejarGuardarEdicionGrupo}>
              {guardandoGrupo ? '...' : 'Guardar'}
            </button>
            <button type="button" className="btn-table-action" onClick={() => setEditandoGrupo(false)}>Cancelar</button>
          </div>
        ) : (
          <div>
            <strong>Grupo {grupo.nombre}</strong> — {grupo.docente_nombre} — Cupo {grupo.cupo_disponible}/{grupo.cupo_maximo}
          </div>
        )}
        <div style={{ display: 'flex', gap: '0.3rem' }}>
          {!editandoGrupo && (
            <button type="button" className="btn-table-action" onClick={manejarIniciarEdicionGrupo} title="Editar grupo">
              ✏️
            </button>
          )}
          <button
            type="button"
            className="btn-table-action btn-eliminar"
            disabled={eliminandoGrupo}
            onClick={() => onEliminarGrupo(grupo)}
            title="Eliminar grupo"
          >
            {eliminandoGrupo ? '...' : '🗑️'}
          </button>
        </div>
      </div>

      {error && <p style={{ color: '#c62828', fontSize: '0.85rem', margin: '0.5rem 0' }}>{error}</p>}

      {cargandoHorarios ? (
        <p style={{ fontSize: '0.85rem', margin: '0.5rem 0' }}>Cargando horarios...</p>
      ) : horarios.length > 0 ? (
        <table className="sigma-table" style={{ marginTop: '0.5rem' }}>
          <thead>
            <tr>
              <th>Día</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Salón</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {horarios.map((h) => (
              horarioEditandoId === h.id ? (
                <tr key={h.id}>
                  <td colSpan={5}>
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', padding: '0.4rem 0' }}>
                      <select
                        value={formHorarioEdicion.diaSemana}
                        onChange={(e) => setFormHorarioEdicion((p) => ({ ...p, diaSemana: e.target.value }))}
                        className="programacion__select-tabla"
                      >
                        {DIAS_SEMANA.map((d) => (
                          <option key={d.valor} value={d.valor}>{d.etiqueta}</option>
                        ))}
                      </select>
                      <input
                        type="time"
                        value={formHorarioEdicion.horaInicio}
                        onChange={(e) => setFormHorarioEdicion((p) => ({ ...p, horaInicio: e.target.value }))}
                        className="programacion__input-tabla"
                      />
                      <input
                        type="time"
                        value={formHorarioEdicion.horaFin}
                        onChange={(e) => setFormHorarioEdicion((p) => ({ ...p, horaFin: e.target.value }))}
                        className="programacion__input-tabla"
                      />
                      <select
                        value={formHorarioEdicion.salonId}
                        onChange={(e) => setFormHorarioEdicion((p) => ({ ...p, salonId: e.target.value }))}
                        className="programacion__select-tabla"
                      >
                        {salones.map((s) => (
                          <option key={s.id} value={s.id}>{s.nombre}</option>
                        ))}
                      </select>
                      <button
                        type="button"
                        className="programacion__btn-agregar-grupo"
                        disabled={guardandoEdicionHorario}
                        onClick={() => manejarGuardarEdicionHorario(h.id)}
                      >
                        {guardandoEdicionHorario ? '...' : 'Guardar'}
                      </button>
                      <button type="button" className="btn-table-action" onClick={() => setHorarioEditandoId(null)}>Cancelar</button>
                    </div>
                  </td>
                </tr>
              ) : (
                <tr key={h.id}>
                  <td>{DIAS_SEMANA.find((d) => d.valor === h.dia_semana)?.etiqueta || h.dia_semana}</td>
                  <td>{h.hora_inicio}</td>
                  <td>{h.hora_fin}</td>
                  <td>{h.salon_nombre}</td>
                  <td style={{ display: 'flex', gap: '0.3rem' }}>
                    <button
                      type="button"
                      className="btn-table-action"
                      onClick={() => manejarIniciarEdicionHorario(h)}
                      title="Editar horario"
                    >
                      ✏️
                    </button>
                    <button
                      type="button"
                      className="btn-table-action btn-eliminar"
                      disabled={eliminandoHorarioId === h.id}
                      onClick={() => manejarEliminarHorario(h.id)}
                      title="Eliminar horario"
                    >
                      {eliminandoHorarioId === h.id ? '...' : '✕'}
                    </button>
                  </td>
                </tr>
              )
            ))}
          </tbody>
        </table>
      ) : (
        <p style={{ fontSize: '0.85rem', color: '#64748b', margin: '0.5rem 0' }}>Sin horario definido todavía.</p>
      )}

      <div className="programacion__form-acciones" style={{ flexWrap: 'wrap', marginTop: '0.5rem', gap: '0.4rem' }}>
        <select
          value={formHorario.diaSemana}
          onChange={(e) => setFormHorario((p) => ({ ...p, diaSemana: e.target.value }))}
          className="programacion__select-tabla"
        >
          <option value="">Día</option>
          {DIAS_SEMANA.map((d) => (
            <option key={d.valor} value={d.valor}>{d.etiqueta}</option>
          ))}
        </select>
        <input
          type="time"
          value={formHorario.horaInicio}
          onChange={(e) => setFormHorario((p) => ({ ...p, horaInicio: e.target.value }))}
          className="programacion__input-tabla"
        />
        <input
          type="time"
          value={formHorario.horaFin}
          onChange={(e) => setFormHorario((p) => ({ ...p, horaFin: e.target.value }))}
          className="programacion__input-tabla"
        />
        <select
          value={formHorario.salonId}
          onChange={(e) => setFormHorario((p) => ({ ...p, salonId: e.target.value }))}
          className="programacion__select-tabla"
        >
          <option value="">Salón</option>
          {salones.map((s) => (
            <option key={s.id} value={s.id}>{s.nombre}</option>
          ))}
        </select>
        <button
          type="button"
          className="programacion__btn-agregar-grupo"
          disabled={guardandoHorario}
          onClick={manejarAgregarHorario}
        >
          {guardandoHorario ? 'Guardando...' : '＋ Agregar bloque'}
        </button>
      </div>
    </div>
  );
}

// ==========================================
// VISTA PRINCIPAL
// ==========================================
export default function VistaCrearProgramacion() {
  const navegar = useNavigate();
  const { usuario } = useAutenticacion();

  const [pasoActual, setPasoActual] = useState(1);

  const [periodoAcademico, setPeriodoAcademico] = useState(null);
  const [planEstudio, setPlanEstudio] = useState(null);
  const [filasPlan, setFilasPlan] = useState([]);
  const [docentes, setDocentes] = useState([]);
  const [salones, setSalones] = useState([]);
  const [programacionAcademica, setProgramacionAcademica] = useState(null);
  const [gruposCreados, setGruposCreados] = useState([]);

  const [semestreSeleccionado, setSemestreSeleccionado] = useState(null);
  const [formGrupos, setFormGrupos] = useState({});

  const [cargandoInicial, setCargandoInicial] = useState(true);
  const [error, setError] = useState('');
  const [guardando, setGuardando] = useState(false);
  const [eliminandoId, setEliminandoId] = useState(null);

  useEffect(() => {
    async function inicializar() {
      try {
        const periodo = await obtenerPeriodoAcademicoActivo();
        setPeriodoAcademico(periodo);

        if (!periodo) {
          setCargandoInicial(false);
          return;
        }

        const [plan, listaDocentes, listaSalones, programacionesExistentes] = await Promise.all([
          obtenerPlanVigente(usuario.programa_academico_id),
          obtenerDocentes(),
          obtenerSalones(),
          obtenerProgramacionesAcademicas({ periodo_academico: periodo.id }),
        ]);

        setDocentes(listaDocentes);
        setSalones(listaSalones);

        if (plan) {
          setPlanEstudio(plan);
          const filas = await obtenerAsignaturasDelPlan(plan.id);
          setFilasPlan(filas);
        }

        if (programacionesExistentes.length > 0) {
          const programacion = programacionesExistentes[0];
          setProgramacionAcademica(programacion);
          const grupos = await obtenerGrupos({ programacion_academica: programacion.id });
          setGruposCreados(grupos);
        }
      } catch {
        setError('No se pudo cargar la información necesaria para crear la programación académica.');
      } finally {
        setCargandoInicial(false);
      }
    }
    inicializar();
  }, [usuario]);

  const crearProgramacionSiNoExiste = useCallback(async () => {
    if (programacionAcademica) return programacionAcademica.id;
    if (!periodoAcademico) throw new Error('No hay un periodo académico activo.');
    const nueva = await crearProgramacionAcademica(periodoAcademico.id);
    setProgramacionAcademica(nueva);
    return nueva.id;
  }, [programacionAcademica, periodoAcademico]);

  const semestresDisponibles = [...new Set(filasPlan.map((f) => f.semestre))].sort((a, b) => a - b);
  const asignaturasDelSemestre = filasPlan.filter((f) => f.semestre === semestreSeleccionado);

  function manejarCambioFormGrupo(asignaturaId, campo, valor) {
    setFormGrupos((previo) => ({
      ...previo,
      [asignaturaId]: { ...previo[asignaturaId], [campo]: valor },
    }));
  }

  function gruposCreadosPara(asignaturaId) {
    return gruposCreados.filter((g) => g.asignatura === asignaturaId);
  }

  async function manejarGuardarGrupo(fila) {
    const datosForm = formGrupos[fila.asignatura] || {};
    if (!datosForm.nombre || !datosForm.cupoMaximo || !datosForm.docenteId) {
      setError('Completa nombre de grupo, cupo y docente antes de guardar.');
      return;
    }
    setError('');
    setGuardando(true);
    try {
      const idProgramacion = await crearProgramacionSiNoExiste();
      const nuevoGrupo = await crearGrupo({
        nombre: datosForm.nombre,
        cupoMaximo: Number(datosForm.cupoMaximo),
        programacionAcademicaId: idProgramacion,
        asignaturaId: fila.asignatura,
        docenteId: Number(datosForm.docenteId),
      });
      setGruposCreados((previo) => [...previo, nuevoGrupo]);
      setFormGrupos((previo) => ({ ...previo, [fila.asignatura]: {} }));
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardando(false);
    }
  }

  async function manejarEliminarGrupo(grupo) {
    const confirmado = window.confirm(`¿Eliminar el grupo "${grupo.nombre}" de ${grupo.asignatura_nombre}?`);
    if (!confirmado) return;
    setError('');
    setEliminandoId(grupo.id);
    try {
      await eliminarGrupo(grupo.id);
      setGruposCreados((previo) => previo.filter((g) => g.id !== grupo.id));
    } catch (err) {
      setError(err.message);
    } finally {
      setEliminandoId(null);
    }
  }

  function manejarGrupoActualizado(grupoActualizado) {
    setGruposCreados((previo) =>
      previo.map((g) => (g.id === grupoActualizado.id ? grupoActualizado : g))
    );
  }

  function manejarFinalizar() {
    navegar('/programacion-academica/publicar');
  }

  if (cargandoInicial) {
    return <p style={{ padding: '2rem' }}>Cargando información del plan de estudios...</p>;
  }

  if (!periodoAcademico) {
    return (
      <div className="programacion__tarjeta-blanca" style={{ margin: '2rem' }}>
        <p>No hay un periodo académico activo en este momento.</p>
      </div>
    );
  }

  if (!planEstudio) {
    return (
      <div className="programacion__tarjeta-blanca" style={{ margin: '2rem' }}>
        <p>Tu programa académico aún no tiene un plan de estudios vigente registrado.</p>
      </div>
    );
  }

  return (
    <div className="programacion-container">
      <header className="programacion__header">
        <div className="programacion__header-izq">
          <h2 className="programacion__titulo-vista">Crear Programación Académica</h2>
          <p className="programacion__subtitulo-vista">
            Registra la programación académica para el periodo {periodoAcademico.nombre}.
          </p>
        </div>
        <button className="programacion__btn-volver" type="button" onClick={() => navegar(-1)}>
          ↩ Volver al panel
        </button>
      </header>

      {error && (
        <div className="programacion__alerta-azul" style={{ backgroundColor: '#fbe9e9', borderColor: '#c62828' }}>
          <span className="programacion__alerta-icono">!</span>
          <p style={{ color: '#c62828' }}>{error}</p>
        </div>
      )}

      <section className="programacion__stepper-card">
        <div className="programacion__stepper">
          <div className={`programacion__step ${pasoActual === 1 ? 'programacion__step--active' : ''}`} onClick={() => setPasoActual(1)}>
            <div className="programacion__step-numero">1</div>
            <div className="programacion__step-label">
              <span>Seleccionar</span>
              <strong>Semestre</strong>
            </div>
          </div>
          <div className="programacion__step-flecha">→</div>

          <div className={`programacion__step ${pasoActual === 2 ? 'programacion__step--active' : ''}`} onClick={() => semestreSeleccionado && setPasoActual(2)}>
            <div className="programacion__step-numero">2</div>
            <div className="programacion__step-label">
              <span>Grupos, Docentes</span>
              <strong>y Horarios</strong>
            </div>
          </div>
          <div className="programacion__step-flecha">→</div>

          <div className={`programacion__step ${pasoActual === 3 ? 'programacion__step--active' : ''}`} onClick={() => setPasoActual(3)}>
            <div className="programacion__step-numero">3</div>
            <div className="programacion__step-label">
              <span>Revisar y</span>
              <strong>Finalizar</strong>
            </div>
          </div>
        </div>

        <div className="programacion__periodo-badge-box">
          <span className="programacion__periodo-icono">📅</span>
          <div className="programacion__periodo-info">
            <span className="programacion__periodo-label">Periodo Académico</span>
            <strong className="programacion__periodo-valor">{periodoAcademico.nombre}</strong>
          </div>
        </div>
      </section>

      <div className="programacion__layout-grid">
        <main className="programacion__col-principal">

          {/* PASO 1: Seleccionar semestre */}
          {pasoActual === 1 && (
            <div className="programacion__tarjeta-blanca">
              <h3 className="programacion__tarjeta-titulo">1. Seleccionar Semestre</h3>
              <p className="programacion__tarjeta-sub">
                Elige el semestre de "{planEstudio.nombre}" para el cual deseas crear la programación.
              </p>

              <div className="programacion__alerta-azul">
                <span className="programacion__alerta-icono">i</span>
                <p>Solo se muestran los semestres definidos en tu plan de estudios vigente.</p>
              </div>

              <div className="programacion__form-acciones" style={{ flexWrap: 'wrap', gap: '0.5rem' }}>
                {semestresDisponibles.map((semestre) => (
                  <button
                    key={semestre}
                    type="button"
                    className={semestre === semestreSeleccionado ? 'programacion__btn-continuar' : 'programacion__btn-limpiar'}
                    onClick={() => setSemestreSeleccionado(semestre)}
                  >
                    Semestre {semestre}
                  </button>
                ))}
              </div>

              <div className="programacion__form-acciones">
                <button
                  type="button"
                  className="programacion__btn-continuar"
                  disabled={!semestreSeleccionado}
                  onClick={() => setPasoActual(2)}
                >
                  Continuar →
                </button>
              </div>
            </div>
          )}

          {/* PASO 2: Grupos, docentes y horarios por asignatura del semestre */}
          {pasoActual === 2 && (
            <div className="programacion__tarjeta-blanca">
              <h3 className="programacion__tarjeta-titulo">2. Grupos, Docentes y Horarios — Semestre {semestreSeleccionado}</h3>
              <p className="programacion__tarjeta-sub">
                Crea al menos un grupo con su docente para cada asignatura, y define sus bloques de horario y salón.
              </p>

              {asignaturasDelSemestre.map((fila) => {
                const gruposDeEstaAsignatura = gruposCreadosPara(fila.asignatura);
                const datosForm = formGrupos[fila.asignatura] || {};

                return (
                  <div key={fila.id} className="programacion__asignatura-bloque">
                    <div className="programacion__asignatura-row-header">
                      <div className="programacion__row-header-info">
                        <div>
                          <strong>{fila.asignatura_nombre}</strong>
                          <span className="programacion__codigo-tag">{fila.asignatura_codigo}</span>
                        </div>
                      </div>
                      <div className="programacion__row-header-meta">
                        <div className="programacion__meta-item"><span>Créditos</span><strong>{fila.creditos}</strong></div>
                        <div className="programacion__meta-item"><span>Grupos</span><strong>{gruposDeEstaAsignatura.length}</strong></div>
                      </div>
                    </div>

                    <div style={{ padding: '0.5rem 1rem' }}>
                      {gruposDeEstaAsignatura.map((g) => (
                        <FilaGrupoConHorarios
                          key={g.id}
                          grupo={g}
                          docentes={docentes}
                          salones={salones}
                          onEliminarGrupo={manejarEliminarGrupo}
                          eliminandoGrupo={eliminandoId === g.id}
                          onGrupoActualizado={manejarGrupoActualizado}
                        />
                      ))}
                    </div>

                    <div className="programacion__form-acciones" style={{ flexWrap: 'wrap', padding: '0.75rem 1rem' }}>
                      <input
                        type="text"
                        placeholder="Nombre del grupo (ej. A, B, C...)"
                        value={datosForm.nombre || ''}
                        onChange={(e) => manejarCambioFormGrupo(fila.asignatura, 'nombre', e.target.value)}
                        className="programacion__input-tabla"
                      />
                      <input
                        type="number"
                        placeholder="Cupo máximo"
                        value={datosForm.cupoMaximo || ''}
                        onChange={(e) => manejarCambioFormGrupo(fila.asignatura, 'cupoMaximo', e.target.value)}
                        className="programacion__input-tabla"
                      />
                      <select
                        value={datosForm.docenteId || ''}
                        onChange={(e) => manejarCambioFormGrupo(fila.asignatura, 'docenteId', e.target.value)}
                        className="programacion__select-tabla"
                      >
                        <option value="">Selecciona un docente</option>
                        {docentes.map((d) => (
                          <option key={d.id} value={d.id}>{d.primer_nombre} {d.primer_apellido}</option>
                        ))}
                      </select>
                      <button
                        type="button"
                        className="programacion__btn-agregar-grupo"
                        disabled={guardando}
                        onClick={() => manejarGuardarGrupo(fila)}
                      >
                        {guardando ? 'Guardando...' : gruposDeEstaAsignatura.length > 0 ? '＋ Agregar otro grupo' : '＋ Crear grupo'}
                      </button>
                    </div>
                  </div>
                );
              })}

              <div className="programacion__footer-navegacion-pasos">
                <button type="button" className="programacion__btn-navegacion-atras" onClick={() => setPasoActual(1)}>
                  ← Anterior
                </button>
                <button type="button" className="programacion__btn-navegacion-siguiente" onClick={() => setPasoActual(3)}>
                  Siguiente →
                </button>
              </div>
            </div>
          )}

          {/* PASO 3: Revisar y finalizar */}
          {pasoActual === 3 && (
            <div className="programacion__tarjeta-blanca">
              <h3 className="programacion__tarjeta-titulo">3. Revisar y Finalizar</h3>
              <p className="programacion__tarjeta-sub">
                Resumen de los grupos creados para el semestre {semestreSeleccionado}.
              </p>

              {gruposCreados.length === 0 ? (
                <p>Aún no has creado ningún grupo.</p>
              ) : (
                <table className="sigma-table">
                  <thead>
                    <tr>
                      <th>Asignatura</th>
                      <th>Grupo</th>
                      <th>Docente</th>
                      <th>Cupo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {gruposCreados.map((g) => (
                      <tr key={g.id}>
                        <td>{g.asignatura_codigo} - {g.asignatura_nombre}</td>
                        <td>{g.nombre}</td>
                        <td>{g.docente_nombre}</td>
                        <td>{g.cupo_disponible} / {g.cupo_maximo}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              <div className="programacion__footer-navegacion-pasos">
                <button type="button" className="programacion__btn-navegacion-atras" onClick={() => setPasoActual(2)}>
                  ← Anterior
                </button>
                <button type="button" className="programacion__btn-navegacion-siguiente" onClick={manejarFinalizar}>
                  Ir a Publicar Programación →
                </button>
              </div>
            </div>
          )}

        </main>

        <aside className="programacion__sidebar">
          <div className="programacion__sidebar-card">
            <h4 className="programacion__sidebar-titulo">Resumen del periodo</h4>
            <div className="programacion__sidebar-lista">
              <div className="programacion__sidebar-item"><span>Periodo Académico:</span><strong>{periodoAcademico.nombre}</strong></div>
              <div className="programacion__sidebar-item"><span>Plan de estudios:</span><strong>{planEstudio.nombre}</strong></div>
              <div className="programacion__sidebar-item">
                <span>Estado:</span>
                <span className={`programacion__status-badge ${programacionAcademica?.estado === 'publicada' ? 'programacion__status-badge--verde' : 'programacion__status-badge--amarillo'}`}>
                  {programacionAcademica ? (programacionAcademica.estado === 'publicada' ? 'Publicada' : 'En creación') : 'Aún no creada'}
                </span>
              </div>
              <div className="programacion__sidebar-item"><span>Grupos creados:</span><strong>{gruposCreados.length}</strong></div>
            </div>
          </div>

          <div className="programacion__sidebar-card programacion__sidebar-card--tips">
            <h4 className="programacion__sidebar-titulo"><span style={{ marginRight: '6px' }}>💡</span>Tips</h4>
            <ul className="programacion__tips-list">
              <li>Cada asignatura puede tener varios grupos; vuelve a este semestre para agregar más.</li>
              <li>Cada grupo puede tener varios bloques de horario (ej. lunes y miércoles).</li>
              <li>La programación solo será visible para los estudiantes una vez publicada.</li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}