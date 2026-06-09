"""
Ruta del Almuerzo — Backend
Caso 06: Rutas Enredadas
Ejecutar: uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import sqlite3, os
from datetime import datetime, date

app = FastAPI(title="Ruta del Almuerzo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "db", "ruta.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cur  = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS zonas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        color_hex TEXT DEFAULT '#22C55E'
    );
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        telefono TEXT,
        direccion_defecto TEXT,
        zona_id INTEGER REFERENCES zonas(id),
        creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS menus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio INTEGER NOT NULL,
        disponible INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER REFERENCES clientes(id),
        menu_id INTEGER REFERENCES menus(id),
        zona_id INTEGER REFERENCES zonas(id),
        direccion_entrega TEXT NOT NULL,
        notas TEXT,
        estado TEXT DEFAULT 'pendiente',
        orden_ruta INTEGER,
        fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
        fecha_entrega DATETIME
    );
    """)

    if not cur.execute("SELECT 1 FROM zonas LIMIT 1").fetchone():
        cur.executescript("""
        INSERT INTO zonas (nombre, descripcion, color_hex) VALUES
            ('Zona A - Centro',  'Microcentro y alrededores', '#22C55E'),
            ('Zona B - Norte',   'Providencia y Las Condes',  '#3B82F6'),
            ('Zona C - Sur',     'Ñuñoa y Macul',             '#8B5CF6');

        INSERT INTO menus (nombre, descripcion, precio) VALUES
            ('Menú del día',  'Plato + ensalada + bebida', 3500),
            ('Vegetariano',   'Opción vegetal completa',   3500),
            ('Sin gluten',    'Libre de gluten',           4000),
            ('Especial',      'Menú premium del chef',     4500);

        INSERT INTO clientes (nombre_completo, telefono, direccion_defecto, zona_id) VALUES
            ('Alejandro Ramos', '+56912345601', 'Av. Libertador 1250, Piso 4B', 1),
            ('Sofía Méndez',    '+56912345602', 'Calle Florida 455, Local 12',  1),
            ('Carlos Martínez', '+56912345603', 'Belgrano 2100, Oficina 801',   2),
            ('Marina López',    '+56912345604', 'Av. Corrientes 3455, PB',      3),
            ('Juan Torres',     '+56912345605', 'Huérfanos 1150, Of. 301',      1);

        INSERT INTO pedidos (cliente_id, menu_id, zona_id, direccion_entrega, estado, orden_ruta) VALUES
            (1, 1, 1, 'Av. Libertador 1250, Piso 4B', 'entregado', 1),
            (2, 2, 1, 'Calle Florida 455, Local 12',  'entregado', 2),
            (5, 1, 1, 'Huérfanos 1150, Of. 301',      'en_ruta',   3),
            (3, 1, 2, 'Belgrano 2100, Oficina 801',   'entregado', 4),
            (4, 3, 3, 'Av. Corrientes 3455, PB',      'pendiente', 5);
        """)

    conn.commit()
    conn.close()

init_db()

# ── Modelos ──────────────────────────────────────────────────

class PedidoCreate(BaseModel):
    nombre_completo:   str
    direccion_entrega: str
    menu_id:           int
    notas:             Optional[str] = None

# ── Helpers ──────────────────────────────────────────────────

def detectar_zona(direccion: str) -> int:
    """Asigna zona según palabras clave en la dirección."""
    addr = direccion.lower()
    if any(w in addr for w in ['providencia', 'las condes', 'norte', 'italia']):
        return 2
    if any(w in addr for w in ['ñuñoa', 'macul', 'sur', 'irarrázaval', 'corrientes']):
        return 3
    return 1  # Centro por defecto

# ── Rutas ────────────────────────────────────────────────────

@app.get("/api")
def root():
    return {"mensaje": "Ruta del Almuerzo API funcionando", "docs": "/docs"}

@app.get("/menus")
def listar_menus():
    conn = get_db()
    menus = conn.execute("SELECT * FROM menus WHERE disponible=1").fetchall()
    conn.close()
    return [dict(m) for m in menus]

@app.post("/pedidos", status_code=201)
def crear_pedido(pedido: PedidoCreate):
    conn    = get_db()
    cur     = conn.cursor()
    zona_id = detectar_zona(pedido.direccion_entrega)

    # Buscar o crear cliente
    cliente = cur.execute(
        "SELECT id FROM clientes WHERE nombre_completo=?",
        (pedido.nombre_completo,)
    ).fetchone()

    if cliente:
        cliente_id = cliente["id"]
    else:
        cur.execute(
            "INSERT INTO clientes (nombre_completo, direccion_defecto, zona_id) VALUES (?,?,?)",
            (pedido.nombre_completo, pedido.direccion_entrega, zona_id)
        )
        cliente_id = cur.lastrowid

    # Calcular orden en ruta (último + 1 para la zona)
    max_orden = cur.execute(
        "SELECT MAX(orden_ruta) FROM pedidos WHERE zona_id=? AND date(fecha_pedido)=date('now')",
        (zona_id,)
    ).fetchone()[0] or 0

    cur.execute(
        """INSERT INTO pedidos
           (cliente_id, menu_id, zona_id, direccion_entrega, notas, estado, orden_ruta)
           VALUES (?,?,?,?,?,'pendiente',?)""",
        (cliente_id, pedido.menu_id, zona_id,
         pedido.direccion_entrega, pedido.notas, max_orden + 1)
    )
    nuevo_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {"id": nuevo_id, "zona_id": zona_id, "mensaje": "Pedido creado correctamente"}

@app.get("/pedidos/hoy")
def pedidos_hoy():
    conn    = get_db()
    pedidos = conn.execute("""
        SELECT p.id, c.nombre_completo AS cliente,
               p.direccion_entrega AS direccion,
               p.zona_id, p.estado, p.orden_ruta,
               m.nombre AS menu, p.notas
        FROM pedidos p
        JOIN clientes c ON c.id = p.cliente_id
        JOIN menus m    ON m.id = p.menu_id
        WHERE date(p.fecha_pedido) = date('now')
        ORDER BY p.zona_id, p.orden_ruta
    """).fetchall()
    conn.close()
    return [dict(p) for p in pedidos]

@app.patch("/pedidos/{pedido_id}/entregar")
def marcar_entregado(pedido_id: int):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE pedidos SET estado='entregado', fecha_entrega=datetime('now') WHERE id=?",
        (pedido_id,)
    )
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    conn.commit()
    conn.close()
    return {"mensaje": f"Pedido {pedido_id} marcado como entregado"}

@app.get("/dashboard/hoy")
def dashboard_hoy():
    conn = get_db()
    cur  = conn.cursor()

    total      = cur.execute("SELECT COUNT(*) FROM pedidos WHERE date(fecha_pedido)=date('now')").fetchone()[0]
    entregados = cur.execute("SELECT COUNT(*) FROM pedidos WHERE date(fecha_pedido)=date('now') AND estado='entregado'").fetchone()[0]
    pendientes = total - entregados

    por_zona = cur.execute("""
        SELECT z.nombre, COUNT(p.id) AS total
        FROM pedidos p
        JOIN zonas z ON z.id = p.zona_id
        WHERE date(p.fecha_pedido) = date('now')
        GROUP BY p.zona_id
        ORDER BY total DESC
    """).fetchall()

    por_hora = cur.execute("""
        SELECT strftime('%H', fecha_pedido) AS hora, COUNT(*) AS total
        FROM pedidos
        WHERE date(fecha_pedido) >= date('now', '-7 days')
        GROUP BY hora
        ORDER BY hora
    """).fetchall()

    por_semana = cur.execute("""
        SELECT strftime('%w', fecha_pedido) AS dia, COUNT(*) AS total
        FROM pedidos
        WHERE date(fecha_pedido) >= date('now', '-7 days')
        GROUP BY dia
    """).fetchall()

    conn.close()
    return {
        "total":      total,
        "entregados": entregados,
        "pendientes": pendientes,
        "por_zona":   [dict(r) for r in por_zona],
        "por_hora":   [dict(r) for r in por_hora],
        "por_semana": [dict(r) for r in por_semana],
    }

@app.get("/zonas")
def listar_zonas():
    conn  = get_db()
    zonas = conn.execute("SELECT * FROM zonas").fetchall()
    conn.close()
    return [dict(z) for z in zonas]

app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")
