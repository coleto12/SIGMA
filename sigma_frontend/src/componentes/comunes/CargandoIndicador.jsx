/**
 * Indicador de carga reutilizable.
 */
function CargandoIndicador() {
  return (
    <div className="cargando-indicador" role="status" aria-label="Cargando">
      <span className="cargando-indicador__circulo" />
    </div>
  );
}

export default CargandoIndicador;
