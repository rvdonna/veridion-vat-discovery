  UK VAT Discovery & Validation Pipeline

A simple and efficient script for extracting and validating VAT numbers for companies in the UK, starting from raw Companies House data.



 What the project does (and how it's structured)

1. `build_sample.py` (Data Cleaning):
   * I tried to filter out inactive companies, micro-entities, or those with revenues lower than £90,000. These don't have a declared VAT number, and the chances of my program selecting such companies were high.
   * I extracted a clean sample of 75 companies.

2. `research_probes.py` (Testing Alternative Sources):
   I chose 2 sources to test direct registries:
   * PEPPOL Directory: The official European e-invoicing network where many companies keep an identification code like `9932:GB` followed by the VAT number. The result was 0 out of 75, which showed me that ordinary private companies in the UK do not use PEPPOL for invoicing.
   * The Gazette: The Official Public Record where major changes, insolvencies, and legal corporate notices are published. Result: 15 out of 75 (20%), which indicates that while it serves as a reliable secondary source for companies with recent legal filings, it depends too heavily on specific corporate events to be used as a primary VAT discovery tool.

3. `find_vat.py` (Project Core - Search & Validation):
   * I used the Modulo 97 rule (the first 7 digits multiplied by fixed weights and divided by 97 must yield the exact last 2 digits).(I just found out about i had no idea that such thing existed)
   * I put it in the code because web pages on the internet are full of 9-digit numbers (phone numbers, addresses, internal codes). Without this filter, sending all numbers to HMRC would waste time and potentially throw errors. This mathematical function locally checks if a number has the structure of a VAT number.



 Problems I encountered along the way (and how I solved them)

* Sample size and RAM memory:
  * What happened: Initially, I ran into inactive companies or micro-entities (which under £90k don't have a VAT obligation). Also, to avoid maxing out RAM on a test program, I made the selection from the first 800,000 companies in the archive , in order to run smoothly and faster.
  * How I solved it (`build_sample.py`):* I introduced a strict filter: Active companies, Private Limited structures, valid postcodes, and FULL or MEDIUM accounting tiers, while eliminating holding companies and passive real estate firms.

* Incomplete coverage of direct registries:
  * What happened: I initially assumed I could pull most VAT numbers directly from PEPPOL or The Gazette.
  * How I solved it: The test script `research_probes.py` showed that while The Gazette provides solid data for about 20% of companies, these registries are insufficient as standalone primary sources.

* IP blocks and Rate-Limiting on the search engine:
  * What happened: Automated queries on the search engine quickly led to Timeout errors and soft-bans/anti-bot blocks.
  * How I solved it: I moved the searches to Yahoo UK , added a real browser `User-Agent` header, and introduced a short pause between requests to mimic human behavior and avoid getting blocked.However, while running the script on my pc i kept receiving the same errors and the return 0 out of 75.Given the fact that a few tests earlier the number was 17 out of 75 i decided to run some tests to see if after visiting the web page , i get the number 403 or 404 (which i found out that if that number shows up it means that maybe the script got stuck on a captcha filter).After confirming that my script was stuck and returning the same errors all over again i ve moved on my personal laptop and switched the ip address (i switched from wi fi to personal hotspot from my mobile phone). After doing this everything worked out again.


* Noise in web results (Irrelevant 9-digit numbers):
  * What happened: Web pages return many 9-digit numbers that are not VAT numbers, generating useless requests.
  * How I solved it: I implemented the official Modulo 97 mathematical checksum algorithm (`valid_uk_vat_checksum`). Only numbers that respect the mathematical structure are sent forward for final official validation at HMRC, guaranteeing 100% precision.



 Results on the 75-company sample
* 17 officially confirmed companies (22.67%) with 100% precision (zero false positives, all passed through Modulo 97 and confirmed by the HMRC name).
* Results are saved in `data/vat_results.csv`.



 Optional section: Beyond the UK (Germany)

If we were to move the project to Germany:
* What gets easier: Searching is much more structured due to the law obligating companies to have an Impressum (Legal Notice) page on their website. I know I have to search directly on `domain.de/impressum` for the `DE` prefix + 9 digits.
* What gets harder: Official data from the commercial register (Handelsregister) is much more regionally fragmented compared to a single centralized ZIP file from the UK Companies House.
* Conclusion: The biggest challenge remains Discovery (finding the number on the internet). Verification itself is easy anywhere in the EU once you have the number, using the official VIES system.



Conclusions:
*Altough I used Ai for creating the core architecture and giving me lines of code that on the first hand looked pretty unfamiliar for me, I understood them fast and knew what to add and also what to remove in order to get a functional script for the project. To add on , I want to aknowledge the fact that i couldn't get the project to this point without using Ai as a copilot.



 How to run


python src/build_sample.py
python src/research_probes.py
python src/find_vat.py
 
 
 
 