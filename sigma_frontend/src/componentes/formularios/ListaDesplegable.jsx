/**
 * Lista desplegable (select) reutilizable.
 * Usada en filtros como Programa académico, Periodo, Nivel académico.
 */
function ListaDesplegable({ etiqueta, opciones = [] }) {
  return (
    <div className="lista-desplegable">
      {etiqueta && <label className="lista-desplegable__etiqueta">{etiqueta}</label>}
      <select className="lista-desplegable__select">
        {opciones.map((opcion) => (
          <option key={opcion} value={opcion}>
            {opcion}
          </option>
        ))}
      </select>
    </div>
  );
}

export default ListaDesplegable;
