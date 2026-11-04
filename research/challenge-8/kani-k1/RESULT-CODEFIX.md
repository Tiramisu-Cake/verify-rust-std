# RESULT-CODEFIX — v8

- Branch: `experiment/kani-k1-codefix-20261104`; owner `k1-network`; slug `codefix`.
- Build: `6bc006d2-eff0-406e-92a5-06c934e5e97f`, SUCCESS / COMPLETE / gate=true.
- Source: `63bbd6d309b8063a515dae5be1a082e7e6836992`; library: `56efe5c477ded5bc06a975f6a843822d09100894`.
- Request: `codefix-v8-20261104-02`; SHA256 `c8b6de28b7cca912b4aa6729c172d765e4de6cbdeb31586eea6a688d66347cb3`.
- Kani: `cd355b0bccd32300713bc2ce4f765dafa1510607`; nightly `2026-10-22`.
- Diagnostic, gcb-e2-standard-4, jobs=1; inventory cfg-off, verification controls cfg-on.

1. ZST doc: зафиксированы наблюдавшиеся pointer-check failures; причина не установлена, используется ptr::read.
2. Network N≥9: явно только порядок; перестановка суффикса проверяется отдельно, композиционный claim убран.
3. Комментарии wrap/specfix/module: геометрия отделена от инициализации и прав, которые дают фикстуры.
4. Module doc: ограничения default fn / trait-generic F на pin; ссылки kani#5116/#4908, без Actions ids; профили фиксируют comparator.
5. Добавлен прямой swap_if_less с совпадающими позициями, arbitrary u8/bool, full-value assert и 2 covers.
6. Добавлен Freeze !Copy bytes86 fallback N2 через Unstable entry; const размер/stack/marker, все байты и 3 covers.
7. Оба allow(dead_code) сняты; подтверждённых сирот нет, пять используемых ArbitraryValue impl-семейств и PFC/macro зависимости сохранены.

Inventory: **204 = 202 v7 + 2**, полный набор совпал; удалений/контролей нет. Статика сохраняет тела/атрибуты 202 и 8 контролей.
Delta: `network::swap_same_position_u8`, `network::unstable_freeze_noncopy_bytes86_fallback_n2`.

| Harness | Expect / status | Время, с | Failed/total | Covers |
|---|---|---:|---:|---:|
| network::swap_same_position_u8 | SUCCESS / SUCCESS | 0.28875694 | 0/69 | 2/2 |
| network::unstable_freeze_noncopy_bytes86_fallback_n2 | SUCCESS / SUCCESS | 8.783918 | 0/544 | 3/3 |
| assembly::reject_mutant_swap_u8_n2 | FAILED / FAILED | 0.5040002 | 1/80 | 1/1 |

Мутант: ровно `assertion failed: v[0] <= v[1]`, assembly.rs:25; Kani exit 1 ожидаем. Новые харнессы ≤60 с; covers 5/5.
Warnings: targeted log-grep `smallsort/verify` вернул только координату ошибки контроля; verify warnings **0**, repair не нужен.
Статика/rustfmt/diff-check/≤100: PASS; 71 tooling tests OK; build-bound check-tooling против `59893bff1f`: PASS.
Verify source lines: **3065 → 3147**. Library diff только verify*; сборок 1, repairs 0; стоимость **$0.6345 / $1.50**.
Evidence: [bounded reports/pages](codefix/evidence/verification-report.json), [summary](codefix/evidence/summary.md); имена/identities/SHA сверены.
Область результата: diagnostic двух новых доменов; прежние 202 корня в этой сборке не запускались повторно.
