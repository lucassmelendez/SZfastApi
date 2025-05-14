-- Script de inicialización para Supabase
-- Este script debe ejecutarse en el SQL Editor de Supabase

-- Crear la tabla de alumnos
CREATE TABLE IF NOT EXISTS alumno (
    rut INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL
);

-- Establecer políticas RLS (Row Level Security) para la tabla
-- Por defecto, denegamos todo acceso
ALTER TABLE alumno ENABLE ROW LEVEL SECURITY;

-- Política de lectura: permitir lectura a todos los usuarios autenticados
CREATE POLICY alumno_select_policy
    ON alumno 
    FOR SELECT 
    USING (auth.role() = 'authenticated');

-- Política de inserción: permitir inserción a todos los usuarios autenticados
CREATE POLICY alumno_insert_policy
    ON alumno 
    FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated');

-- Política de actualización: permitir actualización a todos los usuarios autenticados
CREATE POLICY alumno_update_policy
    ON alumno 
    FOR UPDATE 
    USING (auth.role() = 'authenticated');

-- Política de borrado: permitir borrado a todos los usuarios autenticados
CREATE POLICY alumno_delete_policy
    ON alumno 
    FOR DELETE 
    USING (auth.role() = 'authenticated');

-- Insertar algunos datos de ejemplo
INSERT INTO alumno (rut, nombre, email)
VALUES 
    (12345678, 'Juan Pérez', 'juan.perez@ejemplo.com'),
    (23456789, 'María López', 'maria.lopez@ejemplo.com'),
    (34567890, 'Carlos Rodríguez', 'carlos.rodriguez@ejemplo.com')
ON CONFLICT (rut) DO NOTHING;

-- NOTA: Las políticas RLS son opcionales y se pueden ajustar según tus necesidades
-- Si estás empezando, puedes omitir las políticas y simplemente crear la tabla 