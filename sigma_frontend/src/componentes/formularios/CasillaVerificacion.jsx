/**
 * Casilla de verificación reutilizable (ej: "Recordar sesión").
 */
function CasillaVerificacion({ etiqueta }) {
  return (
    <label className="casilla-verificacion">
      <input type="checkbox" />
      <span>{etiqueta}</span>
    </label>
  );
}

export default CasillaVerificacion;
