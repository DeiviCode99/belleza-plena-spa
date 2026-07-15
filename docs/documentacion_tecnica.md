# Documentación Técnica — Belleza Plena SPA

**Sistema de Gestión Integral para SPA**

---

## Contenido

1. [Contexto](#1-contexto)
2. [Análisis](#2-análisis)
   - 2.1 Estándares y Criterios de Calidad
   - 2.2 Requerimientos Funcionales
   - 2.3 Requerimientos No Funcionales
   - 2.4 Modelo de Negocio
3. [Diseño](#3-diseño)
   - 3.1 Casos de Uso
   - 3.2 Diagrama de Arquitectura
   - 3.3 Base de Datos
   - 3.4 Flujo de Autenticación
4. [Implementación](#4-implementación)
   - 4.1 Backend (Django REST Framework)
   - 4.2 Frontend (React + Vite)
   - 4.3 Progressive Web App (PWA)
5. [Despliegue](#5-despliegue)
   - 5.1 Backend — Render
   - 5.2 Frontend — Vercel
   - 5.3 Base de Datos — Supabase PostgreSQL
   - 5.4 Script de Build (setup.sh)
6. [Seguridad](#6-seguridad)
7. [Bugs Conocidos y Trabajo Pendiente](#7-bugs-conocidos-y-trabajo-pendiente)
8. [Conclusiones](#8-conclusiones)

---

## 1. Contexto

**Belleza Plena** es un SPA (Salón de Belleza y Bienestar) que requiere un sistema de gestión moderno para digitalizar sus operaciones diarias: registro de pacientes, programación de citas, asignación de colaboradores, control de servicios y tratamientos, historias clínicas, y generación de reportes mensuales.

### Problema Original

El establecimiento operaba con métodos manuales o semidigitalizados:
- Registro de pacientes en hojas físicas
- Agenda de citas en papel
- Historial de consumo sin digitalizar
- Reportes financieros elaborados manualmente
- Sin control de saldos pendientes por paciente

### Solución Propuesta

Aplicación web progresiva (PWA) con arquitectura cliente-servidor que permite:
- Gestión centralizada de pacientes, citas, servicios y colaboradores
- Autenticación segura mediante Supabase Auth (JWT)
- Disponibilidad desde cualquier dispositivo con navegador (mobile-first)
- Instalación como aplicación nativa en dispositivos móviles
- Reportes mensuales en PDF
- Historias clínicas digitales por paciente

---

## 2. Análisis

### 2.1 Estándares y Criterios de Calidad

#### ISO/IEC 25010:2011

| Característica | Evaluación | Implementación |
|---|---|---|
| **Seguridad** | Alto | JWT dual (ES256 + HS256), RLS, CSP, HSTS, HTTPS forzado |
| **Eficiencia de Desempeño** | Medio | Sin paginación aún en API; respuesta <500ms en CRUD simples |
| **Mantenibilidad** | Alto | Backend modular (DRF ViewSets), frontend componentizado |
| **Portabilidad** | Alto | PWA instalable en Android/iOS; frontend responsive |
| **Usabilidad** | Medio | Interfaz mobile-first con bottom sheets, skeletons, animaciones |
| **Fiabilidad** | Pendiente | Sin pruebas automatizadas aún |

#### Estándares de Código

- **Backend**: PEP 8 (Python), Django 6.0, Django REST Framework
- **Frontend**: ESLint + React Hooks, TailwindCSS utility-first
- **API**: OpenAPI 3.0.3 via `drf-spectacular` (Swagger UI + ReDoc)
- **Autenticación**: RFC 7519 (JWT) con Supabase Auth ES256 + fallback HS256
- **Control de Versiones**: Git con GitHub

### 2.2 Requerimientos Funcionales

| ID | Módulo | Descripción | Actor |
|---|---|---|---|
| **RF-01** | Autenticación | Inicio de sesión mediante Supabase Auth con email/contraseña | Administrador |
| **RF-02** | Dashboard | Vista resumen con stats, citas próximas, acciones rápidas | Administrador |
| **RF-03** | Gestión de Pacientes | CRUD completo: datos personales, contacto emergencia, condiciones médicas, etiquetas | Administrador |
| **RF-04** | Gestión de Citas | CRUD con selección de paciente, colaborador, servicio, aperitivos. Cálculo automático de saldo. Cambio de estado | Administrador |
| **RF-05** | Historias Clínicas | Visualización de citas por paciente. Exportación a PDF | Administrador |
| **RF-06** | Gestión de Colaboradores | CRUD de trabajadores | Administrador |
| **RF-07** | Gestión de Servicios | CRUD con nombre, duración, precio, tratamientos asociados | Administrador |
| **RF-08** | Gestión de Tratamientos | CRUD básico | Administrador |
| **RF-09** | Gestión de Aperitivos | CRUD con nombre y precio | Administrador |
| **RF-10** | Reportes Mensuales | Listado de meses con ingresos. Descarga de PDF con top servicios y colaboradores | Administrador |
| **RF-11** | Panel de Configuración | Acceso unificado a gestión de workers, treatments, services, snacks | Administrador |
| **RF-12** | PWA | Instalación como app nativa. Service worker con cacheo de API (NetworkFirst, 5 min) | Todos |

### 2.3 Requerimientos No Funcionales

| ID | Categoría | Descripción | Métrica |
|---|---|---|---|
| **RNF-01** | Seguridad | Autenticación JWT con Supabase + SimpleJWT fallback. RLS en BD | Token expira cada 8h (access), 7d (refresh) |
| **RNF-02** | Rendimiento | Respuesta API < 500ms en CRUD | Sin paginación implementada aún |
| **RNF-03** | Disponibilidad | Sistema operativo 24/7 via Render + Vercel | Uptime del servicio |
| **RNF-04** | Compatibilidad | PWA instalable en Android e iOS | Manifest + Service Worker funcional |
| **RNF-05** | Mantenibilidad | Código modular con separación de responsabilidades | DRF ViewSets, componentes React |
| **RNF-06** | Portabilidad | Frontend responsive (mobile-first) | TailwindCSS breakpoints |
| **RNF-07** | Usabilidad | Interfaz intuitiva con feedback visual | Skeleton loading, toasts, animaciones |

### 2.4 Modelo de Negocio

Belleza Plena SPA opera bajo un modelo de **servicios por cita**:

1. **Paciente** agenda una **cita** seleccionando un **servicio** y un **colaborador**
2. El servicio puede incluir múltiples **tratamientos** (M2M)
3. Durante la cita, el paciente puede consumir **aperitivos**
4. El **saldo pendiente** se calcula automáticamente: `precio_servicio + suma_precio_aperitivos`
5. Las citas tienen 3 estados: **Pendiente → Realizada / Cancelada**
6. Cada paciente tiene una **historia clínica** (OneToOne) creada automáticamente con su primera cita
7. Los pacientes tienen **etiquetas** para segmentación: Nuevo, Antiguo, Pago Pendiente, Jodido
8. Los reportes mensuales muestran ingresos, top servicios, top colaboradores

**Flujo de valor:**
```
Paciente agenda → Colaborador ejecuta → Servicio entregado → Pago registrado → Reporte generado
```

---

## 3. Diseño

### 3.1 Casos de Uso

```
┌─────────────────────────────────────────────────────────┐
│                    Belleza Plena SPA                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Administrador                                    │   │
│  │  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │ Iniciar Sesión│  │ Ver Dashboard│              │   │
│  │  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │ CRUD Pacientes│  │ CRUD Citas   │              │   │
│  │  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │ Gestionar     │  │ Ver Historias│              │   │
│  │  │ Colaboradores │  │ Clínicas     │              │   │
│  │  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │ CRUD Servicios│  │ CRUD         │              │   │
│  │  │ /Tratamientos │  │ Aperitivos   │              │   │
│  │  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │ Generar       │  │ Descargar    │              │   │
│  │  │ Reportes      │  │ PDF Reporte  │              │   │
│  │  └──────────────┘  └──────────────┘              │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Diagrama de Arquitectura

```
                           ┌─────────────────────────────┐
                           │       Usuario Final          │
                           │    (Navegador / PWA)         │
                           └──────────┬──────────────────┘
                                      │ HTTPS
                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND — Vercel                             │
│  React 19 + Vite + TailwindCSS + React Router v6                │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐      │
│  │ AuthContext  │  │  axiosClient │  │ Service Worker    │      │
│  │ (Supabase   │──│  (JWT Bearer │  │ (PWA cache API)   │      │
│  │  JS Client) │  │   interceptor│  │                   │      │
│  └──────┬──────┘  └──────┬───────┘  └───────────────────┘      │
└─────────┼─────────────────┼─────────────────────────────────────┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPABASE AUTH                                 │
│  auth.signInWithPassword() → JWT (ES256)                        │
│  auth.refreshSession() → Nuevo token                            │
│  JWKS endpoint: /.well-known/jwks.json                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND — Render (Gunicorn)                    │
│  Django 6.0 + Django REST Framework                              │
│  ┌──────────────────┐  ┌──────────────────────────┐             │
│  │ SupabaseJWT       │  │  ViewSets (CRUD)          │            │
│  │ Authentication    │  │  Paciente, Cita,          │            │
│  │ ES256 via JWKS    │  │  Colaborador, Servicio,   │            │
│  │ HS256 fallback    │  │  Tratamiento, Aperitivo,  │            │
│  └──────────────────┘  │  HistoriaClinica           │            │
│                        └──────────────────────────┘             │
│  ┌──────────────────┐  ┌──────────────────────────┐             │
│  │ ReportLab (PDF)   │  │ Middleware: CORS, CSP,   │            │
│  └──────────────────┘  │ Security Headers, WhiteNoise           │
│                        └──────────────────────────┘             │
└──────────────────────────┬───────────────────────────────────────┘
                           │ SQL direct connection (bypasses RLS)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPABASE PostgreSQL 17                        │
│  Tablas: Paciente, Cita, Servicio, Tratamiento, Aperitivo,      │
│          Colaborador, HistoriaClinica + M2M tables               │
│  RLS: deny_all policies en TODAS las tablas públicas            │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Base de Datos

#### Modelo Relacional

```
Paciente (1) ──── (0..N) Cita (N..M) Aperitivo
    │                       │
    │                       ├── (1) Servicio ── (M..M) Tratamiento
    │                       │
    │                       └── (1) Colaborador
    │
    └── (1..1) HistoriaClinica
```

#### Tablas (7 modelos + M2M implícitas)

| Tabla | Columnas clave | Relaciones |
|---|---|---|
| `negocio_paciente` | id, nombres, apellidos, tipo_documento, numero_documento, celular, direccion, fecha_nacimiento, emergencia_nombre, emergencia_number, condiciones_medicas, alergias, extras, etiquetas_pac, created_at | → HistoriaClinica (1:1) |
| `negocio_colaborador` | id, nombres, apellidos, tipo_documento, numero_documento, celular, created_at | ← Cita (FK) |
| `negocio_servicio` | id, nombre, duracion, precio, created_at | ← Cita (FK), → Tratamiento (M2M) |
| `negocio_tratamiento` | id, nombre | ← Servicio (M2M) |
| `negocio_aperitivo` | id, nombre, precio | ← Cita (M2M) |
| `negocio_cita` | id, fecha_hora, hora, estado, notas, saldo_pend, created_at | → Paciente (FK), → Colaborador (FK), → Servicio (FK), → Aperitivo (M2M) |
| `negocio_historiaclinica` | id, observaciones, recomendaciones, created_at | → Paciente (1:1 FK) |

#### Migraciones

```
0001_initial.py → 0002_rename_etiquitas_pac → 0003_remove_tratamiento_descripcion
```

La migración `0003` eliminó `duracion` y `descripcion` de `Tratamiento`, y agregó `extras` a `Paciente`.

### 3.4 Flujo de Autenticación

```
Usuario        React App              Supabase Auth          Django API
  │               │                       │                    │
  │ Email+Pass    │                       │                    │
  │──────────────▶│                       │                    │
  │               │ signInWithPassword()  │                    │
  │               │──────────────────────▶│                    │
  │               │ JWT (ES256)           │                    │
  │               │◀──────────────────────│                    │
  │               │                       │                    │
  │               │ GET /api/pacientes    │                    │
  │               │ (Bearer token)        │                    │
  │               │───────────────────────────────────────────▶│
  │               │                       │   Validate JWT via │
  │               │                       │   JWKS (ES256)     │
  │               │                       │   or HS256 fallback│
  │               │ 200 JSON              │                    │
  │               │◀───────────────────────────────────────────│
  │ ←── 401 ──│                    │
  │               │ refreshSession()      │                    │
  │               │──────────────────────▶│                    │
  │               │ new token             │                    │
  │               │◀──────────────────────│                    │
  │               │ Retry original request│                    │
  │               │───────────────────────────────────────────▶│
  │ Datos         │                       │                    │
  │◀──────────────│                       │                    │
```

---

## 4. Implementación

### 4.1 Backend (Django REST Framework)

#### Estructura

```
BACKEND/
├── backend/
│   ├── settings.py       # Config: DB, CORS, CSP, Auth, JWT, Security
│   ├── urls.py           # Health check, admin, API, Swagger, JWT endpoints
│   └── wsgi.py           # Gunicorn entry point
├── negocio/
│   ├── models.py         # 7 modelos de datos
│   ├── views.py          # ViewSets + APIViews
│   ├── serializers.py    # ModelSerializers + nested CitaSerializer
│   ├── urls.py           # Router + rutas adicionales
│   ├── authentication.py # SupabaseJWTAuthentication
│   ├── views_reportes.py # 4 endpoints de reportes + PDF
│   ├── signals.py        # Auto-creación HistoriaClinica
│   ├── admin.py          # Registro de modelos
│   ├── tests.py          # Vacío
│   └── management/commands/
│       ├── enable_rls.py
│       └── create_supabase_user.py
├── setup.sh
├── requirements.txt
└── Procfile
```

#### Endpoints API

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Health check |
| GET|POST | `/api/pacientes/` | CRUD pacientes |
| GET|POST | `/api/citas/` | CRUD citas |
| GET|POST | `/api/trabajadores/` | CRUD colaboradores |
| GET|POST | `/api/servicios/` | CRUD servicios |
| GET|POST | `/api/tratamientos/` | CRUD tratamientos |
| GET|POST | `/api/aperitivos/` | CRUD aperitivos |
| GET|POST | `/api/historias/` | CRUD historias clínicas |
| GET | `/api/historias-clinicas/` | Historias por paciente |
| GET | `/api/reportes/meses/` | Meses con datos |
| GET | `/api/reportes/meses/{mes}/` | Detalle del mes |
| GET | `/api/reportes/meses/{mes}/pdf/` | PDF descargable |
| GET | `/api/docs/` | Swagger UI |

#### Autenticación Dual (authentication.py)

1. Extrae token Bearer del header
2. Detecta algoritmo (ES256 o HS256)
3. ES256: obtiene clave pública desde JWKS endpoint de Supabase
4. HS256: decodifica con `SUPABASE_JWT_SECRET` (fallback legacy)
5. Crea/recupera usuario Django asociado al `sub`

#### Serializadores Destacados

**CitaSerializer** es el más complejo:
- Campos anidados read-only: `paciente`, `colaborador`, `servicio`
- Campos write-only: `paciente_id`, `colaborador_id`, `servicio_id`
- M2M `aperitivos` write-only + `aperitivos_info` read-only
- `create()` calcula `saldo_pend = servicio.precio + suma(aperitivos.precio)`
- `update()` recalcula automáticamente

#### Reportes PDF (ReportLab)

Usa `reportlab` con:
- Header: "Belleza Plena SPA"
- Tabla resumen con colores emerald
- Top 5 servicios y colaboradores
- Footer con fecha de generación

#### Señales

```python
@receiver(post_save, sender=Cita)
def crear_historia_clinica(sender, instance, created, **kwargs):
    if created:
        if not HistoriaClinica.objects.filter(paciente=instance.paciente).exists():
            HistoriaClinica.objects.create(paciente=instance.paciente)
```

### 4.2 Frontend (React + Vite)

#### Estructura

```
FRONTEND/frontend/
├── index.html
├── vite.config.js          # PWA plugin, Workbox caching
├── tailwind.config.js      # Brand colors, animations
├── vercel.json             # SPA rewrites
└── src/
    ├── main.jsx
    ├── App.jsx             # Routes
    ├── index.css           # Tailwind + animations + utilities
    ├── context/AuthContext.jsx
    ├── lib/
    │   ├── supabase.js     # Supabase client init
    │   ├── axiosClient.js  # Axios + JWT interceptor
    │   └── api.js          # API functions
    └── components/
        ├── auth/           # Login, ProtectedRoute
        ├── dashboard/      # Dashboard, StatsCard
        ├── layout/         # Layout, Header, Sidebar, PageTransition
        ├── patients/       # PatientList, PatientForm, PatientView
        ├── appointments/   # AppointmentList, AppointmentForm
        ├── medical-records/ # MedicalRecordList
        ├── services/       # ServicesList, ServicesForm
        ├── workers/        # WorkersList, WorkersForm
        ├── treatments/     # TreatmentsList, TreatmentsForm
        ├── snacks/         # SnacksList, SnacksForm
        ├── reports/        # ReportsList
        ├── settings/       # SettingsPanel
        ├── pwa/            # InstallPrompt
        └── ui/             # Skeleton
```

#### AuthContext

- Almacena `user`, `session`, `loading`
- Provee `login(email, password)` y `logout()`
- Se suscribe a `onAuthStateChange` de Supabase

#### Axios Interceptor

- Inyecta `Authorization: Bearer <token>` en cada request
- En 401: intenta refresh automático con `supabase.auth.refreshSession()`
- Si falla refresh: redirige a `/login`

#### Routing

```
/login          → Login (público)
/dashboard      → Dashboard
/citas          → AppointmentList
/pacientes      → PatientList
/historias-clinicas → MedicalRecordList
/configuracion  → SettingsPanel
/reportes       → ReportsList
```

#### UI/UX Features

- **Design System**: Colores brand (emerald 50-900), Inter font
- **Responsive**: Sidebar oculta en mobile con overlay
- **Transiciones**: PageTransition (fade-in-up), modales bottom-sheet
- **Feedback**: Skeleton shimmer, react-toastify, botones scale(0.97)
- **Dual render**: Tablas desktop / Cards mobile

### 4.3 PWA

Configurada con `vite-plugin-pwa`:

- **Manifest**: name, short_name, theme_color #10b981, display standalone, icons 192x192 + 512x512
- **Service Worker**: `registerType: 'autoUpdate'`
- **Runtime Caching**:
  - API Django (`/api/`): NetworkFirst, cache 5 min, max 100 entries
  - Supabase Auth (`supabase.co/auth/`): NetworkFirst, cache 1 day, max 50 entries

**InstallPrompt** muestra banner cuando el navegador dispara `beforeinstallprompt`.

---

## 5. Despliegue

### 5.1 Backend — Render

- **Tipo**: Web Service
- **Servidor**: Gunicorn WSGI
- **Build**: `bash setup.sh`
- **Start**: `gunicorn backend.wsgi --bind 0.0.0.0:$PORT`
- **Health Check**: `GET /` → 200 OK
- **URL**: `belleza-plena-api.onrender.com`

### 5.2 Frontend — Vercel

- **Tipo**: SPA
- **Build**: `npm run build`
- **Output**: `dist/`
- **Rewrites**: Todas las rutas a `index.html` (SPA)
- **Auto-deploy**: En cada push a la rama principal

### 5.3 Base de Datos — Supabase PostgreSQL

- **Versión**: PostgreSQL 17
- **Conexión**: Directa desde Django (no via Supabase REST API)
- **Pooler**: `aws-1-us-east-2.pooler.supabase.com`
- **SSL**: `sslmode=require`
- **RLS**: `deny_all` en todas las tablas public (19 tablas)

### 5.4 Script de Build (setup.sh)

```bash
#!/usr/bin/env bash
set -e
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser --noinput 2>/dev/null || true
python manage.py create_supabase_user ... 2>/dev/null || true
python manage.py enable_rls 2>/dev/null || true
```

---

## 6. Seguridad

| Medida | Implementación |
|---|---|
| **JWT Dual** | ES256 vía JWKS (Supabase) + HS256 fallback (secret local) |
| **RLS** | `deny_all` en todas las tablas públicas — bloquea Supabase REST API |
| **CORS** | Solo `FRONTEND_URL` permitido |
| **CSP** | Scripts, estilos, conexiones restringidas |
| **HSTS** | `max-age=31536000` en producción |
| **HTTPS** | `SECURE_SSL_REDIRECT` forzado en producción |
| **Cookies** | `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `HTTPONLY` |
| **Proxy SSL** | `SECURE_PROXY_SSL_HEADER` para Render |
| **XSS** | `SECURE_BROWSER_XSS_FILTER` |
| **Referrer** | `same-origin` |
| **Frame** | `CSP_FRAME_ANCESTORS: 'none'` |

### ⚠️ Exposición de Secretos

Los archivos `.env` con credenciales reales fueron commiteados al repositorio:
- `SUPABASE_DB_PASSWORD`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE`
- `SUPABASE_JWT_SECRET`, `DJANGO_SECRET_KEY`

**Acción recomendada**: Rotar todas las claves y limpiar historial git.

---

## 7. Bugs Conocidos y Trabajo Pendiente

### Bugs Activos (3 críticos)

| # | Archivo | Descripción | Gravedad |
|---|---|---|---|
| **B-01** | `negocio/views.py:57` | `HistoriasPorPaciente` referencia `cita.historiaclinica` pero la relación OneToOne es Paciente→HistoriaClinica, no Cita | **Alta** |
| **B-02** | `negocio/serializers.py:114` | `HistoriaClinicaSerializer` declara `cita = CitaSerializer()` pero el modelo no tiene campo `cita` | **Alta** |
| **B-03** | `negocio/views.py:62` | `historia.tratamiento` — el modelo `HistoriaClinica` no tiene campo `tratamiento` | **Alta** |

### Bugs Menores

| # | Archivo | Descripción |
|---|---|---|
| **B-04** | `frontend/src/lib/api.js` | `getMedicalRecords` usa `axios.get` directo sin JWT → 401 |
| **B-05** | `frontend/src/components/medical-records/MedicalRecordList.jsx` | Referencia `patient.email` que no existe en el modelo |
| **B-06** | `frontend/src/components/patients/PatientView.jsx` | Referencia `patient.email` que no existe en el modelo |
| **B-07** | `frontend/src/components/treatments/TreatmentsList.jsx` | Referencia `treatment.duracion` y `treatment.descripcion` eliminados en migración 0003 |
| **B-08** | `negocio/models.py` | `Paciente.extras` es TextField, frontend lo trata como array — inconsistencia |
| **B-09** | `frontend/src/components/treatments/TreatmentsList.jsx:160` | Modal título: "¿Eliminar Cita?" → debería ser "¿Eliminar Tratamiento?" |

### Trabajo Pendiente

| Prioridad | Tarea | Área |
|---|---|---|
| 🔴 Alta | Corregir bugs B-01, B-02, B-03 | Backend |
| 🔴 Alta | Rotar claves expuestas en git | Seguridad |
| 🟡 Media | Paginación global DRF | Backend |
| 🟡 Media | django-filter para búsqueda | Backend |
| 🟡 Media | Corregir B-04, B-05, B-07, B-08, B-09 | Frontend |
| 🟢 Baja | Tests unitarios | QA |
| 🟢 Baja | Reorganizar negocio/ en submódulos | Backend |
| 🟢 Baja | Migrar datos del backup (249 pacientes) | Migración |
| 🟢 Baja | Notificaciones push tiempo real | Mejora |
| 🟢 Baja | Dockerizar | DevOps |

---

## 8. Conclusiones

1. **Arquitectura sólida**: Django 6.0 + React 19 + Supabase PostgreSQL proporciona una base estable y escalable.

2. **Seguridad multicapa**: JWT dual, RLS, CSP, HSTS cubren los principales vectores de ataque.

3. **PWA funcional**: Service worker con NetworkFirst permite experiencia offline parcial y nativa en mobile.

4. **Interfaz mobile-first**: Bottom-sheets, cards, skeletons, animaciones — experiencia moderna.

5. **Bugs críticos en endpoint de historias**: B-01, B-02, B-03 impiden el funcionamiento de `GET /api/historias-clinicas/`. Causa raíz: el modelo `HistoriaClinica` está relacionado OneToOne con `Paciente`, pero el código lo trata como relacionado con `Cita`.

6. **Secretos expuestos en git**: Prioritario rotar credenciales.

7. **Sin cobertura de pruebas**: `tests.py` vacío.

8. **Próximo paso recomendado**: Corregir bugs críticos → rotar secretos → paginación y filtros → tests.

---

## Apéndice A: Tecnologías

### Backend
| Tecnología | Versión |
|---|---|
| Django | 6.0.7 |
| Django REST Framework | 3.17.1 |
| djangorestframework-simplejwt | 5.5.1 |
| django-cors-headers | 4.9.0 |
| django-csp | 3.8 |
| django-environ | 0.14.0 |
| drf-spectacular | 0.30.0 |
| gunicorn | 26.0.0 |
| psycopg2-binary | 2.9.12 |
| PyJWT | 2.13.0 |
| reportlab | 5.0.0 |
| whitenoise | 6.12.0 |
| cryptography | 49.0.0 |

### Frontend
| Tecnología | Versión |
|---|---|
| React | 19.1.0 |
| Vite | 6.3.5 |
| react-router-dom | 6.30.1 |
| @supabase/supabase-js | 2.109.0 |
| axios | 1.9.0 |
| tailwindcss | 3.4.1 |
| lucide-react | 0.517.0 |
| react-toastify | 11.0.5 |
| vite-plugin-pwa | 1.3.0 |
| jspdf | 3.0.1 |
| html2canvas | 1.4.1 |

## Apéndice B: Variables de Entorno

### Backend
```
SUPABASE_DB_HOST, SUPABASE_DB_PASSWORD, SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE, SUPABASE_JWT_SECRET, SUPABASE_PROJECT_REF
DJANGO_SECRET_KEY, DJANGO_DEBUG, FRONTEND_URL, BACKEND_URL
```

### Frontend
```
VITE_API_URL, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY
```

## Apéndice C: Comandos

```bash
# Backend
python manage.py runserver
python manage.py makemigrations && python manage.py migrate
python manage.py enable_rls
python manage.py create_supabase_user email password

# Frontend
npm run dev     # Desarrollo
npm run build   # Producción
```

---

*Documentación generada el 15 de Julio de 2026*
*Proyecto: Belleza Plena SPA — Sistema de Gestión Integral*
