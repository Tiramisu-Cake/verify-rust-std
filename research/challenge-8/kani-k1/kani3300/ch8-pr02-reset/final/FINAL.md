# PR-02 — финальный локальный кандидат

- g0 input: `dee2b6c723b06c97b37256b650bd0a380674b4f9`; документы коммитятся в основной `/root/verify-rust-std-kani3300-g0`.
- Source worktree: `/root/kani-fix-ch8-pr02-final`; branch: `work/ch8-pr02-final`.
- Final source SHA: `05da1a7a8ce7921d3f685d9595eab797870ca629`.
- Final source tree: `0cee3bfb0223a906a421cea932471963fff5840b`.
- Единственный parent: `932fb8395a58f8c86c0d702ba2cae835823b2962`; ровно один новый коммит.
- Author: `Tiramisu-Cake <igkharin@gmail.com>`; subject: `Reset uninitialized-memory state for automatic harnesses`; без skip-ci и Co-Authored-By.
- U-03 source: `f7e89f1942fa6f671f20ec45fde98d9d736dc122`; tree: `b6b84905327747cf1970ffe78c1266eeff2a7c56`.
- Полный source delta от PR-02: один compiler-файл и шесть каталогов / 24 файла регрессий. CI/package/research-файлов в source delta нет.

## SHA256 и точная сверка

Все patch hashes ниже получены из необработанных stdout Git через Python subprocess, без RTK-представления. Команда `git diff <from> <to> [-- kani-compiler]` без full-index.

- PR-02 → final, полный diff: `2f3f4b4fe7f6be3de0818bfd2b8dd8f4fe61bd47a607c404d9711fcbd5796357`.
- PR-02 → final, compiler diff: `f7beb5f9fc63e3a0a63536c44b922f07937d91829ecb551a3cbea3d517f232da`.
- Compiler diff побайтово совпадает с U-01, U-02 и U-03; проверено непосредственно по всем четырём Git-объектам:
  - `f695f653efaa1f7ac6774a079104de8cc0ff81fc`.
  - `09a6d1cb2cba63e67e60aeefbd909d1f64849b76`.
  - `f7e89f1942fa6f671f20ec45fde98d9d736dc122`.
- U-03 → final, diff: `923500b4dd7f153608c24d2151c1cff84f9fa123ed3dcc6b4a0e69f1937043f5`; только удаления ниже (4 файла одного каталога):

```text
D	tests/script-based-pre/autoharness_entry_reset_uninit_read/config.yml
D	tests/script-based-pre/autoharness_entry_reset_uninit_read/expected
D	tests/script-based-pre/autoharness_entry_reset_uninit_read/main.rs
D	tests/script-based-pre/autoharness_entry_reset_uninit_read/run.sh
```

Все 24 оставшихся fixture-файла и compiler-файл побайтово идентичны U-03; file modes также совпадают. Hashes содержимого Git blobs:

| Path | Mode | SHA256 |
| --- | --- | --- |
| `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` | `100644` | `7adb8aa87530e797aa3b1dff994c21408c00343cba7ebc052a6268cf5e805f8c` |
| `tests/script-based-pre/autoharness_entry_reset_argument_seed/config.yml` | `100644` | `00e9504001960ae960235c3e76d5c6566c5fb5be5bd399412105390de1626de9` |
| `tests/script-based-pre/autoharness_entry_reset_argument_seed/expected` | `100644` | `6971bc6f59c3f536fadec9d0eee2d6f5b09204e74f2d44aec5a5e72004758423` |
| `tests/script-based-pre/autoharness_entry_reset_argument_seed/main.rs` | `100644` | `7cf1881b211c46b816086e190c9e6b165c4421494c53e554cdfd46d37cbfca64` |
| `tests/script-based-pre/autoharness_entry_reset_argument_seed/run.sh` | `100755` | `f2c148c36483a257517e32e1ef10de9169337bcb4c0fe79f3d2af5977cadd91b` |
| `tests/script-based-pre/autoharness_entry_reset_contract_seed/config.yml` | `100644` | `00e9504001960ae960235c3e76d5c6566c5fb5be5bd399412105390de1626de9` |
| `tests/script-based-pre/autoharness_entry_reset_contract_seed/expected` | `100644` | `bd740a4425509359e9e341cec3030ac90e299ed9635b8b6bf2feb69ccf1baa84` |
| `tests/script-based-pre/autoharness_entry_reset_contract_seed/main.rs` | `100644` | `3a970577523e0c5c4b652c7437627a7f5fb400111e12b45adde5112afad199cd` |
| `tests/script-based-pre/autoharness_entry_reset_contract_seed/run.sh` | `100755` | `08224e79cbac0b8283a903bd5065533f42321d9f5907e26215b79b8835267d77` |
| `tests/script-based-pre/autoharness_entry_reset_initialized_read/config.yml` | `100644` | `00e9504001960ae960235c3e76d5c6566c5fb5be5bd399412105390de1626de9` |
| `tests/script-based-pre/autoharness_entry_reset_initialized_read/expected` | `100644` | `bd740a4425509359e9e341cec3030ac90e299ed9635b8b6bf2feb69ccf1baa84` |
| `tests/script-based-pre/autoharness_entry_reset_initialized_read/main.rs` | `100644` | `27f29c2ba17dc60349f5b246b790e8588d3a7792ebd6f22a32674ea05e6072b4` |
| `tests/script-based-pre/autoharness_entry_reset_initialized_read/run.sh` | `100755` | `a71322d2895511411d7807867cee2e42f4eda120057f28417a73cfd4a5c6f383` |
| `tests/script-based-pre/autoharness_entry_reset_no_seed/config.yml` | `100644` | `00e9504001960ae960235c3e76d5c6566c5fb5be5bd399412105390de1626de9` |
| `tests/script-based-pre/autoharness_entry_reset_no_seed/expected` | `100644` | `bd740a4425509359e9e341cec3030ac90e299ed9635b8b6bf2feb69ccf1baa84` |
| `tests/script-based-pre/autoharness_entry_reset_no_seed/main.rs` | `100644` | `efcf52bb6e653ca78a59b0b8157514c6b3fb5fe9986c4be70df25466f2b6d471` |
| `tests/script-based-pre/autoharness_entry_reset_no_seed/run.sh` | `100755` | `5bb6f63995b1e716d7e89b1f5eff65b82eda6e9eb63902838b722970fa64802e` |
| `tests/script-based-pre/autoharness_entry_reset_seed_only/config.yml` | `100644` | `00e9504001960ae960235c3e76d5c6566c5fb5be5bd399412105390de1626de9` |
| `tests/script-based-pre/autoharness_entry_reset_seed_only/expected` | `100644` | `bd740a4425509359e9e341cec3030ac90e299ed9635b8b6bf2feb69ccf1baa84` |
| `tests/script-based-pre/autoharness_entry_reset_seed_only/main.rs` | `100644` | `e11f8cd3788d7ac6debb2ab089cd60751a8c03046761923030277a837fde5404` |
| `tests/script-based-pre/autoharness_entry_reset_seed_only/run.sh` | `100755` | `0f2c9206b95087882f50b13adc1cb012f9ddd5b066ab862ae52f4b6a69c412d0` |
| `tests/script-based-pre/autoharness_entry_reset_uninit_off/config.yml` | `100644` | `00e9504001960ae960235c3e76d5c6566c5fb5be5bd399412105390de1626de9` |
| `tests/script-based-pre/autoharness_entry_reset_uninit_off/expected` | `100644` | `bd740a4425509359e9e341cec3030ac90e299ed9635b8b6bf2feb69ccf1baa84` |
| `tests/script-based-pre/autoharness_entry_reset_uninit_off/main.rs` | `100644` | `492524571f780de0716c378f70e2a5ed84df31460b021d40d5bef5f88965c30b` |
| `tests/script-based-pre/autoharness_entry_reset_uninit_off/run.sh` | `100755` | `fe5be1ab5fe7279fa45947c8ab216bb186dc3f4aaa75c0f94b01f1f7afee6ecc` |

## Проверки и пределы

- PASS: прямой parent и единственный коммит, точный список 25 изменённых файлов, compiler diff identity U-01..03, byte/mode identity всех оставшихся файлов, только 4 удаления относительно U-03.
- PASS: `git diff --check` для source delta и `bash -n` для шести сохранённых run.sh; source worktree чистый.
- Новый compiler diff не создавался; готовый reviewed compiler diff сохранён. Удалена только явно указанная дефектная новая фикстура. Новый semantic review/CI не запускался.
- Результаты U-03 и U-01 arm B сохранены в RESULT-U03.md как переданные координатором. Полный suite на финальном SHA не запускался; независимый proof credit не устанавливается.
- Локальные cargo/rustc/Kani/CBMC, push/CI/публикации и ledger changes: NONE.
- Чужой untracked `kani3300/ch8-e/e01/` в g0 оставлен без изменений и не включён в коммит.

## Текст PR

- Новый черновик: `kani3300/c2-slices/pr-texts/PR-02-v2.md`; без внутренних имён стадий и ссылок на research-документы, disclosure сохранён дословно.
- Исходный PR-02.md не изменён, SHA256: `60603d0736236dceb958608e7bf1b92fe9d53440de0a0cbb541b8e7fb3d3df75`.
- PR-02-v2.md SHA256: `b721f5b18f2e268055365411dbc2c61aa628a648e17ef656ebaa7cf9bafd1a81`.
- RESULT-U03.md SHA256: `b73add28768baad426ae16b133cbdabfeed703a1224690948c3a65e3bf774850`.
- Итоговый g0 commit SHA сообщается в READY-строке ответа; он не встраивается в собственное содержимое коммита.
