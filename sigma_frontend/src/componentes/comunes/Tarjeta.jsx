/**
 * Contenedor tipo tarjeta reutilizable, usado en paneles
 * de la vista de inicio, recomendaciones y tipos de información.
 */
function Tarjeta({ titulo, children }) {
  return (
    <div className="tarjeta">
      {titulo && <h3 className="tarjeta__titulo">{titulo}</h3>}
      <div className="tarjeta__contenido">{children}</div>
    </div>
  );
}

export default Tarjeta;
