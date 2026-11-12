# Бриф для аудита: регрессия памяти `proof_for_contract` + `-Z uninit-checks` в Kani #3300 Part 1

12 ноября 2026. Нужно независимое мнение: как устранить регрессию или как честно сузить заявленную область, не теряя основную цель Part 1.

## Контекст

Part 1 (Kani, `model-checking/kani` #3300) добавляет проверку инициализации для `MaybeUninit`-хранилища, включая flat-слоты `[MaybeUninit<T>; N]` / `[MaybeUninit<T>]`, и передачу shadow-состояния union-значений через вызовы (протокол аргумент/возврат). Аудит раунда 2 — `AUDIT-REPORT-KANI3300-PART1-R2-RU.md` @ `124a45e373`. После него закрыты:

- B1 (потеря проверок при неразрешённом вызове) — встроен;
- ложный отказ `raw_eq` на promoted-константах — модель M1 (маска из байтов immutable allocation);
- тот же отказ в режиме проверки контракта — M2-B/S3 (анализ проходит через трамплин регистрации контракта).

Текущий кандидат цепочки: `4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c` (Uninit Quick без двух тяжёлых тестов — всё PASS, run 43257528539).

Открыт один блокер: ресурсный.

## Симптом

Минимальные входы (в `kani3300/m2a/cases/`):

```rust
#[inline(never)]
fn select(a: MaybeUninit<u8>, b: MaybeUninit<u8>, first: bool) -> MaybeUninit<u8> {
    if first { a } else { b }
}

#[kani::ensures(|result: &MaybeUninit<u8>| unsafe { result.assume_init_read() == 17 })]
fn postcondition_target() -> MaybeUninit<u8> {
    select(MaybeUninit::new(17), MaybeUninit::uninit(), true)   // P2: false
}

#[kani::proof_for_contract(postcondition_target)]
fn postcondition_reads_initialized_return() { let _unread = postcondition_target(); }
```

P1 — корректный (ожидается SUCCESS), P2 — чтение неинициализированного возврата в `ensures` (ожидается uninit FAILURE). Флаги: `-Z uninit-checks -Z function-contracts`, CBMC 6.11.0, Ubuntu 24.04, 16 GB. Сторож убивает cbmc при RSS > 6 GiB.

## Измерения (P1; P2 ведёт себя так же)

| Вариант (исходник) | symex steps | VCC (после упрощения) | SAT / память | Исход |
|---|---|---|---|---|
| upstream `bf9c58e662` | 4 908 | 222 (66) | 285k vars / 17.1M clauses; ~1.4 GB, ~46 с | FAILED: ложный frame `Check that *var_N is assignable` в `mem_init::store_argument`, Unsupported «raw pointers and unions» |
| R1 `1cd96e354` (первый коммит Part 1, один коммит поверх upstream) | 10 005 | 509 (120) | > 6.3 GB за 10 с | убит |
| A1 `613c188313` / A2R `b207847932` / A3R `a0a2386001` | 11–14k | 699–948 | > 6.4–8.1 GB | убит |
| V01 `51fe0993de`: R1 без demonic return selection | 11 504 | 572 (168) | > 6.5 GB | убит |
| V02 `48d10f9ff2`: эмиссия R1 + рантайм `mem_init.rs` upstream | 11 396 | 536 (191) | 844k / 51.2M; решается | FAILED (детали не сняты) |
| R4-A/B/C (`75090c4986`, `2983edc2a0`, `8ebc167850`): split buffer, порядок usize-арифметики, single-element copy fallback | ~10k | ~510–570 (120) | > 6.3–6.6 GB | убиты |
| R5-01 `bcc1a2af3f`: буфер аргументов upstream + копирование R1 | 11 639 | 476 (182) | 846k / 51.2M; решается | FAILED |
| R5-02 `899ffb5f26`: буфер R1 + копирование upstream | 9 971 | 569 (120) | > 6.7 GB | убит |
| R6-01 `25197eb23e`: представление буфера R1 (поля object/offset в `MEM_INIT_STATE`) + выбор/сброс upstream | 11 167 | 563 (162) | > 6.5 GB | убит |
| R6-02b `405c1f0592`: представление upstream (указатель `saved_address` в отдельном `static`) + выбор R1 | 9 340 | 381 (115) | 830k / 51.2M; 50 с, 1.95 GB | FAILED: ложный frame `*var_17 / *var_9 is assignable` (как upstream) |
| R1+skip `56cbc5c4a4` (контроль к R6-02b) | 8 672 | 473 (96) | > 6.7 GB | убит |
| R7 B1 `b4eb8294b7`: отдельный private snapshot из 12 скалярных полей (object/offset) + DFCC targets | 18 099 | 877 (147) | > 7.2 GB | убит |
| R8 `2bd63183d8` (+тесты `0ab62c7b0c`): свидетель как пара указателей `saved_base/saved_byte` в private snapshot, store-time проверки round-trip | 31 794 | 1 534 (395) | > 8–9 GB | убит |

Все варианты — прямые потомки R1 (или текущей цепочки для R7/R8); на GitHub достижимы как родители CI-веток `uninit-ci/*` в `Tiramisu-Cake/kani`. Workflow замера: `cargo build-dev`, затем `kani <input> --keep-temps --only-codegen` → `cbmc --show-properties`, `goto-instrument --count-eloc`; затем обычный `kani` под `/usr/bin/time -v` со сторожем.

## Что установлено

1. Регрессия есть уже в R1 — в первом коммите Part 1, а не в поздних стадиях (A3, M1 и т. п.).
2. Бинарный поиск по хункам `library/kani_core/src/mem_init.rs` (R5, R6): дорогая часть — буфер передачи состояния через вызов (store/load argument). Изменения в `copy`/`bless` дают лишь вторичный рост (17M → 51M клауз вместе с эмиссией R1), но не OOM.
3. Хранение свидетеля как `usize` из `pointer_object`/`pointer_offset` (R1, R6-01, R7) — OOM. Хранение одного указателя в отдельном `static` (R6-02b) — решаемо (≈2 GB), но DFCC видит этот `static` как пользовательскую память и даёт ложный frame-отказ, ровно как upstream. Перенос в маркированное `MEM_INIT_STATE` (R1) и был попыткой этот frame-отказ убрать.
4. Пара указателей в private snapshot (R8) — ещё хуже.
5. Даже upstream строит 17M клауз на этой скалярной программе: shadow-модель контрактов в целом тяжёлая.

## Чего мы не знаем

- Какое конкретно выражение/VCC раздувает формулу при битблэстинге: ширины не сняты (полные `--show-vcc` / DIMACS не делали).
- Как именно DFCC обрабатывает маркированный private static (snapshot/havoc/сравнение в frame-проверке) и почему значения из `pointer_object` там так дороги.
- Был ли P1 на upstream «полезно» решаем: upstream падает раньше на ложном frame и Unsupported, то есть сравнение «1.4 GB против OOM» — не сравнение двух корректных моделей.

## Варианты, которые видим

A. **Узкий fail-closed.** В Part 1 объявить Unsupported (до эффекта, с диагностикой) комбинацию `proof_for_contract` + передача union shadow-состояния через вызов (store/load argument в теле, проверяемом по контракту). Всё остальное (ordinary harness, contract Assert без PFC, flat-слоты, raw_eq) остаётся. Upstream в этом месте и так не даёт полезного ответа (ложный frame/Unsupported), поэтому это не регрессия функциональности, а честная граница.

B. **Указательный буфер (как upstream) + исключение из DFCC frame.** Решаемость как у R6-02b, но нужно, чтобы DFCC не считал этот `static` пользовательской памятью (свой маркер или явное `assigns`/exemption). Требует понимания DFCC-кодирования private state; риск — скрыть настоящие frame-ошибки.

C. **Разобраться в кодировании.** Снять ширины VCC/DIMACS для R1 и R6-02b, найти конкретный дорогой терм (например, сравнения `pointer_object` по всем объектам или snapshot private static в frame-проверке) и устранить его точечно. Дольше, но может вернуть полную поддержку.

## Вопросы аудитору

1. Достаточно ли варианта A для Part 1 с учётом цели (SmallSort scratch — обычные harness без `proof_for_contract`), и как его правильно оформить (где ставить Unsupported, какие контроли)?
2. Есть ли у варианта B корректная реализация без ослабления frame-проверок пользовательской памяти? Как DFCC в Kani/CBMC обходит `MEM_INIT_STATE` и можно ли так же пометить отдельный указательный буфер?
3. Если идти по C — какие минимальные диагностики снять первыми (команды CBMC 6.11), чтобы найти дорогой терм?
4. Видите ли вы ошибку в выводах 1–4 (например, сравнение с upstream некорректно из-за раннего frame-отказа)?
