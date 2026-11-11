# KANI3300 A2R
- Выполнена ровно A2R по заданию research `3d5ce04887`; Cloud $0.
- raw_eq проверяет все байты обоих pointee через CheckAs полного extent; неизвестный layout → Unsupported.
- Оба операнда добавлены в initial targets для учёта предшествующих записей.
- Новый selector raw-eq-uninit: ожидаются 4 SUCCESS и 3 uninit FAILURE; закреплены имена падающих harnesses.
- Transmute-ошибки прежнего fixture объяснены pinned rustc InstSimplify; массивы 3 байта/padding 12 байт сохраняют intrinsic.
- Pat/enum offsets и все файлы трёх прежних selectors сохранены побайтно; восстановление golden ожидает CI.
- rustfmt --config-path rustfmt.toml, diff --check, pinned API hashes и статический -D warnings/clippy audit PASS.
- Независимое Luna HIGH ревью PASS: REVIEW.md; identities и тесты — в review packets / TEST-MANIFEST.json.
- Kani: 85fc5cd2ca77 + b207847932da поверх 3dc0227cee; автор Tiramisu-Cake; Kani push не выполнялся.
- Сборки/clippy/Kani/CBMC/Miri и CI NOT_RUN; proof credit отсутствует. Подробнее: NOTES.md.
A2R READY b207847932da34ac19886c1337f5b69ace0b0843
