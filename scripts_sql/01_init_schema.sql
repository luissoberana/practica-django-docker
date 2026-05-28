-- =====================================================================
-- 📄 SCRIPT COMPLETO DE DEFINICIÓN DE BASE DE DATOS (Neon Postgres)
-- Objetivo: Esquema completo del dominio para la API de Impuestos
-- =====================================================================

-- 1. TABLA DE PAÍSES Y TASAS IMPOSITIVAS
-- Guarda la parametrización de cada país (ej: Colombia -> CO -> 19%)
CREATE TABLE IF NOT EXISTS api_pais (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo_iso VARCHAR(2) NOT NULL UNIQUE, -- Restricción UNIQUE para evitar duplicados
    tasa_impuesto NUMERIC(5, 4) NOT NULL,  -- Permite guardar decimales exactos como 0.1900
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA DE HISTORIAL DE CÁLCULOS (AUDITORÍA)
-- Registra cada operación realizada para auditoría interna y consumo de n8n
CREATE TABLE IF NOT EXISTS api_historialcalculo (
    id BIGSERIAL PRIMARY KEY,
    monto NUMERIC(12, 2) NOT NULL,
    impuesto_calculado NUMERIC(12, 2) NOT NULL,
    total NUMERIC(12, 2) NOT NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    pais_id BIGINT NOT NULL,
    
    -- Llave foránea que conecta el historial directamente con el país correspondiente
    CONSTRAINT fk_historial_pais 
        FOREIGN KEY (pais_id) 
        REFERENCES api_pais(id) 
        ON DELETE CASCADE
);

-- =====================================================================
-- ⚡ ÍNDICES DE OPTIMIZACIÓN (Cruciales para consultas masivas desde n8n)
-- =====================================================================

-- Optimiza las búsquedas cuando filtramos por el código del país (ej: 'CO')
CREATE INDEX IF NOT EXISTS idx_pais_codigo_iso 
    ON api_pais(codigo_iso);

-- Optimiza los JOINS entre el historial y la tabla de países
CREATE INDEX IF NOT EXISTS idx_historial_pais_id 
    ON api_historialcalculo(pais_id);

-- Optimiza los reportes que filtran por rangos de fechas (ej: recaudos del mes)
CREATE INDEX IF NOT EXISTS idx_historial_fecha 
    ON api_historialcalculo(fecha_creacion);