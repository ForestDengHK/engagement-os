---
name: sql-queries
description: Use when writing SQL, optimizing a slow query, translating between dialects (including Oracle-to-Fabric migrations), or building analytical queries with CTEs, window functions or aggregations — Snowflake, BigQuery, Databricks, PostgreSQL, Redshift, Oracle 19c, Microsoft Fabric (Warehouse T-SQL, SQL analytics endpoint, Spark SQL); Fabric's T-SQL notes also help with SQL Server / Azure SQL.
user-invocable: false
---

# SQL Queries Skill

Write correct, performant, readable SQL across all major data warehouse dialects.

## Dialect-Specific Reference

Sources and dates for the Oracle 19c and Microsoft Fabric sections: [references/dialect-sources.md](references/dialect-sources.md).

### PostgreSQL (including Aurora, RDS, Supabase, Neon)

**Date/time:**
```sql
-- Current date/time
CURRENT_DATE, CURRENT_TIMESTAMP, NOW()

-- Date arithmetic
date_column + INTERVAL '7 days'
date_column - INTERVAL '1 month'

-- Truncate to period
DATE_TRUNC('month', created_at)

-- Extract parts
EXTRACT(YEAR FROM created_at)
EXTRACT(DOW FROM created_at)  -- 0=Sunday

-- Format
TO_CHAR(created_at, 'YYYY-MM-DD')
```

**String functions:**
```sql
-- Concatenation
first_name || ' ' || last_name
CONCAT(first_name, ' ', last_name)

-- Pattern matching
column ILIKE '%pattern%'  -- case-insensitive
column ~ '^regex_pattern$'  -- regex

-- String manipulation
LEFT(str, n), RIGHT(str, n)
SPLIT_PART(str, delimiter, position)
REGEXP_REPLACE(str, pattern, replacement)
```

**Arrays and JSON:**
```sql
-- JSON access
data->>'key'  -- text
data->'nested'->'key'  -- json
data#>>'{path,to,key}'  -- nested text

-- Array operations
ARRAY_AGG(column)
ANY(array_column)
array_column @> ARRAY['value']
```

**Performance tips:**
- Use `EXPLAIN ANALYZE` to profile queries
- Create indexes on frequently filtered/joined columns
- Use `EXISTS` over `IN` for correlated subqueries
- Partial indexes for common filter conditions
- Use connection pooling for concurrent access

---

### Snowflake

**Date/time:**
```sql
-- Current date/time
CURRENT_DATE(), CURRENT_TIMESTAMP(), SYSDATE()

-- Date arithmetic
DATEADD(day, 7, date_column)
DATEDIFF(day, start_date, end_date)

-- Truncate to period
DATE_TRUNC('month', created_at)

-- Extract parts
YEAR(created_at), MONTH(created_at), DAY(created_at)
DAYOFWEEK(created_at)

-- Format
TO_CHAR(created_at, 'YYYY-MM-DD')
```

**String functions:**
```sql
-- Case-insensitive by default (depends on collation)
column ILIKE '%pattern%'
REGEXP_LIKE(column, 'pattern')

-- Parse JSON
column:key::string  -- dot notation for VARIANT
PARSE_JSON('{"key": "value"}')
GET_PATH(variant_col, 'path.to.key')

-- Flatten arrays/objects
SELECT f.value FROM table, LATERAL FLATTEN(input => array_col) f
```

**Semi-structured data:**
```sql
-- VARIANT type access
data:customer:name::STRING
data:items[0]:price::NUMBER

-- Flatten nested structures
SELECT
    t.id,
    item.value:name::STRING as item_name,
    item.value:qty::NUMBER as quantity
FROM my_table t,
LATERAL FLATTEN(input => t.data:items) item
```

**Performance tips:**
- Use clustering keys on large tables (not traditional indexes)
- Filter on clustering key columns for partition pruning
- Set appropriate warehouse size for query complexity
- Use `RESULT_SCAN(LAST_QUERY_ID())` to avoid re-running expensive queries
- Use transient tables for staging/temp data

---

### BigQuery (Google Cloud)

**Date/time:**
```sql
-- Current date/time
CURRENT_DATE(), CURRENT_TIMESTAMP()

-- Date arithmetic
DATE_ADD(date_column, INTERVAL 7 DAY)
DATE_SUB(date_column, INTERVAL 1 MONTH)
DATE_DIFF(end_date, start_date, DAY)
TIMESTAMP_DIFF(end_ts, start_ts, HOUR)

-- Truncate to period
DATE_TRUNC(created_at, MONTH)
TIMESTAMP_TRUNC(created_at, HOUR)

-- Extract parts
EXTRACT(YEAR FROM created_at)
EXTRACT(DAYOFWEEK FROM created_at)  -- 1=Sunday

-- Format
FORMAT_DATE('%Y-%m-%d', date_column)
FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', ts_column)
```

**String functions:**
```sql
-- No ILIKE, use LOWER()
LOWER(column) LIKE '%pattern%'
REGEXP_CONTAINS(column, r'pattern')
REGEXP_EXTRACT(column, r'pattern')

-- String manipulation
SPLIT(str, delimiter)  -- returns ARRAY
ARRAY_TO_STRING(array, delimiter)
```

**Arrays and structs:**
```sql
-- Array operations
ARRAY_AGG(column)
UNNEST(array_column)
ARRAY_LENGTH(array_column)
value IN UNNEST(array_column)

-- Struct access
struct_column.field_name
```

**Performance tips:**
- Always filter on partition columns (usually date) to reduce bytes scanned
- Use clustering for frequently filtered columns within partitions
- Use `APPROX_COUNT_DISTINCT()` for large-scale cardinality estimates
- Avoid `SELECT *` -- billing is per-byte scanned
- Use `DECLARE` and `SET` for parameterized scripts
- Preview query cost with dry run before executing large queries

---

### Redshift (Amazon)

**Date/time:**
```sql
-- Current date/time
CURRENT_DATE, GETDATE(), SYSDATE

-- Date arithmetic
DATEADD(day, 7, date_column)
DATEDIFF(day, start_date, end_date)

-- Truncate to period
DATE_TRUNC('month', created_at)

-- Extract parts
EXTRACT(YEAR FROM created_at)
DATE_PART('dow', created_at)
```

**String functions:**
```sql
-- Case-insensitive
column ILIKE '%pattern%'
REGEXP_INSTR(column, 'pattern') > 0

-- String manipulation
SPLIT_PART(str, delimiter, position)
LISTAGG(column, ', ') WITHIN GROUP (ORDER BY column)
```

**Performance tips:**
- Design distribution keys for collocated joins (DISTKEY)
- Use sort keys for frequently filtered columns (SORTKEY)
- Use `EXPLAIN` to check query plan
- Avoid cross-node data movement (watch for DS_BCAST and DS_DIST)
- `ANALYZE` and `VACUUM` regularly
- Use late-binding views for schema flexibility

---

### Databricks SQL

**Date/time:**
```sql
-- Current date/time
CURRENT_DATE(), CURRENT_TIMESTAMP()

-- Date arithmetic
DATE_ADD(date_column, 7)
DATEDIFF(end_date, start_date)
ADD_MONTHS(date_column, 1)

-- Truncate to period
DATE_TRUNC('MONTH', created_at)
TRUNC(date_column, 'MM')

-- Extract parts
YEAR(created_at), MONTH(created_at)
DAYOFWEEK(created_at)
```

**Delta Lake features:**
```sql
-- Time travel
SELECT * FROM my_table TIMESTAMP AS OF '2024-01-15'
SELECT * FROM my_table VERSION AS OF 42

-- Describe history
DESCRIBE HISTORY my_table

-- Merge (upsert)
MERGE INTO target USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

**Performance tips:**
- Use Delta Lake's `OPTIMIZE` and `ZORDER` for query performance
- Leverage Photon engine for compute-intensive queries
- Use `CACHE TABLE` for frequently accessed datasets
- Partition by low-cardinality date columns

---

### Oracle Database 19c

**Date/time:**
```sql
-- DATE always carries a time (to the second); TIMESTAMP(n) adds fractional seconds
SYSDATE, SYSTIMESTAMP  -- DB server OS clock: DATE / TIMESTAMP WITH TIME ZONE

-- Date arithmetic: plain numbers are days
order_date + 7, order_date - 1/24, order_date + INTERVAL '10' MINUTE
end_date - start_date  -- NUMBER of days (fraction = part of a day)
ADD_MONTHS(order_date, 1)  -- month-end in -> month-end out

-- Truncate to period (always returns DATE)
TRUNC(order_date)  -- midnight
TRUNC(order_date, 'MM'), TRUNC(order_date, 'Q'), TRUNC(order_date, 'IW')  -- IW = ISO Monday

-- Parse/format: always pass a format model; never rely on NLS_DATE_FORMAT
DATE '2024-01-31', TO_DATE('31/01/2024 13:45', 'DD/MM/YYYY HH24:MI')
TO_CHAR(order_date, 'YYYY-MM-DD HH24:MI:SS')

-- Whole-day filter: half-open range (= DATE '2024-01-31' misses rows after midnight)
WHERE order_date >= DATE '2024-01-01' AND order_date < DATE '2024-02-01'
```

**String functions:**
```sql
-- '' IS NULL: a zero-length string is NULL, so col = '' is never true
first_name || ' ' || last_name  -- || ignores NULLs ('a' || NULL = 'a')
NVL(col, 'n/a'), NVL2(col, 'set', 'unset'), COALESCE(a, b, c)
DECODE(status, 'A', 'Active', NULL, 'Missing', 'Other')  -- DECODE matches NULL to NULL

-- LISTAGG: 4000-byte limit (32767 if MAX_STRING_SIZE = EXTENDED); default ON OVERFLOW ERROR
LISTAGG(DISTINCT product_name, ', ' ON OVERFLOW TRUNCATE '...' WITH COUNT)
    WITHIN GROUP (ORDER BY product_name)

-- Regex (REGEXP_LIKE is a condition, not a function: use in WHERE / CASE WHEN)
WHERE REGEXP_LIKE(email, '^[^@]+@[^@]+$')
REGEXP_SUBSTR(str, '[0-9]+', 1, 2), REGEXP_REPLACE(str, '[[:space:]]+', ' ')
```

**Row limiting, KEEP, MERGE, hierarchies:**
```sql
-- Row limiting clause runs after ORDER BY (also OFFSET n ROWS, WITH TIES)
SELECT * FROM orders ORDER BY amount DESC FETCH FIRST 10 ROWS ONLY
-- ROWNUM pitfall: assigned before ORDER BY (and ROWNUM > n is never true)
SELECT * FROM orders WHERE ROWNUM <= 10 ORDER BY amount DESC  -- 10 arbitrary rows, sorted

-- KEEP: value from the first/last row of each group, no self-join
SELECT customer_id,
    MAX(amount) KEEP (DENSE_RANK LAST ORDER BY order_date) AS last_order_amount
FROM orders GROUP BY customer_id

MERGE INTO dim_customer t
USING stg_customer s
ON (t.customer_id = s.customer_id)  -- parentheses required; ON columns can't be updated
WHEN MATCHED THEN UPDATE SET t.name = s.name
    DELETE WHERE s.is_deleted = 'Y'  -- deletes only rows this MERGE just updated
WHEN NOT MATCHED THEN INSERT (customer_id, name) VALUES (s.customer_id, s.name)

-- CONNECT BY (Oracle-only) vs recursive WITH (no RECURSIVE keyword, column list required)
SELECT employee_id, LEVEL, SYS_CONNECT_BY_PATH(last_name, '/') AS path FROM employees
START WITH manager_id IS NULL CONNECT BY NOCYCLE PRIOR employee_id = manager_id

WITH org (employee_id, depth) AS (
    SELECT employee_id, 1 FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.employee_id, o.depth + 1 FROM employees e JOIN org o ON e.manager_id = o.employee_id
) SELECT * FROM org
```

**Performance tips:**
- Plans: `EXPLAIN PLAN FOR ...` then `SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY)`. For actual row counts, add `/*+ GATHER_PLAN_STATISTICS */` and run `DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST')`
- Partition pruning: compare the bare partition key with a DATE literal or an explicit-format `TO_DATE`. `TRUNC`/`CAST` or an implicit conversion on the key blocks pruning, so check `Pstart`/`Pstop` in the plan. Full partition-wise joins need both tables equipartitioned on the join key
- Materialized views: `REFRESH FAST` applies MV-log or partition-change-tracking deltas, `COMPLETE` rebuilds, `FORCE` tries fast first (`DBMS_MVIEW.REFRESH('MV', method => 'F'|'C'|'?'|'P')`). With `ENABLE QUERY REWRITE`, queries on base tables may silently read the MV, so check `EXPLAIN PLAN` / `DBMS_MVIEW.EXPLAIN_REWRITE` before porting
- Prefer ANSI `LEFT JOIN` to `(+)`: if `(+)` is left off one join condition, the join silently becomes an inner join
- Hints (`/*+ ... */`) are silently ignored when misspelled. Use them sparingly, and don't port them verbatim

---

### Microsoft Fabric (Warehouse and SQL analytics endpoint T-SQL, Spark SQL)

**Which engine:**
- **Warehouse**: read-write T-SQL (DDL, DML, `MERGE`, CTAS, `COPY INTO`, procedures). Snapshot isolation; write conflicts are detected per table
- **Lakehouse SQL analytics endpoint**: same engine, read-only over the lakehouse's Delta tables (views, functions, and procedures are allowed); sync lag is usually under a minute
- **Spark SQL (notebooks)** writes Lakehouse tables (Runtime 2.0 = Spark 4.1 / Delta 4.2). Three-part names (`my_lakehouse.dbo.orders`) cross items in one workspace

**Date/time (T-SQL):**
```sql
-- No SYSDATE; stored datetime2/time keep at most 6 fractional digits
SYSDATETIME(), GETDATE(), CAST(SYSDATETIME() AS datetime2(6))

-- Date arithmetic ("+ n" isn't allowed on date/datetime2)
DATEADD(day, 7, order_date)
DATEADD(month, 1, order_date)  -- clamps to month end, doesn't snap like ADD_MONTHS
DATEDIFF(day, start_date, end_date)  -- counts boundaries crossed; DATEDIFF_BIG for large spans

-- Truncate to period (returns the input's type)
DATETRUNC(month, order_date), EOMONTH(order_date)
DATETRUNC(iso_week, order_date)  -- Monday; DATETRUNC(week, ...) follows @@DATEFIRST

-- Parse/format with CONVERT styles
CONVERT(varchar(10), order_date, 23)  -- yyyy-MM-dd (126 = ISO 8601 with time)
CONVERT(date, '31/01/2024', 103)  -- dd/MM/yyyy
```

**String functions (T-SQL):**
```sql
-- '' is a real value (not NULL); + typically yields NULL if any operand is NULL
CONCAT(first_name, ' ', last_name), CONCAT_WS(', ', addr1, addr2, city)  -- NULL-safe
ISNULL(col, 'n/a')  -- col's type (can truncate); COALESCE uses the highest-precedence type
STRING_AGG(CAST(name AS varchar(max)), ', ') WITHIN GROUP (ORDER BY name)  -- no DISTINCT
WHERE REGEXP_LIKE(email, '^[^@]+@[^@]+$')  -- regex scalar functions: preview
-- Default collation Latin1_General_100_BIN2_UTF8 is case-sensitive; override per expression
WHERE name COLLATE Latin1_General_100_CI_AS_KS_WS_SC_UTF8 = 'acme'
```

**Row limiting:**
```sql
SELECT TOP (10) WITH TIES * FROM dbo.orders ORDER BY amount DESC
SELECT * FROM dbo.orders ORDER BY order_id OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY
-- QUALIFY (Fabric-only T-SQL): filter on window functions without a subquery
SELECT * FROM dbo.orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) = 1
```

**Surface area (Microsoft Learn, updated Sept–Oct 2026):**
- Supported: `MERGE` (GA, needs a terminating `;`), `TRUNCATE TABLE`, CTAS, `SELECT INTO`, `COPY INTO`, `#temp` tables (no `##global`), `ALTER TABLE` add nullable column / `DROP COLUMN` (`ALTER COLUMN` in preview), `sp_rename`
- `BIGINT IDENTITY` only (no seed or increment; unique but not sequential). PK/UNIQUE must be `NONCLUSTERED NOT ENFORCED` and FK `NOT ENFORCED`, all added via `ALTER TABLE`. No `DEFAULT` constraints
- Not supported: recursive CTEs, materialized views, triggers, sequences, synonyms, partitioned tables, computed columns, `SET TRANSACTION ISOLATION LEVEL`, multi-column statistics
- No `datetime`/`datetimeoffset`, `nvarchar`/`nchar`, `tinyint`, `money`, `xml` or `json` columns. Use `datetime2(0-6)`, UTF-8 `varchar`, `smallint`, `decimal`. `varchar(max)` holds up to 16 MB
- Lakehouse to SQL endpoint: Delta `STRING` becomes `varchar(8000)` (truncating), or `varchar(max)` with the new metadata sync. `TIMESTAMP` becomes `datetime2`. `TIMESTAMP_NTZ` isn't supported by the SQL endpoint or Direct Lake

**Spark SQL / Delta (Lakehouse notebooks):**
```sql
MERGE INTO silver.customer t USING staging.customer s
ON t.customer_id = s.customer_id
WHEN MATCHED AND s.is_deleted THEN DELETE
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *

OPTIMIZE silver.customer ZORDER BY (region) VORDER  -- compact; VORDER forces V-Order
VACUUM silver.customer RETAIN 168 HOURS  -- 7-day default; also limits time travel
SELECT * FROM silver.customer VERSION AS OF 42  -- or TIMESTAMP AS OF '2026-10-01'
```

**Performance tips:**
- Plans and history: `SET SHOWPLAN_XML ON` returns the estimated plan without executing. `queryinsights.exec_requests_history` / `long_running_queries` keep 30 days of history
- Statistics are auto-created and refreshed at query time. Manual `CREATE`/`UPDATE STATISTICS ... WITH FULLSCAN` is single-column only; inspect with `DBCC SHOW_STATISTICS`
- Warehouse tables can't be partitioned; use `CLUSTER BY` (preview, up to 4 columns, set at `CREATE TABLE`). V-Order is on by default, and disabling it is irreversible
- Lakehouse: new workspaces default to the `writeHeavy` profile (V-Order off). For Direct Lake tables, enable V-Order or use `readHeavyForPBI`, schedule `OPTIMIZE`, and avoid high-cardinality partitions. Direct Lake on SQL falls back to DirectQuery when it reads SQL views
- Warehouse time travel: `OPTION (FOR TIMESTAMP AS OF '2026-10-01T00:00:00')`. Timestamps are UTC with at most 3 fractional digits; retention is 1–120 days (default 30)

---

### Porting Oracle to Fabric — common gotchas

| Oracle construct | Fabric T-SQL / Spark SQL equivalent | Note |
|---|---|---|
| `NVL(a, b)`, `NVL2` | `COALESCE(a, b)` or `ISNULL(a, b)`; Spark has `nvl`, `nvl2` | `ISNULL` returns `a`'s type, which can truncate `b` |
| `''` is NULL | `''` is a non-NULL value in T-SQL and Spark | Convert on load (`NULLIF(col, '')`) or rewrite `IS NULL` filters; `'a' + NULL` is NULL, so use `CONCAT` |
| `DATE` (has a time) | `datetime2(0)`, or `date` only if the time is always midnight; Spark `TIMESTAMP` | `datetime2` starts at year 0001 (Oracle allows 4712 BC); `TIMESTAMP(7-9)` loses digits beyond 6; avoid Spark `TIMESTAMP_NTZ` |
| `NUMBER(p,s)` / bare `NUMBER` | `decimal(p,s)` (p ≤ 38, 0 ≤ s ≤ p); `int`/`bigint` for small `NUMBER(p)` | Bare `NUMBER` has no fixed scale: profile the data, then pick `decimal(38,s)` or `float`. Negative scale isn't supported |
| `VARCHAR2(n BYTE \| CHAR)`, `NVARCHAR2`, `CLOB` | `varchar(n)` (UTF-8, n = bytes); `varchar(max)` | With `CHAR` semantics and multibyte data, size by bytes (up to 4n). No `nvarchar` columns |
| Sequence `.NEXTVAL` / identity | `BIGINT IDENTITY` (Warehouse); `ROW_NUMBER()` + current max key (Spark) | No `SEQUENCE`. IDENTITY values have gaps and no order. Delta identity-column writes aren't supported in Fabric. Load legacy keys with `IDENTITY_INSERT`, then `DBCC CHECKIDENT(..., RESEED)` |
| `ROWNUM <= n` | `TOP (n)`, `OFFSET ... FETCH`, `ROW_NUMBER()` + `QUALIFY`; Spark `LIMIT` | `ROWNUM` before `ORDER BY` returned arbitrary rows; port the intended order |
| `(+)` outer join | `LEFT` / `RIGHT JOIN ... ON` | Predicates that carry `(+)` on the optional table go in `ON`, not `WHERE` |
| `CONNECT BY` / recursive `WITH` | No recursive CTEs in Warehouse or SQL endpoint; flatten in Spark or precompute a path/bridge table | Apache Spark 4.1 (Runtime 2.0) release notes list recursive CTEs; test before relying on them |
| `DECODE` | `CASE`, `IIF`; Spark `decode()` | `DECODE` treats NULL = NULL; `CASE x WHEN NULL` never matches, so add `WHEN x IS NULL` |
| `LISTAGG ... WITHIN GROUP` | `STRING_AGG(...) WITHIN GROUP (ORDER BY ...)`; Spark `listagg` / `string_agg` | T-SQL has no `DISTINCT` or `ON OVERFLOW`: dedupe in a subquery, and cast to `varchar(max)` for results over 8000 bytes |
| `MINUS` | `EXCEPT`; Spark accepts `EXCEPT` or `MINUS` | |
| `SYSDATE` / `SYSTIMESTAMP` | `SYSDATETIME()`, `GETDATE()`; Spark `current_timestamp()` | `SYSDATE` is the DB server's OS clock; check which time zone the Fabric clock uses (time travel is UTC) |
| `TRUNC(d)`, `TRUNC(d, 'MM')`, `ADD_MONTHS` | `CAST(d AS date)`, `DATETRUNC(month, d)`, `DATEADD(month, n, d)`; Spark `trunc`, `date_trunc`, `add_months` | `'IW'` maps to `iso_week`. `DATEADD` only clamps (02-29 + 1 month = 03-29) where `ADD_MONTHS` keeps month-end, so use `EOMONTH` |
| `MERGE` | T-SQL `MERGE` (GA); Spark `MERGE INTO` | T-SQL: parentheses around `ON` are optional, at most 2 `WHEN MATCHED` (one `UPDATE`, one `DELETE`), and `WHEN NOT MATCHED BY SOURCE` is available. Oracle's `UPDATE ... DELETE WHERE` becomes a second `WHEN MATCHED AND ... THEN DELETE`. A terminating `;` is required. Dedupe the source in every engine |
| PL/SQL packages, procedures, triggers | Warehouse T-SQL stored procedures (group them by schema); Spark notebooks for Lakehouse logic; pipelines for orchestration | No packages or triggers. Table-level write conflicts mean writers to one table must be serialised |
| Materialized views + query rewrite | Warehouse: CTAS / aggregate tables refreshed by procedures or pipelines. Lakehouse: `CREATE MATERIALIZED LAKE VIEW` (Fabric picks incremental, full, or skip refresh) | No transparent query rewrite, so point reports at the aggregate. MLVs reject all-uppercase schema names (`SALES`) |
| Partitioning, partition pruning | Warehouse: none, use `CLUSTER BY` (preview). Lakehouse: Delta partitions, liquid clustering, Z-Order | Don't carry daily/high-cardinality partitions into Delta; aim for at least ~1 GB per partition |
| Synonyms, virtual columns, `DEFAULT` | Not supported in Warehouse | Resolve names when porting; compute in views/ETL; supply defaults in `INSERT` |
| Collation (`NLS_COMP = BINARY` default) | `Latin1_General_100_BIN2_UTF8` default (also case-sensitive); a CI warehouse can be chosen only at creation | Joins, filters and `DISTINCT` change if either side is CI (`NLS_COMP=LINGUISTIC` or a CI warehouse). Cross-warehouse queries across collations can fail; use `COLLATE` per expression |
| Hints `/*+ ... */` | Subset of T-SQL query/join hints | Drop Oracle hints; re-tune from the Fabric plan |

---

## Common SQL Patterns

### Window Functions

```sql
-- Ranking
ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC)
RANK() OVER (PARTITION BY category ORDER BY revenue DESC)
DENSE_RANK() OVER (ORDER BY score DESC)

-- Running totals / moving averages
SUM(revenue) OVER (ORDER BY date_col ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as running_total
AVG(revenue) OVER (ORDER BY date_col ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7d

-- Lag / Lead
LAG(value, 1) OVER (PARTITION BY entity ORDER BY date_col) as prev_value
LEAD(value, 1) OVER (PARTITION BY entity ORDER BY date_col) as next_value

-- First / Last value
FIRST_VALUE(status) OVER (PARTITION BY user_id ORDER BY created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
LAST_VALUE(status) OVER (PARTITION BY user_id ORDER BY created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)

-- Percent of total
revenue / SUM(revenue) OVER () as pct_of_total
revenue / SUM(revenue) OVER (PARTITION BY category) as pct_of_category
```

### CTEs for Readability

```sql
WITH
-- Step 1: Define the base population
base_users AS (
    SELECT user_id, created_at, plan_type
    FROM users
    WHERE created_at >= DATE '2024-01-01'
      AND status = 'active'
),

-- Step 2: Calculate user-level metrics
user_metrics AS (
    SELECT
        u.user_id,
        u.plan_type,
        COUNT(DISTINCT e.session_id) as session_count,
        SUM(e.revenue) as total_revenue
    FROM base_users u
    LEFT JOIN events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u.plan_type
),

-- Step 3: Aggregate to summary level
summary AS (
    SELECT
        plan_type,
        COUNT(*) as user_count,
        AVG(session_count) as avg_sessions,
        SUM(total_revenue) as total_revenue
    FROM user_metrics
    GROUP BY plan_type
)

SELECT * FROM summary ORDER BY total_revenue DESC;
```

### Cohort Retention

```sql
WITH cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', first_activity_date) as cohort_month
    FROM users
),
activity AS (
    SELECT
        user_id,
        DATE_TRUNC('month', activity_date) as activity_month
    FROM user_activity
)
SELECT
    c.cohort_month,
    COUNT(DISTINCT c.user_id) as cohort_size,
    COUNT(DISTINCT CASE
        WHEN a.activity_month = c.cohort_month THEN a.user_id
    END) as month_0,
    COUNT(DISTINCT CASE
        WHEN a.activity_month = c.cohort_month + INTERVAL '1 month' THEN a.user_id
    END) as month_1,
    COUNT(DISTINCT CASE
        WHEN a.activity_month = c.cohort_month + INTERVAL '3 months' THEN a.user_id
    END) as month_3
FROM cohorts c
LEFT JOIN activity a ON c.user_id = a.user_id
GROUP BY c.cohort_month
ORDER BY c.cohort_month;
```

### Funnel Analysis

```sql
WITH funnel AS (
    SELECT
        user_id,
        MAX(CASE WHEN event = 'page_view' THEN 1 ELSE 0 END) as step_1_view,
        MAX(CASE WHEN event = 'signup_start' THEN 1 ELSE 0 END) as step_2_start,
        MAX(CASE WHEN event = 'signup_complete' THEN 1 ELSE 0 END) as step_3_complete,
        MAX(CASE WHEN event = 'first_purchase' THEN 1 ELSE 0 END) as step_4_purchase
    FROM events
    WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT
    COUNT(*) as total_users,
    SUM(step_1_view) as viewed,
    SUM(step_2_start) as started_signup,
    SUM(step_3_complete) as completed_signup,
    SUM(step_4_purchase) as purchased,
    ROUND(100.0 * SUM(step_2_start) / NULLIF(SUM(step_1_view), 0), 1) as view_to_start_pct,
    ROUND(100.0 * SUM(step_3_complete) / NULLIF(SUM(step_2_start), 0), 1) as start_to_complete_pct,
    ROUND(100.0 * SUM(step_4_purchase) / NULLIF(SUM(step_3_complete), 0), 1) as complete_to_purchase_pct
FROM funnel;
```

### Deduplication

```sql
-- Keep the most recent record per key
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY entity_id
            ORDER BY updated_at DESC
        ) as rn
    FROM source_table
)
SELECT * FROM ranked WHERE rn = 1;
```

## Error Handling and Debugging

When a query fails:

1. **Syntax errors**: Check for dialect-specific syntax (e.g., `ILIKE` not available in BigQuery, `SAFE_DIVIDE` only in BigQuery)
2. **Column not found**: Verify column names against schema -- check for typos, case sensitivity (PostgreSQL is case-sensitive for quoted identifiers)
3. **Type mismatches**: Cast explicitly when comparing different types (`CAST(col AS DATE)`, `col::DATE`)
4. **Division by zero**: Use `NULLIF(denominator, 0)` or dialect-specific safe division
5. **Ambiguous columns**: Always qualify column names with table alias in JOINs
6. **Group by errors**: All non-aggregated columns must be in GROUP BY (except in BigQuery which allows grouping by alias)
