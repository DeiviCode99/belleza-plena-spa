# Plan de Modernización — Belleza Plena SPA

**Fecha:** 14 de julio de 2026
**Versión:** 1.0
**Estado:** Aprobado

---

## Índice

1. [Descripción del Proyecto](#1-descripción-del-proyecto)
2. [Estado Actual](#2-estado-actual)
3. [Arquitectura Propuesta](#3-arquitectura-propuesta)
4. [Stack Tecnológico](#4-stack-tecnológico)
5. [Fases de Migración](#5-fases-de-migración)
6. [Mejoras y Aportes](#6-mejoras-y-aportes)
7. [Seguridad](#7-seguridad)
8. [Diagramas](#8-diagramas)
9. [Timeline](#9-timeline)

---

## 1. Descripción del Proyecto

**Belleza Plena SPA** es un sistema de gestión integral para un centro de estética y spa. Desarrollado originalmente hace ~2 años, permite administrar pacientes, citas, servicios, colaboradores, tratamientos, aperitivos, historias clínicas y reportes mensuales en PDF.

### Funcionalidades actuales

| Módulo | Descripción |
|--------|-------------|
| **Dashboard** | Vista general con estadísticas |
| **Pacientes** | CRUD completo con datos médicos, contacto y etiquetas (Nuevo, Antiguo, Pago Pendiente, Jodido) |
| **Citas** | Agenda con asignación de paciente + colaborador + servicio + aperitivos, cálculo automático de saldo pendiente |
| **Historias Clínicas** | Registro médico por paciente con observaciones y recomendaciones |
| **Servicios** | Catálogo con duración, precio y vinculación a tratamientos |
| **Tratamientos** | Clasificación de tipos de tratamiento |
| **Colaboradores** | Registro del personal del SPA |
| **Aperitivos** | Productos adicionales (bebidas/snacks) vendidos en citas |
| **Reportes** | Reportes mensuales en PDF |

### Objetivo de la modernización

Migrar de un sistema local (una sola computadora) a una arquitectura cloud accesible desde cualquier dispositivo mediante un dominio privado para empleados, con autenticación JWT, base de datos en la nube y seguridad profesional.

---

## 2. Estado Actual

### Backend — Django 5.2 + DRF

| Aspecto | Estado Actual |
|---------|---------------|
| **Framework** | Django 5.2.3 + Django REST Framework |
| **Base de datos** | PostgreSQL 17.6 local |
| **Modelos** | 7 modelos: Paciente, Colaborador, Servicio, Tratamiento, Aperitivo, Cita, HistoriaClinica |
| **Autenticación** | ❌ No existe |
| **API** | REST completa con ViewSets + router |
| **Documentación** | CoreAPI en `/api/docs/` |
| **Reportes** | reportlab (importado pero sin uso efectivo) |
| **Pruebas** | ❌ `tests.py` vacío |
| **Despliegue** | `python manage.py runserver` (solo dev) |
| **CORS** | Solo localhost:5173 |

### Frontend — React 19 + Vite + Tailwind

| Aspecto | Estado Actual |
|---------|---------------|
| **Framework** | React 19.1 (JSX, sin TypeScript) |
| **Router** | react-router-dom instalado pero NO usado (navegación por estado) |
| **Estado** | useState local, sin estado global |
| **HTTP** | Axios 1.9 |
| **Estilos** | Tailwind CSS 3 + Bootstrap 5 (instalado, no usado) |
| **Login** | ❌ No existe |
| **API URL** | Hardcodeada `localhost:8000` |
| **Notificaciones** | react-toastify |
| **PDF** | jsPDF + html2canvas |

### Base de datos

| Entidad | Registros |
|---------|-----------|
| Pacientes | ~250 (reales del SPA) |
| Colaboradores | 1 (David Zapata) |
| Aperitivos | 1 (Ensalada de Frutas) |
| Citas, Servicios, Tratamientos, Historias | 0 (en el dump disponible) |
| Usuarios auth | 0 |

### Problemas críticos identificados

| # | Problema | Severidad | Impacto |
|---|----------|-----------|---------|
| 1 | Sin autenticación en API | 🔴 CRÍTICO | Cualquier persona accede/modifica datos |
| 2 | SECRET_KEY en código fuente | 🔴 CRÍTICO | Compromiso total de sesiones |
| 3 | DB password `root` en código | 🔴 CRÍTICO | Acceso no autorizado a DB |
| 4 | DEBUG=True | 🔴 CRÍTICO | Stack traces expuestos |
| 5 | ALLOWED_HOSTS vacío | 🟡 ALTO | Bloquea cualquier despliegue real |
| 6 | Sin rate limiting | 🟡 ALTO | Ataques de fuerza bruta |
| 7 | Sin HTTPS | 🟡 ALTO | Datos viajan en texto plano |
| 8 | Vista `HistoriasPorPaciente` rota | 🟡 ALTO | Error 500 en producción |
| 9 | Código muerto (create huérfana, reportlab) | 🟢 MEDIO | Ruido en codebase |
| 10 | Sin variables de entorno | 🟢 MEDIO | Configuración no portable |
| 11 | Backup de hace ~8 meses | 🟡 ALTO | Datos recientes no respaldados |

---

## 3. Arquitectura Propuesta

### Enfoque: Híbrido Supabase + Django

Se elige un enfoque híbrido (Opción 3) donde:
- **Supabase Auth** maneja la autenticación JWT de empleados
- **Supabase PostgreSQL** aloja la base de datos en la nube
- **Django** conserva toda la lógica de negocio, validaciones, cálculos y reportes PDF
- **Frontend React** se conecta a Django con JWT de Supabase

Esto evita reescribir el backend, aprovecha la seguridad de Supabase Auth y mantiene la flexibilidad de Django para lógica compleja.

```
                     ┌─────────────────────────────────────┐
                     │         Empleado SPA                │
                     │   (Navegador: spa.tudominio.com)    │
                     └──────────────┬──────────────────────┘
                                    │
                         HTTPS (SSL)
                                    │
                    ┌───────────────┴───────────────┐
                    │        Frontend React          │
                    │    (Vercel / Netlify / VPS)    │
                    │                                │
                    │   AuthContext ←→ Supabase JS   │
                    │   Axios + JWT Interceptor      │
                    └───────────────┬───────────────┘
                                    │
                          ┌─────────┴─────────┐
                          │                   │
                    ┌─────┴─────┐    ┌────────┴────────┐
                    │  Supabase  │    │  Django API     │
                    │    Auth    │    │   (VPS/Docker)  │
                    │  (JWT)     │    │                 │
                    └─────┬─────┘    │  - Verifica JWT  │
                          │          │  - Lógica negocio│
                          │          │  - CRUD          │
                          │          │  - Reportes PDF  │
                          │          └────────┬────────┘
                          │                   │
                          └─────────┬─────────┘
                                    │
                         ┌──────────┴──────────┐
                         │   Supabase Database  │
                         │  (PostgreSQL Cloud)  │
                         │   - Datos del SPA    │
                         │   - Backups auto     │
                         │   - SSL/TLS          │
                         └─────────────────────┘
```

### Capas del backend

```
HTTP Request (con JWT)
       │
       ▼
┌─────────────────────────┐
│   SupabaseJWTMiddleware │  ← Verifica token con Supabase Auth
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│   DRF ViewSets          │  ← PacienteViewSet, CitaViewSet, etc.
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│   Serializers           │  ← Validación de datos
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│   Service Layer (NUEVO) │  ← Lógica de negocio extraída
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│   Django ORM            │  ← Apunta a Supabase PostgreSQL
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│   Supabase DB           │
│   (PostgreSQL Cloud)    │
└─────────────────────────┘
```

---

## 4. Stack Tecnológico

### Propuesto

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|-----------|
| **Frontend** | React + Vite + Tailwind | 19 / 6 / 3 | UI del sistema |
| **Backend** | Django + DRF | 5.2 / latest | API REST + lógica de negocio |
| **Base de datos** | Supabase PostgreSQL | 15+ | Almacenamiento cloud |
| **Autenticación** | Supabase Auth + JWT | — | Login de empleados |
| **HTTP Client** | Axios + @supabase/supabase-js | 1.9 / latest | Conexión frontend-backend |
| **Servidor** | Gunicorn + Nginx | latest / alpine | WSGI production + proxy |
| **Contenedores** | Docker + Docker Compose | latest | Entorno reproducible |
| **Dominio** | spa.tudominio.com / api.tudominio.com | — | Acceso privado empleados |
| **SSL** | Let's Encrypt + Certbot | latest | HTTPS |
| **CI/CD** | GitHub Actions (opcional) | — | Despliegue automático |

### Nuevas dependencias

**Backend (Python):**
```
django-environ                 → Variables de entorno
djangorestframework-simplejwt  → JWT (o middleware Supabase custom)
gunicorn                       → Servidor WSGI de producción
psycopg2-binary                → Driver PostgreSQL (actualizar)
```

**Frontend (Node):**
```
@supabase/supabase-js          → Cliente Supabase (auth)
```

### Dependencias a eliminar

| Dependencia | Razón |
|-------------|-------|
| `mysqlclient` | Nunca se usó (se trabaja con PostgreSQL) |
| `bootstrap` | No se usa (Tailwind es el framework visual) |
| `@react-pdf/renderer` | No se usa (jsPDF cubre PDFs) |
| `coreapi` | Obsoleto; migrar a drf-spectacular si se desea documentación |

---

## 5. Fases de Migración

### Fase 0: Preparación (1-2 días)

**Objetivo:** Tener el entorno listo sin tocar el sistema actual.

**Tareas:**

- [ ] Crear cuenta en Supabase (app.supabase.com) con proyecto "belleza-plena-db"
- [ ] Instalar dependencias nuevas:
  ```bash
  pip install python-dotenv django-environ djangorestframework-simplejwt
  npm install @supabase/supabase-js
  ```
- [ ] Crear archivo `.env` con todas las variables (NUNCA subir a git):
  ```env
  SUPABASE_DB_HOST=db.xxxxx.supabase.co
  SUPABASE_DB_PASSWORD=contraseña-generada
  SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
  SUPABASE_SERVICE_ROLE=eyJhbGciOiJIUzI1NiIs...
  DJANGO_SECRET_KEY=<nueva-clave-segura>
  DJANGO_DEBUG=False
  FRONTEND_URL=https://spa.tudominio.com
  BACKEND_URL=https://api.tudominio.com
  ```
- [ ] Agregar `.env` a `.gitignore`
- [ ] Configurar `django-environ` en `settings.py`

**Archivos a crear:**
- `BACKEND/.env`
- `BACKEND/.env.example`

**Archivos a modificar:**
- `BACKEND/backend/settings.py` — integrar django-environ
- `.gitignore` — agregar `.env`, `*.sql`

**Riesgo:** ✅ Ninguno. No se toca el sistema actual.

---

### Fase 1: Migrar Base de Datos a Supabase (1 día)

**Objetivo:** Mover estructura + datos del SPA a la nube.

**Tareas:**

- [ ] Ir al PC del SPA y tomar backup fresco:
  ```sql
  pg_dump -U postgres -d belleza_plena > respaldo_julio_2026.sql
  ```
- [ ] Configurar `settings.py` para apuntar a Supabase DB:
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'HOST': env('SUPABASE_DB_HOST'),
          'PORT': '6543',
          'NAME': 'postgres',
          'USER': 'postgres',
          'PASSWORD': env('SUPABASE_DB_PASSWORD'),
          'OPTIONS': {'sslmode': 'require'},
      }
  }
  ```
- [ ] Ejecutar migraciones: `python manage.py migrate`
- [ ] Importar datos desde backup SQL (solo INSERTs, no CREATE TABLE)
- [ ] Verificar integridad:
  ```python
  python manage.py shell
  >>> Paciente.objects.count()  # → ~250
  >>> Colaborador.objects.count()  # → ~1
  ```

**Archivos a modificar:**
- `BACKEND/backend/settings.py` — configuración de base de datos

**Riesgo:** ⚠️ Medio. Tener el backup local antes de comenzar. Si algo sale mal, se restaura desde el archivo `.sql`.

---

### Fase 2: Autenticación JWT en Backend (2-3 días)

**Objetivo:** Proteger todos los endpoints con JWT de Supabase.

**Tareas:**

- [ ] Crear `negocio/auth.py` con middleware de autenticación Supabase:
  ```python
  class SupabaseJWTAuthentication(BaseAuthentication):
      def authenticate(self, request):
          auth = request.headers.get('Authorization')
          if not auth:
              raise AuthenticationFailed('Token requerido')
          try:
              user = supabase.auth.get_user(auth.split(' ')[1])
              return (user, auth)
          except Exception:
              raise AuthenticationFailed('Token inválido o expirado')
  ```
- [ ] Configurar DRF para usar el nuevo sistema de autenticación:
  ```python
  REST_FRAMEWORK = {
      'DEFAULT_AUTHENTICATION_CLASSES': [
          'negocio.auth.SupabaseJWTAuthentication',
      ],
      'DEFAULT_PERMISSION_CLASSES': [
          'rest_framework.permissions.IsAuthenticated',
      ],
      'DEFAULT_THROTTLE_CLASSES': [
          'rest_framework.throttling.AnonRateThrottle',
          'rest_framework.throttling.UserRateThrottle',
      ],
      'DEFAULT_THROTTLE_RATES': {
          'anon': '10/hour',
          'user': '1000/hour',
      },
  }
  ```
- [ ] Crear endpoints de gestión de usuarios:
  - `POST /api/auth/register/` → solo admin, crea empleado en Supabase Auth
  - `POST /api/auth/login/` → devuelve JWT desde Supabase
- [ ] Agregar permisos por rol si es necesario (admin vs empleado)

**Archivos a crear:**
- `BACKEND/negocio/auth.py`

**Archivos a modificar:**
- `BACKEND/backend/settings.py` — configuración DRF
- `BACKEND/negocio/urls.py` — rutas de auth

**Riesgo:** ✅ Bajo. Si hay bugs, solo afecta requests nuevos. Los datos en DB no se tocan.

---

### Fase 3: Login en Frontend (2-3 días)

**Objetivo:** Agregar pantalla de login, protección de rutas e inyección de JWT en requests.

**Tareas:**

- [ ] Instalar `@supabase/supabase-js`
- [ ] Crear `src/context/AuthContext.jsx`:
  - `signIn(email, password)` → llama a Supabase Auth
  - Almacena sesión en memoria + localStorage
  - Provee `user`, `session`, `loading`, `logout` a toda la app
  - Manejo automático de refresh token
- [ ] Crear `src/pages/LoginPage.jsx` con diseño profesional del SPA:
  ```
  ┌───────────────────────────────────────┐
  │                                       │
  │     🧖‍♀️ Belleza Plena SPA          │
  │                                       │
  │     Correo electrónico                │
  │     [____________________________]    │
  │                                       │
  │     Contraseña                        │
  │     [____________________________]    │
  │                                       │
  │     [Iniciar Sesión]                  │
  │                                       │
  │     © 2026 Belleza Plena SPA         │
  └───────────────────────────────────────┘
  ```
- [ ] Configurar interceptor de Axios para adjuntar JWT automáticamente:
  ```javascript
  api.interceptors.request.use(config => {
      const session = supabase.auth.session()
      if (session?.access_token) {
          config.headers.Authorization = `Bearer ${session.access_token}`
      }
      return config
  })
  ```
- [ ] Modificar `App.jsx` para protección condicional:
  ```jsx
  if (loading) return <LoadingScreen />
  if (!user) return <LoginPage onLogin={handleLogin} />
  return <MainApp />
  ```
- [ ] Configurar `VITE_API_URL` como variable de entorno (`.env`)
- [ ] Actualizar timeout de Axios de 1s a 10s

**Archivos a crear:**
- `FRONTEND/.env`
- `FRONTEND/src/context/AuthContext.jsx`
- `FRONTEND/src/pages/LoginPage.jsx`

**Archivos a modificar:**
- `FRONTEND/src/App.jsx` — integrar AuthContext y LoginPage
- `FRONTEND/src/lib/axiosClient.js` — interceptor JWT, timeout 10s
- `FRONTEND/src/lib/api.js` — unificar llamadas (eliminar axios global)
- `FRONTEND/vite.config.js` — opcional: proxy para desarrollo

**Riesgo:** ✅ Bajo. Solo código nuevo; el sistema actual sigue funcionando.

---

### Fase 4: Seguridad y Configuración (1 día)

**Objetivo:** Corregir todas las vulnerabilidades identificadas.

**Tareas:**

| Hoy | → | Meta |
|-----|---|------|
| `DEBUG = True` | → | `DEBUG = False` |
| `ALLOWED_HOSTS = []` | → | `ALLOWED_HOSTS = [env('BACKEND_URL')]` |
| Secrets hardcodeados | → | Todo en `.env` |
| Sin SSL | → | HTTPS + Let's Encrypt |
| Sin rate limiting | → | DRF Throttling |
| CORS localhost | → | `CORS_ALLOWED_ORIGINS = [env('FRONTEND_URL')]` |

- [ ] Configurar headers de seguridad Django:
  ```python
  SECURE_SSL_REDIRECT = True
  SECURE_HSTS_SECONDS = 31536000  # 1 año
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  SECURE_CONTENT_TYPE_NOSNIFF = True
  SECURE_BROWSER_XSS_FILTER = True
  X_FRAME_OPTIONS = 'DENY'
  CSRF_COOKIE_SECURE = True
  SESSION_COOKIE_SECURE = True
  SESSION_COOKIE_HTTPONLY = True
  ```

**Archivos a modificar:**
- `BACKEND/backend/settings.py` — seguridad, CORS, hosts

**Riesgo:** ✅ Bajo.

---

### Fase 5: Despliegue (2-3 días)

**Objetivo:** Sistema funcionando 24/7 en servidor, accesible desde dominio privado.

**Tareas:**

- [ ] Crear `Dockerfile` para Django:
  ```dockerfile
  FROM python:3.12-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir gunicorn django-environ psycopg2-binary
  COPY . .
  RUN python manage.py collectstatic --noinput
  CMD ["gunicorn", "backend.wsgi", "--bind", "0.0.0.0:8000", "--workers", "4"]
  ```
- [ ] Crear `docker-compose.yml`:
  ```yaml
  services:
    backend:
      build: .
      ports: ["8000:8000"]
      env_file: .env
      volumes:
        - static_volume:/app/static

    nginx:
      image: nginx:alpine
      ports: ["80:80", "443:443"]
      volumes:
        - ./nginx.conf:/etc/nginx/conf.d/default.conf
        - static_volume:/static
        - ./certbot/conf:/etc/letsencrypt
      depends_on:
        - backend

  volumes:
    static_volume:
  ```
- [ ] Configurar Nginx como proxy inverso con SSL
- [ ] Obtener certificado SSL con Let's Encrypt + Certbot
- [ ] Desplegar frontend (Vercel o Netlify recomendados por simplicidad):
  - Conectar repo de GitHub
  - Configurar variable `VITE_API_URL`
  - Despliegue automático en cada push
- [ ] Configurar DNS:
  - `spa.tudominio.com` → Frontend (Vercel/Netlify)
  - `api.tudominio.com` → Backend (VPS con Docker)
  - `db.tudominio.com` → Supabase (uso interno, no público)

**Archivos a crear:**
- `BACKEND/Dockerfile`
- `BACKEND/docker-compose.yml`
- `BACKEND/nginx.conf`

**Riesgo:** ⚠️ Medio. Configuración de servidores y DNS requiere cuidado.

---

### Fase 6: Pruebas y Corte Final (1-2 días)

**Objetivo:** Verificación completa del sistema y transición a producción.

**Tareas:**

- [ ] Pruebas de humo (smoke tests):
  - [ ] Login con credenciales de empleado
  - [ ] CRUD pacientes: crear, listar, editar, eliminar
  - [ ] CRUD citas con cálculo automático de saldo pendiente
  - [ ] CRUD servicios, tratamientos, colaboradores, aperitivos
  - [ ] Visualización y edición de historias clínicas
  - [ ] Generación de reportes PDF
  - [ ] Cierre de sesión → bloqueo de acceso a todas las rutas
  - [ ] Recarga de página → sesión persistente (refresh token)
- [ ] Verificar ciclo de vida del token:
  - [ ] Token expira → redirige a login
  - [ ] Refresh token renueva sesión automáticamente
- [ ] Migración final de datos:
  ```bash
  # 1. Backup fresco del SPA
  pg_dump -U postgres -d belleza_plena > backup_final.sql

  # 2. Reset completo en Supabase (drop + recreate)
  # 3. Ejecutar migraciones
  python manage.py migrate

  # 4. Importar datos frescos
  psql "$SUPABASE_DB_URL" < backup_final.sql

  # 5. Verificar
  python manage.py shell -c "print(Paciente.objects.count())"
  ```
- [ ] Crear cuentas de empleados en Supabase Auth (admin dashboard)
- [ ] Capacitación con empleados (~1 hora):
  - Cómo acceder a `spa.tudominio.com`
  - Cómo iniciar sesión
  - El sistema se ve igual que antes
  - Cerrar sesión al terminar turno
- [ ] **CORTE**: Apagar servidor local. El sistema funciona 100% en la nube.

**Riesgo:** ✅ Controlado. Se puede revertir volviendo a encender el servidor local.

---

## 6. Mejoras y Aportes

### Mejoras de código (refactorización)

| Problema | Solución | Archivo |
|----------|----------|---------|
| `HistoriasPorPaciente` usa `cita.historiaclinica` (relación incorrecta) | Corregir a `paciente.historia_clinica` | `BACKEND/negocio/views.py` |
| Lógica de negocio en `CitaSerializer.create/update` | Extraer a `services.py` | `BACKEND/negocio/services.py` (nuevo) |
| Función `create()` huérfana en views.py (líneas 104-108) | Eliminar | `BACKEND/negocio/views.py` |
| `reportlab` importado sin usar en views.py | Eliminar import | `BACKEND/negocio/views.py` |
| `mysqlclient` en requirements.txt | Eliminar | `BACKEND/requirements.txt` |
| `getMedicalRecords` usa axios global en vez de instancia configurada | Unificar en `api.js` usando `api` | `FRONTEND/src/lib/api.js` |
| Timeout de Axios = 1s (muy bajo) | Cambiar a 10s | `FRONTEND/src/lib/axiosClient.js` |

### Mejoras de arquitectura

| Problema | Solución |
|----------|----------|
| App monolítica `negocio/` | Dividir en apps por dominio si el proyecto crece: `pacientes/`, `citas/`, `servicios/` |
| Sin pruebas automatizadas | Agregar tests con pytest + factory_boy |
| Sin logging | Configurar logging estructurado (archivo + stdout) |
| Sin auditoría | Agregar campo `updated_at` a modelos + log de cambios |
| Navegación por estado (sin URLs) | Implementar react-router-dom para URLs navegables |
| Código CRUD duplicado en cada módulo | Crear hook `useCrud(endpoint)` para reutilizar lógica |
| API URL hardcodeada en frontend | Usar `import.meta.env.VITE_API_URL` |

### Mejoras de UX

- [ ] Estados de carga (spinners / skeletons) en todas las vistas
- [ ] Manejo global de errores con ErrorBoundary
- [ ] Confirmación antes de eliminar (ya existe parcialmente)
- [ ] Filtros y búsqueda server-side en vez de solo client-side
- [ ] Notificaciones toast consolidadas (react-toastify ya instalado)
- [ ] Responsive design para tablets (los empleados pueden usar tablets)

### Mejoras de datos

- [ ] Limpiar encoding de caracteres (PatiÃ±o → Patiño)
- [ ] Validar y limpiar placeholders (0000000000, 2000-01-01)
- [ ] Agregar constraints de integridad faltantes (CHECK en teléfonos, emails)
- [ ] Estandarizar formatos de número telefónico
- [ ] Migrar `emergency_number` de varchar(10) a varchar(20) (hay números internacionales)

---

## 7. Seguridad

### Línea base actual (vulnerabilidades)

| # | Vulnerabilidad | Severidad | Estado post-migración |
|---|---------------|-----------|----------------------|
| 1 | Sin autenticación en API | 🔴 CRÍTICO | ✅ JWT obligatorio |
| 2 | SECRET_KEY en código fuente | 🔴 CRÍTICO | ✅ En variable de entorno |
| 3 | DB password en código | 🔴 CRÍTICO | ✅ En variable de entorno |
| 4 | DEBUG=True | 🔴 CRÍTICO | ✅ DEBUG=False |
| 5 | ALLOWED_HOSTS vacío | 🟡 ALTO | ✅ Configurado |
| 6 | Sin rate limiting | 🟡 ALTO | ✅ 10 req/hora anónimo |
| 7 | Sin HTTPS | 🟡 ALTO | ✅ Let's Encrypt + redirección |
| 8 | Sin headers de seguridad | 🟢 MEDIO | ✅ HSTS, XSS, nosniff, XFO |

### Esquema de seguridad post-migración

```
┌─────────────────────────────┐
│         Internet            │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│      Cloudflare (opcional)  │
│  - DDoS protection          │
│  - WAF                      │
│  - SSL/TLS                  │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│         Nginx               │
│  - HTTPS termination        │
│  - Rate limiting            │
│  - Static files             │
│  - Proxy → Django           │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│     Django + DRF            │
│  - JWT validation           │
│  - CORS (dominio específico)│
│  - Throttling               │
│  - CSRF seguro (vía JWT)    │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│   Supabase PostgreSQL       │
│  - SSL requerido            │
│  - Backups automáticos      │
│  - Acceso restringido por IP│
└─────────────────────────────┘
```

### Políticas de seguridad

```python
# Django settings.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# DRF throttling
'DEFAULT_THROTTLE_RATES': {
    'anon': '10/hour',
    'user': '1000/hour',
}
```

---

## 8. Diagramas

### Flujo de autenticación

```
FRONTEND                    SUPABASE AUTH                  DJANGO API
   │                            │                             │
   │── POST /auth/login ───────►│                             │
   │   {email, password}        │                             │
   │                            │                             │
   │◄── {access_token, ────────│                             │
   │     refresh_token,         │                             │
   │     user}                  │                             │
   │                            │                             │
   │── GET /api/pacientes/ ─────┼────────────────────────────►│
   │   Authorization: Bearer   │                             │
   │   eyJhbGciOiJIUzI1Ni...   │                             │
   │                            │                             │
   │                            │── Verificar JWT ──────────►│
   │                            │   (supabase.auth.get_user) │
   │                            │                             │
   │                            │◄── Token válido ───────────│
   │                            │                             │
   │                            │                             │── SELECT *
   │                            │                             │   FROM pacientes
   │                            │                             │◄── 250 registros
   │                            │                             │
   │◄──────── 200 OK ──────────┼────────────────────────────│
   │   [{id:1, nombres:...}]   │                             │
```

### Flujo de navegación (login → dashboard)

```
Usuario abre spa.tudominio.com
         │
         ▼
┌─────────────────────────────────┐
│  ¿Hay sesión activa?            │
│  ────────────────               │
│  NO → LoginPage                 │
│  SÍ → Dashboard                 │
└─────────────────────────────────┘
         │
         ▼ (login exitoso)
┌─────────────────────────────────┐
│  AuthContext almacena:          │
│  - access_token (memoria)       │
│  - refresh_token (localStorage) │
│  - user {id, email, rol}        │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  MainLayout                    │
│  ┌──────────┬────────────────┐ │
│  │ Sidebar  │ Main Content   │ │
│  │          │                │ │
│  │ 📊 Dash  │ Dashboard      │ │
│  │ 📅 Citas │ con stats      │ │
│  │ 👥 Ptes  │                │ │
│  │ 📋 HC    │                │ │
│  │ ⚙️ Conf  │                │ │
│  └──────────┴────────────────┘ │
└─────────────────────────────────┘
         │
         ▼ (cerrar sesión)
┌─────────────────────────────────┐
│  - Token eliminado              │
│  - Redirige a LoginPage         │
│  - APIs ya no responden (401)   │
└─────────────────────────────────┘
```

### Diagrama de componentes del frontend

```
App.jsx
  │
  ├── AuthProvider (Context)
  │     ├── user: {id, email, rol}
  │     ├── session: {access_token, refresh_token}
  │     ├── loading: boolean
  │     ├── login(email, password)
  │     └── logout()
  │
  ├── [loading] → LoadingScreen
  ├── [!user]   → LoginPage
  │
  └── [user]    → MainLayout
        ├── Sidebar
        │     ├── Dashboard (BarChart3)
        │     ├── Citas (Calendar)
        │     ├── Pacientes (Users)
        │     ├── Historias Clínicas (FileText)
        │     └── Configuración (Settings)
        │
        ├── Header
        │     ├── Título dinámico
        │     ├── Avatar + nombre empleado
        │     └── Botón cerrar sesión
        │
        └── Main Content (renderActiveView)
              ├── Dashboard
              ├── AppointmentList / AppointmentForm
              ├── PatientList / PatientForm / PatientView
              ├── MedicalRecordList
              └── SettingsPanel
                    ├── WorkersList / WorkersForm
                    ├── TreatmentsList / TreatmentsForm
                    ├── ServicesList / ServicesForm
                    └── SnacksList / SnacksForm
```

---

## 9. Timeline

| Fase | Duración | Depende de | Riesgo |
|------|----------|------------|--------|
| 0. Preparación | 1-2 días | — | ✅ Ninguno |
| 1. Migrar DB | 1 día | Fase 0 + backup fresco del SPA | ⚠️ Medio |
| 2. Auth Backend | 2-3 días | Fase 0 | ✅ Bajo |
| 3. Login Frontend | 2-3 días | Fase 2 | ✅ Bajo |
| 4. Seguridad | 1 día | Fase 2 | ✅ Bajo |
| 5. Despliegue | 2-3 días | Fases 0-4 | ⚠️ Medio |
| 6. Pruebas + Corte | 1-2 días | Fase 5 | ✅ Controlado |
| **Total** | **10-15 días** | | |

### Dependencia clave

```
Fase 0 ─► Fase 2 ─► Fase 3 ─► Fase 5 ─► Fase 6
  │                      ▲                      ▲
  └────► Fase 1 ─────────┘                      │
         (requiere backup fresco del SPA)       │
                                                 │
  ┌──────────────────────────────────────────────┘
  │
  Fase 4 (puede hacerse en paralelo con Fase 3)
```

> **Nota importante:** La Fase 1 requiere acceso a la computadora del SPA para el backup fresco. Puedes avanzar con las Fases 0, 2, 3 y 4 mientras tanto usando el backup viejo para desarrollo. El backup fresco solo se necesita al final (Fase 6) para el corte definitivo.

---

## Archivos a crear/modificar — Resumen

### Nuevos

| Archivo | Propósito |
|---------|-----------|
| `BACKEND/.env` | Variables de entorno (no subir a git) |
| `BACKEND/.env.example` | Template de variables para otros entornos |
| `BACKEND/negocio/auth.py` | Middleware de autenticación Supabase/JWT |
| `BACKEND/negocio/services.py` | Capa de servicios (lógica de negocio extraída) |
| `BACKEND/Dockerfile` | Imagen Docker del backend |
| `BACKEND/docker-compose.yml` | Orquestación de servicios (Django + Nginx) |
| `BACKEND/nginx.conf` | Configuración de proxy inverso Nginx |
| `FRONTEND/.env` | Variables de entorno del frontend |
| `FRONTEND/src/context/AuthContext.jsx` | Contexto de autenticación |
| `FRONTEND/src/pages/LoginPage.jsx` | Pantalla de inicio de sesión |
| `FRONTEND/src/hooks/useCrud.js` | Hook genérico para operaciones CRUD |

### Modificar

| Archivo | Cambio principal |
|---------|------------------|
| `BACKEND/backend/settings.py` | django-environ, seguridad, DRF auth, CORS, hosts |
| `BACKEND/negocio/views.py` | Corregir HistoriasPorPaciente, eliminar código muerto |
| `BACKEND/negocio/serializers.py` | Extraer lógica de negocio a services.py |
| `BACKEND/requirements.txt` | Agregar django-environ, gunicorn, psycopg2-binary; eliminar mysqlclient, coreapi |
| `FRONTEND/src/App.jsx` | Integrar AuthContext, LoginPage |
| `FRONTEND/src/lib/axiosClient.js` | Interceptor JWT, timeout 10s |
| `FRONTEND/src/lib/api.js` | Unificar llamadas (eliminar axios global) |
| `FRONTEND/vite.config.js` | Variable de entorno VITE_API_URL |
| `.gitignore` | Agregar `.env`, `*.sql` |

---

*Documento generado el 14 de julio de 2026 como parte del proceso de modernización del sistema Belleza Plena SPA.*
