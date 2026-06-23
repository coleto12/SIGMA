import React from 'react';
import Tarjeta from '../../componentes/comunes/Tarjeta.jsx';
import ListaDesplegable from '../../componentes/formularios/ListaDesplegable.jsx';
import Boton from '../../componentes/comunes/Boton.jsx';
import './reportes.css';

/**
 * Vista de Reportes: generación de reportes institucionales
 * (matrícula, ocupación de grupos, solicitudes, etc.).
 */
function VistaReportes() {
  const manejarGeneracion = (e) => {
    e.preventDefault();
    console.log("Generando archivo exportable...");
  };

  return (
    <div className="vista-reportes">
      
      {/* Encabezado Principal */}
      <header className="reportes-header">
        <h2>Reportes Estadísticos</h2>
        <p>Genera, consulta y exporta informes consolidados sobre el estado del sistema de matrícula.</p>
      </header>

      {/* Panel de Filtros / Barra de Herramientas */}
      <section className="reportes-toolbar-card">
        <h4 className="toolbar-title">Configuración del Reporte</h4>
        <form onSubmit={manejarGeneracion} className="reportes-toolbar-flex">
          <div className="toolbar-field-grow">
            <ListaDesplegable 
              etiqueta="Tipo de reporte" 
              opciones={['Matrícula por programa', 'Ocupación de grupos', 'Solicitudes por estado']} 
            />
          </div>
          <div className="toolbar-field-shrink">
            <ListaDesplegable 
              etiqueta="Periodo académico" 
              opciones={['2026-1', '2025-2']} 
            />
          </div>
          <div className="toolbar-button-align">
            <Boton tipo="submit" claseEstilo="boton-reporte-ejecutar">
              <span className="material-icons-outlined icon-inside-btn">analytics</span>
              Generar reporte
            </Boton>
          </div>
        </form>
      </section>

      {/* Sección Informativa y Catálogo de Módulos */}
      <h3 className="reportes-section-title">Formatos Disponibles</h3>
      <div className="vista-reportes__tarjetas grid-reportes-cards">
        
        <Tarjeta titulo="Matrícula por programa">
          <div className="report-card-body">
            <span className="material-icons-outlined report-card-icon color-blue">workspace_premium</span>
            <div className="report-card-text">
              <p>Resumen detallado de estudiantes admitidos y matriculados oficialmente por programa académico.</p>
              <span className="file-format-badge">Excel / PDF</span>
            </div>
          </div>
        </Tarjeta>

        <Tarjeta titulo="Ocupación de grupos">
          <div className="report-card-body">
            <span className="material-icons-outlined report-card-icon color-purple">groups</span>
            <div className="report-card-text">
              <p>Porcentaje y métricas de cupos ocupados, disponibles y reservados por grupo y asignatura.</p>
              <span className="file-format-badge">Excel</span>
            </div>
          </div>
        </Tarjeta>

        <Tarjeta titulo="Solicitudes por estado">
          <div className="report-card-body">
            <span className="material-icons-outlined report-card-icon color-amber">stacked_bar_chart</span>
            <div className="report-card-text">
              <p>Distribución en tiempo real de las solicitudes de carga según su estado (Borrador, En revisión, Validada).</p>
              <span className="file-format-badge">PDF</span>
            </div>
          </div>
        </Tarjeta>

      </div>
    </div>
  );
}

export default VistaReportes;