import React from 'react';
import './ayuda-soporte.css';

function VistaAyudaSoporte() {
  const faqs = [
    { 
      q: "¿Qué hago si una asignatura no me aparece en la oferta?", 
      a: "Debes comunicarte directamente con el coordinador de tu programa académico para verificar si hay cupos disponibles o si el grupo requiere apertura." 
    },
    { 
      q: "¿Cuánto tiempo tarda la aprobación de mi solicitud?", 
      a: "El Departamento Académico suele revisar y aprobar las solicitudes en un plazo máximo de 48 horas hábiles." 
    },
    { 
      q: "¿Puedo modificar una solicitud que ya fue enviada?", 
      a: "No de forma directa. Si necesitas hacer cambios, debes esperar a que tu departamento genere una observación o rechazo para que se habilite la edición." 
    }
  ];

  return (
    <div className="sigma-solicitud-container no-aside">
      <div className="sigma-solicitud-main">
        <header className="sigma-solicitud-header">
          <h2>Centro de Ayuda y Soporte</h2>
          <p className="margin-top-xs">Resuelve tus dudas sobre el proceso de matrícula o contacta con soporte técnico.</p>
        </header>

        {/* PREGUNTAS FRECUENTES */}
        <section className="sigma-form-card">
          <h4 className="form-section-title font-bold margin-bottom-md">Preguntas frecuentes</h4>
          <div className="faq-container">
            {faqs.map((faq, idx) => (
              <div key={idx} className="faq-item border-bottom-gray pb-12 margin-top-md">
                <strong className="text-slate font-size-sm display-block">¿{faq.q}</strong>
                <p className="text-muted-dark font-size-xs margin-top-xs line-height-md">{faq.a}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CANALES DE ATENCIÓN DIRECTA */}
        <div className="grid-dos-columnas-iguales">
          <section className="sigma-form-card margin-bottom-none">
            <div className="display-flex gap-sm align-center">
              <span className="material-icons-outlined text-blue font-size-lg">email</span>
              <div>
                <strong className="text-slate font-size-sm display-block">Soporte Técnico SIGMA</strong>
                <p className="text-muted-dark font-size-xs margin-top-xs">soporte.sigma@unicartagena.edu.co</p>
              </div>
            </div>
          </section>

          <section className="sigma-form-card margin-bottom-none">
            <div className="display-flex gap-sm align-center">
              <span className="material-icons-outlined text-success font-size-lg">business</span>
              <div>
                <strong className="text-slate font-size-sm display-block">Tu Departamento Académico</strong>
                <p className="text-muted-dark font-size-xs margin-top-xs">Campus Piedra de Bolívar</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

export default VistaAyudaSoporte;