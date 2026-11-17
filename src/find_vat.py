import re
import time
import html
import requests
import pandas as pd


def valid_uk_vat_checksum(vat_9: str) -> bool:
    if not vat_9.isdigit() or len(vat_9) != 9:
        return False

    weights = [8, 7, 6, 5, 4, 3, 2]
    total = 0
    for i in range(7):
        total = total + (int(vat_9[i]) * weights[i])
    check = int(vat_9[7:])

    return check in ((97 - total % 97) % 97, (97 - (total + 55) % 97) % 97)


def verify_hmrc_web(session: requests.Session, vat_9: str):
    url = "https://www.tax.service.gov.uk/check-vat-number/enter-vat-details"
    try:
        r_get = session.get(url, timeout=10)
        m_csrf = re.search(r'name="csrfToken"\s+value="([^"]+)"', r_get.text)
        if not m_csrf:
            return None
        csrf = m_csrf.group(1)

        r_post = session.post(
            url,
            data={"csrfToken": csrf, "target": vat_9},
            timeout=10
        )
        if "Valid UK VAT number" in r_post.text:
            m_name = re.search(
                r'<p class="govuk-body">([^<]+)</p>',
                r_post.text
            )
            if m_name:
                return html.unescape(m_name.group(1).strip())
    except Exception:
        pass
    return None


def search_web_candidates(session: requests.Session, company_name: str, postcode: str, crn: str):
    clean_name = re.sub(r"\b(LIMITED|LTD|PLC|UK)\b", "", company_name.upper()).strip()
    queries = [
        f'"{clean_name}" "VAT" GB',
        f'{clean_name} "{postcode}" VAT'
    ]
    candidates = []
    crn_digits = re.sub(r"\D", "", crn)

    for q in queries:
        url = f"https://uk.search.yahoo.com/search?p={requests.utils.quote(q)}"
        try:
            resp = session.get(url, timeout=8)
            if resp.status_code != 200:
                continue
            text = re.sub(r"<[^>]+>", " ", resp.text)
            text = html.unescape(re.sub(r"\s+", " ", text))

            matches = re.findall(
                r"(?:VAT|GB)[^\d]{0,20}(\d{3}\s?\d{4}\s?\d{2}|\d{9})",
                text,
                flags=re.IGNORECASE
            )
            for raw in matches:
                digits = re.sub(r"\D", "", raw)
                if len(digits) == 9 and digits != crn_digits and digits != crn_digits.zfill(9):
                    if valid_uk_vat_checksum(digits) and digits not in candidates:
                        candidates.append(digits)
        except Exception:
            continue

        if candidates:
            break

    return candidates


df = pd.read_csv("data/75_companies.csv")
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
})

coduri_vat = []
nume_hmrc_lista = []
surse_lista = []
gasite = 0

for index, row in df.iterrows():
    nume = str(row["CompanyName"]).strip()
    crn = str(row["CompanyNumber"]).strip()
    postcode = str(row["RegAddress.PostCode"]).strip()

    coduri_valide_matematic = search_web_candidates(session, nume, postcode, crn)
    vat_valid = None
    nume_oficial = None
    sursa_gasita = None

    tokens_firma = [
        t for t in re.sub(r"[^A-Z0-9\s]", "", nume.upper()).split()
        if t not in {"LIMITED", "LTD", "THE", "AND", "UK", "HOLDINGS"}
    ]

    for cod in coduri_valide_matematic:
        hmrc_name = verify_hmrc_web(session, cod)
        if hmrc_name:
            hmrc_upper = hmrc_name.upper()
            if any(tok in hmrc_upper for tok in tokens_firma[:2]):
                vat_valid = "GB" + cod
                nume_oficial = hmrc_name
                sursa_gasita = "WEB_SEARCH + HMRC_VERIFIED"
                gasite += 1
                break

    coduri_vat.append(vat_valid)
    nume_hmrc_lista.append(nume_oficial)
    surse_lista.append(sursa_gasita)

    print(f"[{index+1}/75] {nume} -> Candidate Mod97: {coduri_valide_matematic} -> {vat_valid if vat_valid else 'Negasit'}")
    time.sleep(1.2)

df["VAT_Number"] = coduri_vat
df["Verified_Name"] = nume_hmrc_lista
df["Discovery_Source"] = surse_lista
df.to_csv("data/vat_results.csv", index=False)

print(f"\nTotal VAT gasite si confirmate: {gasite} din 75")