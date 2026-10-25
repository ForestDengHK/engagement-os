# Sources for kw-dialects.md (retrieved 2026-10-25)

Dates: Microsoft Learn = the page's displayed "Last updated on" date. Oracle HTML pages show no per-page date, so each one gets its book's part number and revision month from the book's title page. Delta Lake and Apache Spark pages show no date.

## 1. Oracle Database 19c

Books (all 19c):
- SQL Language Reference E96310-37, August 2026: https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/index.html
- PL/SQL Packages and Types Reference E96430-45, October 2026: https://docs.oracle.com/en/database/oracle/oracle-database/19/arpls/index.html
- Database Reference E96196-45, September 2026: https://docs.oracle.com/en/database/oracle/oracle-database/19/refrn/index.html
- VLDB and Partitioning Guide E96199-12, March 2024: https://docs.oracle.com/en/database/oracle/oracle-database/19/vldbg/index.html
- Data Warehousing Guide E96243-05, March 2021. This is the oldest source used, but it is still the current 19c edition: https://docs.oracle.com/en/database/oracle/oracle-database/19/dwhsg/index.html

Pages (prefix https://docs.oracle.com/en/database/oracle/oracle-database/19/):
- sqlrf/Data-Types.html: DATE fields and range, TIMESTAMP precision 0-9, NUMBER(p,s) and bare NUMBER, VARCHAR2 BYTE/CHAR and NLS_LENGTH_SEMANTICS, "Datetime/Interval Arithmetic" (numbers = days)
- sqlrf/Nulls.html: zero-length string treated as NULL; concatenation is the only operator that doesn't return NULL; DECODE treats NULL = NULL
- sqlrf/TRUNC-date.html, sqlrf/ROUND-and-TRUNC-Date-Functions.html (Table 7-13: IW = ISO Monday, D/DAY depend on NLS_TERRITORY)
- sqlrf/ADD_MONTHS.html (month-end rule), sqlrf/SYSDATE.html, sqlrf/SYSTIMESTAMP.html, sqlrf/TO_DATE.html, sqlrf/Literals.html (INTERVAL '10' MINUTE)
- sqlrf/LISTAGG.html: DISTINCT, ON OVERFLOW ERROR (default) / TRUNCATE ... WITH COUNT, 4000/32767-byte limits
- sqlrf/NVL2.html, sqlrf/DECODE.html, sqlrf/REGEXP_SUBSTR.html (position, occurrence), sqlrf/Pattern-matching-Conditions.html ("REGEXP_LIKE Condition")
- sqlrf/SELECT.html: row_limiting_clause, recursive subquery factoring rules and SEARCH clause; syntax text in sqlrf/img_text/row_limiting_clause.html and sqlrf/img_text/subquery_factoring_clause.html (no RECURSIVE keyword)
- sqlrf/ROWNUM-Pseudocolumn.html: ROWNUM assigned before ORDER BY; ROWNUM > n is always false
- sqlrf/FIRST.html: KEEP (DENSE_RANK FIRST/LAST)
- sqlrf/MERGE.html and sqlrf/img_text/merge.html: `ON ( condition )`, ON columns can't be updated, DELETE WHERE affects only updated rows, can't update the same row twice
- sqlrf/Hierarchical-Queries.html: CONNECT BY, NOCYCLE, SYS_CONNECT_BY_PATH, ORDER SIBLINGS BY
- sqlrf/Joins.html: (+) restrictions, including the silent inner join when (+) is missing from one condition
- sqlrf/The-UNION-ALL-INTERSECT-MINUS-Operators.html
- sqlrf/EXPLAIN-PLAN.html; arpls/DBMS_XPLAN.html: DISPLAY, DISPLAY_CURSOR, the 'ALLSTATS LAST' format, gather_plan_statistics
- sqlrf/Comments.html (Hints): use sparingly; misspelled hints are ignored without error
- vldbg/partition-pruning.html (3.1.7 tips: TRUNC/CAST and implicit conversions on the key block pruning; Pstart/Pstop); vldbg/partition-wise-joins.html (equipartitioning or reference partitioning)
- dwhsg/refreshing-materialized-views.html (Table 7-1: C/F/P/?), dwhsg/basic-query-rewrite-materialized-views.html (QUERY_REWRITE_ENABLED, QUERY_REWRITE_INTEGRITY=ENFORCED default, EXPLAIN_REWRITE), dwhsg/basic-materialized-views.html
- sqlrf/CREATE-MATERIALIZED-VIEW.html; arpls/DBMS_MVIEW.html
- refrn/NLS_COMP.html: default BINARY

## 2. Microsoft Fabric

Fabric pages (prefix https://learn.microsoft.com/en-us/fabric/):
- data-warehouse/tsql-surface-area: 2026-09-29. Covers MERGE GA, IDENTITY, #temp tables, TRUNCATE, ALTER TABLE subset, ALTER COLUMN preview, QUALIFY, GROUP BY ALL, and the unsupported list (recursive queries, materialized views, triggers, synonyms, SET TRANSACTION ISOLATION LEVEL, multi-column statistics, regex TVFs)
- data-warehouse/tables: 2026-10-14. CTAS, unsupported features (partitioned tables, sequence, computed columns, triggers, synonyms), collation, statistics
- data-warehouse/data-types: 2026-06-11. Supported and unsupported types, datetime2 precision of 6, 16 MB varchar(max), Delta-to-SQL mapping
- data-warehouse/collation: 2025-08-14
- data-warehouse/table-constraints: 2026-09-09
- data-warehouse/identity: 2026-08-26
- data-warehouse/temp-tables: 2026-07-27
- data-warehouse/ingest-data-copy: 2026-06-24
- data-warehouse/statistics: 2025-12-11
- data-warehouse/time-travel: 2026-05-21
- data-warehouse/query-warehouse: 2026-02-13 (cross-database, three-part names)
- data-warehouse/limitations: 2026-09-02 (same-region requirement)
- data-warehouse/transactions: 2026-06-03 (snapshot isolation, table-level write-write conflicts)
- data-warehouse/data-clustering: 2025-11-18 (CLUSTER BY, preview, up to 4 columns)
- data-warehouse/guidelines-warehouse-performance: 2026-06-15 (Warehouse V-Order on by default; disabling it is irreversible)
- data-warehouse/query-insights: 2026-08-24
- data-warehouse/migration-assistant: 2026-09-29 (sources: Synapse dedicated pool, SQL Server, Teradata preview; Oracle isn't listed)
- data-warehouse/sql-analytics-endpoint-performance: 2026-09-16 (sync lag, partition size of about 1 GB)
- data-engineering/lakehouse-sql-analytics-endpoint: 2026-10-07 (read-only; varchar(max) only with the new metadata sync)
- data-engineering/delta-optimization-and-v-order: 2026-08-04
- data-engineering/configure-resource-profile-configurations: 2026-03-05 (writeHeavy default)
- data-engineering/table-compaction: 2026-08-25 (OPTIMIZE ... ZORDER BY ... VORDER)
- data-engineering/lakehouse-table-maintenance: 2026-08-04 (VACUUM 7-day default)
- data-engineering/runtime: 2026-10-22 (Runtime 2.0 GA default with Spark 4.1 and Delta 4.2; Runtime 1.3 EOSA)
- data-engineering/materialized-lake-views/overview-materialized-lake-view: 2026-09-30
- data-engineering/materialized-lake-views/create-materialized-lake-view: 2026-09-30 (no all-uppercase schema names)
- fundamentals/delta-lake-interoperability: 2026-10-07 (TIMESTAMP_NTZ not supported by the SQL endpoint or Direct Lake; Delta identity-column writes unsupported)
- fundamentals/table-maintenance-optimization: 2026-08-26
- fundamentals/direct-lake-overview: 2026-09-18 (Direct Lake on SQL falls back to DirectQuery for views)

T-SQL reference pages (prefix https://learn.microsoft.com/en-us/sql/t-sql/, `?view=fabric`). Each one's "Applies to" includes Warehouse in Microsoft Fabric:
- statements/merge-transact-sql: 2026-07-21 (Fabric syntax block; `;` required)
- queries/select-qualify-clause-transact-sql: 2026-09-29 (applies only to Fabric)
- queries/nested-common-table-expression: 2025-10-06 (recursive CTEs not supported)
- functions/datetrunc-transact-sql: 2026-09-21; functions/eomonth-transact-sql: 2026-10-08; functions/dateadd-transact-sql: 2026-09-21; functions/datediff-transact-sql: 2026-10-08
- functions/cast-and-convert-transact-sql: 2026-10-14 (styles 23, 103, 112, 126)
- functions/string-agg-transact-sql: 2025-11-18; functions/concat-ws-transact-sql: 2025-11-18; functions/concat-transact-sql, functions/isnull-transact-sql, language-elements/coalesce-transact-sql, language-elements/string-concatenation-transact-sql, language-elements/add-transact-sql: all 2026-09-21
- functions/regexp-like-transact-sql: 2026-10-14 (preview in Fabric DW)
- statements/collations: 2026-09-21 (COLLATE unrestricted in SELECT)
- statements/set-showplan-xml-transact-sql: 2026-07-21
- queries/top-transact-sql, queries/select-order-by-clause-transact-sql, data-types/datetime2-transact-sql, data-types/char-and-varchar-transact-sql, language-elements/set-operators-except-and-intersect-transact-sql: all 2026-09-21; data-types/decimal-and-numeric-transact-sql: 2026-10-14

Delta Lake (no date shown): https://docs.delta.io/delta-batch/ (time travel), https://docs.delta.io/delta-update/ (MERGE, WHEN NOT MATCHED BY SOURCE, multiple-match failure), https://docs.delta.io/delta-utility/ (VACUUM 7-day default, DESCRIBE HISTORY, RESTORE)

## 3. Porting table
Uses the sources above, plus:
- Apache Spark 4.1.0 SQL built-in functions (nvl, nvl2, decode, trunc, date_trunc, add_months, listagg, string_agg): https://spark.apache.org/docs/4.1.0/api/sql/index.html
- Spark 4.1.0 set operators (EXCEPT | MINUS): https://spark.apache.org/docs/4.1.0/sql-ref-syntax-qry-select-setops.html
- Spark 4.1.0 release notes ("[SPARK-24497] Recursive CTE support"): https://spark.apache.org/releases/spark-release-4.1.0.html

## Conflicts found
1. varchar(max) cap. The Fabric data-types page (2026-06-11) and the SQL endpoint page (2026-10-07) say 16 MB, but the T-SQL char/varchar reference (2026-09-21) says "1 MB in Fabric Data Warehouse". I used 16 MB because two Fabric-specific pages agree; the 1 MB figure looks like the old preview limit.
2. Lakehouse STRING mapping. The data-types page (2026-06-11) says varchar(8000). The SQL endpoint page (2026-10-07) says varchar(max) is available on endpoints with the new metadata sync, and 8 KB truncation applies otherwise. I reported both.
3. Automatic statistics. The tables page (2026-10-14) says "Statistical updating doesn't happen automatically." The statistics page (2025-12-11) describes automatic create and refresh at query time plus proactive refresh. I trust the statistics page because it is the detailed, feature-specific page; manual UPDATE STATISTICS after big loads is harmless either way.
4. Spark V-Order default. The runtime page (2026-10-22) says the native writers "default to V-order". The V-Order page (2026-08-04) and resource-profile page (2026-03-05) say V-Order is off by default in new workspaces (writeHeavy, `spark.sql.parquet.vorder.default=false`). I trust the latter two: they give the explicit config value and agree with each other. The runtime-page text looks stale. The Warehouse is a separate case, with V-Order on by default.
5. SQL endpoint collation. The data-types page says Lakehouse varchar columns get Latin1_General_100_BIN2_UTF8. The collation page says SQL analytics endpoints follow the workspace default collation, which can be CI. This is unresolved; check sys.databases on the endpoint.
6. Minor: the time-travel page says both that time-travel hints "can be used with" temp tables and that they "don't affect" them. This doesn't change the guidance.

## Unverified / omitted
- Case sensitivity of identifiers (table and column names) under the BIN2 collation. No Fabric page states it, so I omitted it.
- Which time zone GETDATE()/SYSDATETIME() use in Fabric. Not found, so the porting table only says to check it.
- Recursive CTE syntax in Spark (`WITH RECURSIVE`) and whether Fabric Runtime 2.0 exposes it. The only source is a line in the Apache release notes, and the Spark 4.1 CTE reference page doesn't document it. I gave no syntax.
- Spark ANSI-mode default in Fabric Runtime 2.0, and Spark add_months month-end behaviour beyond the doc example. Not checked; omitted.
- Whether Fabric MERGE supports an OUTPUT clause. The Fabric/Synapse syntax block lists none, but no page says so explicitly; omitted.
- ISNULL truncating the replacement value is inferred from "returns the same type as check_expression".
- The STRING_AGG 8000-byte behaviour is inferred from the return-type table (varchar(1..8000) input gives varchar(8000)); the exact error isn't quoted.
- No DISTINCT in STRING_AGG is inferred from the syntax block.
- Whether SET DATEFIRST works in Fabric. Not checked.
- Oracle REGEXP_COUNT/REGEXP_INSTR, CURRENT_DATE, and the plan operation name for MV rewrite: not checked, so left out.
- Power BI aggregations and other semantic-model alternatives to MVs: not checked, so left out.
- Cross-workspace T-SQL without OneLake shortcuts: not verified. The section says "one workspace".
- Oracle-specific migration tooling (for example SSMA for Oracle targeting Fabric): not checked. The Fabric Migration Assistant lists no Oracle source.
