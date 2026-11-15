# Draft для Limitations #752 — не опубликовано

Текст ниже относится к production std `872d5a43380752786415bc00d2a12ce0e930cb37`
и его Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`. Источник точных roots,
assurance и границ — [INVENTORY](INVENTORY.md). Не переносить сюда S1 NOT_RUN как результат.

> The bounded helper contract proofs check the following write sets on the named
> element, comparator, length, and allocation domains: the two selected elements
> for swap_if_less, the inclusive begin..tail range for insert_tail, the input
> slice for insertion_sort_shift_left, and the destination ranges for sort4_stable
> and bidirectional_merge. The latter two contracts require readable sources,
> writable destinations, and disjoint source/destination spans. Within these
> qualified contract instances, source memory is outside the destination write
> set. Verified-summary consumers are restricted to their matching proved domains;
> a safety-only merge summary does not guarantee destination initialization.
>
> These write-set and disjointness results do not provide a temporal aliasing or
> immutable-byte permission model. In particular, a write within an allowed outer
> input or scratch frame may still violate a live shared reference passed to a
> comparator. Local ManuallyDrop values, gap guards, subsequent reuse of storage,
> and unwind behavior require separate reasoning; the current results do not
> establish complete borrow coverage. Dedicated transient write-then-restore
> controls have been designed but have not been run.
>
> The helper write sets do not describe arbitrary FnMut effects through captured
> references, raw pointers, or global state. Their contract proofs use the specified
> read-only comparator instances. Legal callbacks that update disjoint external
> state or permitted UnsafeCell storage require an explicit additional footprint;
> they are not ruled out by Rust. Listing the closure object alone does not specify
> the transitive footprint of its captures. Existing mutating Cell route checks
> cover selected interior-mutability cases, not general aliasing enforcement.
>
> On this submitted tool pin, the three generic SmallSort trait entry families
> have no direct contracts. Concrete N2 forwarding-wrapper proofs execute real
> trait entries but do not establish generic trait contracts. A separate S1 source
> candidate at std 75a4d1ea6eb60c63c27c1b18e662740d93bafb08 adds contracts to all
> six implementation bodies on upstream Kani 0aac16ef62da9e9d5645782d458593e5d78143ba,
> which includes the fixes associated with #4908 and #5116. Its planned N0..3
> mechanism proofs are NOT_RUN; its frames are scoped to the named KeyLess ZST
> comparator instances. It supplies no new proof credit for this submission.

Перед публикацией сверить текущее #752 отдельно: эта стадия не проверяет live head/ruling
и ничего не публикует. Нельзя заменять текст формулировкой «all immutable mutations checked».
Отсутствие returned references не снимает callback/local temporary borrow obligations;
#733 не считается принятым scope exception. #5040/RFC0016 — upstream follow-up,
а не включённый checker текущих roots. Успех будущего N1 уточнит только dst-frame confinement;
для снятия temporal limitation нужны N2 rejection и legal companions на exact qualified pin.
