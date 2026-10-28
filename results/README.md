# Mérési eredmények

Minden futás egy saját mappába kerül: `<dátum>_<idő>_<név>` (UTC idő). A mappákban a
`manifest.json` rögzíti a futtatás környezetét (csomagverziók, a bemeneti fájlok SHA-256
kivonata), mellette vannak a nyers kimenetek és az összesítők (`summary.md`, `metrics.json`).

| Mappa | Tartalom |
|---|---|
| `2026-10-17_102331_check_interrupted` | megszakadt futás (a modellkiszolgáló indítása miatt elakadt) |
| `2026-10-17_104137_dev_check_1` | fejlesztési minták, 1. kör (7B modell) |
| `2026-10-17_110519_dev_check_2` | fejlesztési minták, 2. kör (7B és 14B) |
| `2026-10-17_113935_dev_check_final` | fejlesztési minták, végleges beállítás |
| `2026-10-25_154631_lab_eval` | tesztalkalmazás (`data/lab`) |
| `2026-10-25_160933_requests_eval` | a 14 tesztkérés |
| `2026-10-25_manual_scoring` | a magyarázatok kézi pontozása és a mintacímkék ellenőrzése |
| `install_checks/` | a telepítési tesztek kimenetei (minden tesztfutásnál új mappa) |
| `sample_scans/` | a minták beolvasása az első, szűk elemzőbeállítással |
| `setup/` | a környezet, az Ollama és a modellek telepítési adatai |

## Korábbi nevek

A projekt 2026. október 28-án átszerveződött. A 10-28 előtti futások `manifest.json` és
naplófájljai még a régi útvonalakat tartalmazzák; a régi és az új nevek megfelelése:

| Régi | Új |
|---|---|
| `artifacts/m1/<időbélyeg>` | `results/install_checks/<dátum>_<idő>` |
| `artifacts/m1/environment.json` | `results/setup/environment.json` |
| `artifacts/m2/<időbélyeg>` | `results/sample_scans/<dátum>_<idő>` |
| `artifacts/m2/handoff.json` | `results/sample_scans/model_handshake_2026-09-19.json` |
| `artifacts/m2/investigations` | `results/sample_scans/investigations` |
| `artifacts/m2/model-install.json` | `results/setup/model_install_qwen2.5-coder_7b_2026-09-19.json` |
| `artifacts/m2/runtime-install.json` | `results/setup/ollama_install.json` |
| `artifacts/m3/check-<időbélyeg>` | `results/2026-10-17_<idő>_...` (lásd fent) |
| `artifacts/m3/model-install-<modell>.json` | `results/setup/model_install_<modell>.json` |
| `artifacts/m4/lab-20261025T154631Z` | `results/2026-10-25_154631_lab_eval` |
| `artifacts/m4/requests-20261025T160933Z` | `results/2026-10-25_160933_requests_eval` |
| `artifacts/m4/manual-20261025` | `results/2026-10-25_manual_scoring` |
| `src/vuln_assistant/` | `src/vulnscan/` (`contracts.py` → `records.py`, `evidence.py` → `runinfo.py`, `diagnostic.py` → `handshake.py`) |
| `rules/m3_python_taint.yml`, `rules/m2_python.yml` | `semgrep/injection.yml`, `semgrep/patterns.yml` |
| `prompts/m3_*_system.txt` | `prompts/review.txt`, `verify.txt`, `intent.txt` |
| `data/m2/` | `data/samples/`, `data/requests_dev.json` |
| `TestData/security_lab`, `TestData/m4_requests.json` | `data/lab`, `data/requests_test.json` |
| elemzőprofilok `m2`, `m3` | `basic`, `full` |
| szabályazonosítók `m3-python-*` | `python-*` |
