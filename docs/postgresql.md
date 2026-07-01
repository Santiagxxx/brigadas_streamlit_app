# Configuración de PostgreSQL

La aplicación usa PostgreSQL cuando encuentra el secreto o variable de entorno `DATABASE_URL`.

## Secreto requerido

```toml
DATABASE_URL = "postgresql://usuario:password@host:5432/base?sslmode=require"
```

## Tabla

La aplicación crea la tabla automáticamente al iniciar. También puedes ejecutar manualmente el archivo:

```text
scripts/create_postgres_table.sql
```

## Modo local

Si `DATABASE_URL` no está configurado, la aplicación usa SQLite local como respaldo para pruebas.
