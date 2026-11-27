# REV2 u64 N18/N19 consumer · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO_WITH_NITS**. Пины: Std `099f0c438c08e7870dd8df513a8cf7a993c39e47` / tree `f2076c5316`, Control `d15d3c49f57740f89686a90ce17814e3fe54919a` / tree `27ae39f1a845f473cac270ec20ecdfbb47bd7559`, review-trigger `7debf5a70e`, task g0 `1e6caef0f1`, handoff g0 `3599161912`.

1. Should-fix (документ). Handoff `:77`: projection SHA-256 `U64-N19-ODD-CENTER` был усечён до 62 символов. **Исправлено координатором** на `52b516e11943e768fbcd7324a507af020d63091779e7f6e95e6cd41f3f1809b5` по `members` индекса 45938919685/1. Замороженные входы пакета это не затрагивает.
2. Риск стоимости. Сквозные `U64-N18/N19-ACTUAL-BITS` могут выйти за профиль: оценка 10–14 млн дизъюнктов против 8,04 млн у N17 (VT 81 с) и 13,1 млн у отсечённого insert-step. Запасной маршрут есть: локальные copy-back слоты и дешёвые контроли в том же job; при отсечке positive длина идёт по составному правилу.
3. Nit. Ветки по константе `N` могут оставить UNREACHABLE чужие метки; прецеденты допускают.
4. Операционно: новый trigger без `[skip ci]`.

Проверено и в порядке: фактический `small_sort_network::<u64,_>` на `v[1..1+N]` с `u64_less`, без stubs/assume/contracts; маски и свидетели контролей; единственный отказ `SORTED_POPCOUNT`; copy-back корень с одним `copy_nonoverlapping::<u64>` и скалярными постами; координаты; только скалярные сравнения, циклы ≤19; Std-дельта 3 файла, rustfmt чист; SHA-256 request `18dbcbde…`, roster `aeb4cfe5…`, bindings `d804b49d…`, bundle `3dee3db6…` (HEAD `099f0c438c`); 15/16 хэшей опор совпали, 16-й исправлен (п. 1); переменная `CH8_REV2_U64_N18_N19_CONSUMER_TRIGGER_TREE`; часы; suite 130/130.
