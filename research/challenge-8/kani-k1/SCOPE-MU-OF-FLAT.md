# Открытый scope: MaybeUninit массива MaybeUninit, 2026-11-12

Текущее решение: **(a)**, для qualification использовать `[MaybeUninit<T>;N]` напрямую, без внешнего MU.
`MaybeUninit<[MaybeUninit<T>;N]>` сейчас **не входит в поддержанный layout domain**. Это ограничение Kani,
не утверждение, что сама Rust-идиома или корректный unwrap такого массива являются UB.
Это верификация корректности, не security-работа.

Различать:

- `[MaybeUninit<T>;N]` / `[MaybeUninit<T>]` — обязательный flat scratch scope Part1-B;
- `MaybeUninit<[u8;N]>` — уже поддержанный D0-like storage, не исключать его по наличию внешнего MU;
- `MaybeUninit<[MaybeUninit<T>;N]>` — отдельный nested MU-of-flat layout, источник раннего Unsupported у 4 C1-T2 inputs.

Расширение (b) оставить отдельным решением владельца/контрактом, не реализовывать в C1-T2 repair/M2/M3 исподволь.
Для него нужны validity/required-read mask отдельно от typed preserve и raw extent, сохранение false при unwrap/transfer,
padding/stride/offset, аргумент/return/reset, N=0/ZST и контроль intended inner-payload read. Нельзя обходить layout guard
all-true mask: валидное значение массива MU не означает initialized payload каждого элемента.

Никакого issue/PR или source fix этим документом не открывается. Current workaround — построить flat array напрямую
и выполнить реальные byte writes. Поддержку nested idiom не заявлять; отдельный boundary regression может ждать своего задания.
