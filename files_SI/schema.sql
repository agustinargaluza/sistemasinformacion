-- =============================================
-- RUTA DEL ALMUERZO — Base de datos
-- Caso 06: Rutas Enredadas
-- =============================================

-- Tabla de zonas geográficas
CREATE TABLE IF NOT EXISTS zonas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    color_hex TEXT DEFAULT '#22C55E'
);

-- Tabla de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT NOT NULL,
    telefono TEXT,
    direccion_defecto TEXT,
    zona_id INTEGER REFERENCES zonas(id),
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de menús disponibles
CREATE TABLE IF NOT EXISTS menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio INTEGER NOT NULL,
    disponible INTEGER DEFAULT 1
);

-- Tabla principal de pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER REFERENCES clientes(id),
    menu_id INTEGER REFERENCES menus(id),
    zona_id INTEGER REFERENCES zonas(id),
    direccion_entrega TEXT NOT NULL,
    notas TEXT,
    estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente','en_ruta','entregado','cancelado')),
    orden_ruta INTEGER,
    fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega DATETIME
);

-- =============================================
-- DATOS DE PRUEBA
-- =============================================

INSERT INTO zonas (nombre, descripcion, color_hex) VALUES
    ('Zona A - Centro',     'Microcentro y alrededores',     '#22C55E'),
    ('Zona B - Norte',      'Providencia y Las Condes',      '#3B82F6'),
    ('Zona C - Sur',        'Ñuñoa y Macul',                 '#8B5CF6');

INSERT INTO menus (nombre, descripcion, precio, disponible) VALUES
    ('Menú del día',   'Plato principal + ensalada + bebida',     3500, 1),
    ('Vegetariano',    'Opción vegetal completa',                  3500, 1),
    ('Sin gluten',     'Libre de gluten, certificado',             4000, 1),
    ('Especial',       'Menú premium del chef',                    4500, 1);

INSERT INTO clientes (nombre_completo, telefono, direccion_defecto, zona_id) VALUES
    ('Alejandro Ramos',  '+56912345601', 'Av. Libertador 1250, Piso 4B', 1),
    ('Sofía Méndez',     '+56912345602', 'Calle Florida 455, Local 12',  1),
    ('Carlos Martínez',  '+56912345603', 'Belgrano 2100, Oficina 801',   2),
    ('Marina López',     '+56912345604', 'Av. Corrientes 3455, PB',      3),
    ('Juan Torres',      '+56912345605', 'Huérfanos 1150, Of. 301',      1),
    ('Ana Castillo',     '+56912345606', 'Moneda 970, Piso 12',          1),
    ('Pedro Soto',       '+56912345607', 'Av. Italia 550, Of. 3',        2),
    ('Lucía Vargas',     '+56912345608', 'Irarrázaval 3240, Depto 5',    3),
    ('Diego Morales',    '+56912345609', 'Estado 359, Piso 8',           1),
    ('Valentina Cruz',   '+56912345610', 'Av. Providencia 1234, Of. 2',  2);

INSERT INTO pedidos (cliente_id, menu_id, zona_id, direccion_entrega, notas, estado, orden_ruta, fecha_pedido) VALUES
    (1,  1, 1, 'Av. Libertador 1250, Piso 4B',      NULL,              'entregado',  1,  datetime('now','-2 hours')),
    (2,  2, 1, 'Calle Florida 455, Local 12',        'Sin cebolla',     'entregado',  2,  datetime('now','-2 hours')),
    (5,  1, 1, 'Huérfanos 1150, Of. 301',            NULL,              'en_ruta',    3,  datetime('now','-1 hour')),
    (6,  3, 1, 'Moneda 970, Piso 12',                'Alérgica al trigo','pendiente', 4,  datetime('now','-1 hour')),
    (9,  4, 1, 'Estado 359, Piso 8',                 NULL,              'pendiente',  5,  datetime('now','-30 minutes')),
    (3,  1, 2, 'Belgrano 2100, Oficina 801',         NULL,              'entregado',  6,  datetime('now','-2 hours')),
    (7,  2, 2, 'Av. Italia 550, Of. 3',              'Dejar en recepción','pendiente',7,  datetime('now','-45 minutes')),
    (10, 1, 2, 'Av. Providencia 1234, Of. 2',        NULL,              'pendiente',  8,  datetime('now','-20 minutes')),
    (4,  3, 3, 'Av. Corrientes 3455, PB',            NULL,              'en_ruta',    9,  datetime('now','-1 hour')),
    (8,  4, 3, 'Irarrázaval 3240, Depto 5',          'Timbre no funciona','pendiente',10, datetime('now','-15 minutes'));

-- Pedidos históricos para gráficos del dashboard (última semana)
INSERT INTO pedidos (cliente_id, menu_id, zona_id, direccion_entrega, estado, orden_ruta, fecha_pedido, fecha_entrega) VALUES
    (1, 1, 1, 'Av. Libertador 1250', 'entregado', 1, datetime('now','-1 day','-3 hours'), datetime('now','-1 day','-1 hour')),
    (2, 2, 1, 'Calle Florida 455',   'entregado', 2, datetime('now','-1 day','-3 hours'), datetime('now','-1 day','-1 hour')),
    (3, 1, 2, 'Belgrano 2100',       'entregado', 3, datetime('now','-1 day','-2 hours'), datetime('now','-1 day','-30 minutes')),
    (4, 3, 3, 'Av. Corrientes 3455', 'entregado', 4, datetime('now','-1 day','-2 hours'), datetime('now','-1 day','-30 minutes')),
    (5, 4, 1, 'Huérfanos 1150',      'entregado', 5, datetime('now','-2 days','-3 hours'),datetime('now','-2 days','-1 hour')),
    (6, 1, 1, 'Moneda 970',          'entregado', 1, datetime('now','-2 days','-3 hours'),datetime('now','-2 days','-1 hour')),
    (7, 2, 2, 'Av. Italia 550',      'entregado', 2, datetime('now','-2 days','-2 hours'),datetime('now','-2 days','-45 minutes')),
    (8, 1, 3, 'Irarrázaval 3240',    'entregado', 3, datetime('now','-3 days','-3 hours'),datetime('now','-3 days','-1 hour')),
    (9, 3, 1, 'Estado 359',          'entregado', 1, datetime('now','-3 days','-2 hours'),datetime('now','-3 days','-30 minutes')),
    (10,4, 2, 'Av. Providencia 1234','entregado', 2, datetime('now','-3 days','-2 hours'),datetime('now','-3 days','-30 minutes'));
