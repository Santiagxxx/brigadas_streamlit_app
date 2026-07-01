# Despliegue en Streamlit Community Cloud

Configuración recomendada:

| Campo | Valor |
|---|---|
| Repository | `Santiagxxx/brigadas_streamlit_app` |
| Branch | `main` |
| Main file path | `app.py` |

## Secrets

En App settings > Secrets agrega:

```toml
ADMIN_PASSWORD = "tu_clave_segura"
DATABASE_URL = "postgresql://usuario:password@host:5432/base?sslmode=require"
```

La app crea la tabla `submissions` al iniciar si todavía no existe.
