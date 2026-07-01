from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.constants import REGION_OPTIONS
from modules.db import (
    count_records,
    delete_all_records,
    get_recent_records,
    get_records_for_export,
    init_db,
    insert_submission,
)
from modules.excel_export import EXPORT_FILE_NAME, build_excel_bytes
from modules.validation import validate_submission

st.set_page_config(
    page_title="Formulario Brigadas",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
.block-container { padding-top: 1.6rem; padding-bottom: 2rem; }
[data-testid="stMetric"] { background: #f8fafc; border: 1px solid #e5e7eb; padding: 14px; border-radius: 14px; }
.small-note { color: #64748b; font-size: 0.92rem; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

init_db()


def get_admin_password() -> str:
    try:
        secret_password = st.secrets.get("ADMIN_PASSWORD", "")
    except Exception:
        secret_password = ""
    return secret_password or os.environ.get("ADMIN_PASSWORD", "admin123")


@st.cache_data(ttl=20, show_spinner=False)
def cached_export_excel(total_records_version: int) -> bytes:
    # total_records_version invalida caché cuando cambia la cantidad de registros.
    records = get_records_for_export()
    return build_excel_bytes(records)


def normalize_code(value: str) -> str:
    return " ".join(value.strip().upper().split())


def render_form_page() -> None:
    st.title("Formulario de Brigadas")
    st.caption("La información diligenciada queda almacenada y el administrador puede descargarla en el formato Excel original.")

    brigadas_realizadas = st.selectbox(
        "BRIGADAS REALIZADAS *",
        options=[1, 2],
        index=0,
        help="Al seleccionar 2, se habilita el campo # PERSONAS BRIGADA 2.",
    )

    with st.form("brigadas_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            codigo_mca = st.text_input("CODIGO MCA *", placeholder="Ejemplo: MCA001")
            personas_brigada_1 = st.number_input("# PERSONAS BRIGADA 1 *", min_value=0, step=1, value=0)
        with col2:
            nombre_mca = st.text_input("NOMBRE MCA *", placeholder="Nombre del MCA")
            region = st.selectbox(
                "REGION *",
                options=["", *REGION_OPTIONS],
                index=0,
                format_func=lambda option: "Selecciona una región" if option == "" else option,
            )
            if brigadas_realizadas == 2:
                personas_brigada_2 = st.number_input("# PERSONAS BRIGADA 2 *", min_value=0, step=1, value=0)
            else:
                personas_brigada_2 = 0
                st.number_input("# PERSONAS BRIGADA 2", min_value=0, step=1, value=0, disabled=True)
                st.caption("Este campo se habilita cuando seleccionas 2 en BRIGADAS REALIZADAS.")

        submitted = st.form_submit_button("Guardar información", type="primary", use_container_width=True)

    if submitted:
        payload = {
            "codigo_mca": normalize_code(codigo_mca),
            "nombre_mca": nombre_mca.strip(),
            "brigadas_realizadas": int(brigadas_realizadas),
            "personas_brigada_1": int(personas_brigada_1),
            "personas_brigada_2": int(personas_brigada_2),
            "region": str(region).strip(),
        }
        errors = validate_submission(payload)
        if errors:
            for error in errors:
                st.error(error)
        else:
            row_id = insert_submission(payload)
            st.cache_data.clear()
            st.success(f"Registro guardado correctamente. ID interno: {row_id}")


def render_admin_page() -> None:
    st.title("Panel de administración")
    st.caption("Descarga el Excel consolidado con el mismo formato del archivo FORMATOBRIGADAS.xlsx.")

    admin_password = get_admin_password()
    password = st.text_input("Contraseña de administrador", type="password")
    if password != admin_password:
        st.info("Ingresa la contraseña para ver y descargar los registros.")
        if admin_password == "admin123":
            st.warning("Clave local por defecto: admin123. Cámbiala en .streamlit/secrets.toml o en la variable ADMIN_PASSWORD antes de publicar.")
        return

    total = count_records()
    recent = get_recent_records(limit=500)

    col1, col2, col3 = st.columns(3)
    col1.metric("Registros totales", total)
    col2.metric("Vista previa", min(total, 500))
    col3.metric("Formato", "A:F")

    st.subheader("Vista previa de registros recientes")
    if recent:
        df = pd.DataFrame(recent)
        df = df.rename(
            columns={
                "id": "ID",
                "created_at": "Fecha registro",
                "codigo_mca": "CODIGO MCA",
                "nombre_mca": "NOMBRE MCA",
                "brigadas_realizadas": "BRIGADAS REALIZADAS",
                "personas_brigada_1": "# PERSONAS BRIGADA 1",
                "personas_brigada_2": "# PERSONAS BRIGADA 2",
                "region": "REGION",
            }
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no hay registros guardados.")

    st.subheader("Descargas")
    excel_bytes = cached_export_excel(total)
    st.download_button(
        label="Descargar Excel con formato original",
        data=excel_bytes,
        file_name=EXPORT_FILE_NAME,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True,
    )

    if recent:
        csv_df = pd.DataFrame(get_records_for_export())
        st.download_button(
            label="Descargar CSV simple",
            data=csv_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="brigadas_respuestas.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with st.expander("Zona de mantenimiento"):
        st.warning("Esta acción elimina todos los registros de la base local SQLite.")
        confirmation = st.text_input("Escribe ELIMINAR para borrar todos los registros")
        if st.button("Borrar registros", disabled=confirmation != "ELIMINAR"):
            delete_all_records()
            st.cache_data.clear()
            st.success("Registros eliminados.")
            st.rerun()


def main() -> None:
    st.sidebar.title("Brigadas")
    page = st.sidebar.radio("Menú", ["Formulario", "Admin"])
    st.sidebar.markdown(
        "<p class='small-note'>El Excel se genera con la plantilla original: Hoja1, columnas A:F.</p>",
        unsafe_allow_html=True,
    )

    if page == "Formulario":
        render_form_page()
    else:
        render_admin_page()


if __name__ == "__main__":
    main()
