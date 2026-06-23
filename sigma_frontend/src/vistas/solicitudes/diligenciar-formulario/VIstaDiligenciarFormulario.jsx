import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAutenticacion } from '../../../contexto/ContextoAutenticacion.jsx';
import { obtenerPeriodoAcademicoActivo, obtenerPlanVigente, obtenerAsignaturasDelPlan, obtenerHistorialAcademico, obtenerPrerrequisitos } from '../../../servicios/servicioAcademico.js';
import { obtenerGrupos, obtenerHorarios } from '../../../servicios/servicioProgramacion.js';
import {
  obtenerPeriodoMatriculaPublicado,
  obtenerRequisitosDocumentales,
  crearSolicitud,
  obtenerSolicitudesMatricula,
  obtenerAsignaturasDeSolicitud,
  agregarAsignaturaASolicitud,
  quitarAsignaturaDeSolicitud,
  obtenerDocumentosDeSolicitud,
  subirDocumentoAdjunto,
  confirmarEnvioSolicitud,
} from '../../../servicios/servicioMatricula.js';
import './diligenciar-formulario.css';

const DIAS_ABREVIADOS = {
  lunes: 'Lun', martes: 'Mar', miercoles: 'Mié',
  jueves: 'Jue', viernes: 'Vie', sabado: 'Sáb',
};

function formatearHorarios(horarios) {
  if (!horarios || horarios.length === 0) return 'Sin horario definido';
  return horarios
    .map((h) => `${DIAS_ABREVIADOS[h.dia_semana] || h.dia_semana} ${h.hora_inicio}-${h.hora_fin} (${h.salon_nombre})`)
    .join(', ');
}

// ==========================================
// SUB-COMPONENTE 1: SELECCIONAR ASIGNATURAS (PASO 1)
// ==========================================
function SeleccionarAsignaturasPaso({ solicitud, onSolicitudCreada, asignaturasSeleccionadas, onCambioAsignaturas, bloqueado }) {
  const { usuario } = useAutenticacion();
  const [grupos, setGrupos] = useState([]);
  const [horariosPorGrupo, setHorariosPorGrupo] = useState({});
  const [semestrePorAsignaturaId, setSemestrePorAsignaturaId] = useState({});
  const [creditosPorAsignaturaId, setCreditosPorAsignaturaId] = useState({});
  const [asignaturasAprobadas, setAsignaturasAprobadas] = useState(new Set());
  const [prerrequisitosPorAsignaturaId, setPrerrequisitosPorAsignaturaId] = useState({});
  const [semestreSeleccionado, setSemestreSeleccionado] = useState('todos');
  const [cargando, setCargando] = useState(true);
  const [procesandoGrupoId, setProcesandoGrupoId] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    async function cargar() {
      try {
        const [listaGrupos, plan, historial] = await Promise.all([
          obtenerGrupos(),
          obtenerPlanVigente(usuario.programa_academico_id),
          obtenerHistorialAcademico(),
        ]);
        setGrupos(listaGrupos);

        // Asignaturas ya aprobadas (no se pueden volver a matricular,
        // ver Modelo de Negocio 4.3.2).
        const aprobadas = new Set(
          historial.filter((h) => h.estado === 'aprobada').map((h) => h.asignatura)
        );
        setAsignaturasAprobadas(aprobadas);

        // Trae el horario real de cada grupo (día/hora/salón), para que
        // el estudiante pueda ver de una vez si dos grupos se cruzan,
        // antes incluso de intentar seleccionarlos.
        const entradasHorarios = await Promise.all(
          listaGrupos.map((g) => obtenerHorarios(g.id).then((h) => [g.id, h]))
        );
        setHorariosPorGrupo(Object.fromEntries(entradasHorarios));

        // Prerrequisitos de cada asignatura única ofrecida, para poder
        // inhabilitar de antemano las que el estudiante no cumple (ver
        // CU19: "el sistema inhabilita en tiempo real las asignaturas
        // para las que el Estudiante no cumple prerrequisitos").
        const idsAsignaturasUnicas = [...new Set(listaGrupos.map((g) => g.asignatura))];
        const entradasPrereqs = await Promise.all(
          idsAsignaturasUnicas.map((idAsig) => obtenerPrerrequisitos(idAsig).then((p) => [idAsig, p]))
        );
        setPrerrequisitosPorAsignaturaId(Object.fromEntries(entradasPrereqs));

        // Cruza cada asignatura con su semestre y créditos reales dentro
        // del plan de estudios vigente del estudiante.
        if (plan) {
          const filasPlan = await obtenerAsignaturasDelPlan(plan.id);
          const mapaSemestre = {};
          const mapaCreditos = {};
          filasPlan.forEach((fila) => {
            mapaSemestre[fila.asignatura] = fila.semestre;
            mapaCreditos[fila.asignatura] = fila.creditos;
          });
          setSemestrePorAsignaturaId(mapaSemestre);
          setCreditosPorAsignaturaId(mapaCreditos);
        }
      } catch {
        setError('No se pudo cargar la oferta de grupos disponible.');
      } finally {
        setCargando(false);
      }
    }
    cargar();
  }, [usuario]);

  const idsSeleccionados = new Set(asignaturasSeleccionadas.map((a) => a.grupo));

  // Calcula, para un grupo dado, el motivo por el cual el estudiante NO
  // puede seleccionarlo (null si sí puede). Se evalúa preventivamente,
  // antes de que el estudiante intente marcarlo (ver CU19, requisito
  // especial de inhabilitar en tiempo real).
  function motivoNoElegible(grupo) {
    if (asignaturasAprobadas.has(grupo.asignatura)) {
      return 'Ya aprobaste esta asignatura';
    }
    const prerrequisitos = prerrequisitosPorAsignaturaId[grupo.asignatura] || [];
    const prerreqFaltante = prerrequisitos.find(
      (p) => !asignaturasAprobadas.has(p.asignatura_prerrequisito)
    );
    if (prerreqFaltante) {
      return `Requiere "${prerreqFaltante.asignatura_prerrequisito_codigo}" aprobada`;
    }
    // Cruce de horario con algo ya seleccionado en esta solicitud.
    const horariosDeEsteGrupo = horariosPorGrupo[grupo.id] || [];
    for (const otraSel of asignaturasSeleccionadas) {
      if (otraSel.grupo === grupo.id) continue;
      const horariosOtro = horariosPorGrupo[otraSel.grupo] || [];
      for (const hNuevo of horariosDeEsteGrupo) {
        for (const hOtro of horariosOtro) {
          if (hNuevo.dia_semana !== hOtro.dia_semana) continue;
          if (hNuevo.hora_inicio < hOtro.hora_fin && hOtro.hora_inicio < hNuevo.hora_fin) {
            return 'Se cruza con otra asignatura ya seleccionada';
          }
        }
      }
    }
    // Límite de créditos (ver validación real en el backend; este es
    // solo el aviso preventivo en el frontend).
    const MAXIMO_CREDITOS = 12;
    const creditosDeEsteGrupo = creditosPorAsignaturaId[grupo.asignatura] ?? 0;
    const creditosYaSeleccionados = asignaturasSeleccionadas.reduce((suma, sel) => {
      const g = grupos.find((gr) => gr.id === sel.grupo);
      return suma + (g ? (creditosPorAsignaturaId[g.asignatura] ?? 0) : 0);
    }, 0);
    if (creditosYaSeleccionados + creditosDeEsteGrupo > MAXIMO_CREDITOS) {
      return `Superarías el máximo de ${MAXIMO_CREDITOS} créditos`;
    }
    return null;
  }

  async function alternarSeleccion(grupo) {
    if (bloqueado) return;
    setError('');
    const yaSeleccionado = idsSeleccionados.has(grupo.id);

    if (yaSeleccionado) {
      const item = asignaturasSeleccionadas.find((a) => a.grupo === grupo.id);
      setProcesandoGrupoId(grupo.id);
      try {
        await quitarAsignaturaDeSolicitud(item.id);
        onCambioAsignaturas(asignaturasSeleccionadas.filter((a) => a.id !== item.id));
      } catch (err) {
        setError(err.message);
      } finally {
        setProcesandoGrupoId(null);
      }
      return;
    }

    setProcesandoGrupoId(grupo.id);
    try {
      const idSolicitud = solicitud?.id ?? (await onSolicitudCreada());
      const nuevaAsignatura = await agregarAsignaturaASolicitud(idSolicitud, grupo.id);
      onCambioAsignaturas([...asignaturasSeleccionadas, nuevaAsignatura]);
    } catch (err) {
      setError(err.message);
    } finally {
      setProcesandoGrupoId(null);
    }
  }

  // Agrupa los grupos disponibles por el semestre real de su asignatura
  // dentro del plan de estudios (los que no se encuentren en el plan,
  // p.ej. electivas sin semestre fijo, caen en "Sin semestre asignado").
  const semestresDisponibles = [...new Set(Object.values(semestrePorAsignaturaId))].sort((a, b) => a - b);
  const gruposFiltrados = semestreSeleccionado === 'todos'
    ? grupos
    : grupos.filter((g) => semestrePorAsignaturaId[g.asignatura] === Number(semestreSeleccionado));

  const gruposPorSemestre = {};
  gruposFiltrados.forEach((grupo) => {
    const semestre = semestrePorAsignaturaId[grupo.asignatura] ?? 'Sin semestre asignado';
    if (!gruposPorSemestre[semestre]) gruposPorSemestre[semestre] = [];
    gruposPorSemestre[semestre].push(grupo);
  });
  const semestresOrdenados = Object.keys(gruposPorSemestre).sort((a, b) => {
    if (a === 'Sin semestre asignado') return 1;
    if (b === 'Sin semestre asignado') return -1;
    return Number(a) - Number(b);
  });

  const MAXIMO_CREDITOS = 12;
  const totalCreditosSeleccionados = asignaturasSeleccionadas.reduce((suma, sel) => {
    const grupoCorrespondiente = grupos.find((g) => g.id === sel.grupo);
    const creditos = grupoCorrespondiente ? (creditosPorAsignaturaId[grupoCorrespondiente.asignatura] ?? 0) : 0;
    return suma + creditos;
  }, 0);

  return (
    <div className="sigma-form-card no-padding">
      <div className="card-padding-title display-flex-space">
        <h4 className="form-section-title font-bold">Grupos disponibles</h4>
        <span className="credits-indicator text-success-bold">
          Asignaturas seleccionadas: <strong className="badge-credits-status">{asignaturasSeleccionadas.length}</strong>
          {' '}— Créditos:{' '}
          <strong
            className="badge-credits-status"
            style={{ backgroundColor: totalCreditosSeleccionados > MAXIMO_CREDITOS ? '#fbe9e9' : undefined, color: totalCreditosSeleccionados > MAXIMO_CREDITOS ? '#c62828' : undefined }}
          >
            {totalCreditosSeleccionados}/{MAXIMO_CREDITOS}
          </strong>
        </span>
      </div>
      <p className="form-section-subtitle px-24">Selecciona los grupos que deseas cursar.</p>

      <div className="px-24" style={{ paddingBottom: '0.75rem' }}>
        <label style={{ fontSize: '0.85rem', fontWeight: 600, marginRight: '0.5rem' }}>Filtrar por semestre:</label>
        <select value={semestreSeleccionado} onChange={(e) => setSemestreSeleccionado(e.target.value)}>
          <option value="todos">Todos los semestres</option>
          {semestresDisponibles.map((s) => (
            <option key={s} value={s}>{s}° semestre</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="instructions-box alert-blue-bg margin-bottom-md" style={{ margin: '0 24px 16px', backgroundColor: '#fbe9e9' }}>
          <p style={{ margin: 0, color: '#c62828', fontSize: '0.85rem' }}>{error}</p>
        </div>
      )}

      {cargando ? (
        <p className="px-24" style={{ paddingBottom: '1rem' }}>Cargando oferta disponible...</p>
      ) : grupos.length === 0 ? (
        <p className="px-24" style={{ paddingBottom: '1rem' }}>No hay grupos disponibles en este momento.</p>
      ) : (
        semestresOrdenados.map((semestre) => (
          <div key={semestre} style={{ marginBottom: '1.25rem' }}>
            <h5 className="px-24" style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1f4e5f', margin: '0.5rem 0' }}>
              {semestre === 'Sin semestre asignado' ? semestre : `${semestre}° Semestre`}
            </h5>
            <table className="sigma-table margin-top-sm">
              <thead>
                <tr>
                  <th width="40"></th>
                  <th>Asignatura</th>
                  <th>Código</th>
                  <th>Grupo</th>
                  <th>Docente</th>
                  <th>Horario</th>
                  <th>Cupo disponible</th>
                </tr>
              </thead>
              <tbody>
                {gruposPorSemestre[semestre].map((grupo) => {
                  const seleccionado = idsSeleccionados.has(grupo.id);
                  const procesando = procesandoGrupoId === grupo.id;
                  const motivoBloqueo = !seleccionado ? motivoNoElegible(grupo) : null;
                  const checkboxDeshabilitado = bloqueado || procesando || !!motivoBloqueo;
                  return (
                    <tr key={grupo.id} style={motivoBloqueo ? { opacity: 0.55 } : undefined}>
                      <td>
                        <input
                          type="checkbox"
                          checked={seleccionado}
                          disabled={checkboxDeshabilitado}
                          title={motivoBloqueo || ''}
                          onChange={() => alternarSeleccion(grupo)}
                        />
                      </td>
                      <td><strong>{grupo.asignatura_nombre}</strong></td>
                      <td className="text-muted-dark">{grupo.asignatura_codigo}</td>
                      <td>{grupo.nombre}</td>
                      <td>{grupo.docente_nombre}</td>
                      <td className="text-muted-dark" style={{ fontSize: '0.8rem' }}>
                        {formatearHorarios(horariosPorGrupo[grupo.id])}
                      </td>
                      <td>
                        {motivoBloqueo ? (
                          <span className="badge badge-danger" style={{ fontSize: '0.7rem' }}>{motivoBloqueo}</span>
                        ) : (
                          <span className={`badge ${grupo.cupo_disponible > 0 ? 'badge-success' : 'badge-danger'}`}>
                            {grupo.cupo_disponible > 0 ? `${grupo.cupo_disponible} disponibles` : 'Sin cupo'}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ))
      )}
    </div>
  );
}

// ==========================================
// SUB-COMPONENTE 2: ADJUNTAR DOCUMENTOS (PASO 2)
// ==========================================
function AdjuntarDocumentosPaso({ solicitud, periodoMatricula, bloqueado }) {
  const [requisitos, setRequisitos] = useState([]);
  const [documentos, setDocumentos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [subiendoId, setSubiendoId] = useState(null);
  const [error, setError] = useState('');

  const cargarDatos = useCallback(async () => {
    if (!periodoMatricula || !solicitud) return;
    setCargando(true);
    try {
      const [listaRequisitos, listaDocumentos] = await Promise.all([
        obtenerRequisitosDocumentales(periodoMatricula.id),
        obtenerDocumentosDeSolicitud(solicitud.id),
      ]);
      setRequisitos(listaRequisitos);
      setDocumentos(listaDocumentos);
    } catch {
      setError('No se pudieron cargar los requisitos documentales.');
    } finally {
      setCargando(false);
    }
  }, [periodoMatricula, solicitud]);

  useEffect(() => {
    cargarDatos();
  }, [cargarDatos]);

  async function manejarSeleccionArchivo(requisito, evento) {
    const archivo = evento.target.files?.[0];
    if (!archivo) return;
    setError('');
    setSubiendoId(requisito.id);
    try {
      await subirDocumentoAdjunto({
        solicitudMatriculaId: solicitud.id,
        requisitoDocumentalId: requisito.id,
        archivo,
      });
      await cargarDatos();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubiendoId(null);
      evento.target.value = '';
    }
  }

  function documentoAdjuntadoPara(requisitoId) {
    return documentos.find((d) => d.requisito_documental === requisitoId);
  }

  if (!solicitud) {
    return (
      <div className="instructions-box alert-blue-bg">
        <p className="text-blue" style={{ margin: 0 }}>
          Primero selecciona al menos una asignatura en el paso anterior.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="instructions-box alert-blue-bg">
        <div className="alert-sol-title">
          <span className="material-icons-outlined text-blue">info</span>
          <strong className="text-blue">Instrucciones</strong>
        </div>
        <ul className="instructions-list text-blue">
          <li>Adjunta los documentos solicitados en los formatos permitidos.</li>
          <li>Asegúrate de que los documentos sean legibles y estén completos.</li>
        </ul>
      </div>

      {error && (
        <div className="instructions-box margin-bottom-md" style={{ backgroundColor: '#fbe9e9' }}>
          <p style={{ margin: 0, color: '#c62828', fontSize: '0.85rem' }}>{error}</p>
        </div>
      )}

      <div className="sigma-form-card no-padding">
        <div className="card-padding-title">
          <h4 className="form-section-title">Documentos requeridos</h4>
        </div>
        {cargando ? (
          <p className="px-24" style={{ paddingBottom: '1rem' }}>Cargando requisitos...</p>
        ) : requisitos.length === 0 ? (
          <p className="px-24" style={{ paddingBottom: '1rem' }}>
            El Jefe de Departamento aún no ha definido requisitos documentales para este periodo.
          </p>
        ) : (
          <table className="sigma-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Documento requerido</th>
                <th>Descripción</th>
                <th>Formato</th>
                <th>Estado</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              {requisitos.map((requisito, indice) => {
                const documento = documentoAdjuntadoPara(requisito.id);
                const subiendo = subiendoId === requisito.id;
                return (
                  <tr key={requisito.id}>
                    <td>{indice + 1}</td>
                    <td><strong>{requisito.nombre}</strong></td>
                    <td>{requisito.descripcion}</td>
                    <td>{requisito.formato}</td>
                    <td>
                      <span className={`badge ${documento ? 'badge-success' : 'badge-warning'}`}>
                        {documento ? 'Adjuntado' : 'Pendiente'}
                      </span>
                    </td>
                    <td>
                      <label className={`btn-table-action ${documento ? 'text-blue-btn' : 'btn-upload-blue'}`} style={{ cursor: (subiendo || bloqueado) ? 'not-allowed' : 'pointer', opacity: bloqueado ? 0.5 : 1 }}>
                        <span className="material-icons-outlined">{documento ? 'cached' : 'upload'}</span>
                        {subiendo ? 'Subiendo...' : documento ? 'Reemplazar' : 'Adjuntar'}
                        <input
                          type="file"
                          accept=".pdf,.jpg,.jpeg,.png"
                          style={{ display: 'none' }}
                          disabled={subiendo || bloqueado}
                          onChange={(e) => manejarSeleccionArchivo(requisito, e)}
                        />
                      </label>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}

// ==========================================
// VISTA CONTENEDORA PRINCIPAL
// ==========================================
function VistaDiligenciarFormulario() {
  const navegar = useNavigate();
  const { usuario } = useAutenticacion();

  const [paso, setPaso] = useState(1);
  const [periodoAcademico, setPeriodoAcademico] = useState(null);
  const [periodoMatricula, setPeriodoMatricula] = useState(null);
  const [solicitud, setSolicitud] = useState(null);
  const [asignaturas, setAsignaturas] = useState([]);
  const [cargandoInicial, setCargandoInicial] = useState(true);
  const [errorInicial, setErrorInicial] = useState('');
  const [confirmandoEnvio, setConfirmandoEnvio] = useState(false);

  // Carga el contexto general (periodo activo, periodo de matrícula) y,
  // si el Estudiante ya tiene una solicitud pendiente para este periodo,
  // la reutiliza en lugar de forzar a crear una nueva.
  useEffect(() => {
    async function inicializar() {
      try {
        const [periodoAct, periodoMat] = await Promise.all([
          obtenerPeriodoAcademicoActivo(),
          obtenerPeriodoMatriculaPublicado(),
        ]);
        setPeriodoAcademico(periodoAct);
        setPeriodoMatricula(periodoMat);

        if (periodoMat) {
          const solicitudesExistentes = await obtenerSolicitudesMatricula({
            periodo_matricula: periodoMat.id,
            estado: 'pendiente_revision',
          });
          if (solicitudesExistentes.length > 0) {
            const solicitudActual = solicitudesExistentes[0];
            setSolicitud(solicitudActual);
            const asignaturasExistentes = await obtenerAsignaturasDeSolicitud(solicitudActual.id);
            setAsignaturas(asignaturasExistentes);
          }
        }
      } catch {
        setErrorInicial('No se pudo cargar la información del periodo de matrícula.');
      } finally {
        setCargandoInicial(false);
      }
    }
    inicializar();
  }, []);

  // Crea la SolicitudMatricula en segundo plano la primera vez que el
  // Estudiante selecciona una asignatura (ver decisión de diseño: no hay
  // un botón "iniciar solicitud" separado, se crea de forma transparente).
  async function crearSolicitudSiNoExiste() {
    if (solicitud) return solicitud.id;
    if (!periodoMatricula) throw new Error('No hay un periodo de matrícula publicado actualmente.');
    const nuevaSolicitud = await crearSolicitud(usuario.estudiante_id, periodoMatricula.id);
    setSolicitud(nuevaSolicitud);
    return nuevaSolicitud.id;
  }

  async function manejarConfirmarEnvio() {
    if (!solicitud) return;
    const confirmado = window.confirm(
      'Una vez confirmes el envío, no podrás modificar las asignaturas ni los documentos hasta que el Jefe de Departamento revise tu solicitud. ¿Confirmas el envío?'
    );
    if (!confirmado) return;
    setErrorInicial('');
    setConfirmandoEnvio(true);
    try {
      const actualizada = await confirmarEnvioSolicitud(solicitud.id);
      setSolicitud(actualizada);
      navegar('/solicitudes/consultar-estado-solicitud');
    } catch (err) {
      setErrorInicial(err.message);
    } finally {
      setConfirmandoEnvio(false);
    }
  }

  if (cargandoInicial) {
    return <p className="px-24" style={{ padding: '2rem' }}>Cargando información de matrícula...</p>;
  }

  if (errorInicial) {
    return (
      <div className="instructions-box" style={{ backgroundColor: '#fbe9e9', margin: '2rem' }}>
        <p style={{ margin: 0, color: '#c62828' }}>{errorInicial}</p>
      </div>
    );
  }

  if (!periodoMatricula) {
    return (
      <div className="instructions-box alert-blue-bg" style={{ margin: '2rem' }}>
        <p className="text-blue" style={{ margin: 0 }}>
          El Jefe de Departamento aún no ha publicado el periodo de matrícula. Vuelve a intentarlo más tarde.
        </p>
      </div>
    );
  }

  return (
    <div className="sigma-solicitud-container">
      <div className="sigma-solicitud-main">
        <header className="sigma-solicitud-header">
          <h2>{paso === 1 ? 'Seleccionar Asignaturas' : paso === 2 ? 'Adjuntar Documentos' : 'Confirmación de envío'}</h2>
          <p>
            {paso === 1
              ? 'Selecciona los grupos que deseas cursar en el periodo vigente.'
              : paso === 2
              ? 'Adjunta los documentos requeridos para completar tu solicitud de matrícula académica.'
              : 'Revisa el resumen de tu solicitud antes de finalizar.'}
          </p>
        </header>

        <section className="sigma-form-card padding-sm">
          <div className="solicitud-stepper">
            <div className={`sol-step ${paso === 1 ? 'active' : 'completed'}`}>
              <span className="sol-step-num">{paso > 1 ? '✓' : '1'}</span>
              <span className="sol-step-text">Asignaturas</span>
            </div>
            <div className="sol-step-line"></div>
            <div className={`sol-step ${paso === 2 ? 'active' : paso > 2 ? 'completed' : 'disabled'}`}>
              <span className="sol-step-num">{paso > 2 ? '✓' : '2'}</span>
              <span className="sol-step-text">Documentos</span>
            </div>
            <div className="sol-step-line"></div>
            <div className={`sol-step ${paso === 3 ? 'active' : 'disabled'}`}>
              <span className="sol-step-num">3</span>
              <span className="sol-step-text">Confirmación</span>
            </div>
          </div>
        </section>

        <div className="form-solicitud-body">
          {solicitud?.enviada_formalmente && (
            <div className="instructions-box" style={{ backgroundColor: '#fff8e1', marginBottom: '1rem' }}>
              <p style={{ margin: 0, color: '#9a6700' }}>
                Ya enviaste formalmente esta solicitud. No puedes modificar las asignaturas ni los documentos
                hasta que el Jefe de Departamento la revise.
              </p>
            </div>
          )}

          {errorInicial && (
            <div className="instructions-box" style={{ backgroundColor: '#fbe9e9', marginBottom: '1rem' }}>
              <p style={{ margin: 0, color: '#c62828' }}>{errorInicial}</p>
            </div>
          )}

          {paso === 1 && (
            <SeleccionarAsignaturasPaso
              solicitud={solicitud}
              onSolicitudCreada={crearSolicitudSiNoExiste}
              asignaturasSeleccionadas={asignaturas}
              onCambioAsignaturas={setAsignaturas}
              bloqueado={!!solicitud?.enviada_formalmente}
            />
          )}
          {paso === 2 && (
            <AdjuntarDocumentosPaso solicitud={solicitud} periodoMatricula={periodoMatricula} bloqueado={!!solicitud?.enviada_formalmente} />
          )}
          {paso === 3 && (
            <div className="sigma-form-card">
              <h4 className="form-section-title">Resumen de tu solicitud</h4>
              <p>Solicitud #{solicitud?.id} — {asignaturas.length} asignatura(s) seleccionada(s).</p>
              <p className="text-muted-dark">
                Una vez confirmes, tu solicitud quedará <strong>enviada formalmente</strong> y ya no
                podrás modificar las asignaturas ni los documentos hasta que el Jefe de Departamento
                la revise. Podrás consultar su avance desde "Consultar estado".
              </p>
            </div>
          )}

          <footer className="form-actions-footer">
            {paso > 1 ? (
              <button type="button" className="btn-sol-cancelar" onClick={() => setPaso(paso - 1)}>
                ← Anterior
              </button>
            ) : (
              <span className="required-legend">Selecciona al menos una asignatura para continuar</span>
            )}

            <div className="action-buttons">
              <button type="button" className="btn-sol-cancelar" onClick={() => navegar(-1)}>Cancelar</button>
              {paso < 3 ? (
                <button
                  type="button"
                  className="btn-sol-siguiente"
                  disabled={paso === 1 && asignaturas.length === 0}
                  onClick={() => setPaso(paso + 1)}
                >
                  Siguiente <span className="material-icons-outlined">arrow_forward</span>
                </button>
              ) : (
                <button
                  type="button"
                  className="btn-sol-siguiente"
                  onClick={manejarConfirmarEnvio}
                  disabled={confirmandoEnvio || !!solicitud?.enviada_formalmente}
                >
                  {confirmandoEnvio ? 'Enviando...' : solicitud?.enviada_formalmente ? 'Ya enviada' : 'Confirmar y enviar'}
                  <span className="material-icons-outlined">check</span>
                </button>
              )}
            </div>
          </footer>
        </div>
      </div>

      <aside className="sigma-solicitud-aside">
        <div className="aside-sol-card alert-blue-bg">
          <div className="alert-sol-title">
            <span className="material-icons-outlined text-blue">info</span>
            <strong className="text-blue">Información importante</strong>
          </div>
          <p className="aside-sol-text">La información será verificada por tu departamento académico.</p>
        </div>

        <div className="aside-sol-card">
          <h5 className="aside-sol-title">Estado de la solicitud</h5>
          <div className="vertical-stepper">
            <div className={`v-step ${paso === 1 ? 'v-step-in-progress' : 'v-step-completed'}`}>
              <div className="v-step-circle">{paso > 1 ? '✓' : '1'}</div>
              <div className="v-step-content">
                <p className="v-step-title-text">Asignaturas</p>
                <p className="v-step-status-tag">{paso === 1 ? 'En progreso' : 'Completado'}</p>
              </div>
            </div>
            <div className={`v-step ${paso === 2 ? 'v-step-in-progress' : paso > 2 ? 'v-step-completed' : 'v-step-pending'}`}>
              <div className="v-step-circle">{paso > 2 ? '✓' : '2'}</div>
              <div className="v-step-content">
                <p className="v-step-title-text">Documentos</p>
                <p className="v-step-status-tag">{paso === 2 ? 'En progreso' : paso > 2 ? 'Completado' : 'Pendiente'}</p>
              </div>
            </div>
            <div className={`v-step ${paso === 3 ? 'v-step-in-progress' : 'v-step-pending'}`}>
              <div className="v-step-circle">3</div>
              <div className="v-step-content">
                <p className="v-step-title-text">Confirmación</p>
                <p className="v-step-status-tag">{paso === 3 ? 'En progreso' : 'Pendiente'}</p>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}

export default VistaDiligenciarFormulario;