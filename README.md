# vulnscan

Statikus sérülékenységkereső Python-kódhoz, a szakdolgozatom gyakorlati része. Három
befecskendezéses hibát keres – eval-befecskendezés (CWE-95), parancsbefecskendezés (CWE-78),
SQL-befecskendezés (CWE-89) –, a Bandit és a Semgrep eredményeit egy helyben futó nyelvi
modellel (Qwen2.5-Coder, Ollama) egészíti ki, és magyar vagy angol nyelvű kéréseket fogad.
Az elemzett kódot csak olvassa: nem futtatja, és hálózatra sem küld semmit.

## Telepítés (Windows, PowerShell)

Kell hozzá a [uv](https://docs.astral.sh/uv/) és a CPython 3.11.13 (a uv letölti, ha hiányzik).

```powershell
uv sync --locked
./scripts/ollama.ps1 -Action Install      # Ollama 0.34.2 a .tools mappába, ellenőrzött hash-sel
./scripts/ollama.ps1 -Action Start
uv run --locked python scripts/pull_model.py --model qwen2.5-coder:14b
```

A modellkiszolgáló csak a `127.0.0.1:11435` címen figyel. Leállítás:
`./scripts/ollama.ps1 -Action Stop`.

## Használat

```powershell
# egy fájl vagy mappa elemzése (a --root a munkaterület, a cél ezen belül van)
uv run --locked python -m vulnscan analyse cases/sql_concat_bad.py --root data/samples

# természetes nyelvű kérés
uv run --locked python -m vulnscan ask "Vizsgáld meg a cases mappát SQL-befecskendezésre." --root data/samples
uv run --locked python -m vulnscan ask "Magyarázd el az előző elemzés első találatát." --root data/samples
```

Modell nélkül (`--no-model`) csak a statikus elemzők futnak.

## Ellenőrzés és mérések

```powershell
./scripts/check.ps1             # ruff és egységtesztek
./scripts/check.ps1 -Dev        # mérés a fejlesztési mintákon, kérésforgatókönyvek, demo
./scripts/check.ps1 -Lab        # mérés a tesztalkalmazáson (data/lab)
./scripts/check.ps1 -Requests   # a 14 tesztkérés
./scripts/check.ps1 -All        # minden (a két modellel kb. egy óra)
```

A szkript először commitolja az aktuális állapotot, majd minden lépés kimenetét a
`results/<dátum>_<idő>_check/` mappába menti (UTC idő).

## Felépítés

| Mappa | Tartalom |
|---|---|
| `src/vulnscan/` | a program: elemzőillesztők, modellkapcsolat, kérésértelmezés, jelentés |
| `semgrep/` | a Semgrep-szabályok (`injection.yml` a taint-szabályok) |
| `prompts/` | a modell rendszerpromptjai |
| `scripts/` | mérő- és segédszkriptek |
| `tests/` | egységtesztek |
| `data/samples/` | 18 fejlesztési minta címkékkel |
| `data/lab/` | a témavezetőtől kapott tesztalkalmazás |
| `data/requests_dev.json`, `data/requests_test.json` | a fejlesztési és a teszt kérések |
| `results/` | a mérések eredményei (lásd `results/README.md`) |
