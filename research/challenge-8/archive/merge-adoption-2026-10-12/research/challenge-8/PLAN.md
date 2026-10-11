# Challenge 8: действующая дорожная карта

Нормативная матрица R1–R7, шесть специализаций, resource/callback интерфейсы,
W0–W10 и финальные критерии — в [COMPLETION-PLAN](COMPLETION-PLAN.md).
Этот routing document не содержит второй очереди экспериментов или бюджета.
Миссии/права — [WORK-POLICY](WORK-POLICY.md); свежие факты —
[STATUS](STATUS.md) и checkpoint своей ветки; процедура — [AGENT-RUNBOOK](AGENT-RUNBOOK.md).

Постоянные направления: select/sort4 — полная actual sort4 и caller applicability,
затем sort8; merge/insert_tail — actual insert_tail, guard/Drop/CURRENT recovery,
затем arbitrary merge; VeriFast — review, интеграция и подготовка патчей.
Следующий шаг агент выбирает внутри разрешённой миссии с учётом первого blocker,
actual caller и времени/бюджета открытой сессии. Конкретное действующее поручение
не заменяется общим roadmap. Внешняя подача требует отдельного поручения.

[Предыдущий исследовательский PLAN](https://github.com/Tiramisu-Cake/verify-rust-std/blob/fbc063ce609cc549358e3bbc0f8b3a12b75b3945/research/challenge-8/PLAN.md)
сохраняет старые решения, бюджеты и phase closeouts как историю. Его «CURRENT»,
STOP и Actions-команды относятся к своим датированным заданиям, не к новым
сессиям. При переносе этой общей редакции сохранить branch-local прежний PLAN
в архиве, не удалять связанные доказательства/evidence.
