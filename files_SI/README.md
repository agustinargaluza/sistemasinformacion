# Ruta del Almuerzo 🚲
**Caso 06: Rutas Enredadas**
Proyecto final — Sistemas de Información, Ingeniería Comercial UCN

---

## Estructura del repositorio

```
/
├── frontend/
│   ├── index.html        ← Portal del cliente (hacer pedidos)
│   ├── matias.html       ← App de Matías (ruta del día)
│   └── dashboard.html    ← Panel de control operativo
├── backend/
│   ├── main.py           ← API FastAPI
│   ├── requirements.txt  ← Dependencias Python
│   └── db/               ← Se crea automáticamente con ruta.db
└── db/
    └── schema.sql        ← Script DDL + datos de prueba
```

---

## Cómo correr el proyecto

### 1. Backend (Python)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

La API queda disponible en: http://localhost:8000
Documentación automática: http://localhost:8000/docs

### 2. Frontend

Abre directamente en el navegador:
- `frontend/index.html`     → Portal del cliente
- `frontend/matias.html`    → App de Matías
- `frontend/dashboard.html` → Dashboard

> Si el backend no está corriendo, las pantallas igual funcionan con datos de demo.

---

## Endpoints de la API

| Método | Ruta                         | Descripción                     |
|--------|------------------------------|---------------------------------|
| GET    | `/`                          | Estado de la API                |
| GET    | `/menus`                     | Lista los menús disponibles     |
| POST   | `/pedidos`                   | Crea un nuevo pedido            |
| GET    | `/pedidos/hoy`               | Pedidos del día agrupados       |
| PATCH  | `/pedidos/{id}/entregar`     | Marca un pedido como entregado  |
| GET    | `/dashboard/hoy`             | KPIs y estadísticas del día     |
| GET    | `/zonas`                     | Lista las zonas geográficas     |

---

## Stack tecnológico

| Capa       | Tecnología       | Justificación                                      |
|------------|------------------|----------------------------------------------------|
| Frontend   | HTML + CSS + JS  | Sin dependencias, fácil de desplegar y mantener    |
| Backend    | Python + FastAPI | Rápido de desarrollar, documentación automática    |
| Base datos | SQLite           | Sin instalación extra, perfecta para prototipo     |

---

## Integrantes del equipo
*(completar con nombres y RUT)*

---
*UCN — Ingeniería Comercial — 2025*
