import React, { useState } from 'react';
import './realizar-solicitud.css';

// ==========================================
// SUB-COMPONENTE: SELECCIONAR ASIGNATURAS (PASO 1)
// ==========================================
function SeleccionarAsignaturasPaso1() {
  const asignaturas = [
    { id: 1, nombre: 'Cálculo Integral', codigo: 'MAT102', creditos: 4, grupo: '2', horario: 'Lun - Mié 08:00 - 12:00', aula: 'A-201, A-202', estado: 'Disponible', checked: true },
    { id: 2, nombre: 'Física Mecánica', codigo: 'FIS101', creditos: 4, grupo: '2', horario: 'Mar - Jue 08:00 - 12:00', aula: 'B-103, B-104', estado: 'Disponible', checked: true },
    { id: 3, nombre: 'Programación I', codigo: 'PROG101', creditos: 3, grupo: '3', horario: 'Lun - Mié 14:00 - 18:00', aula: 'Lab 1, Lab 2, Lab 3', estado: 'Disponible', checked: true },
    { id: 4, nombre: 'Álgebra Lineal', codigo: 'ALG101', creditos: 3, grupo: '2', horario: 'Mar - Jue 14:00 - 16:00', aula: 'A-203, A-204', estado: 'Disponible', checked: false },
    { id: 5, nombre: 'Estructuras Discretas', codigo: 'SIS202', creditos: 3, grupo: '2', horario: 'Vie 08:00 - 12:00', aula: 'A-205, A-206', estado: 'Disponible', checked: true },
    { id: 6, nombre: 'Base de Datos', codigo: 'SIS203', creditos: 3, grupo: '2', horario: 'Vie 14:00 - 18:00', aula: 'Lab 4, Lab 5', estado: 'Disponible', checked: false },
  ];

  return (
    <div className="sigma-form-card no-padding">
      <div className="card-padding-title display-flex-space">
        <h4 className="form-section-title font-bold">Asignaturas disponibles</h4>
        <span className="credits-indicator text-success-bold">Créditos seleccionados: <strong className="badge-credits-status">13 de 18</strong></span>
      </div>
      <p className="form-section-subtitle px-24">Selecciona las asignaturas que deseas cursar.</p>

      <table className="sigma-table margin-top-sm">
        <thead>
          <tr>
            <th width="40"><input type="checkbox" /></th>
            <th>Asignatura</th>
            <th>Código</th>
            <th>Créditos</th>
            <th>Grupo(s)</th>
            <th>Horario</th>
            <th>Aula</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {asignaturas.map((asig) => (
            <tr key={asig.id}>
              <td><input type="checkbox" defaultChecked={asig.checked} /></td>
              <td><strong>{asig.nombre}</strong></td>
              <td className="text-muted-dark">{asig.codigo}</td>
              <td>{asig.creditos}</td>
              <td>{asig.grupo}</td>
              <td className="horario-cell">{asig.horario}</td>
              <td>{asig.aula}</td>
              <td><span className="badge badge-success">{asig.estado}</span></td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Leyendas de estado inferiores */}
      <div className="table-legends px-24 py-16">
        <span className="legend-item"><span className="circle-legend bg-success"></span> Disponible</span>
        <span className="legend-item"><span className="circle-legend bg-warning"></span> Cupo limitado</span>
        <span className="legend-item"><span className="circle-legend bg-danger"></span> No disponible</span>
      </div>
    </div>
  );
}

// ==========================================
// COMPONENTE CONTENEDOR PRINCIPAL
// ==========================================
function VistaRealizarSolicitud() {
  const [paso, setPaso] = useState(1);

  return (
    <div className="sigma-solicitud-container">
      {/* CUERPO CENTRAL */}
      <div className="sigma-solicitud-main">
        <header className="sigma-solicitud-header">
          <h2>Realizar Solicitud de Matrícula</h2>
          <p>Selecciona las asignaturas que deseas cursar en el período académico y envía tu solicitud.</p>
        </header>

        {/* STEPPER SUPERIOR GENERAL */}
        <section className="sigma-form-card padding-sm">
          <div className="solicitud-stepper">
            <div className={`sol-step ${paso === 1 ? 'active' : 'completed'}`}>
              <span className="sol-step-num">1</span>
              <span className="sol-step-text">Seleccionar asignaturas</span>
            </div>
            <div className="sol-step-line"></div>
            <div className="sol-step disabled">
              <span className="sol-step-num">2</span>
              <span className="sol-step-text">Validar requisitos</span>
            </div>
            <div className="sol-step-line"></div>
            <div className="sol-step disabled">
              <span className="sol-step-num">3</span>
              <span className="sol-step-text">Resumen de solicitud</span>
            </div>
            <div className="sol-step-line"></div>
            <div className="sol-step disabled">
              <span className="sol-step-num">4</span>
              <span className="sol-step-text">Confirmación de envío</span>
            </div>
          </div>
        </section>

        {/* BANNER DE INFORMACIÓN IMPORTANTE */}
        <div className="instructions-box alert-blue-bg margin-bottom-md">
          <div className="alert-sol-title">
            <span className="material-icons-outlined text-blue">info</span>
            <strong className="text-blue">Información importante</strong>
          </div>
          <p className="alert-sol-text text-blue margin-top-xs">
            Verifica cuidadosamente tu selección de asignaturas. Una vez enviada la solicitud, será revisada por tu departamento académico.
          </p>
        </div>

        {/* INFORMACIÓN DEL PERÍODO */}
        <section className="sigma-form-card grid-info-periodo">
          <div>
            <span className="info-label">Período académico</span>
            <p className="info-value">2026-1 (14 enero - 30 mayo 2026)</p>
          </div>
          <div>
            <span className="info-label">Programa académico</span>
            <p className="info-value">Ingeniería de Sistemas</p>
          </div>
          <div>
            <span className="info-label">Semestre a cursar</span>
            <p className="info-value">V Semestre</p>
          </div>
          <div>
            <span className="info-label">Estado del estudiante</span>
            <p className="info-value"><span className="badge badge-success">Activo</span></p>
          </div>
        </section>

        {/* CONTENIDO DEL PASO (SUBCOMPONENTE) */}
        {paso === 1 && <SeleccionarAsignaturasPaso1 />}

        {/* ACCIONES INFERIORES */}
        <footer className="form-actions-footer margin-top-lg">
          <button type="button" className="btn-sol-cancelar">Cancelar</button>
          <div className="action-buttons">
            <button type="button" className="btn-sol-siguiente">
              Siguiente <span className="material-icons-outlined">arrow_forward</span>
            </button>
          </div>
        </footer>
      </div>

      {/* PANEL ASIDE LATERAL DERECHO */}
      <aside className="sigma-solicitud-aside">
        
        {/* CARD 1: RESUMEN SELECCIÓN */}
        <div className="aside-sol-card">
          <h5 className="aside-sol-title font-bold">Resumen de tu selección</h5>
          <div className="resumen-list margin-top-sm">
            <div className="resumen-row"><span>Asignaturas seleccionadas</span><strong>4</strong></div>
            <div className="resumen-row"><span>Créditos totales</span><strong>13</strong></div>
            <div className="resumen-row"><span>Créditos máximos permitidos</span><strong>18</strong></div>
            <div className="resumen-row"><span>Créditos mínimos requeridos</span><strong>12</strong></div>
          </div>
          
          <div className="alert-inner-blue margin-top-md">
            <span className="material-icons-outlined text-blue font-size-md">info</span>
            <div className="alert-inner-content">
              <strong className="text-blue font-size-sm">Estás dentro del rango permitido</strong>
              <p className="text-blue font-size-xs">Puedes continuar con tu solicitud.</p>
            </div>
          </div>
        </div>

        {/* CARD 2: DETALLES GRÁFICOS */}
        <div className="aside-sol-card text-center">
          <h5 className="aside-sol-title text-left font-bold">Detalles de créditos</h5>
          <div className="radial-progress-container margin-top-md">
            {/* Simulación del gráfico radial */}
            <div className="circle-progress-mock">
              <div className="circle-inner-text">
                <span className="inner-number">13</span>
                <span className="inner-subtext">de 18</span>
              </div>
            </div>
          </div>
          <div className="radial-legends margin-top-md">
            <span className="radial-legend-item"><span className="dot-legend bg-success"></span> Seleccionados: 13</span>
            <span className="radial-legend-item"><span className="dot-legend bg-gray-light"></span> Disponibles: 5</span>
          </div>
        </div>

        {/* CARD 3: REQUISITOS VERIFICADOS */}
        <div className="aside-sol-card">
          <h5 className="aside-sol-title font-bold">Requisitos verificados</h5>
          <div className="requisitos-checklist margin-top-sm">
            <div className="req-check-item">
              <div className="check-left"><span className="material-icons-outlined text-success">check_circle</span> Académicos</div>
              <span className="badge badge-success">Cumple</span>
            </div>
            <div className="req-check-item">
              <div className="check-left"><span className="material-icons-outlined text-success">check_circle</span> Financieros</div>
              <span className="badge badge-success">Cumple</span>
            </div>
            <div className="req-check-item">
              <div className="check-left"><span className="material-icons-outlined text-success">check_circle</span> Disciplinarios</div>
              <span className="badge badge-success">Cumple</span>
            </div>
            <div className="req-check-item">
              <div className="check-left"><span className="material-icons-outlined text-success">check_circle</span> Documentos</div>
              <span className="badge badge-success">Cumple</span>
            </div>
          </div>
        </div>

        {/* CARD 4: BOTÓN INFERIOR DE DUDAS */}
        <div className="aside-sol-card alert-orange-bg">
          <div className="alert-sol-title">
            <span className="material-icons-outlined text-orange">help_outline</span>
            <strong className="text-orange">¿Dudas sobre tu matrícula?</strong>
          </div>
          <p className="font-size-xs text-orange margin-top-xs">Consulta las fechas y requisitos del proceso en la sección correspondiente.</p>
          <button type="button" className="btn-aside-outline-blue margin-top-md">
            <span className="material-icons-outlined">calendar_today</span> Ir a Fechas y Requisitos
          </button>
        </div>

      </aside>
    </div>
  );
}

export default VistaRealizarSolicitud;