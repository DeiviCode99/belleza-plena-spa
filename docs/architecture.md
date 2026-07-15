# Arquitectura del Sistema

```mermaid
graph TB
    subgraph Frontend["Frontend — Vercel"]
        REACT["React 19 + Vite"]
        TAILWIND["TailwindCSS"]
        ROUTER["React Router v6"]
        SUPABASE_JS["Supabase JS Client"]
        AXIOS["Axios"]
        UI["lucide-react / react-toastify"]
    end

    subgraph Backend["Backend — Render"]
        DJANGO["Django 6.0 + DRF"]
        GUNICORN["Gunicorn"]
        JWT["SimpleJWT + SupabaseJWT"]
        REPORTLAB["ReportLab (PDF)"]
        SPECTACULAR["drf-spectacular (Swagger)"]
        WHITENOISE["WhiteNoise (Static)"]
        CORS["django-cors-headers"]
        CSP["django-csp"]
        RLS_CMD["enable_rls (management command)"]
    end

    subgraph Supabase["Supabase"]
        PG["PostgreSQL 17"]
        AUTH["Supabase Auth (JWT ES256)"]
    end

    USER["🧑‍💼 Usuario"] -->|HTTPS| REACT
    REACT -->|Auth: Login/Logout| SUPABASE_JS
    SUPABASE_JS --> AUTH
    REACT -->|API Calls: Bearer JWT| AXIOS
    AXIOS -->|GET/POST/PUT/DELETE| DJANGO
    DJANGO -->|validate JWT| JWT
    JWT -->|ES256 via JWKS| AUTH
    JWT -->|HS256 fallback| DJANGO
    DJANGO -->|SQL| PG
    DJANGO -->|RLS setup| RLS_CMD
    RLS_CMD -->|ALTER TABLE ENABLE RLS| PG
    DJANGO -->|PDF| REPORTLAB
    DJANGO -->|API Schema| SPECTACULAR
    GUNICORN --> DJANGO
    WHITENOISE -->|Static Files| DJANGO
    CORS -->|Allow Frontend Origin| DJANGO
    CSP -->|Security Headers| DJANGO

    classDef frontend fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    classDef backend fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    classDef supabase fill:#fff3e0,stroke:#e65100,color:#bf360c
    classDef user fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c

    class Frontend,REACT,TAILWIND,ROUTER,SUPABASE_JS,AXIOS,UI frontend
    class Backend,DJANGO,GUNICORN,JWT,REPORTLAB,SPECTACULAR,WHITENOISE,CORS,CSP,RLS_CMD backend
    class Supabase,PG,AUTH supabase
    class USER user
```

## Flujo de Autenticación

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as React App
    participant SA as Supabase Auth
    participant D as Django API
    participant DB as PostgreSQL

    U->>F: Email + Password
    F->>SA: supabase.auth.signInWithPassword()
    SA-->>F: access_token (ES256 JWT)
    F->>F: Store session
    F->>D: GET /api/pacientes (Bearer access_token)
    D->>D: Validate JWT via JWKS
    D-->>F: 200 JSON data
    Note over F,D: Session refresh on 401
    F->>SA: supabase.auth.refreshSession()
    SA-->>F: new access_token
    F->>D: Retry with new token
```

## Seguridad Implementada

| Medida | Cómo |
|---|---|
| **RLS** | `enable_rls` command → `deny_all` policy on all public tables |
| **CORS** | `django-cors-headers` → solo `FRONTEND_URL` permitido |
| **CSP** | `django-csp` → scripts, styles, conexiones restringidas |
| **HSTS** | `Strict-Transport-Security: max-age=31536000` |
| **HTTPS** | `SECURE_SSL_REDIRECT` forzado en producción |
| **Cookies** | `SESSION_COOKIE_SECURE` + `CSRF_COOKIE_SECURE` + `HTTPONLY` |
| **Proxy SSL** | `SECURE_PROXY_SSL_HEADER` para Render |
| **JWT** | Dual auth: Supabase ES256 (via JWKS) + SimpleJWT HS256 fallback |
