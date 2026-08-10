import duckdb
import polars as pl
import pyarrow as pa

# 1. DuckDB: conexão em memória, query simples
con = duckdb.connect(":memory:")
resultado = con.execute("SELECT 1 + 1 AS soma").fetchone()
print("DuckDB OK — SELECT 1+1 =", resultado[0])

# 2. Polars: criar um DataFrame simples e agregar
df = pl.DataFrame({"heroi": ["Bane", "Bane", "Hoodwink"], "vitoria": [1, 0, 1]})
agregado = df.group_by("heroi").agg(pl.col("vitoria").sum())
print("Polars OK —\n", agregado)

# 3. PyArrow: criar uma Table e confirmar schema
tabela = pa.table({"col": [1, 2, 3]})
print("PyArrow OK — schema:", tabela.schema)

# 4. Integração: DuckDB lendo direto de um DataFrame Polars (sem cópia via pandas)
resultado_integrado = con.execute("SELECT heroi, SUM(vitoria) FROM df GROUP BY heroi").fetchall()
print("DuckDB + Polars integrados OK —", resultado_integrado)
