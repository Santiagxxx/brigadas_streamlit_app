from __future__ import annotations

from typing import Dict, List

from modules.constants import REGION_OPTIONS


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def validate_submission(payload: Dict[str, object]) -> List[str]:
    errors: List[str] = []

    codigo = _clean_text(payload.get("codigo_mca"))
    nombre = _clean_text(payload.get("nombre_mca"))
    region = _clean_text(payload.get("region")).upper()

    if not codigo:
        errors.append("El campo CODIGO MCA es obligatorio.")
    if not nombre:
        errors.append("El campo NOMBRE MCA es obligatorio.")
    if not region:
        errors.append("El campo REGION es obligatorio.")
    elif region not in REGION_OPTIONS:
        errors.append("REGION debe ser una de las opciones habilitadas del formulario.")

    try:
        brigadas = int(payload.get("brigadas_realizadas", 0))
    except (TypeError, ValueError):
        brigadas = 0
    if brigadas not in (1, 2):
        errors.append("BRIGADAS REALIZADAS debe ser 1 o 2, porque el formato tiene columnas para Brigada 1 y Brigada 2.")

    for field, label in [
        ("personas_brigada_1", "# PERSONAS BRIGADA 1"),
        ("personas_brigada_2", "# PERSONAS BRIGADA 2"),
    ]:
        try:
            value = int(payload.get(field, 0))
        except (TypeError, ValueError):
            errors.append(f"{label} debe ser un número entero.")
            continue
        if value < 0:
            errors.append(f"{label} no puede ser negativo.")

    if brigadas == 1 and int(payload.get("personas_brigada_2", 0) or 0) > 0:
        errors.append("Si solo se realizó 1 brigada, el campo # PERSONAS BRIGADA 2 debe quedar en 0.")

    return errors
