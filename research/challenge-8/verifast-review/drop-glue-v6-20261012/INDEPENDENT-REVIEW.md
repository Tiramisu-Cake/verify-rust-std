# Независимые адресные reviews

Два built-in reviewer работали read-only с фиксированными входами. Никаких proof/compiler/refiner/build execution, worktree/coordinator edits или внешних сообщений. Основной агент отвечает за итоговый пакет. Ниже — компактная фиксация возвращённых выводов, не копия raw logs.

## Семантика — independent_semantics, GPT-6 Sol / high

Проверены exact merge checkpoint420, proof/infra f8c7cb7e, tool e0a94e3e и review K. Вывод: False Node/Sym defect исправлен; `_literal_false_with_loc` требует location-bearing Node. Missing/malformed post fails closed по коду. V6 absent unit return handling оправдан exact generated shape gate и не даёт absent non-unit/ordinary Return или Some/None mismatch; подтверждённой новой soundness ошибки не найдено. Main generated pair gate сохраняет CFG/unwind и вызывает официальный core. General Call/Drop unwind TODOs не закрыты этим gate.

Отдельный независимый ответ на finding F1: dict collapse действительно допускает duplicate identical unwind arm. Exact translator pattern требует ровно два arms и отклоняет третий до glue translation. Authentic positive AST имеет два arms. Это admission-only hardening, а не доказанный reachable verifier soundness defect или опровержение bounded positive. Нужен duplicate/extra-arm isolated negative и строгая cardinality admission.

Вердикт: bounded concrete-u64 normal semantic claim допустим в сохранённых границах; интеграция заблокирована fresh admission/receiver-end/retirement, actual late-panic cleanup и caller premise provenance gates. V8 NOT_RUN, перенос v6 PASS запрещён.

## Raw evidence — independent_evidence, GPT-6 Luna / high

Независимо сверены archive SHA `9d629426...d2c0bc3`, inventory 730/730, text index `8f1d3e...94ef6d` и 399 indexed sources/chunks, manifest/config/source certificate/profile/compile/case receipts. Build ID/proof/infra/tool/profile соответствуют pinned result. Whole Build FAILURE/run_exit1/accepted=false сохранены. Binary hashes проверены по archived receipts; executable bytes не включены для независимого rehash.

Raw positive all4stages0, natural caller source-linked read/guard, unique private glue→selected method binding, full normal/current contract, official refinement, return/free/leak, 0 errors/288 statements. Helper4 fresh и обе ordinary normal/unwind smoke groups соответствуют scoped claims, не actual insert_tail panic theorem.

Все шесть raw negative logs достигли предназначенного обязательства: after-drop false196; before-call false195; unavailable len field при physical packing197; source-quarter points_to через prelude264/req55/call197; duplicate full effect197; real dead-code206 после normal return/leak. Raw classifications остаются INCONCLUSIVE. Missing receiver не является method refusal, before-call false не даёт runtime caller-glue credit.

Reviewer дополнительно прочитал собственный scoped `replay-gates.py` и `NEGATIVE-GATE-REPLAY.json`: corrected auditor source SHA `3e3e1b917a7cc301fee16074a80f7470a98ebcc4d4eb04b61781e54cbcc28a51` соответствует checkpoint420; исходные sources/stages/receipts hash-bound, все шесть negative gates совпали. Явно переиспользуются старые full admissions; это не полный rerun classifier и не новая proof. В ранее предоставленных v6/v7/v8 text-replay directories отдельный historical negative-replay artifact не обнаружен (там tool source trees); review не заявляет проверку такого не найденного receipt. Собственный воспроизводимый scoped replay сохранён отдельно.

Вердикт: archived evidence поддерживает bounded positive normal result; не profile acceptance/generic insert_tail/panic cleanup. Нет возражения против итогового раздельного решения REVIEW.md.

Final addressed semantic sanity review completed after REVIEW.md/INDEPENDENT-REVIEW.md were written: **GO**, no materially misleading claims or required correction; no edits/execution.
