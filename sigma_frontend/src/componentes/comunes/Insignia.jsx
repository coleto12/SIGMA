/**
 * Insignia de estado (ej: "Vigente", "Con errores", "Exitosa").
 * estado: "exito" | "error" | "advertencia" | "info"
 */
function Insignia({ texto, estado = 'info' }) {
  return <span className={`insignia insignia--${estado}`}>{texto}</span>;
}

export default Insignia;
