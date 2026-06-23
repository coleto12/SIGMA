/**
 * Campo de texto/contraseña/correo reutilizable con etiqueta e ícono.
 */
function CampoTexto({ etiqueta, tipo = 'text', marcadorPosicion, icono }) {
  return (
    <div className="campo-texto">
      {etiqueta && <label className="campo-texto__etiqueta">{etiqueta}</label>}
      <div className="campo-texto__contenedor">
        {icono && <span className={`campo-texto__icono campo-texto__icono--${icono}`} />}
        <input className="campo-texto__input" type={tipo} placeholder={marcadorPosicion} />
      </div>
    </div>
  );
}

export default CampoTexto;
