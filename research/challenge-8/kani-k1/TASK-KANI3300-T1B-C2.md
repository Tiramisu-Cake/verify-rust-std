# KANI3300 T1b-C2 — переупаковка пакета C (3 roots) после REQUEST_INVALID

**Выдано координатором 2026-11-11.** Основание: `kani3300/t1b-s/RESULT-KANI3300-T1B-C.md` (build 5fee5ac5: REQUEST_INVALID,
combined patch 114 путей / diffstat 6990 B > 4096 B; Kani NOT_RUN; $0.027). Runtime **Codex**, одна стадия, Cloud $0 до GO.
T1B-S и ответ планера (`kani3300/t1b-s/PLANNER-T1B-A3-ANSWER.md`) в силе, кроме состава roots ниже.

## Решение координатора по бюджету

Остаток под cap $0.80 = **$0.449**. 5 roots ($0.4725) и 4 roots ($0.459) не помещаются. Пакет **C2 = 3 roots**:
`cmp3_into_iter_next` (писатель), `cmp3_index_range_len` (failing), `cmp3_manually_drop_unsized_len` (passing contrast);
timeout 1m каждому, один invocation, фильтры прежние. Резерв (3×1+30)×$0.0135 = **$0.4455 ≤ $0.449**. Calibration pair
исключена (pin/uninit-checks уже подтверждены в T1a/A/A2/A3; failing root сам показывает активность проверок) — отметить в
PRE-BUILD как отклонение от рекомендации планера.

## Что сделать

1. Combined patch собрать так же, как deployment-патч A3 (production CMP2 + diagnostic 12b4137c42 по тем же ~14 путям),
   без исторических test-файлов. Kani diagnostic commit не менять.
2. Проверить **все** bounded-ограничения prepare до dispatch, включая diffstat ≤ 4096 B (`tools/kani_k1.py:335–337`) — и
   добавить эту проверку в preflight (минимальная правка + service/error-path тест + ревью), чтобы отказ ловился до Build.
3. PRE-BUILD.md (≤ 30 строк), `RUN-REQUEST-C2.json`, identities; независимое ревью пакета.

## Результат

`kani3300/t1b-c2/`. Коммит `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <research sha>`, стоп.
Dispatch — только после GO координатора.

## Запреты

- Никаких Build/dispatch/Cloud до GO; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно.
- Raw logs/archives/credentials не читать, identity guard не обходить. Никаких Actions/PR/issue/комментариев, push в Kani.
  Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
