# TASK — worker13: S1-04 control checkout depth (одна стадия, коротко)

Это верификация корректности, не security-работа. Отвечай кратко.

Факт: control 2a532e5913 опубликован на uninit-ci/ch8-s1k-e, run 43829165289 (отменён координатором).
Job light-model-u5, шаг «Validate control and synthetic wrapper»: `git -C .../control diff --name-only 0aac16ef62 HEAD`
→ exit 128. Причина: checkout CI control с fetch-depth: 2, а control = HEAD → 40b5d9cf4 → 0aac (нужно ≥3).
В S1-03 control был прямым ребёнком 0aac, поэтому 2 хватало. Твой локальный validate этого не ловит (полный repo).

1. fetch-depth для checkout CI control (во всех jobs): 0 или точная достаточная глубина; обоснуй. Остальные checkout
   не трогать, если им 2 достаточно (проверь каждый: какие git-операции по ним делаются).
2. В synthetic tests/preflight — проверка, что глубина каждого checkout покрывает все git-операции validate
   (симуляция shallow clone с той же глубиной). Пройтись по всем git-командам check_package/validate.
3. Новый control (parent 40b5d9cf4, без [skip ci]), хеши/CI-REQUEST, короткий review. g0 kani3300/ch8-s1/s1-04/depth-fix/HANDOFF.
   Коммиты g0 [skip ci], author Tiramisu-Cake <igkharin@gmail.com>.
   Последней строкой READY <control> <g0> или STOP <причина>.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
