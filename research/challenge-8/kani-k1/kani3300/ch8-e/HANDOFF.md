# Handoff — одна design стадия завершена

Задание: `TASK-CH8-E-DESIGN-W15.md`, исходный g0
`1038c006f9616e88e4792b025bd877674c008def`.
P′/U/SEL1 exact source/tree pins — в [DESIGN.md](DESIGN.md).

Результат: **STOP E / unsupported quantified-pointer ON invariant**.
Статически установлен явный frontend guard U/SEL1; минимальный pointer witness
и loop reproducer, exact source coordinates и связанный #5141 — в
[CONTROLS.md](CONTROLS.md). Compile результат конкретного MRE не измерен.
Это STOP выбранного encoding, не доказательство невозможности E всеми методами.

Передано integrator13: [PATCH-PROPOSAL-13.md](PATCH-PROPOSAL-13.md) с точными
head/после-copy/break/repair точками, fixed frame, ghost ranks и отдельным ZST
zero-iteration случаем. Proposal **не готов к применению**, пока не разрешены
must-init invariant и alloc-enabled symbolic storage → actual core binding.
`smallsort.rs` и verify.rs не менялись. Новая tool/shadow модель не открывалась.

Установлено только чтением source: loop clauses реализованы; символический
primitive storage без constant CAP существует в alloc-enabled Kani, но не в
core::kani; decreases expressions могут быть stale; can_dereference использует
assert, а не pure assume-able init; SEL1 не снимает quantifier rejection.
Поведение uninit shadow после loop havoc **UNKNOWN**, его потеря не утверждается.
Bounded controls не обозначены arbitrary-length proof.

Следующая разрешаемая стадия: сначала изолированные E-Q/E-S/E-H controls и решение
представления init invariant в сохранённых checks. При новом summary — отдельный
§6 design gate (inside/outside/alias/fixed witness/false-bit/normal-return controls).
Если альтернативы требуют нового compiler/trusted model, вернуть отдельный
кандидат/решение владельцу; автоматически не интегрировать core patch и не dispatch.
Sorting/permutation, fallback/threshold composition и A1-R3 intake — последующие стадии.

Validation этой стадии: Git identities и source ranges прочитаны на pins;
проверка whitespace/scope и commit author выполняется перед handoff.
Все runtime/control outcomes NOT_RUN; obligations closed=0; independent proof
credit=NONE. Никаких cargo/rustc/Kani/CBMC, CI, push, публикаций, ledger изменений
и чтения raw evidence. Исходный `ch8-s1/kani-host-list/` нами не изменялся.
Во время чтения shared g0 продвинулся другими участниками до
`e844b91afac1a1a029bf090a190c1cac3667f25d` (включая регистрацию ранее untracked
host-list); чужие commits сохранены. Исходный task/pins остаются от 1038c006f9;
наш commit добавляет только четыре файла ch8-e поверх актуального g0.
