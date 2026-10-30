# Следующие варианты — только предложение, без реализации в OPT

## Специализация u64 oracle

Гипотеза: typed arbitrary u64 probe и обычное сравнение полных u64 уменьшат
инструментацию общего bytewise oracle. Эквивалентность надо доказать отдельно:
у u64 нет padding, все битовые комбинации допустимы, а прежний matches_value_probe
читает только первые восемь из 128 arbitrary probe bytes. Их проекция покрывает
все u64; оставшиеся байты в этих u64-гармониках не наблюдаются.
Это не переход к ключу x>>1: payload bit и полные multiplicities должны сохраниться.

Отдельный кандидат должен сохранить independent arbitrary input/dst, оба backing,
requires/modifies/ensures и comparator. Oracle меняется — контроль обязателен:
повторить full-value corruption x^=1 с ожидаемым отказом counts при sorted keys,
а также контроль unsorted halves с точной проверкой precondition.
Сравнивать peak/VT на matched источниках и прежних flags/timeouts; успех заранее неизвестен.
В текущей сессии ни typed probe, ни какой-либо новый oracle не реализовывались.

## Локальная декомпозиция merge

Альтернатива: отдельно специфицировать merge_up/merge_down и связать их с инвариантами
потреблённых левых/правых диапазонов, initialized dst и сохранения полных counts.
Нужны frame для src/dst, непересечение записей и корректный центральный остаток;
нельзя заменить bounded oracle более слабой sortedness или trusted summary.
Новый контракт/композиция потребуют собственных negative controls и независимого review.
Это отдельная задача: в OPT реализации, контракт и trusted premises не менялись.
