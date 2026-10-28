"""Deterministic natural-language rendering of an analysis report (Hungarian/English).

The wording around the findings is fixed text, so the summary never states more than the
recorded evidence. Only the explanation and fix fields come from the model, and they are
labelled as such.
"""

from .analysis import AnalysisReport, Detection
from .records import FAMILY_NAMES

TEXT = {
    "hu": {
        "header": "Elemzett cél: {target} ({files} fájl). Felismerők: {tools}.",
        "focus": "Szűrés: csak a(z) {family} hibacsalád ({name}).",
        "hidden": "Más hibacsaládba tartozó, itt nem megjelenített találatok száma: {count}.",
        "incomplete": "FIGYELEM: az elemzés nem teljes, ezért a hiányzó találat nem jelent biztonságot:",
        "none": (
            "Nem találtam a vizsgált hibacsaládokba (SQL-befecskendezés, parancsbefecskendezés, "
            "veszélyes dinamikus kódkiértékelés) tartozó lehetséges sérülékenységet. Ez nem "
            "bizonyítja, hogy a kód biztonságos."
        ),
        "count": "Lehetséges sérülékenységek száma: {count}.",
        "item": "{index}. {name} ({family}) – {path}, {line}. sor. Jelezte: {by}.",
        "code": "   Kód: {code}",
        "explanation": "   Magyarázat (modell): {text}",
        "source": "   Bemenet forrása (modell): {text}",
        "fix": "   Javasolt javítás (modell): {text}",
        "scanner": "   Elemzői üzenet: {text}",
        "footer": (
            "A találatok statikus elemzésből származnak; a kihasználhatóságot nem "
            "ellenőriztük. A modell szövegei tévedhetnek."
        ),
        "model": "modell",
    },
    "en": {
        "header": "Analysed target: {target} ({files} file(s)). Detectors: {tools}.",
        "focus": "Filter: only the {family} family ({name}).",
        "hidden": "Findings of other families not shown: {count}.",
        "incomplete": "WARNING: the analysis is incomplete, so a missing finding does not mean safety:",
        "none": (
            "No potential vulnerability was found in the analysed families (SQL injection, OS "
            "command injection, eval injection). This does not prove that the code is secure."
        ),
        "count": "Potential vulnerabilities: {count}.",
        "item": "{index}. {name} ({family}) – {path}, line {line}. Reported by: {by}.",
        "code": "   Code: {code}",
        "explanation": "   Explanation (model): {text}",
        "source": "   Input source (model): {text}",
        "fix": "   Suggested fix (model): {text}",
        "scanner": "   Scanner message: {text}",
        "footer": (
            "Findings come from static analysis; exploitability was not verified. "
            "Model-written text may be wrong."
        ),
        "model": "model",
    },
}


def visible_detections(report: AnalysisReport) -> list[Detection]:
    return [
        detection
        for file in report.files
        for detection in file.detections
        if report.focus is None or detection.family == report.focus
    ]


def render_detection(index: int, detection: Detection, language: str) -> list[str]:
    text = TEXT[language]
    by = ", ".join(text["model"] if tool == "model" else tool for tool in detection.detected_by)
    name = FAMILY_NAMES[detection.family][language]
    lines = [
        text["item"].format(
            index=index,
            name=name[0].upper() + name[1:],
            family=detection.family,
            path=detection.path,
            line=detection.line,
            by=by,
        ),
        text["code"].format(code=detection.code_line),
    ]
    if detection.explanation_source == "model":
        lines.append(text["explanation"].format(text=detection.explanation))
        if detection.input_source:
            lines.append(text["source"].format(text=detection.input_source))
        lines.append(text["fix"].format(text=detection.fix))
    for message in detection.scanner_messages:
        lines.append(text["scanner"].format(text=message))
    return lines


def render_summary(report: AnalysisReport) -> str:
    text = TEXT[report.language]
    tools = sorted({scan.tool for file in report.files for scan in file.scans})
    if report.mode == "scanners+model":
        tools.append(text["model"])
    lines = [
        text["header"].format(target=report.target, files=len(report.files), tools=", ".join(tools))
    ]
    if report.focus:
        lines.append(
            text["focus"].format(
                family=report.focus, name=FAMILY_NAMES[report.focus][report.language]
            )
        )
    if not report.complete:
        lines.append(text["incomplete"])
        lines += [f" - {problem}" for problem in report.problems]
    detections = visible_detections(report)
    if detections:
        lines.append(text["count"].format(count=len(detections)))
        for index, detection in enumerate(detections, start=1):
            lines += render_detection(index, detection, report.language)
    else:
        lines.append(text["none"])
    if report.hidden_other_families:
        lines.append(text["hidden"].format(count=report.hidden_other_families))
    lines.append(text["footer"])
    return "\n".join(lines)
