/*
Lab 5 — Widoki i widoki systemowe PostgreSQL do analizy struktury, statystyk i wydajności
Wersja do uruchomienia w pgAdmin Query Tool.

Cel:
1. Utworzyć przykładową bazę treningową.
2. Zbudować zwykłe widoki analityczne oraz widok zmaterializowany.
3. Zrozumieć rolę schematów jako przestrzeni nazw i pokazać interakcje między schematami.
4. Sprawdzić strukturę tabel przez information_schema i pg_catalog.
5. Sprawdzić statystyki tabel, indeksów, aktywności i zapytań.
6. Porównać plan zapytania przed i po dodaniu indeksu.
7. Zobaczyć wpływ ANALYZE/VACUUM ANALYZE na statystyki wykorzystywane przez planner.

Uwaga:
- Skrypt używa wyłącznie SQL PostgreSQL.
- Część pg_stat_statements może wymagać konfiguracji serwera:
  shared_preload_libraries = 'pg_stat_statements'
  oraz restartu serwera.
*/

DROP SCHEMA IF EXISTS lab5_reporting CASCADE;
DROP SCHEMA IF EXISTS lab5_archive CASCADE;
DROP SCHEMA IF EXISTS lab5 CASCADE;
CREATE SCHEMA lab5;
SET search_path TO lab5, public;

-- ============================================================
-- 1. Struktura bazy treningowej
-- ============================================================

CREATE TABLE lab5.customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    city TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE lab5.products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    active BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE lab5.orders (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES lab5.customers(customer_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    order_status TEXT NOT NULL CHECK (order_status IN ('new', 'paid', 'shipped', 'cancelled')),
    order_date TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE lab5.order_items (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES lab5.orders(order_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES lab5.products(product_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

-- ============================================================
-- 2. Dane testowe
-- ============================================================

INSERT INTO lab5.customers(email, first_name, last_name, city, created_at)
SELECT
    'user' || g || '@example.com',
    'Name' || g,
    'Surname' || g,
    (ARRAY['Warszawa', 'Kraków', 'Gdańsk', 'Poznań', 'Wrocław', 'Łódź'])[1 + (g % 6)],
    now() - ((g % 365) || ' days')::interval
FROM generate_series(1, 20000) AS g;

INSERT INTO lab5.products(sku, product_name, category, price, active)
SELECT
    'SKU-' || g,
    'Product ' || g,
    (ARRAY['book', 'electronics', 'home', 'sport', 'beauty'])[1 + (g % 5)],
    round((10 + random() * 990)::numeric, 2),
    g % 20 <> 0
FROM generate_series(1, 1000) AS g;

INSERT INTO lab5.orders(customer_id, order_status, order_date)
SELECT
    1 + (random() * 19999)::int,
    (ARRAY['new', 'paid', 'shipped', 'cancelled'])[1 + (random() * 3)::int],
    now() - ((random() * 180)::int || ' days')::interval
FROM generate_series(1, 80000) AS g;

INSERT INTO lab5.order_items(order_id, product_id, quantity, unit_price)
SELECT
    1 + (random() * 79999)::int,
    1 + (random() * 999)::int,
    1 + (random() * 4)::int,
    p.price
FROM generate_series(1, 220000) AS g
JOIN LATERAL (
    SELECT price
    FROM lab5.products
    WHERE product_id = 1 + (random() * 999)::int
    LIMIT 1
) AS p ON true;

ANALYZE lab5.customers;
ANALYZE lab5.products;
ANALYZE lab5.orders;
ANALYZE lab5.order_items;

-- ============================================================
-- 3. Schematy w bazie danych i interakcje między nimi
-- ============================================================

/*
Schemat w PostgreSQL jest przestrzenią nazw wewnątrz jednej bazy danych.
Dzięki schematom można rozdzielać obiekty według odpowiedzialności, np.:
- lab5           - dane transakcyjne,
- lab5_reporting - obiekty raportowe,
- lab5_archive   - dane audytowe lub archiwalne.

Interakcje między schematami są możliwe przez pełne nazwy obiektów:
schema_name.object_name. Dotyczy to zapytań SELECT, JOIN, widoków,
kluczy obcych oraz uprawnień.
*/

CREATE SCHEMA IF NOT EXISTS lab5_reporting;
CREATE SCHEMA IF NOT EXISTS lab5_archive;

DROP VIEW IF EXISTS lab5_reporting.v_status_changes;
DROP VIEW IF EXISTS lab5_reporting.v_orders_with_customer;
DROP TABLE IF EXISTS lab5_archive.order_status_log;

-- Tabela pomocnicza w osobnym schemacie może mieć klucz obcy do tabeli w lab5.
CREATE TABLE lab5_archive.order_status_log (
    log_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES lab5.orders(order_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    old_status TEXT,
    new_status TEXT NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT now()
);

INSERT INTO lab5_archive.order_status_log(order_id, old_status, new_status)
SELECT order_id, NULL, order_status
FROM lab5.orders
WHERE order_id <= 10;

-- Widok w schemacie raportowym może korzystać z tabel z innego schematu.
CREATE OR REPLACE VIEW lab5_reporting.v_orders_with_customer AS
SELECT
    o.order_id,
    o.order_date,
    o.order_status,
    c.customer_id,
    c.email,
    c.city,
    count(oi.order_item_id) AS lines_count,
    coalesce(sum(oi.quantity * oi.unit_price), 0) AS order_value
FROM lab5.orders AS o
JOIN lab5.customers AS c
    ON c.customer_id = o.customer_id
LEFT JOIN lab5.order_items AS oi
    ON oi.order_id = o.order_id
GROUP BY o.order_id, o.order_date, o.order_status, c.customer_id, c.email, c.city;

-- Widok może też łączyć dane z kilku schematów jednocześnie.
CREATE OR REPLACE VIEW lab5_reporting.v_status_changes AS
SELECT
    l.log_id,
    l.changed_at,
    o.order_id,
    c.email,
    l.old_status,
    l.new_status
FROM lab5_archive.order_status_log AS l
JOIN lab5.orders AS o
    ON o.order_id = l.order_id
JOIN lab5.customers AS c
    ON c.customer_id = o.customer_id;

-- Lista schematów używanych w ćwiczeniu.
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name LIKE 'lab5%'
ORDER BY schema_name;

-- Obiekty rozdzielone między schematy.
SELECT
    n.nspname AS schema_name,
    c.relname AS object_name,
    CASE c.relkind
        WHEN 'r' THEN 'table'
        WHEN 'v' THEN 'view'
        WHEN 'm' THEN 'materialized view'
        WHEN 'i' THEN 'index'
        WHEN 'S' THEN 'sequence'
        ELSE c.relkind::text
    END AS object_type
FROM pg_catalog.pg_class AS c
JOIN pg_catalog.pg_namespace AS n
    ON n.oid = c.relnamespace
WHERE n.nspname IN ('lab5', 'lab5_reporting', 'lab5_archive')
ORDER BY schema_name, object_type, object_name;

-- Odczyt przez pełną nazwę schema.object.
SELECT *
FROM lab5_reporting.v_orders_with_customer
ORDER BY order_id
LIMIT 10;

-- search_path decyduje, gdzie PostgreSQL szuka nazw bez prefiksu schematu.
SET search_path TO lab5_reporting, lab5, public;

SELECT *
FROM v_orders_with_customer
ORDER BY order_id
LIMIT 5;

SET search_path TO lab5, public;

-- Przykład modelu uprawnień dla oddzielenia raportowania od danych źródłowych.
-- W środowisku ćwiczeniowym zostawiamy to jako komentarz, bo rola może nie istnieć.
-- CREATE ROLE readonly_reporter LOGIN PASSWORD 'change_me';
-- GRANT USAGE ON SCHEMA lab5_reporting TO readonly_reporter;
-- GRANT SELECT ON ALL TABLES IN SCHEMA lab5_reporting TO readonly_reporter;


-- ============================================================
-- 4. Zwykłe widoki analityczne
-- ============================================================

CREATE OR REPLACE VIEW lab5.v_order_details AS
SELECT
    o.order_id,
    o.order_date,
    o.order_status,
    c.customer_id,
    c.email,
    c.city,
    oi.order_item_id,
    p.product_id,
    p.product_name,
    p.category,
    oi.quantity,
    oi.unit_price,
    oi.quantity * oi.unit_price AS line_total
FROM lab5.orders AS o
JOIN lab5.customers AS c
    ON c.customer_id = o.customer_id
JOIN lab5.order_items AS oi
    ON oi.order_id = o.order_id
JOIN lab5.products AS p
    ON p.product_id = oi.product_id;

CREATE OR REPLACE VIEW lab5.v_sales_by_city AS
SELECT
    city,
    count(DISTINCT order_id) AS orders_count,
    count(*) AS lines_count,
    sum(line_total) AS revenue
FROM lab5.v_order_details
GROUP BY city;

CREATE OR REPLACE VIEW lab5.v_sales_by_category AS
SELECT
    category,
    count(DISTINCT order_id) AS orders_count,
    sum(quantity) AS sold_units,
    sum(line_total) AS revenue
FROM lab5.v_order_details
GROUP BY category;

DROP MATERIALIZED VIEW IF EXISTS lab5.mv_daily_sales;
CREATE MATERIALIZED VIEW lab5.mv_daily_sales AS
SELECT
    date_trunc('day', order_date)::date AS sales_day,
    category,
    count(DISTINCT order_id) AS orders_count,
    sum(quantity) AS sold_units,
    sum(line_total) AS revenue
FROM lab5.v_order_details
GROUP BY date_trunc('day', order_date)::date, category;

CREATE UNIQUE INDEX mv_daily_sales_uq
    ON lab5.mv_daily_sales(sales_day, category);

-- REFRESH MATERIALIZED VIEW lab5.mv_daily_sales;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY lab5.mv_daily_sales;

-- ============================================================
-- 5. Widoki systemowe: struktura tabel i kolumn
-- ============================================================

SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'lab5'
ORDER BY table_name;

SELECT table_name, ordinal_position, column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'lab5'
ORDER BY table_name, ordinal_position;

SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
LEFT JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
   AND tc.table_schema = kcu.table_schema
LEFT JOIN information_schema.constraint_column_usage AS ccu
    ON tc.constraint_name = ccu.constraint_name
   AND tc.table_schema = ccu.table_schema
WHERE tc.table_schema = 'lab5'
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

SELECT
    rc.constraint_name,
    kcu.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column,
    rc.update_rule,
    rc.delete_rule
FROM information_schema.referential_constraints AS rc
JOIN information_schema.key_column_usage AS kcu
    ON rc.constraint_name = kcu.constraint_name
   AND rc.constraint_schema = kcu.constraint_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON rc.unique_constraint_name = ccu.constraint_name
   AND rc.unique_constraint_schema = ccu.constraint_schema
WHERE rc.constraint_schema = 'lab5'
ORDER BY kcu.table_name, rc.constraint_name;

SELECT schemaname, viewname, definition
FROM pg_catalog.pg_views
WHERE schemaname = 'lab5'
ORDER BY viewname;

SELECT schemaname, tablename, indexname, indexdef
FROM pg_catalog.pg_indexes
WHERE schemaname = 'lab5'
ORDER BY tablename, indexname;

SELECT
    n.nspname AS schema_name,
    c.relname AS object_name,
    c.relkind,
    CASE c.relkind
        WHEN 'r' THEN 'table'
        WHEN 'i' THEN 'index'
        WHEN 'v' THEN 'view'
        WHEN 'm' THEN 'materialized view'
        WHEN 'S' THEN 'sequence'
        ELSE c.relkind::text
    END AS object_type,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size
FROM pg_catalog.pg_class AS c
JOIN pg_catalog.pg_namespace AS n
    ON n.oid = c.relnamespace
WHERE n.nspname = 'lab5'
ORDER BY pg_total_relation_size(c.oid) DESC;

-- ============================================================
-- 6. Statystyki tabel, indeksów i operacji
-- ============================================================

SELECT
    schemaname,
    relname,
    seq_scan,
    idx_scan,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'lab5'
ORDER BY relname;

SELECT
    schemaname,
    relname AS table_name,
    indexrelname AS index_name,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'lab5'
ORDER BY idx_scan DESC, indexrelname;

SELECT
    schemaname,
    relname AS table_name,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_indexes_size(relid)) AS indexes_size,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_stat_user_tables
WHERE schemaname = 'lab5'
ORDER BY pg_total_relation_size(relid) DESC;

SELECT
    schemaname,
    tablename,
    attname,
    null_frac,
    n_distinct,
    most_common_vals,
    most_common_freqs
FROM pg_stats
WHERE schemaname = 'lab5'
  AND tablename IN ('orders', 'order_items', 'products')
ORDER BY tablename, attname;

SELECT
    datname,
    pid,
    usename,
    state,
    wait_event_type,
    wait_event,
    now() - query_start AS query_duration,
    left(query, 120) AS query_preview
FROM pg_stat_activity
WHERE datname = current_database()
ORDER BY query_start NULLS LAST;

-- ============================================================
-- 7. Pomiar planów zapytań: przed i po indeksach
-- ============================================================

EXPLAIN (ANALYZE, BUFFERS)
SELECT o.order_status, count(*) AS orders_count
FROM lab5.orders AS o
WHERE o.order_status = 'paid'
  AND o.order_date >= now() - interval '30 days'
GROUP BY o.order_status;

EXPLAIN (ANALYZE, BUFFERS)
SELECT p.category, sum(oi.quantity * oi.unit_price) AS revenue
FROM lab5.order_items AS oi
JOIN lab5.products AS p ON p.product_id = oi.product_id
JOIN lab5.orders AS o ON o.order_id = oi.order_id
WHERE o.order_date >= now() - interval '30 days'
GROUP BY p.category
ORDER BY revenue DESC;

CREATE INDEX IF NOT EXISTS idx_orders_status_date ON lab5.orders(order_status, order_date);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON lab5.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON lab5.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON lab5.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON lab5.products(category);

ANALYZE lab5.orders;
ANALYZE lab5.order_items;
ANALYZE lab5.products;

EXPLAIN (ANALYZE, BUFFERS)
SELECT o.order_status, count(*) AS orders_count
FROM lab5.orders AS o
WHERE o.order_status = 'paid'
  AND o.order_date >= now() - interval '30 days'
GROUP BY o.order_status;

EXPLAIN (ANALYZE, BUFFERS)
SELECT p.category, sum(oi.quantity * oi.unit_price) AS revenue
FROM lab5.order_items AS oi
JOIN lab5.products AS p ON p.product_id = oi.product_id
JOIN lab5.orders AS o ON o.order_id = oi.order_id
WHERE o.order_date >= now() - interval '30 days'
GROUP BY p.category
ORDER BY revenue DESC;

-- ============================================================
-- 8. Wpływ UPDATE/DELETE na statystyki i VACUUM
-- ============================================================

UPDATE lab5.orders
SET order_status = 'cancelled'
WHERE order_status = 'new'
  AND order_id % 10 = 0;

DELETE FROM lab5.order_items
WHERE order_item_id % 50 = 0;

SELECT schemaname, relname, n_tup_upd, n_tup_del, n_dead_tup,
       last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'lab5'
ORDER BY n_dead_tup DESC;

ANALYZE lab5.orders;
ANALYZE lab5.order_items;

VACUUM (ANALYZE) lab5.orders;
VACUUM (ANALYZE) lab5.order_items;

SELECT schemaname, relname, n_dead_tup, last_vacuum, last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lab5'
ORDER BY relname;

-- ============================================================
-- 9. pg_stat_statements jako dodatek
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

SELECT
    calls,
    round(total_exec_time::numeric, 2) AS total_exec_time_ms,
    round(mean_exec_time::numeric, 2) AS mean_exec_time_ms,
    rows,
    left(query, 120) AS query_preview
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
ORDER BY total_exec_time DESC
LIMIT 10;

-- SELECT pg_stat_statements_reset();

-- ============================================================
-- 10. Zadania dla studentów
-- ============================================================

/*
Zadanie 1. Utwórz widok lab5.v_customer_summary z podsumowaniem klienta.
Zadanie 2. Utwórz widok zmaterializowany lab5.mv_product_sales i dodaj unikalny indeks.
Zadanie 3. Napisz zapytanie z information_schema znajdujące wszystkie kolumny typu text.
Zadanie 4. Pokaż wszystkie klucze obce z regułami ON UPDATE i ON DELETE.
Zadanie 5. Porównaj EXPLAIN (ANALYZE, BUFFERS) dla SELECT * FROM lab5.orders WHERE customer_id = 100 przed i po indeksie orders(customer_id).
Zadanie 6. Wykonaj UPDATE/DELETE, sprawdź pg_stat_user_tables przed i po VACUUM (ANALYZE).
Zadanie 7. Utwórz schemat lab5_sandbox i tabelę lab5_sandbox.order_notes z kluczem obcym do lab5.orders.
Zadanie 8. Utwórz widok w lab5_reporting, który łączy dane z lab5.orders, lab5.customers i lab5_sandbox.order_notes.
Zadanie 9. Zmień search_path i sprawdź, jak działa zapytanie do widoku bez prefiksu schematu.
Zadanie 10. Opcjonalnie uruchom pg_stat_statements i znajdź najwolniejsze zapytania.
*/

-- Zadanie 1
DROP VIEW IF EXISTS lab5.v_customer_summary;
CREATE OR REPLACE VIEW lab5.v_customer_summary AS
SELECT 
    customer_id, 
    email, -- zamiast imienia i nazwiska używamy maila, bo jest w tym widoku
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(line_total) AS total_value,
    MAX(order_date) AS last_order_date
FROM lab5.v_order_details
GROUP BY customer_id, email;

-- Zadanie 2
DROP MATERIALIZED VIEW IF EXISTS lab5.mv_product_sales;
CREATE MATERIALIZED VIEW lab5.mv_product_sales AS
SELECT 
    product_id,
    product_name,
    category,
    COUNT(DISTINCT order_id) AS total_orders, -- w ilu unikalnych zamówieniach pojawił się produkt
    SUM(quantity) AS total_units_sold,        -- łączna liczba sprzedanych sztuk
    SUM(line_total) AS total_revenue           -- łączny przychód ze sprzedaży produktu
FROM lab5.v_order_details
GROUP BY product_id, product_name, category;

CREATE UNIQUE INDEX idx_mv_product_sales ON lab5.mv_product_sales (product_id);

-- Zadanie 3
SELECT table_name, column_name 
FROM information_schema.columns 
WHERE table_schema = 'lab5' AND data_type = 'text';

-- Zadanie 4
SELECT 
    kcu.table_name AS tabela_z_kluczem_obcym, 
    kcu.column_name AS kolumna_klucza_obcego, 
    ccu.table_name AS tabela_odniesienia, 
    ccu.column_name AS kolumna_odniesienia, 
    rc.update_rule AS regula_on_update, 
    rc.delete_rule AS regula_on_delete
FROM information_schema.referential_constraints AS rc
JOIN information_schema.key_column_usage AS kcu 
    ON rc.constraint_name = kcu.constraint_name
   AND rc.constraint_schema = kcu.constraint_schema
JOIN information_schema.constraint_column_usage AS ccu 
    ON rc.unique_constraint_name = ccu.constraint_name
   AND rc.unique_constraint_schema = ccu.constraint_schema
WHERE rc.constraint_schema = 'lab5'
ORDER BY kcu.table_name;

-- Zadanie 5
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM lab5.orders WHERE customer_id = 100;

CREATE INDEX idx_orders_customer_id ON lab5.orders(customer_id);
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM lab5.orders WHERE customer_id = 100;

-- Zadanie 5
UPDATE lab5.orders
SET order_status = 'cancelled'
WHERE order_id % 5 = 0;
DELETE FROM lab5.order_items
WHERE order_item_id % 50 = 0;

-- Zadanie 6
SELECT relname AS tabela, n_tup_upd AS aktualizacje, n_tup_del AS usuniecia, n_dead_tup AS martwe_wiersze
FROM pg_stat_user_tables
WHERE schemaname = 'lab5' AND relname IN ('orders', 'order_items');

VACUUM (ANALYZE) lab5.orders;

VACUUM (ANALYZE) lab5.order_items;

SELECT relname AS tabela, n_tup_upd AS aktualizacje, n_tup_del AS usuniecia, n_dead_tup AS martwe_wiersze
FROM pg_stat_user_tables
WHERE schemaname = 'lab5' AND relname IN ('orders', 'order_items');

-- Zadanie 7
CREATE SCHEMA IF NOT EXISTS lab5_sandbox;

CREATE TABLE lab5_sandbox.order_notes (
    note_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES lab5.orders(order_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    author TEXT NOT NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- Zadanie 8
DROP VIEW IF EXISTS lab5_reporting.v_orders_with_notes;

CREATE OR REPLACE VIEW lab5_reporting.v_orders_with_notes AS
SELECT 
    o.order_id,
    o.order_date,
    o.order_status,
    c.customer_id,
    c.email AS customer_email,
    n.note_id,
    n.author AS note_author,
    n.note_text,
    n.created_at AS note_created_at
FROM lab5.orders AS o
JOIN lab5.customers AS c 
    ON o.customer_id = c.customer_id
LEFT JOIN lab5_sandbox.order_notes AS n 
    ON o.order_id = n.order_id;

-- Zadanie 9
SELECT * FROM v_orders_with_notes LIMIT 5;
SET search_path TO lab5_reporting, lab5, public;
SELECT * FROM v_orders_with_notes LIMIT 5;

-- Zadanie 10