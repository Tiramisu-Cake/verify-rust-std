# Черновик вопроса в tracking issue #56 (Challenge 8) — для публикации владельцем

Публикует только владелец от своего аккаунта; агентам внешние сообщения запрещены.
Контекст: review maintainer'а к PR #678 (2026-09-13) задаёт практическую планку
(длины до порогов 16/32, sort13 и merge, контракты), но не упоминает generic `T`
и паникующий comparator. Вопрос должен снять эту неопределённость, не раскрывая
деталей нашего подхода и не прося ослабить критерии.

---

**Clarifying the acceptance domain for Challenge 8 (element types and comparator behavior)**

Hi maintainers. We are working on a Challenge 8 solution and want to make sure we target the right domain before submitting. The challenge text asks for verification "for all possible slices with arbitrary valid length"; the review on #678 clarifies that length means up to the specialization thresholds (16 for the fallback path, 32 for the general/network paths) and that `sort13_optimal`, `bidirectional_merge` and contract-form correctness are expected. Two points are still unclear to us:

1. **Element types.** Is coverage by a set of representative element types that exercises every specialization (Freeze / non-Freeze, Copy / non-Copy, `size_of <= 16` and `> 16`, ZST, interior mutability) sufficient for acceptance, or is a proof that is generic over `T` (e.g. with a deductive tool) required for the memory-safety part?

2. **Comparator behavior.** For the no-UB criterion, is it sufficient to verify with a pure, total, non-panicking `is_less`, or must the proofs also cover comparators that may panic or keep state (the `CopyOnDrop`-style unwind recovery paths in `insert_tail` / `small_sort_general`)? If panicking comparators are required, is a proof of "no UB on unwind" enough, without any functional guarantee after a panic?

A short answer on these two points would let us scope the submission correctly. Thank you.

---

Куда: https://github.com/model-checking/verify-rust-std/issues/56
После ответа: зафиксировать его цитатой и датой в WORK-POLICY §2 и COMPLETION-PLAN
«Конечные требования», затем снять пометку «предварительно» с минимума подачи.
