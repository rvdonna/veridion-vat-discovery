import time
import requests
import pandas as pd

tabel_1 = pd.read_csv("data/75_companies.csv")
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

gasite_peppol = 0
gasite_ch = 0
gasite_gazette = 0

print("Rulam sondajele pe cele 2 surse ...")

for i, row in tabel_1.iterrows():
    nume = str(row["CompanyName"]).strip()
    nume_curat = nume.replace("LIMITED", "").replace("LTD", "").strip()
    print(f"[{i+1}/75] Verific {nume_curat}...")
  
    try:
        peppol = requests.get(
            f"https://directory.peppol.eu/search/1.0/json?q={requests.utils.quote(nume_curat)}",
            headers=headers,
            timeout=6
        )
        if peppol.status_code == 200 and "9932:GB" in peppol.text:
            print(f"Am gasit firma {(nume_curat)} folosind peppol")
            gasite_peppol += 1
    except Exception:
        pass

    
    try:
        Gazette = requests.get(
            f"https://www.thegazette.co.uk/all-notices/notice/data.json?text={requests.utils.quote(nume_curat)}",
            headers=headers,
            timeout=6
        )
        if Gazette.status_code == 200 and "VAT" in Gazette.text.upper():
            print(f"Am gasit firma {(nume_curat)} folosind Gazette")
            gasite_gazette += 1
    except Exception:
        pass

    time.sleep(0.3)

print("\n--- REZULTATE RESEARCH PROBES ---")
print(f"1. PEPPOL Directory : {gasite_peppol} din 75")
print(f"2. The Gazette (Public Records): {gasite_gazette} din 75")