/**
 * Tabla de datos genérica y reutilizable.
 * Usada en Plan de Estudios, Importaciones recientes, Grupos, etc.
 */
function TablaDatos({ columnas = [], filas = [] }) {
  return (
    <table className="tabla-datos">
      <thead>
        <tr>
          {columnas.map((columna) => (
            <th key={columna}>{columna}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {filas.map((fila, indice) => (
          <tr key={indice}>
            {fila.map((celda, indiceCelda) => (
              <td key={indiceCelda}>{celda}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default TablaDatos;
