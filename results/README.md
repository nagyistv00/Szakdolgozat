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