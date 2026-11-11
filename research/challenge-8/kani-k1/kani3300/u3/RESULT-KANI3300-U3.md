# RESULT-KANI3300-U3
TOOL_ERROR / gate false: build `14dd0792-1c06-47be-b931-94f6096a664a`; 0/20 native PASS, 20 ERROR; приёмка не выполнена.
Authorized head `2021b7cf3518fc72fee611e2a5d306e4bf5b619e`; coordinator GO снял diagnostic-source blocker AMEND 3–4.
Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; candidate `3fd6f408e1d565ba65aaeb86c0c4ad0bbc57ab52`.
Patch SHA-256 `f9187933ecd69858ae03762baa8dd57f5907e456e7457db7cba73092471ae111`; request SHA-256 `8cda1fa64a8b1c7dfce56c44f30fd5d84bce508e9d93cf03a426e188f9c912da`.
Cloud applied tree `d10fbe6d3089a4d015748544963824c1053e94d4` совпал с preflight; check-tooling c98d7cee0d PASS.
Kani build PASS 264s, compiletest build17s; Kani0.68.0 / CBMC6.11.0; общий Cloud status FAILURE.
(a) exact T/array N+size, один data-mask transfer/padding=false; source checks и Copy witness сохранены в коде.
(b) buffer внутри marked MEM_INIT_STATE, numeric return transfer/no-MIR guard; native frame/positive credit UNKNOWN.
v2−U1: production2 files +111/−13; tests c U1T36 files +631/−0; пять golden исправлены Failed Checks формой.
Full IntoIter: summary содержит Unsupported для std::array::IntoIter<usize,2>/MaybeUninit<usize> field; property status UNKNOWN.
Статика PASS и production readiness review без findings не заменяют native verification.
Пути ниже: uninit/<selector>/main.rs. ERROR — compiletest/native gate, а не установленный Kani verification verdict.
| Selector | Native | Доступное наблюдение |
|---|---|---|
| maybe-uninit-wrap-u3-positive | ERROR | positive; cause UNKNOWN |
| maybe-uninit-wrap-u3-padding | ERROR | description uninit u8; property status UNKNOWN |
| maybe-uninit-wrap-u3-source-read | ERROR | description uninit u64; property status UNKNOWN |
| maybe-uninit-wrap-u3-intoiter | ERROR | description Unsupported IntoIter/MU field; status UNKNOWN |
| maybe-uninit-buffer-u3-positive | ERROR | positive; cause UNKNOWN |
| maybe-uninit-buffer-u3-plain-negative | ERROR | description uninit u16; property status UNKNOWN |
| maybe-uninit-buffer-u3-pfc-negative | ERROR | description uninit u16; property status UNKNOWN |
| maybe-uninit-buffer-u3-clause-plain-negative | ERROR | description uninit u16; property status UNKNOWN |
| maybe-uninit-buffer-u3-clause-pfc-negative | ERROR | description uninit u16; property status UNKNOWN |
| maybe-uninit-buffer-u3-frame-negative | ERROR | assignable description; actual frame FAILURE UNKNOWN |
| maybe-uninit-buffer-u3-no-mir-unsupported | ERROR | Unsupported description; property status UNKNOWN |
| maybe-uninit-review-positive | ERROR | positive; cause UNKNOWN |
| maybe-uninit-review-argument-return | ERROR | required Failed Checks absent; cause UNKNOWN |
| maybe-uninit-assume-init | ERROR | description uninit u8; property status UNKNOWN |
| maybe-uninit-partial-copy | ERROR | description uninit [u8;4]; property status UNKNOWN |
| maybe-uninit-reset-alias | ERROR | description uninit u8; property status UNKNOWN |
| maybe-uninit-review-overwrite-copy | ERROR | Failed Checks UNAVAILABLE; required diagnostic absent |
| maybe-uninit-review-overlap-copy | ERROR | both Failed Checks lists UNAVAILABLE; diagnostic absent |
| maybe-uninit-review-repeat-local | ERROR | required Failed Checks absent; cause UNKNOWN |
| maybe-uninit-review-reset-zst | ERROR | required Failed Checks absent; cause UNKNOWN |
Overlap/overwrite: ВСЕ строки Failed Checks недоступны: native16/2 отвергнут размерным лимитом; это НЕ пустой список.
Unreachable/foreign FAILURE не установлены; их наличие/отсутствие без evidence не предполагается.
Native0/1,4/1 также size error; Brief HTTP404. Координатору запрошены bounded errors/excerpts/Failed Checks offsets0,4,11,16,17.
Расход $0.1080, reserve $0; возможный repair reserve $0.540 → total$0.648 ≤ cap$0.90, только после диагноза и нового GO.
Не запускать retry без фактов; сохранить все failures/IDs. Детали и reader limitation: EVIDENCE-KANI3300-U3.md.
Вне manifest NOT_RUN: U1T padded-manually-drop и прочие U1 по NOT-RUN.json; все20 выбранных запускались.
Далее: получить bounded причины ERROR; после native PASS отдельное review, затем отдельный replay U1/U2,U6,U7–U9.
Compound storage U8/U9 и select остаются следующим scope; закрытия этих obligations/independent credit нет.
