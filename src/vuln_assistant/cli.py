"""Command-line interface.

    python -m vuln_assistant analyse TARGET --root WORKSPACE [--lang hu|en] [--no-model]
    python -m vuln_assistant ask "REQUEST" --root WORKSPACE [--interpreter model|rules]

The workspace root must always be given explicitly; targets are resolved inside it.
"""

import argparse
import sys
from pathlib import Path

from .analysis import AnalysisReport
from .intent import ModelInterpreter, ResolvedRequest, RuleInterpreter, resolve_request
from .model import DEFAULT_MODEL, KNOWN_DIGESTS, ModelError, OllamaConnector
from .pipeline import Analyzer
from .report import render_detection, visible_detections
from .review import ModelReviewer
from .scanners import make_scanner
from .workspace import SourceWorkspace, TargetError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE = PROJECT_ROOT / ".runtime" / "last_report.json"

MESSAGES = {
    "hu": {
        "interpretation": "Értelmezés: {action} ({interpreter}).",
        "clarify_target": (
            "Add meg az elemzendő Python-fájl vagy -mappa útvonalát a kijelölt "
            "munkakönyvtáron belül (például: cases/minta.py)."
        ),
        "out_of_scope": (
            "Ez a kérés kívül esik a rendszer feladatkörén: csak a kijelölt munkakönyvtárban "
            "lévő Python-forráskódot elemzem statikusan, hálózati célpontot nem vizsgálok."
        ),
        "reject_target": (
            "Ezt az útvonalat nem elemzem: csak a kijelölt munkakönyvtáron belüli, relatív "
            "útvonal adható meg."
        ),
        "reject_unsupported_action": (
            "Ezt a műveletet nem hajtom végre: a rendszer csak elemez és magyaráz, fájlokat "
            "nem töröl, nem módosít és nem futtat."
        ),
        "reject_instruction_override": (
            "A vizsgált kódban vagy kommentben szereplő utasításokat adatként kezelem, nem "
            "követem őket."
        ),
        "reject_result_fabrication": (
            "Az elemzési hibákat nem rejtem el, és ellenőrzés nélkül nem állítom "
            "biztonságosnak a kódot."
        ),
        "target_not_found": "A megadott cél nem található a munkakönyvtárban: {target}",
        "no_previous": "Nincs korábbi elemzés, amelyre hivatkozni lehetne. Előbb kérj elemzést.",
        "bad_index": "A korábbi elemzésben nincs {index}. találat (összesen: {count}).",
        "model_unavailable": (
            "A helyi modell nem érhető el ({error}). Indítsd el a modellkiszolgálót, vagy "
            "futtasd modell nélkül (--no-model)."
        ),
    },
    "en": {
        "interpretation": "Interpretation: {action} ({interpreter}).",
        "clarify_target": (
            "Please name the Python file or folder to analyse inside the selected workspace "
            "(for example: cases/sample.py)."
        ),
        "out_of_scope": (
            "This request is outside the system's scope: it only analyses Python source code "
            "in the selected workspace statically and does not scan network targets."
        ),
        "reject_target": (
            "I will not analyse this path: only relative paths inside the selected workspace "
            "are accepted."
        ),
        "reject_unsupported_action": (
            "I will not perform this action: the system only analyses and explains; it does "
            "not delete, modify or run files."
        ),
        "reject_instruction_override": (
            "Instructions inside inspected code or comments are treated as data and are not "
            "followed."
        ),
        "reject_result_fabrication": (
            "Analysis failures are not hidden, and code is not declared safe without analysis."
        ),
        "target_not_found": "The target was not found in the workspace: {target}",
        "no_previous": "There is no previous analysis to refer to. Request an analysis first.",
        "bad_index": "The previous analysis has no finding {index} (total: {count}).",
        "model_unavailable": (
            "The local model is unavailable ({error}). Start the model server or run without "
            "the model (--no-model)."
        ),
    },
}


def connector_for(args) -> OllamaConnector:
    return OllamaConnector(model=args.model)


def build_analyzer(workspace: SourceWorkspace, args, language: str) -> Analyzer:
    scanners = [make_scanner(tool, workspace, args.profile) for tool in ("bandit", "semgrep")]
    reviewer = None
    if not args.no_model:
        reviewer = ModelReviewer(connector_for(args))
        reviewer.identify(KNOWN_DIGESTS.get(args.model))
    return Analyzer(workspace, scanners, reviewer, language)


def save_state(report: AnalysisReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")


def run_analysis(workspace, args, target, focus, language) -> int:
    analyzer = build_analyzer(workspace, args, language)
    report = analyzer.analyse(target, focus)
    save_state(report, Path(args.state))
    if args.json:
        save_state(report, Path(args.json))
    print(report.summary)
    return 0 if report.complete else 3


def explain_previous(args, index: int, language: str) -> int:
    text = MESSAGES[language]
    state = Path(args.state)
    if not state.exists():
        print(text["no_previous"])
        return 4
    report = AnalysisReport.model_validate_json(state.read_text(encoding="utf-8"))
    detections = visible_detections(report)
    if not 1 <= index <= len(detections):
        print(text["bad_index"].format(index=index, count=len(detections)))
        return 4
    print("\n".join(render_detection(index, detections[index - 1], language)))
    return 0


def execute(request: ResolvedRequest, workspace, args) -> int:
    text = MESSAGES[request.language]
    print(text["interpretation"].format(action=request.action, interpreter=request.interpreter))
    if request.action == "analyse":
        return run_analysis(workspace, args, request.target, request.focus, request.language)
    if request.action == "explain_existing":
        return explain_previous(args, request.finding_index or 1, request.language)
    if request.action == "target_not_found":
        print(text["target_not_found"].format(target=request.target))
        return 4
    print(text[request.action])
    return 4


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(prog="vuln_assistant", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("analyse", "ask"):
        command = sub.add_parser(name)
        command.add_argument("text" if name == "ask" else "target")
        command.add_argument("--root", required=True, help="explicitly selected workspace")
        command.add_argument("--no-model", action="store_true")
        command.add_argument("--model", default=DEFAULT_MODEL)
        command.add_argument("--profile", default="m3", choices=["m2", "m3"])
        command.add_argument("--state", default=str(DEFAULT_STATE))
        command.add_argument("--json", help="also write the full report to this path")
        if name == "analyse":
            command.add_argument("--lang", default="hu", choices=["hu", "en"])
            command.add_argument("--focus", choices=["CWE-95", "CWE-78", "CWE-89"])
        else:
            command.add_argument("--interpreter", default="model", choices=["model", "rules"])
    args = parser.parse_args(argv)
    try:
        workspace = SourceWorkspace(Path(args.root))
    except (OSError, TargetError) as exc:
        print(f"Invalid workspace root: {exc}", file=sys.stderr)
        return 2
    try:
        if args.command == "analyse":
            return run_analysis(workspace, args, args.target, args.focus, args.lang)
        use_model = args.interpreter == "model" and not args.no_model
        interpreter = ModelInterpreter(connector_for(args)) if use_model else RuleInterpreter()
        intent = interpreter.interpret(args.text)
        name = interpreter.name
        if use_model and interpreter.last_evidence.get("status") == "failed":
            name = "rules (model interpreter failed)"
        request = resolve_request(args.text, intent, workspace, name)
        return execute(request, workspace, args)
    except ModelError as exc:
        language = getattr(args, "lang", None) or "hu"
        print(MESSAGES[language]["model_unavailable"].format(error=exc), file=sys.stderr)
        return 2
    except TargetError as exc:
        print(f"Target error: {exc}", file=sys.stderr)
        return 4
