**APPROVE** для exact F4 candidate g0 `1bd7d58e6cafc64c36c4012651751c038d3e9c64`, package `kani3300/wave0/f4-confirm/`.

Main `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e` / tree `09b828b47c93e90e140e8c41f9048109a2f4a786`; control `1ec3318f5e2c39afb701aa7a5578d4ea0a721224` / tree `34a402bd4ebbabf3ec611327097475c8cb46cfba`, direct parent exact main. Findings original15: нет обязательных исправлений. При изменении кандидата нужен immutable delta re-review; localized findings направляются original15 через координатора.

Передача координатору — через текущий диалог. Отдельный coordinator GO нужен для публикации и одного main confirmation. Сам review dispatch не разрешает. Item1 26/28 сохранён, confirmation prospective 27/28; future full PR CI имеет отдельные candidate/review/GO для 28/28. S2 здесь не рассматривался.

Сохранить UNKNOWN для old exact Cargo failure и actual compilation order; setup hypothesis не causal proof. Runtime NOT_RUN, proof credit NONE. Static/synthetic PASS не устанавливает reproduction или покрытие обоих порядков.

Output только `kani3300/wave0/f4-confirm-review/`. Авторский код не менялся. Без субагентов, смены pane model, compiler/verifier/full runner, CI, push, сообщений другим участникам и ledger изменений.
