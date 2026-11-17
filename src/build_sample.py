import sqlite3
import pandas as pd

zip_path = "data/BasicCompanyDataAsOneFile-2026-11-01.zip"

tabel_1 = pd.read_csv(zip_path, nrows=800000, low_memory=False)

tabel_1.columns = [c.strip().replace(".", "_") for c in tabel_1.columns]

conn = sqlite3.connect(":memory:")
tabel_1.to_sql("companies", conn, index=False, if_exists="replace")

tabel_sql = """
SELECT 
    CompanyName, 
    CompanyNumber, 
    CompanyCategory, 
    CompanyStatus, 
    RegAddress_PostCode AS "RegAddress.PostCode",
    Accounts_AccountCategory AS "Accounts.AccountCategory",
    SICCode_SicText_1 AS "SICCode.SicText_1"
FROM companies
WHERE CompanyStatus = 'Active'
  AND CompanyCategory = 'Private Limited Company'
  AND RegAddress_PostCode IS NOT NULL
  AND TRIM(RegAddress_PostCode) != ''
  AND Accounts_AccountCategory IN ('FULL', 'MEDIUM')
  AND UPPER(CompanyName) NOT LIKE '%HOLDING%'
  AND UPPER(CompanyName) NOT LIKE '%PROPERTIES%'
  AND UPPER(CompanyName) NOT LIKE '%INVESTMENTS%'
  AND UPPER(CompanyName) NOT LIKE '%GROUP%'
"""
tabel_final = pd.read_sql_query(tabel_sql, conn)
conn.close()

compns = tabel_final.sample(n=75, random_state=42)
compns.to_csv("data/75_companies.csv", index=False)

print(f"Am salvat 75 in data/75_companies.csv")