/**
 * Zona de arrastrar y soltar archivos (usada en Carga de Información Académica).
 * Solo vista: el área visual de "Arrastra y suelta tu archivo CSV aquí".
 */
function ZonaArrastrarArchivo() {
  return (
    <div className="zona-arrastrar-archivo">
      <span className="zona-arrastrar-archivo__icono" />
      <p className="zona-arrastrar-archivo__texto">Arrastra y suelta tu archivo CSV aquí</p>
      <p className="zona-arrastrar-archivo__texto-secundario">o haz clic para seleccionarlo desde tu dispositivo</p>
      <button type="button" className="boton boton--secundario">
        Seleccionar archivo
      </button>
      <p className="zona-arrastrar-archivo__formatos">Formatos soportados: .csv · Tamaño máximo: 5MB</p>
    </div>
  );
}

export default ZonaArrastrarArchivo;
