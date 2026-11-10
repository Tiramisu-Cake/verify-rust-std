# Track initialization through MaybeUninit slots

Under `-Z uninit-checks`, check the source byte state before transmuting
`MaybeUninit<T>` to `T` or `ManuallyDrop<T>`. Use the data-byte mask of `T`.
Preserve byte state across whole-slot copies and clear it when an empty slot
overwrites an initialized one. Track field writes and slice offsets by address.

The regressions cover partial copies, alias reads after reset, padded values,
and array-valued slots. Native validation is pending.
