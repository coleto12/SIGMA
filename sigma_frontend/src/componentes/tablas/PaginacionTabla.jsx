/**
 * Control de paginación reutilizable para tablas.
 */
function PaginacionTabla({ paginaActual = 1, totalPaginas = 1 }) {
  return (
    <div className="paginacion-tabla">
      <button type="button" aria-label="Página anterior">‹</button>
      {Array.from({ length: totalPaginas }, (_, indice) => indice + 1).map((numero) => (
        <button
          key={numero}
          type="button"
          className={numero === paginaActual ? 'paginacion-tabla__activo' : ''}
        >
          {numero}
        </button>
      ))}
      <button type="button" aria-label="Página siguiente">›</button>
    </div>
  );
}

export default PaginacionTabla;
