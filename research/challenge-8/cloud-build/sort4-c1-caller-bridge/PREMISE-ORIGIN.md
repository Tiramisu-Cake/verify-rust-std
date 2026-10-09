# Actual first c1 entry: final premise classification

Continues 789b0daffcdd3d1b49c83e979aec486542334b46 and previous
sort4-c1-caller-entry/PREMISE-ORIGIN.md without changing historical results.
Actual source: small_sort_general_with_scratch, first sort4_stable at SmallSort254,
blob40939f922bcb6fdc7ee0d30427fa861827043827,
SHA25685c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1.

**Entry boundary reached; exact actual sort4 invocation not present/executed.**
The source-linked bounded fragment stops just before that call. Its normal and
readonly MIR, stock proof AST, retained check and execution trace are saved.
No complete caller theorem or accepted premise elimination is obtained: all
actual caller positives have raw VF1. Target assertions inside a failed whole
function are intermediate evidence, not completed native-return entailment.

| Premise | Fresh observation in third build | Final proof credit |
|---|---|---|
| source4 initialized storage | Native whole mutable-slice array; array_split4, first4 assertion, array_join executed | NOT_DERIVED as completed caller theorem |
| four CURRENT T owners | Native foreach; split4 and append execute, no snapshot/new owner assumption | NOT_DERIVED as completed caller theorem |
| CURRENT F cell/F.own | Native mutable-reference resources asserted and framed unchanged | NOT_DERIVED as completed caller theorem |
| thread/currentThread | Native generated entry resources asserted | NOT_DERIVED as completed caller theorem |
| source/caller frame and native return | Source-frame selected return/native post/leak checks execute; strict dead-code still rejects function | NOT_PROVED, no leak exemption |
| dst4 optional T storage | Native scratch MU array split/unrolled; four stock open_MaybeUninit calls and array_ construction execute before failure | NOT_DERIVED with full native frame restoration |
| T/F type_interp | No generated heap chunks; not reached in bridge; stock produce_type_interp reviewed but unused | remains supplied in prior c1 theorem |
| size_of<T> > 0 | Ghost conditional bridge only; chosen source path admits ZST at len8..15 | remains supplied/conditional |
| generic MU owner/identity restoration | close returns new(inner(old)), no inverse law; full MU foreach stays opaque | NOT_REACHED; independent resource/model debt |

First complete-entry blocker is strict dead-code rejection of generated len<8 fallback
return and original abort branch, made impossible by selected-path filters.
The checker remains enabled. A certified exact CFG/AST projection or another
sound extraction arrangement needs separate implementation and controls;
existing specialized select/unwind projections do not justify a generic bypass.
In bridge the first recorded error is a harness syntax error at line126:
`pointer_within_limits` is a pure bool, not a predicate. Corrected to `== true`
in734af5d8, but new proof is NOT_RUN. Thus type_interp/MU restoration must not be
called the first observed bridge resource failure. They are source-grounded
remaining debts. Identity lemma call is NOT_REACHED.

Fresh slice projection positives and wrong-equality/raw-destination negatives
all pass intended controls in third build; range and duplicate-source authority
negatives fail at intended boundaries. Narrow translator patch is experimental,
value-only, independently reviewed, and NOT an accepted production profile.
No stronger native entry precondition, new ownership/type_interp assumption,
MU inverse axiom, comparator law, c2 change or disabled check was introduced.
