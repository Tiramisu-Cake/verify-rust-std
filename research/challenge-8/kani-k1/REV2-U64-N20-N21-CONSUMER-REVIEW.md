# REV2 u64 N20/N21 composite consumer · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO_WITH_NITS**, блокеров нет. Пины: Std `97b1df7b0a26e821f5b204c22ce291da5d123d55` / tree `78b555dea0`, Control `c2bcb3744b88f666e006fe4397f37cc83b21b5ba` / tree `23841cd660808a5a0238e6056aa61a87d72c1d15`, review-trigger `9b30a6c866`, task g0 `f16a69904a`, handoff g0 `4784df22b0`.

1. Nit. В admission перечислить внешние шаги отдельным списком: перенос sort9 по длине (guard `smallsort.rs:538`); driver `insertion_sort_shift_left` и цикл регионов `:394–417` нативно не проверены; центр N21 — транскрипция `:1027–1036`; инициализация D при uninit OFF; ранговая индукция merge.
2. Nit. Явно назвать посылку переноса grouped ID `copy_nonoverlapping::<u64>` на `:425` со свидетеля на все входы: `scratch_base`, `v_base`, `len` не зависят от значений.

Проверено и в порядке: рёбра N20 и N21 с опорами из 45919454859, 45938919685, 45946532451 (10/10 VERIFIED); маски и свидетели контролей, единственный отказ; координаты, `copy_back=true`; только скалярные сравнения, циклы ≤34; оценка <25 с VT, <60 с cold; Std-дельта 3 файла, rustfmt чист; SHA-256 request `c15c3f98…`, roster `43480e47…`, bindings `b4d9130b…`, bundle `6640b240…` (HEAD `97b1df7b0a`); 29 уникальных 64-hex хэшей handoff сверены, усечённых нет; авторы; wiring; часы; suite 129/129.
