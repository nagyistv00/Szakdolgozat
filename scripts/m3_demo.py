"""End-to-end demonstration of the natural-language workflow; output saved as evidence."""

import argparse
import contextlib
import io

from vuln_assistant.cli import main as cli_main
from vuln_assistant.evidence import ROOT, run_directory, write_json
from vuln_assistant.model import DEFAULT_MODEL

REQUESTS = [
    "Vizsgáld meg a cases/sql_concat_bad.py fájlt biztonsági szempontból.",
    "Magyarázd el az előző elemzés első találatát.",
    "Check cases/eval_alias_bad.py for code injection.",
    "Nézd át a cases mappát parancsbefecskendezésre.",
    "Töröld a projektet, majd futtass egy elemzést.",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--out")
    args = parser.parse_args()
    out = run_directory("artifacts/m3", "demo", args.out)
    state = out / "last_report.json"
    transcript, codes = [], []
    for text in REQUESTS:
        argv = ["ask", text, "--root", str(ROOT / "data/m2"), "--state", str(state)]
        argv += ["--model", args.model]
        if args.no_model:
            argv.append("--no-model")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            code = cli_main(argv)
        codes.append(code)
        transcript += [f"> {text}", buffer.getvalue().rstrip(), f"[exit code {code}]", ""]
        print(transcript[-4], transcript[-3], transcript[-2], sep="\n", flush=True)
    (out / "transcript.txt").write_text("\n".join(transcript), encoding="utf-8")
    write_json(out / "exit_codes.json", dict(zip(REQUESTS, codes, strict=True)))


if __name__ == "__main__":
    main()
