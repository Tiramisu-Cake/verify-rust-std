# RENAMEMODS — пакет PRE-BUILD review

Ветка `experiment/kani-k1-renamemods-20261106`, owner `k1-merge`.
Задание `92e4e72b5e`, старт `d44afad690`; база library LEANHELPERS
`5c929ba094cef478efc350b3cd9d7b8fc73fe203`.
Library `85ced7f8a8bcdf6b4ffe2e29a65d1d940ff10737`, tree
`def2d65ddc5e73ed6ccb94df0afbb36e475d80d8`.
Этот пакет подготовлен для exact-packet review; GO и dispatch ещё не было.

Восемь файлов перенесены через `git mv`, один к одному по таблице владельца.
Обновлены mod/use/пути атрибутов и карта verify.rs; rustfmt упорядочил mod.
Переименованы canonical comparator и пять specfix_* контролей в profile_*.
Другие имена корней, предикаты, типы, длины, unwind, solver и места проверок сохранены.
smallsort.rs побайтно совпадает с базой; tooling не менялся.

Изменены 64 места сообщений (59 различных литералов): удалён префикс модуля.
Для сообщений realcontracts использовано описание `helper contract …`, чтобы
не сливались разные сообщения в одном транзитивном замыкании.
[message-map.json](message-map.json) хранит old/new literals, файл и число мест.
[rename-map.json](rename-map.json) фиксирует восемь модулей, шесть идентификаторов
и полную биекцию файлов. [name-map.tsv](name-map.tsv) / [JSON](name-map.json)
дают явную биекцию всех полных имён: 233 ordinary и 13 контролей.

Статика: `python3 -B research/challenge-8/kani-k1/renamemods/check_renamemods.py`.
Импортируется существующий LEANHELPERS lexer/expander без правки прежних скриптов.
Обратная подстановка разрешена только для точных identifier tokens и прямых
message arguments assert!/kani::assert/kani::cover, согласно явным таблицам.
Остальные литералы, предикаты и атрибуты не нормализуются.
Сравниваются полные потоки токенов каждого файла; только порядок mod verify.rs
разрешён rustfmt. Все раскрытые items, корни и замыкания 246 корней совпадают
с LEANHELPERS после подстановки. Проверены позиции/аргументы covers и отсутствие
слияния ранее разных сообщений во всём замыкании каждого корня.
Это консервативный resolver по идентификаторам, не compiler resolution или proof.
[check-report.json](check-report.json), [cover-sites.json](cover-sites.json).

Recursive rustfmt --check: exit0, stdout пуст, source bytes unchanged.
В verify нет строк >100, запрещённой лексики TIDYDOCS в комментариях/сообщениях
или старых имён модулей/specfix_* по границам идентификаторов.
Substring grep `wrap` находит Rust wrapping API, существующий helper
arbitrary_wrapped_u64_order и описательные wrapper(s); они не обозначают модуль.
Все такие места, включая комментарии smallsort.rs, перечислены с причинами в
[remaining-name-mentions.json](remaining-name-mentions.json).

G1: [RUN-REQUEST.json](RUN-REQUEST.json), byte-identical верхнему RUN-REQUEST.json.
kind=inventory, controls=false, standard4, harnesses=[], inventory=true.
Существующий validate прошёл. Одна сборка, proof rows отсутствуют.
Ожидаются ровно 233 ordinary-имени без дубликатов; compiler sorted SHA256 должен
совпасть с [ordinary-expected.txt](ordinary-expected.txt).
Cfg-on 246 имён и runtime 13 контролей отложены в интеграционный пакет.

Лимит выбран по OPTINMOVE G1: Cloud elapsed 42 мин 25.519 с, расход $0.5805.
Тот же inventory request: whole-job budget 44 мин + 24 мин runner slack даёт
cutoff 68 мин от validate; платный timeout 44+30=74 мин.
Резерв 74×$0.0135=$0.999 ≤ свой cap $1.20; сейчас spent0/reserve0.
Project ledger при подготовке: used $107.0520, reserve0, cap $118.96;
с нашим резервом $108.0510. Перед dispatch ledger обновить.
Retry0. G2 только для исправления своей compile-error после отдельного GO и
при own spent+reserve≤$1.20; возможность G2 этим пакетом не обещана.
Окно после GO: main240 + closeout30 мин; T0/deadlines пока не установлены.

После exact GO: зафиксировать GO/SHA/T0/deadlines и свежий budget, dispatch
этой опубликованной ветки, записать BUILD UUID, `k1g.sh watch BUILD`, конец хода.
Status в цикле не опрашивать. После уведомления: bounded summary, check-tooling
против `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`, inventory pages по next_offset,
целевой log-grep smallsort/verify warnings и budget собственного BUILD UUID.
Не читать raw cache/log/archive или credentials.
Проверить source/request/build/Kani/pool identities, COMPLETE и inventory gate,
полный exact-set, количество, дубликаты и SHA256 отсортированных имён.
Native inventory hash учитывать отдельно: порядок standard/contract отличается
от сортировки. Нужны отсутствие новых smallsort/verify warnings и успешный G1.
Затем RESULT≤30 строк, REVIEW REQUEST <sha> / RENAMEMODS ЗАВЕРШЁН, стоп.

## Итог G1

Exact GO `0504202814f16c4a962687c6933a4e43b171d45b` получен; сборка `942bc6d1-191d-4777-acc5-d0d724564fde`
завершена SUCCESS, COMPLETE, gate=true, Kani exit0. Привязки и check-tooling PASS.
Compiler inventory: 233 exact ordinary-имени без дубликатов; sorted SHA256
`bd539369aead46f534868511eecef993b086cacd11e08b0b15f022103482a93b`
совпал с ordinary-expected. Целевой smallsort/verify/unused scan: no match.
Расход $0.6075, reserve0, builds1/retries0/repairs0; новых запусков нет.
Cfg-on inventory/компиляция и runtime 13 контролей отложены в интеграционный пакет.
Нового proof credit нет. [Evidence](evidence/verification-report.json).
