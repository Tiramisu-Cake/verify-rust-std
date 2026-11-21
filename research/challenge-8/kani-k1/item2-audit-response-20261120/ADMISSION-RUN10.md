# Допуск координатора по кампании 10 (2026-11-21)

Основание: независимая офлайн-qualification `QUALIFICATION-RUN10.md` (воркер 14), run 44867764794, std `632e4e8d3b8cd94c918979ac7f076afebd327c0f`, tool `0aac16ef62`. Провайдеры P-1/P-3 перенесены с кампании 9 по побайтовой идентичности тел, атрибутов и q-модели и покрытию всех вызовов.

**Допущены как bounded-результаты** (тот же домен и ограничения, что в `ADMISSION-RUN9.md`): network no-merge plain-маршруты **N0, N1, N3, N4, N5, N6, N7, N10, N11, N14, N15**; контроли N2/N17-corrupt.

Сводно с кампанией 9: `small_sort_network` для `u8/KeyLess<u8>`, V34/base1, q:any, нормальный возврат, OFF-профиль — **все длины 0–17**: порядок и полное мультимножество, q-frame, внешний byte frame. Ресурсный профиль: до 9,04 GiB sampled RSS (N17), 12 object bits.

Не покрыто: N18–32 (merge), fallback и general маршруты, generic T/F, UB-классы uninit/validity/permission, контракт `sort13_optimal` как PFC.
