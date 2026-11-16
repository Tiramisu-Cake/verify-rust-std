# Issue MRE — одна стадия подготовки

Подготовлен один kani-host control на чистом upstream
`0aac16ef62da9e9d5645782d458593e5d78143ba`, без SEL1 и std preparation.
Control — `/root/kani-ch8-issue-mre-w14`, branch
`uninit-ci/ch8-issue-mre-w14`; единственный parent — upstream.
Изменены только `.github/workflows/` и `ch8-issue-mre-control/`, stock workflows
удалены. Author `Tiramisu-Cake <igkharin@gmail.com>`, commit `[skip ci]`.
Control `d860e30592bc05cad1e8f10f814397b8dfd36a33`, tree
`ba4b7298f099b2273df90b5a0f8e07826e661078`.
Точные payload/patch/review identities находятся в CI-REQUEST.json.

7 отдельных .rs /10 отдельных вызовов: copy_integer, raw_bool_overwrite,
raw_bool_read; check_body/check_slice_havoc для исходного slice, initialized
storage и thin targets; настоящий отрицательный uninit-read control.
Исходные copy Rust blocks сохранены, исходный slice MRE byte-exact.
Тексты обоих issues и source MRE не изменены; audit_static.py проверяет hashes.

rows.json объявляет исходы до запуска:5 SUCCESS,3 COPY_UNSUPPORTED,
2 UNINIT_FAILURE. Это source predictions, все runtime результаты NOT_RUN.
Copy Unsupported не квалифицирует bool producer/consumer control.
Slice-havoc diagnostic reproduction не означает корректность модели.
Oracle использует structured verification SUCCESS/FAILURE и точные
class/description; сгенерированные property IDs будут сохранены при запуске.
Иные/добавочные failures и неполные результаты не засчитываются.

Флаги как в черновиках; добавлен только JSON export transport.
Каждый receipt сохраняет точный argv/cwd, source/tool/request/rows hashes,
original exit/exception, failed IDs/descriptions/locations и bounded export.
No suppression/default-check weakening. Fallback сохраняет исходные receipts,
незапущенные строки NOT_RUN, незавершённые UNKNOWN.

Одна job30мин, сумма step caps28мин с резервом; setup4мин, build720s,
phase330s, отдельный process30s, RSS6GiB, log heads1MiB/tails4096,
export8MiB. Полный sweep внутри этих ограничений не гарантирован.
Контроль current/floating upstream из draft checklist остаётся отдельным шагом.

27 synthetic/static tests, actionlint1.7.7, frozen package/control check,
patch reconstruction и exact-MRE audit: PASS. Independent Luna HIGH review — GO_STATIC_REVIEW_ONLY (REVIEW.json);
замечание о сохранении argv перед запуском устранено и проверено тестом.
Подготовка не является разрешением CI. Координатор отдельно публикует и
активирует same-tree sibling без skip-ci, sole parent upstream, новую matching
branch, attempt1; без child/retry. CONTROL.patch воспроизводит control tree.

Push/CI/publication/ledger и локальные cargo/rustc/Kani/CBMC не выполнялись.
Proof obligations closed0, proof credit NONE, runtime ALL_NOT_RUN.
