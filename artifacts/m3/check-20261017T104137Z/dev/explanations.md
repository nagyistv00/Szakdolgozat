# Explanation review sheet (repeat 1)

Score each model explanation manually; do not use the model to grade itself.

## eval_direct_bad (label: CWE-95, vulnerable=True)
Model status: completed
- CWE-95, line 2, by bandit, semgrep, model: `return eval(user_text)`
  - Explanation: A 'eval' függvény kódolást futtatja, ami potenciálisan veszélyes lehet. Használjon 'ast.literal_eval' helyett, amely csak biztonságosan értékeket értelmezi.
  - Input source: user_text
  - Fix: Cserélje le a 'eval' függvényt a 'ast.literal_eval'-ra. Példa: return ast.literal_eval(user_text)

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## eval_direct_fixed (label: CWE-95, vulnerable=False)
Model status: completed
- CWE-95, line 5, by model: `return ast.literal_eval(user_text)`
  - Explanation: Az eval függvény közvetlenül az untrusted data értékére hívódik, ami kódvégzést végezhet az untrusted data alapján. Ez káros lehet, mivel az untrusted data közvetlenül az eval függvénybe kerülhet.
  - Input source: user_text
  - Fix: Használjon a safer ast.literal_eval függvényt, amely csak a biztonságosan értelmezhető adatokat értelmezi, vagy használjon egy másik módszert a user_text értékének értelmezésére, amely nem kódvégzést végezhet.

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## eval_alias_bad (label: CWE-95, vulnerable=True)
Model status: completed
- CWE-95, line 3, by model: `return evaluator(user_text)`
  - Explanation: Az eval függvény futtatja a kapott sztringkénti kódot Python kódnak, ami káros hatásokat okozhat az untrusted data miatt.
  - Input source: user_text
  - Fix: Használjon más biztonságosabb módszert a szöveg értékének kiszámításához, például a built-in függvényeket vagy a safer eval alternatívákat.

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
- CWE-95, line 2, by bandit, model: `return eval("1 + 2")`
  - Explanation: A 'eval' függvény az untrusted data-t futtatja Python kódként, ami potenciálisan káros kód futtatására lehet. Ez egy potenciálisan káros biztonsági kockázat.
  - Input source: Az untrusted data a 'eval' függvényben ér el.
  - Fix: A 'eval' függvény helyett a 'ast.literal_eval' függvényt használjuk, amely csak biztonságosan értelmezi a literál értékeket, nem pedig általános Python kódot. Példa: 'ast.literal_eval("1 + 2")'

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## eval_shadow_control (label: CWE-95, vulnerable=False)
Model status: completed
- CWE-95, line 6, by bandit, semgrep, model: `return eval(user_text)`
  - Explanation: Az eval függvény futtatja a kapott Python kódot, ami káros lehet, ha az untrusted data nem megbízható.
  - Input source: user_text
  - Fix: Használjon a safer ast.literal_eval függvényt, amely csak literál értékeket értelmezi, és nem futtat kódot.

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
  - Explanation: Az untrusted data (user_text) bejön a show_value függvényben, és az osztályozott shell=True paraméter miatt az operációs rendszer parancsának futtatására kerülhet. Ez egy potenciális biztonsági kockázat, mivel az untrusted data lehetővé teszi, hogy futtatható parancsokat tartalmazó adatokat tartalmazzon.
  - Input source: user_text
  - Fix: A shell=True paramétert távolítsuk el, és használjunk egy másik módszert a parancs futtatására, például a subprocess.run függvényt a check=True paraméterrel, de a shell=False paraméterrel, majd a user_text-et a parancs részétében használjuk közvetlenül. Példa: subprocess.run(["echo", user_text], check=True)

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## shell_direct_fixed (label: CWE-78, vulnerable=False)
Model status: completed
- CWE-95, line 6, by model: `return subprocess.run([sys.executable, "-c", "import sys; print(sys.argv[1])", user_text], shell=False, check=True)`
  - Explanation: Az untrusted data közvetlenül átadott a subprocess.run függvénynek, ami a shell=False paraméterrel futtatja a Python kódot, ami potenciálisan végrehajtható kódot futtatja.
  - Input source: user_text
  - Fix: A user_text-et nem közvetlenül átadhatjuk a subprocess.run függvénynek. Használjunk egy biztonságosabb módszert, például a subprocess.run függvényt a listában adott paraméterekkel, vagy használjunk egy másik módszert a Python kód végrehajtására, amely nem futtatja a shell-t.

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
  - Explanation: Az untrusted data (user_text) bejön a show_value függvényben, és az osztályozott shell=True paraméter miatt az operációs rendszer parancsának futtatására kerülhet. Ez egy potenciális biztonsági kockázat, mivel az untrusted data lehetővé teszi, hogy további parancsokat is beillesztsenek a futtatandó parancsba.
  - Input source: user_text
  - Fix: A shell=True paramétert távolítsuk el, és használjuk a subprocess.run metódust a parancs futtatásához. Példa: return launch(['echo', user_text], check=True)

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## shell_alias_fixed (label: CWE-78, vulnerable=False)
Model status: completed
- CWE-95, line 2, by model: `print(user_text)`
  - Explanation: A print függvényben közvetlenül használjuk az untrusted data-t, ami lehetővé teszi, hogy a felhasználó által beírt adatok futtatható kódot tartalmazzon.
  - Input source: user_text
  - Fix: Használjuk a formatálási operátort (f-string) vagy a str.format() metódust a print függvényben, hogy elkerüljük a potenciális kódvégzést. Példa: print(f"{user_text}")

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## shell_constant_control (label: CWE-78, vulnerable=False)
Model status: completed
- CWE-78, line 5, by bandit, model: `return subprocess.run("echo fixed", shell=True, check=True)`
  - Explanation: A 'subprocess.run' függvényben a 'shell=True' paraméter használatával futtatott parancs az untrusted data (a 'fixed' szöveg) alapján. Ez egy potenciális operációs rendszer parancs injekciós (CWE-78) kockázat.
  - Input source: A 'fixed' szöveg a 'fixed_value' függvényben.
  - Fix: A 'subprocess.run' függvényben a 'shell=False' paramétert használjuk, és a parancsot listában adjuk meg. Példa: 'subprocess.run(["echo", "fixed"])'

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## shell_text_control (label: CWE-78, vulnerable=False)
Model status: completed
- CWE-78, line 2, by model: `return "subprocess.run(user_text, shell=True)"`
  - Explanation: Az untrusted data (user_text) bejön a subprocess.run függvényben, és a shell=True paraméter használatával a Python kód futtatására szolgál. Ez egy potenciális kockázat, mivel az untrusted data nem korlátozott.
  - Input source: user_text
  - Fix: A shell=True paraméter használata helyett használjon a subprocess.run függvényt a listában átadott argumentumokkal, hogy elkerülje a shell használatát. Példa: subprocess.run(['python', 'script.py', user_text])

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## sql_direct_bad (label: CWE-89, vulnerable=True)
Model status: completed
- CWE-89, line 2, by bandit, semgrep, model: `return cursor.execute(f"SELECT name FROM accounts WHERE name = '{user_text}'")`
  - Explanation: Az SQL lekérdezés dinamikusan épül az untrusted data alapján, ami lehetővé teszi az SQL injekció támadását.
  - Input source: user_text
  - Fix: Használja a paraméteres SQL lekérdezéseket, hogy elkerülje az SQL injekciót. Példa: cursor.execute("SELECT name FROM accounts WHERE name = %s", (user_text,))

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## sql_direct_fixed (label: CWE-89, vulnerable=False)
Model status: completed
- CWE-89, line 2, by model: `return cursor.execute("SELECT name FROM accounts WHERE name = ?", (user_text,))`
  - Explanation: Az SQL lekérdezésben az untrusted data közvetlenül bekerül a SQL kódban, ami lehetővé teszi az SQL injection-vulnerabilityt. Ez történik, mivel a user_text nem paraméterként adja át a cursor.execute metódusnak.
  - Input source: user_text
  - Fix: Használja a paraméteres SQL lekérdezést, hogy elkerülje az SQL injection-vulnerabilityt. Példa: return cursor.execute("SELECT name FROM accounts WHERE name = ?", (user_text,))

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## sql_concat_bad (label: CWE-89, vulnerable=True)
Model status: completed
- CWE-89, line 2, by bandit, model: `query = "SELECT name FROM accounts WHERE name = '" + user_text + "'"`
  - Explanation: Az SQL lekérdezés dinamikusan épül az untrusted data alapján, ami lehetővé teszi az SQL injekció támadását.
  - Input source: user_text
  - Fix: Használja a paraméteres SQL lekérdezéseket, hogy elkerülje az SQL injekciót. Példa: cursor.execute("SELECT name FROM accounts WHERE name = %s", (user_text,))

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |

- CWE-89, line 3, by semgrep, model: `return cursor.execute(query)`
  - Explanation: Az SQL lekérdezés dinamikusan épül az untrusted data alapján, ami lehetővé teszi az SQL injekció támadását.
  - Input source: user_text
  - Fix: Használja a paraméteres SQL lekérdezéseket, hogy elkerülje az SQL injekciót. Példa: cursor.execute("SELECT name FROM accounts WHERE name = %s", (user_text,))

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## sql_concat_fixed (label: CWE-89, vulnerable=False)
Model status: completed
- CWE-89, line 3, by model: `return cursor.execute(query, (user_text,))`
  - Explanation: Az SQL lekérdezés paraméteres formában kell írni, hogy elkerülje az SQL injekció riskusát.
  - Input source: user_text
  - Fix: A user_text-et paraméteres lekérdezés részére kell átadni. Példa: return cursor.execute(query, (user_text,))

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |


## sql_integer_control (label: CWE-89, vulnerable=False)
Model status: completed
- CWE-89, line 3, by bandit, model: `return cursor.execute(f"SELECT name FROM accounts WHERE id = {account_id}")`
  - Explanation: Az SQL lekérdezés dinamikusan épül az untrusted data alapján, ami lehetővé teszi az SQL injekció támadását.
  - Input source: user_text
  - Fix: Használja a paraméteres SQL lekérdezéseket, hogy elkerülje az SQL injekciót. Példa: cursor.execute("SELECT name FROM accounts WHERE id = %s", (account_id,))

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
  - Explanation: A SQL lekérdezés dinamikusan épül a user_text alapján, ami lehetővé teszi, hogy az untrusted data közvetlenül befolyásolja a lekérdezést.
  - Input source: user_text
  - Fix: Használja a paraméteres SQL lekérdezéseket, hogy elkerülje a SQL injekciót. Példa: cursor.execute("SELECT name FROM accounts WHERE name = %s", (user_text,))

| Criterion | Score (0/1) |
|---|---|
| Correct family | |
| Correct line | |
| Correct input source | |
| Fix is correct and safe | |
| Understandable | |

