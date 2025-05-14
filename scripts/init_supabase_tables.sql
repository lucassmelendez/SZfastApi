-- Script de inicialización para Supabase
-- Este script debe ejecutarse en el SQL Editor de Supabase

-- Crear la tabla de roles (si no existe)
CREATE TABLE IF NOT EXISTS rol (
    id_rol SERIAL PRIMARY KEY,
    nombre_rol TEXT NOT NULL
);

-- Insertar roles básicos si no existen
INSERT INTO rol (id_rol, nombre_rol) 
VALUES 
    (1, 'Cliente'),
    (2, 'Administrador'),
    (3, 'Empleado')
ON CONFLICT (id_rol) DO NOTHING;

-- Crear tabla de informes (si no existe)
CREATE TABLE IF NOT EXISTS informe (
    id_informe SERIAL PRIMARY KEY,
    descripcion TEXT
);

-- Insertar un informe por defecto
INSERT INTO informe (id_informe, descripcion) 
VALUES (1, 'Informe general')
ON CONFLICT (id_informe) DO NOTHING;

-- Crear la tabla de clientes
CREATE TABLE IF NOT EXISTS cliente (
    id_cliente SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    telefono TEXT NOT NULL,
    direccion TEXT NOT NULL,
    id_rol INTEGER REFERENCES rol(id_rol),
    rut TEXT NOT NULL,
    contrasena TEXT NOT NULL
);

-- Crear la tabla de empleados
CREATE TABLE IF NOT EXISTS empleado (
    id_empleado SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    rut TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    contrasena TEXT NOT NULL,
    direccion TEXT NOT NULL,
    telefono TEXT NOT NULL,
    rol_id INTEGER REFERENCES rol(id_rol),
    informe_id INTEGER REFERENCES informe(id_informe)
);

-- Establecer políticas RLS (Row Level Security) para la tabla cliente
ALTER TABLE cliente ENABLE ROW LEVEL SECURITY;

-- Política de lectura: permitir lectura a todos los usuarios autenticados
CREATE POLICY cliente_select_policy
    ON cliente 
    FOR SELECT 
    USING (auth.role() = 'authenticated');

-- Política de inserción: permitir inserción a todos los usuarios autenticados
CREATE POLICY cliente_insert_policy
    ON cliente 
    FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated');

-- Política de actualización: permitir actualización a todos los usuarios autenticados
CREATE POLICY cliente_update_policy
    ON cliente 
    FOR UPDATE 
    USING (auth.role() = 'authenticated');

-- Política de borrado: permitir borrado a todos los usuarios autenticados
CREATE POLICY cliente_delete_policy
    ON cliente 
    FOR DELETE 
    USING (auth.role() = 'authenticated');

-- Establecer políticas RLS para la tabla empleado
ALTER TABLE empleado ENABLE ROW LEVEL SECURITY;

-- Política de lectura: permitir lectura a todos los usuarios autenticados
CREATE POLICY empleado_select_policy
    ON empleado 
    FOR SELECT 
    USING (auth.role() = 'authenticated');

-- Política de inserción: permitir inserción a todos los usuarios autenticados
CREATE POLICY empleado_insert_policy
    ON empleado 
    FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated');

-- Política de actualización: permitir actualización a todos los usuarios autenticados
CREATE POLICY empleado_update_policy
    ON empleado 
    FOR UPDATE 
    USING (auth.role() = 'authenticated');

-- Política de borrado: permitir borrado a todos los usuarios autenticados
CREATE POLICY empleado_delete_policy
    ON empleado 
    FOR DELETE 
    USING (auth.role() = 'authenticated');

-- Insertar datos de ejemplo para clientes
INSERT INTO cliente (id_cliente, nombre, apellido, correo, telefono, direccion, id_rol, rut, contrasena) 
VALUES 
    (1, 'test test', 'test', 'test@test.test', '123456789', 'test 123', 1, '11111111-1', 'changeme'),
    (2, 'test2', 'test2', 'test2@test.test', '123456789', 'test2', 1, '11111111-1', 'changeme'),
    (3, 'Justin', 'Serón', 'ju.seron@duocuc.cl', '123456789', 'casa 123', 1, '11111111-1', 'changeme')
ON CONFLICT (id_cliente) DO NOTHING;

-- Insertar datos de ejemplo para empleados
INSERT INTO empleado (id_empleado, nombre, apellido, rut, correo, contrasena, direccion, telefono, rol_id, informe_id) 
VALUES 
    (2, 'admin', 'admin', '12345678-9', 'admin@admin.admin', 'admin123', 'admin', '123456789', 2, 1)
ON CONFLICT (id_empleado) DO NOTHING;

-- NOTA: Las políticas RLS son opcionales y se pueden ajustar según tus necesidades
-- Si estás empezando, puedes omitir las políticas y simplemente crear las tablas 