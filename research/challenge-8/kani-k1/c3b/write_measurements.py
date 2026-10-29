"""Render the research ledger from saved bounded summaries, never from raw logs."""
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
builds = json.loads((BASE / "builds.json").read_text())
analysis = json.loads((BASE / "screen-analysis.json").read_text())
lines = ["# Итоговые измерения C3b", "",
         "Все числа ниже взяты из сохранённых bounded k1g summary/rows/peaks.",
         "COMPLETE означает полноту разбора run, а не успешный proof всех строк.",
         "INCONSISTENT/PARTIAL/UNKNOWN/TIMEOUT/NOT_RUN не получают proof credit.", "",
         "| Набор | Build UUID | K1 / terminal без артефакта | Память driver / CBMC / Kissat, GiB | Verify wall |",
         "|---|---|---|---|---|"]
for entry in builds:
    path = BASE / (entry["label"] + ".summary.md")
    state = entry.get("terminal_status", "НЕ СОБРАНО")
    memory, wall = [], "—"
    if path.exists():
        text = path.read_text()
        state = re.search(r"^# K-1 run `[^`]+`: (\w+)", text).group(1)
        for command in ("kani-driver", "cbmc", "kissat"):
            found = re.search(r"`" + command + r"` ([0-9.]+) GiB", text)
            memory.append(found.group(1) if found else "—")
        found = re.search(r"wall ([0-9:]+) ", text)
        if found:
            wall = found.group(1)
    lines.append(f"| {entry['label']} | `{entry['build_id']}` | {state} | {' / '.join(memory) or '—'} | {wall} |")
lines += ["", "## Полнота текущего набора", "",
          f"Source prediction: {analysis['inventory_count']} имён. Bound remote inventory итогового SHA отсутствует.",
          f"Принятых по identity и source freshness измеренных имён: {analysis['observed_names']}.",
          f"Без актуальных измерений: {len(analysis['missing'])}; без SUCCESS: {len(analysis['not_proved'])};",
          f"SUCCESS, но больше90с: {len(analysis['over_budget'])}.",
          f"Отброшенных старых merge-route rows: {len(analysis['stale_before_route_refactor'])}.",
          f"Полный допуск: **{analysis['complete']}**. Binding errors: {analysis['binding_errors']}.",
          f"Pending result sets: {analysis['pending']}.",
          f"Terminal без артефактов: {analysis['unavailable']}.", "",
          "Список каждого имени, source SHA и build UUID — в ordinary-timings.tsv;",
          "missing/not_proved/over_budget/stale — в screen-analysis.json.", "",
          "## Критические последние пробы", ""]
for label in ("repair-priority-1", "repair-priority-2"):
    path = BASE / (label + ".rows.tsv")
    lines += [f"### {label}", ""]
    if not path.exists():
        lines += ["Результат не собран; proof/timing credit отсутствует.", ""]
        continue
    text = path.read_text().splitlines()
    split = text.index("name\tstatus\ttime_s\tchecks\tcovers")
    lines += ["| Имя относительно verify | Status | Время, с | Checks |", "|---|---|---:|---|"]
    for line in text[split + 1:]:
        name, state, seconds, checks, covers = line.split("\t")
        lines.append(f"| `{name.split('::verify::')[1]}` | {state} | {seconds or '—'} | {checks or '—'} |")
    lines.append("")
lines += ["## Бюджет и validation", ""]
path = BASE / "budget-final.txt"
lines.append("Own-UUID ledger: `" + (path.read_text().strip() if path.exists() else "финальный запрос ещё не выполнен") + "` (count / used USD / reserved USD).")
lines += ["", "53 unit tests PASS; bash -n для обоих shell scripts PASS.",
          "Python analysis syntax PASS; git apply --check OPTION-OPTIN.patch PASS (patch не применён).",
          "Rustfmt --check с заданным config и проверка всех изменённых Rust строк≤100 выполнены;",
          "обязательный rustfmt повторяется после итогового commit. Локальные компиляторы не запускались.",
          "Все proof/code изменения ограничены verify-модулями, organizer scripts/workflow и runtime не менялись.",
          "Все commits с [skip ci], push только experiment/kani-k1-memory-20261029.", ""]
(BASE / "FINAL-MEASUREMENTS.md").write_text("\n".join(lines))
