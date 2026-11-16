# TASK — worker11: три новых ограничения Kani uninit-checks из PROF-ON-01 (одна стадия, только анализ)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: [RESULT.md](kani3300/ch8-profiles/on-ci/run-43798838603/RESULT.md) (g0 d07f0eaa55); распакованный artifact
read-only: /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/profon/art. Kani SEL1 14bc57fdb9 и upstream 0aac16ef62 — исходники read-only.

Для каждого: (A) transmute [MaybeUninit<T>;N] → [T;N] в MaybeUninit::array_assume_init;
(B) false UB в kani::internal::write_any_slice (kani_core lib.rs:716, "Reading from an uninitialized pointer of
type *mut [T]") — havoc для modifies-слайсов; (C) fn-item ZST layout в FnMut::call_mut:

1. Место в kani-compiler (uninit instrumentation), почему construct не поддержан / почему ложный UB;
   есть ли уже upstream issue/PR (gh search, только чтение; кроме C2/#5151 и PolymorphicIter, они известны).
2. Можно ли обойти в нашем harness/source без потери силы (например, не вызывать array_assume_init,
   другой comparator-тип) — конкретный diff-набросок, без коммита в S/profiles.
3. MRE (несколько строк) и черновик issue для B, если это дефект Kani (без внутренних имён/ссылок на наши docs).
4. g0 kani3300/ch8-profiles/on-ci/gaps/: ANALYSIS.md, MRE-*.rs, ISSUE-DRAFT-*.md, HANDOFF.md.
   Коммит [skip ci], author Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <g0> или STOP <причина>.

Код компилятора не писать (WIP 0). Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
