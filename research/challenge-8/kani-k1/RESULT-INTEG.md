# INTEG — состав и inventories готовы; measurement не выполнен

Дата: 2026-10-31 (MSK), задание от 2026-10-30.
Ветка `experiment/kani-k1-integ-20261030`, без OPT/UNSTABLE8.
Library SHA: `b7cd8235fbe4f23d92c9b80635f0c5ce9a5dbc1c`.
Library tree: `4dd5393bbb4524104c8b05cb70910c6836c3b8de`.
Манифесты/запрос controls: `7da2486dc3`; исходный HEAD `b7cbff4fbc`.

| Изменение состава | Число | Причина |
|---|---:|---|
| DIRECT ordinary: B u64 N2..5, B u8 N2..8, A u8 N9 | 12 | Консервативная выборка |
| DIRECT positive opt-in: B u64 N6/7, A u64/u8 N5..8 | 10 | Дорогие; P2 candidate |
| DIRECT TIMEOUT diagnostics: B u64 N8, u8 N9 | 2 | G1 TIMEOUT 600 с |
| DIRECT expected-fail controls | 2 | Диагностика oracle / precondition |
| Старые C u64 N2..5, u8 N2..8 → retired duplicate | 11 | Сохранены opt-in |
| Возврат: 3 swap + 1 Cell route + 27 plain insertion | 31 | Точная выборка П-6 |

Аудит 11 дублей: одинаковые T/F/N и `general_route_properties`, обе ветви general/stable,
общий неизменённый oracle; потребителей имён в library нет. Изменены item-level cfg.
C u64 N6..8, u8 N9 и N0/1 остаются ordinary; старые merge_contract не изменены.
C u64 N6..8 условны: supporting A u64 находятся opt-in, historical DIRECT G2 SUCCESS.
27 plain insertion = 4 lower + 23 grouped; для 23 пар cfg перенесён к Cell-аргументу.
Тела insertion/swap/route не изменены, Cell insertion N6..19 остаются opt-in.
Macro helper swap_contract_arbitrary_indices_case разгейчен отдельно.

Контроль B вызывает настоящий `assert_sorted_and_probe_preserved`; oracle не изменён.
После v[0]^=1 ключ x>>1 сохранён. Ожидается отказ permutation assert merge.rs:846/847,
sortedness assert :844 должен пройти. До measurement это source argument, не proof result.
Исторический G2 FAILED относился к прежнему телу контроля; новый контроль не измерен.
A-контроль должен отказать на merge_inputs_are_sorted; нового measurement результата нет.
Готовый, не отправленный запрос: integ/measurement-candidate.request.json;
placeholder-message в gate недостаточно: нужно вручную сверить единственный file:line отказа.

| Запрос | Source SHA | Результат | USD |
|---|---|---|---:|
| G1 ordinary | 3aac17a107 | list timeout124 | 0.4725 |
| G2 ordinary-retry | 91a8566276 | COMPLETE,176 | 0.6075 |
| G3 controls | 7da2486dc3 | COMPLETE,449 | 0.7020 |

G1 UUID: `ec712f76-dc1d-412d-9800-586bdb29954a`.
G2 UUID: `f347352e-3be4-40ff-a560-2b16debb5967`.
G3 UUID: `3d5461de-d6ac-4daf-b3d9-5194ca90e496`.

G1: 10 минут list было недостаточно, компиляция завершилась за11:05; инвентаря нет.
G2: actual176 = static176, точное множество имён совпало (integ/g2.inventory-check.json).
G3: actual449 = static449, точное множество имён совпало (integ/g3.inventory-check.json).
G2/G3 log-grep unused_*/dead_code/smallsort/verify: no match; check-tooling с base PASS.
Итого spent $1.7820, reserved $0 ≤ $2.50; builds3/3. CAP_USD73.96 не менялся.
Measurement пропущен из-за лимита3 сборок после retry; новый отказ контроля не установлен.
PRE-BUILD REVIEW для measurement не запрашивался; measurement build не запускался.

Числа: P1 **176** =144+12−11+31; P2 **339** =328+22−11; controls **449** имён.
Классы opt-in: budget153, retired11, positive DIRECT10, TIMEOUT2, expected-fail28,
unsupported1, прежние positive opt-in68; ordinary176. Расхождений с прогнозом нет.
P2 patch снимает только cfg:173 строки, включая23 Cell argument cfg и10 positive DIRECT.
Retired/TIMEOUT/controls не возвращает; применение к temp tree даёт static339.
ΣVT П-6 macOS: возвращено +1159.9с, снято −245.6с, DIRECT Mac UNKNOWN.
DIRECT GCB отдельно: ordinary12 Σ708.8219с; positive10 Σ2427.5576с.
Это historical VT для приоритизации, без П-7/jobs или GCB→Mac преобразования.

Локально только Python/rustfmt; генераторы, scope/helper checks, patch apply: PASS.
Rustfmt edition2024/config из TASK: exit0; .rs ≤100 символов, комментариев стало меньше.
Kani9461e07a, toolchain, flags/lane не изменены. Доказательств полного CI нет.
Координатору: после OPT/UNSTABLE8 нужен общий manifest/inventory и полный CI организаторов.
Positive DIRECT P2 — candidate, macOS CI UNKNOWN; branch evidence не проверяет объединение.
Список build/request, bounded summary/inventory/tooling/grep: [integ/](integ/).
