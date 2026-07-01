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

## Base de datos

Para producción, la aplicación usa PostgreSQL cuando existe el secreto o variable de entorno `DATABASE_URL`.

Si no existe `DATABASE_URL`, la app usa SQLite local como respaldo para pruebas locales. Este modo no se recomienda para producción porque el almacenamiento local puede perderse en algunos servicios de hosting.

## Por qué no se guarda directamente cada envío en Excel

Para datos grandes y varios usuarios, Excel no debe ser la base principal porque puede dañarse o bloquearse si dos personas escriben al mismo tiempo. Por eso esta app guarda los registros en una base de datos y genera el Excel con formato cuando el administrador lo descarga.

## Instalación local

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

## Configurar secretos

Copia el archivo de ejemplo:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edita `.streamlit/secrets.toml`:

```toml
ADMIN_PASSWORD = "tu_clave_segura"
DATABASE_URL = "postgresql://usuario:password@host:5432/base?sslmode=require"
```

Si no configuras `ADMIN_PASSWORD`, la app local usa `admin123` como clave temporal.

Si no configuras `DATABASE_URL`, la app usa SQLite local.

## Ejecutar

```bash
streamlit run app.py
```

## Publicar en Streamlit Community Cloud

1. Conecta el repositorio de GitHub.
2. Selecciona la rama `main`.
3. Usa `app.py` como archivo principal.
4. En **App settings > Secrets**, agrega:

```toml
ADMIN_PASSWORD = "tu_clave_segura"
DATABASE_URL = "postgresql://usuario:password@host:5432/base?sslmode=require"
```

La tabla `submissions` se crea automáticamente cuando la app inicia.

## Archivos importantes

```text
app.py                         Interfaz principal de Streamlit
modules/db.py                  Guardado y consulta en PostgreSQL, con SQLite local como respaldo
modules/excel_export.py         Generación del Excel con formato original
modules/validation.py           Validaciones del formulario
templates/FORMATOBRIGADAS.xlsx Plantilla original
data/                          Base SQLite local solo cuando no se configura DATABASE_URL
```
