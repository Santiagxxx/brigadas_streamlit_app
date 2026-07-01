# Formulario de Brigadas en Streamlit

Aplicación en Python + Streamlit para capturar información de brigadas y permitir que un administrador descargue el consolidado en Excel usando el formato original `FORMATOBRIGADAS.xlsx`.

## Estructura del Excel usado

La plantilla adjunta tiene una hoja llamada `Hoja1` y estos encabezados en la fila 1:

| Columna | Encabezado |
|---|---|
| A | CODIGO MCA |
| B | NOMBRE MCA |
| C | BRIGADAS REALIZADAS |
| D | # PERSONAS BRIGADA 1 |
| E | # PERSONAS BRIGADA 2 |
| F | REGION |

La descarga del administrador mantiene esa estructura y copia el estilo del cuerpo del archivo original.

## Por qué no se guarda directamente cada envío en Excel

Para datos grandes y varios usuarios, Excel no debe ser la base principal porque puede dañarse o bloquearse si dos personas escriben al mismo tiempo. Por eso esta app guarda los registros en SQLite y genera el Excel con formato cuando el administrador lo descarga.

Para producción con muchos usuarios, reemplaza SQLite por PostgreSQL, Supabase, Firebase o una base gestionada. La capa de formulario y exportación a Excel puede mantenerse igual.

## Instalación local

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

## Configurar contraseña de administrador

Copia el archivo de ejemplo:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edita `.streamlit/secrets.toml`:

```toml
ADMIN_PASSWORD = "tu_clave_segura"
```

Si no configuras contraseña, la app local usa `admin123` como clave temporal.

## Ejecutar

```bash
streamlit run app.py
```

## Publicar fácilmente

Opción simple:

1. Sube esta carpeta a un repositorio de GitHub.
2. Conecta el repositorio en Streamlit Community Cloud.
3. Define el secreto `ADMIN_PASSWORD` en la configuración de la app.
4. Ejecuta `app.py` como archivo principal.

Nota importante: si el hosting no tiene disco persistente, los datos de SQLite se pueden perder al reiniciar la app. Para uso real con muchos registros, usa un servicio con disco persistente o una base externa.

## Archivos importantes

```text
app.py                         Interfaz principal de Streamlit
modules/db.py                  Guardado y consulta en SQLite
modules/excel_export.py         Generación del Excel con formato original
modules/validation.py           Validaciones del formulario
templates/FORMATOBRIGADAS.xlsx Plantilla original
data/                          Base SQLite local en ejecución
```
