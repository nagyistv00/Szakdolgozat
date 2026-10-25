# Explanation review sheet — qwen2.5-coder:14b, union layer, repeat 1

Score each model explanation manually; do not use the model to grade itself.

## eval_direct_bad (label: CWE-95, vulnerable=True)
Model status: completed
- CWE-95, line 2, by bandit, semgrep, model: `return eval(user_text)`
  - Explanation: A nem megbízható adatot közvetlenül adunk át az `eval` függvénynek, ami tetszőleges Python kódot futtathat.
  - Input source: function parameter `user_text`
  - Fix: Használjon biztonságosabb alternatívát, mint például az `ast.literal_eval` függvényt, amely csak literális értékeket értelmez.

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## eval_direct_fixed (label: CWE-95, vulnerable=False)
Model status: completed

## eval_alias_bad (label: CWE-95, vulnerable=True)
Model status: completed
- CWE-95, line 3, by model: `return evaluator(user_text)`
  - Explanation: A felhasználó által megadott szöveget közvetlenül értékeli ki a `eval` függvénnyel, ami lehetővé teszi bármilyen kód végrehajtást.
  - Input source: function parameter `user_text`
  - Fix: Használjon biztonságosabb alternatívát a `eval` helyett, például egy függvény, amely csak bizonyos típusú adatokat kezel. Ha valóban szükséges dinamikusan kifejezéseket értékelni, használjon biztonságos kifejezésértelmezőt, amely korlátozza a lehetséges műveleteket.

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## eval_alias_fixed (label: CWE-95, vulnerable=False)
Model status: completed

## eval_constant_control (label: CWE-95, vulnerable=False)
Model status: completed
- CWE-95, line 2, by bandit: `return eval("1 + 2")`
- Dismissed F1: The data being evaluated is a hardcoded string, not untrusted input.

## eval_shadow_control (label: CWE-95, vulnerable=False)
Model status: completed
- CWE-95, line 6, by bandit, semgrep, model: `return eval(user_text)`
  - Explanation: A nem megbízható adat érkezik a `user_text` paraméteren keresztül a `parse_value` függvénybe. A `user_text` értékkel hívódik meg az `eval` függvény, ami tetszőleges Python kódot futtathat.
  - Input source: user_text
  - Fix: Használjon biztonságosabb alternatívát, mint például az `ast.literal_eval` függvényt, amely csak literális értékeket értelmez.

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## shell_direct_bad (label: CWE-78, vulnerable=True)
Model status: completed
- CWE-78, line 5, by bandit, semgrep, model: `return subprocess.run(f"echo {user_text}", shell=True, check=True)`
  - Explanation: A felhasználó által megadott `user_text` paraméter közvetlenül belekerül a rendszerhéj parancsba, ami lehetővé teszi a parancs injektálását.
  - Input source: function parameter `user_text`
  - Fix: Használjon `shlex.quote` függvényt a `user_text` paraméter környezeti változóként való formázására, vagy használjon `shell=False` és adja át a parancsot listaként, például: `subprocess.run(['echo', user_text], check=True)`.

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## shell_direct_fixed (label: CWE-78, vulnerable=False)
Model status: completed
- CWE-78, line 6, by model: `return subprocess.run([sys.executable, "-c", "import sys; print(sys.argv[1])", user_text], shell=False, check=True)`
  - Explanation: A támadó által vezérelt `user_text` paraméter közvetlenül bekerül a `subprocess.run` hívásba, ami lehetővé teszi tetszőleges parancsok végrehajtását.
  - Input source: function parameter `user_text`
  - Fix: Használjon `shlex.quote` a `user_text` paraméterrel való formázáshoz, hogy biztonságos legyen a parancs végrehajtása. Példa: `subprocess.run([sys.executable, "-c", "import sys; print(sys.argv[1])", shlex.quote(user_text)], shell=False, check=True)`

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## shell_alias_bad (label: CWE-78, vulnerable=True)
Model status: completed
- CWE-78, line 6, by bandit, semgrep, model: `return launch(command, shell=True, check=True)`
  - Explanation: A felhasználó által megadott `user_text` paraméter közvetlenül hozzáfűzhető egy rendszerparancshoz, amelyet a `shell=True` kapcsolóval futtat. Ez lehetővé teszi a támadó számára, hogy bármilyen parancsot injektáljon.
  - Input source: function parameter `user_text`
  - Fix: Használjon `shlex.quote`-t a felhasználói bemenetre, hogy biztonságosan hozzáadjon a parancshoz. Például: `command = f'echo {shlex.quote(user_text)}'`.

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## shell_alias_fixed (label: CWE-78, vulnerable=False)
Model status: completed

## shell_constant_control (label: CWE-78, vulnerable=False)
Model status: completed
- CWE-78, line 5, by bandit, model: `return subprocess.run("echo fixed", shell=True, check=True)`
  - Explanation: A folyamatban lévő `subprocess.run` hívás `shell=True` paraméterrel rendelkezik, ami OS parancs injekcióra is képes, ha a parancs karakterlánca nem megbízható adatból épül fel.
  - Input source: function `fixed_value`
  - Fix: Használjon `shell=False` és adja át a parancsot listaként, például: `subprocess.run(['echo', 'fixed'], check=True)`.

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## shell_text_control (label: CWE-78, vulnerable=False)
Model status: completed
- Rejected CWE-78 line 2: structural check: no function call on the stated line

## sql_direct_bad (label: CWE-89, vulnerable=True)
Model status: completed
- CWE-89, line 2, by bandit, semgrep, model: `return cursor.execute(f"SELECT name FROM accounts WHERE name = '{user_text}'")`
  - Explanation: Az 'user_text' paraméter közvetlenül bekerül az SQL lekérdezési karakterláncba anélkül, hogy bármilyen tisztítás vagy paraméter kötés lenne használva, ami lehetővé teszi egy támadó számára, hogy rosszindulatú SQL kódot injektáljon.
  - Input source: function parameter 'user_text'
  - Fix: Használjon paraméter kötést az SQL lekérdezési karakterláncban a 'user_text' paraméter helyett. Például: return cursor.execute("SELECT name FROM accounts WHERE name = %s", (user_text,))

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## sql_direct_fixed (label: CWE-89, vulnerable=False)
Model status: completed

## sql_concat_bad (label: CWE-89, vulnerable=True)
Model status: completed
- CWE-89, line 2, by bandit, model: `query = "SELECT name FROM accounts WHERE name = '" + user_text + "'"`
  - Explanation: Az `user_text` paraméter, amely nem megbízható, közvetlenül összefűzi az SQL-lekérdezési karakterlánccal. Ez lehetővé teszi egy támadó számára, hogy rosszindulatú SQL-kódot injektáljon.
  - Input source: function parameter
  - Fix: Használjon paraméteres lekérdezéseket a SQL-lekérdezési karakterláncban. Például: `query = "SELECT name FROM accounts WHERE name = %s"; return cursor.execute(query, (user_text,))`

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |

- CWE-89, line 3, by semgrep, model: `return cursor.execute(query)`
  - Explanation: Az `user_text` paraméter, amely nem megbízható, közvetlenül összefűzi az SQL-lekérdezési karakterlánccal. Ez lehetővé teszi egy támadó számára, hogy rosszindulatú SQL-kódot injektáljon.
  - Input source: function parameter
  - Fix: Használjon paraméteres lekérdezéseket a SQL-lekérdezési karakterláncban. Például: `query = "SELECT name FROM accounts WHERE name = %s"; return cursor.execute(query, (user_text,))`

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## sql_concat_fixed (label: CWE-89, vulnerable=False)
Model status: completed

## sql_integer_control (label: CWE-89, vulnerable=False)
Model status: completed
- CWE-89, line 3, by bandit, model: `return cursor.execute(f"SELECT name FROM accounts WHERE id = {account_id}")`
  - Explanation: A biztonsági probléma létezik, mert a felhasználói bemenet, még ha egész számmá alakították, továbbra is be van ágyazva a SQL lekérdezésbe sztring-interpolációval. Ez lehetővé teszi a SQL injekció ellenőrzés nélküli beillesztését.
  - Input source: user_text
  - Fix: Használjon paraméteres lekérdezéseket a SQL lekérdezés konstrukciójához, hogy elkerülje a SQL injekciót. Például: `return cursor.execute("SELECT name FROM accounts WHERE id = %s", (account_id,))`

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## sql_unexecuted_control (label: CWE-89, vulnerable=False)
Model status: completed
- CWE-89, line 2, by bandit, model: `return f"SELECT name FROM accounts WHERE name = '{user_text}'"`
  - Explanation: Az 'user_text' paraméter közvetlenül bekerül az SQL-lekérdezési karakterláncba anélkül, hogy bármilyen tisztítást vagy paraméter kötést végezne, ami lehetővé teszi egy támadó számára, hogy rosszindulatú SQL-kódot injektáljon.
  - Input source: function parameter 'user_text'
  - Fix: Használjon paraméter kötést az SQL-lekérdezési karakterláncban. Például: return "SELECT name FROM accounts WHERE name = %s"

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |

