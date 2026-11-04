# Unicode typography beta: completed implementation plan

Updated 2026-11-04. The agreed beta is complete and ready for human playtesting.
Later sampler typography refinements are recorded in
[the alignment feedback review](typography-alignment-feedback.md). Its focused
checks and artifacts supersede earlier hashes for the changed lettering and
renderer files; the full-scope checkpoint below remains timestamped history.
All 30 requirements are reconciled in [the audit](unicode-beta-audit.json):
14 supported and 16 supported with explicit practical limits. No required beta
implementation or verification work remains.

The implementation includes Unicode 18 inventory and licensed custom font
coverage, shaping and variation handling, combining marks and expressive emoji,
bidirectional text, grapheme and line breaking, measurement, balloons and export
regressions. Character presence, source identity, sampled style and browser
execution remain separately described in the evidence.

## Final verification

- All 2,336 current Python cases are accounted for by recorded passing phases
  under exact dependency continuity. The final stage retains 2,327 unaffected
  cases and freshly passes all nine cases in the corrected metadata module.
  Earlier coverage accrued as 1,952 + 263 + 121; both interrupted masters remain
  timeouts. No single successful full-suite invocation is claimed.
- All 367 current JavaScript checks passed. The final input comparison verified
  all 448,437 paths and hashes and the canonical decisions for all 199 sources.
- Independent private emoji reproduction passed. Both emoji fonts and their
  manifest stayed byte-identical; 780 provenance leaves were intentionally
  updated through an actual regenerated and checked glyph review.
- Current native/cache/field proofs, dependent-font continuity and the final
  199-source atlas were reviewed using the supplied local PNG/SVG renderer.
- The metadata-only inventory scan now uses the original lazy loader: 2.23
  seconds versus 289.79 seconds. All nine affected cases passed in 34.14 seconds.
  Its assertions and the other drawing/subsetting functions are unchanged.

Final evidence: `output/final-checks/final-current-scope-proof.json`,
`output/final-checks/final-scope-guard-run.json`,
`output/final-checks/after-final-metadata.json`, and
`output/final-checks/final-requirements-continuation-review.json`.
The audit and source ledger were applied only after these actual proofs passed.
The generated style-status report now references the current manifest.

## Limits and handoff

Sampled style and native-source checks are not exhaustive linguistic or
native-reader approval. Host dictionary quality for Thai, Lao, Khmer and Myanmar,
ambiguous text-grid heuristics, and arbitrary Egyptian expression collisions
remain provisional. Browser/editor/export evidence retains its recorded dates
and asset scope; no final-pressure browser execution is claimed. The user's
local-rendering instruction remains in force for this work.

The review corpus is retained in `tools/unicode-checks.html`, `tools/checks.html`
and the linked source/field/atlas reviews. Human review and playtesting are the
next product activity, as agreed in the brief.

## Historical implementation record

The following entries preserve earlier staging, incomplete checks and timeouts.
Their pending/running wording is historical; the completed checkpoint above and
current audit take precedence.

### Latest final validation: second attempt timed out, beta incomplete

The first one-process final attempt timed out and is historical, not a pass.
Its source inputs remained unchanged. Remaining emoji input-loading and full-frame
hole-counting costs are now repaired:79read-only loaders, exact cropped-hole
math and narrowly pinned read-through compatibility.22live controls pass;
actual two-case check passes in22.97s, with four independent preparations at
0.42–0.44s each and warm complete case0.91s. All4006legacy cache files stay
byte-exact. Real private rebuild passed in828.46s: both emoji fonts and manifest
byte-exact; only780expected provenance hashes changed in the honestly regenerated
and published glyph review. No font artwork, metric or layout changed.

A fresh actual collection defines2328cases. Shared-writer/race review assigns
13serial-prefix tests,666native/catalog tests,1596emoji/source/pen tests and
53other units. The exact disjoint union is pinned in
`output/final-checks/parallel-validation-manifest.json`; no case or prior result
is omitted/reused. This is normal full-scope CI sharding, not a subset described
as a whole-suite pass. All13shared writers passed in66.82s before worker launch.

The second final attempt is now **TIMEOUT**, not a full-scope pass. The inner
1790-second budget expired; the outer process terminated with124 after1790.69s.
Authoritative records:
`output/final-checks/final-parallel-validation-run.json` and
`output/final-checks/final-parallel-validation/result.json`.
The serial13, emoji1596 and unit53 batches passed. The native/catalog batch
remains partial: no assertion failure was recorded before interruption in its
first marked-CJK test. Completed batches do not establish complete scope.

Post-run input verification passed, terminal0: all448436inputs unchanged,
0missing,121.35s. Evidence:
`output/final-checks/after-parallel-timeout.json` and
`output/final-checks/post-parallel-inputs-run.json`.
Root session45693 is historical and terminal; its former RUNNING checkpoint is
superseded by this timeout and post-fingerprint result. Remaining native coverage
and its slow marked-CJK path must be resolved before completion can be claimed.
No completion/status draft was applied.

### Historical first final attempt: timed out, superseded by second attempt above

The finalcheck reached its unchanged1800-second ceiling and stopped with124.
It is not a full-suite pass. All four catalog tests and subsequent contextual/
dense/Egyptian cases passed; the run reached activity-emoji skin/sequence tests.
Durable result: `output/final-checks/final-attempt-30m/terminal-summary.json`.
Post-run verification is terminal0: all448428input hashes/pathsets and canonical
source decisions unchanged,0missing. No completion/status draft was applied.

Root acknowledged that the remaining suite cost was insufficiently accounted
for before that launch. Many read-only glyph tests still reopen large WOFF2
fonts perparameter using the original decoder. Only that input-loading work is
being repaired; both independent prepare calls and all assertions stay. Cheap
name/cmap-only inspection must retain lazy behavior; do not introduce eager
full-glyph decode in381font metadata loops. No new fullcheck may start until
short actual-path checks demonstrate these fixes. No product/font change is
planned, and no three-hour/30-minute loop may be silently repeated or extended.

### Historical first-attempt launch checkpoint (superseded)

All known product defects and the three residual test redundancies are fixed.
162 focused controls pass in19.32s; the actual public duplicate/CJK check passes
in11.93s while retaining every1002pair assertion. All13 final performance-code
hashes match. The stable snapshot is terminal0:448428files,0missing,123.16s.

The following records describe the historical launch of root session97476;
its former RUNNING status is superseded by the terminal timeout above:
`/tmp/unicode-final-python-complete.log`, authoritative record
`output/final-checks/final-python-complete-run.json`. It collects2309tests,
ignoresnone, stopsatfirstfailure and has a hard1800-second process-group cap.
Thirtyminutes is a killceiling, **not a runtime estimate**. No implementation
changes or further exploratory checks are planned. All test inputs/code/assets
are frozen until actualterminal plus post-run verification against
`output/final-checks/before-python-final.json`. A running job, timeout or early
failure must never be called a complete-suite pass. After successful terminal
and closureproof, reconcile all30requirements/statuses and onlythen finishgoal.

### Current user instruction (2026-11-03)

The user explicitly directed this run to use the supplied local specimen renderer
and stop actions requiring manual browser approval. No further browser calls,
download attempts, or browser permission requests are to be made for this work.
Use `render_specimen.py`, local PNG/SVG inspection, whole-field guards and
source/runtime tests for current changes. Retain existing dated browser evidence
and its scope honestly; local specimens do not execute the app renderer. This
instruction overrides the browser steps below for this run. The interrupted
actual Download PNG verification is not a blocker requiring another approval.

### Historical performance constraint and repair checkpoint (2026-11-03)

The user explicitly forbids rerunning the three-hour suite/test until its
performance problems are fixed. At this historical checkpoint, no new full run
had been launched; the later attempts and terminal results are recorded above. The
post-integration2221-case command was collection only (1.33s); the35 focused
live tests passed in37.96s. This instruction supersedes the immediate full-run
steps below: fix and verify performance first, then take a fresh input snapshot.

The measured fixes remove repeated manifest parsing and full dependency walks
inside 25087 catalog comparisons, reuse successful identical whole-font proofs
only while every dependency and runtime input remains unchanged, and avoid
redundant drawing decoding when exact GLYF bytes already prove identity. Byte
mismatches still execute the original drawing comparison. All per-glyph,
raw-source, layout, metric, cache and provenance assertions remain in place.
The final focused regression gate passed 146 tests in 16.41 seconds. Actual
measurements cover two parents plus 1002 catalog comparisons in 18.08 seconds
(the repeated 1000 take 0.437 seconds), and five complete TT/dense/CFF font
proofs plus repeated dependency-checked calls in 18.30 seconds. These are
bounded representative measurements, not a whole-suite runtime prediction.
Evidence: `output/final-checks/native-proof-reuse-performance-review.json`.

Emoji qualification inputs are indexed once per content/identity generation;
source edits, replacement and read races invalidate the index. Nine controls
pass. A real independent emoji build into private outputs was profiled with a
hard 60-second limit and stopped at that deadline: **incomplete, not pass**.
All four public products remained unchanged. Contour simplification is its
measured hotspot; no prepared/build result cache substitutes for independent
reproduction. Evidence: `output/final-checks/emoji-build-profile/result.json`.

All new profiling and focused verification commands have hard time limits;
`output/final-checks/run_bounded.py` records and terminates the command's own
process group at its deadline. A timeout is failure, never successful evidence.
No whole-suite run is authorized merely because a timeout wrapper exists:
actual fixes and bounded representative measurements are required first.
Public assets remain at the reviewed integration state. The final input
baseline and complete suite remain pending after performance work.

#### Performance gate passed; final verification now pending

The tests-only native WOFF2 decoder retains exact reference tables after
canonical serialization, fresh font objects and source/library identity checks.
CFF, raw sources and builders retain the original loader. All 159 focused
controls passed in 17.87 seconds, including actual native use, composite/hint/
overlap fidelity and source/read/cache races. A new unprofiled representative
check completed in **119.004 seconds under its original 120-second cap**:
SignWriting 37886 glyphs (75.15s), Khitan 11365 (28.06s), CFF 1301 (8.53s),
and a marked Jigmo parent plus 1001 comparisons (6.96s). Identical historical
proofs reuse only after full dependency validation; 1000 repeated marked
comparisons take 0.409s. No speed ratio is claimed against the earlier profiled
run. Code is frozen; exact hashes and native-backend metrics are in
`output/final-checks/native-proof-reuse-performance-review.json`.

The fresh expanded input snapshot is running with a 360-second cap:
`output/final-checks/final-input-snapshot-run.json`. It includes the source PDF,
Seal review, 4006 pen-cache files and six native decoder libraries in addition
to the reviewed closure. After a successful stable snapshot, the complete
current Python suite will run with a hard **1800-second ceiling**. A timeout
fails the gate; it will not be extended into another three-hour run. The final
post-run fingerprint and requirement/status closure remain mandatory.

#### User clarification about the proposed 30-minute ceiling

The user says a run of that length is appropriate only as a high-confidence
final check and asks what it verifies and why it is slow. No full suite has
started. The 30 minutes was a safety ceiling, not a measured runtime estimate.
The first expanded snapshot succeeded: 448426 files, 0 missing, 124.98 seconds.
It is now historical because read-only cost inspection found three residual
redundancies: repeated complete pressure-lineage proofs, four read-only test
modules bypassing the faster decoder, and public CJK lineage bypassing proof
memoization. Only these test paths are being corrected; every first-state proof,
per-glyph assertion and independent asset rebuild remains. Short bounded
controls must pass and the snapshot must be refreshed before the final suite.
Do not treat the earlier 30-minute proposal as an already-launched run or a
justified runtime prediction. No new product implementation gap was found.

### Current public-policy integration checkpoint (2026-11-03)

The diagnostic is terminal 1: **2159 passed, 13 failed, 7 SWIG deprecation
warnings in 11628.62 seconds (3:13:48)**. All thirteen traces are mapped to
reviewed strict corrections or the Music/Funky geometry repairs. It remains
diagnostic evidence, not the required final complete-suite pass.

The ordinary transactional build produced **381 fonts, 181297704 bytes**.
Only Music and Funky changed; all 379 other fonts are byte-exact. Both actual
fonts and reports exactly match accepted staged candidates. The canonical
source decisions and strict corrections are installed. Actual-public semantic
checks, all 60 Music contexts, 28 fields, the original geomantic and harpoon
bounds, and full 612/326-glyph native/cache/constructor proofs pass. Root
inspected and accepted fresh local Music/Chemical/geomantic 22/44 specimens.

Both affected atlas pages are refreshed and accepted; all 17 pages cover 199
sources with 204 current font references. All 145 regular visual decisions and
123 dense font/report continuity proofs are current. Standardized CJK and all
92 marked companion dependencies remain exact and authenticated. The combining
catalog rebuild produced 1838 drawings and 2 context records from 300 sources.
Asset versions are refreshed; **367 JavaScript tests pass**. Fresh independent
coverage and routed-outline audits passed with 0 missing cmap requirements,
0 unexplained outlines and 0 routing gaps. Their presence/geometry scope does
not claim sequence or linguistic validation. See
`output/final-checks/current-font-data-audits/terminal-summary.json` and
`output/final-checks/dependency-continuity/current-dependency-proof.json`.

The outstanding work is to establish acceptable performance, complete the
actual final input closure (including PDF/source art and pen-cache inputs),
take a stable snapshot, obtain a fresh terminal complete-suite result under a
hard limit, verify the post-run fingerprint, and reconcile all 30 requirement
and status records. The user's performance constraint above takes precedence
over older full-run steps. No further browser/download/approval action is
needed. The beta remains incomplete.

### Earlier diagnostic/staging checkpoint (historical, superseded above)

The second full run stopped after 72 passes on a stale direct raw/current curve
comparison for a treated Mongolian variant. All four catalog tests passed in
that run. B's strict contextual correction now passes 17 tests: all 128
selectors across 512 contexts, ordinary controls, raw→frozen native drawing
identity, current cache/GID/position identity, CGJ and mark-selector behavior,
and 11 negative cases. Only the three assigned contextual modules changed.

C's diagnostic remainder is running in session **53910**:
`/tmp/unicode-remainder-diagnostic.log`. It excludes the three corrected modules
and the already-passed catalog module, gathers all failures, and is **not** a
replacement for a fresh complete suite. All included live tests, shared helpers
and production assets remain frozen until its actual terminal result.

A screened the remaining source assertions and prepared seven isolated strict
updates, with 25 staged tests passing. Patch and evidence:
`output/font-review/final-checks/staged-native-tests/proposed.patch` and
`review.json`. They preserve the original native constructors, distinctions,
shaping and metrics while independently authenticating approved treatment.
Do not apply them until C finishes and every actual diagnostic failure is read.

A also found a genuine Music geometry issue. The pressured low four-bar tremolo
has a tiny extra contour and a combined-field counter failure. Preserving only
the exact derived-native **GID588 / u1D25B_low** fixes all 60 shaping/count
contexts and all 14 individual/combined 384/1024 fields. Its raw Music source and
both constructor/rules hashes are independently authenticated; all other 611
glyphs and all layout/metrics stay exact. Root inspected the 22/44 comparison.
The earlier GID369-only proposal is insufficient and was never published.
See `docs/music-source-preservation-review.json`.

B's minimal policy, builder/helper patch and 12 policy fixtures are staged only
under `output/font-review/final-checks/music-policy-staging/`. Complete 612-glyph
native/cache/policy proof passes, and its WOFF2 glyph/layout data match A's
independent rescue. No live policy or font has changed yet.

The diagnostic has also exposed an equal-length chemical harpoon pair whose
painted widths differ by seven units, beyond the existing six-unit semantic
bound. The first isolated repair preserved that single already hand-inked native
glyph, authenticated by replaying the pinned chemical and alphabet-ink
constructors. Its isolated candidate now passes all 326-glyph native/cache
proofs, all 12 field checks and all five harpoon semantic checks; root inspected
and accepted its local 22/44 comparison. All other 325 glyphs stay byte-exact.
That historical single-harpoon stage passed 24 combined policy fixtures and
is superseded by the extended Funky candidate below. A has strict staged
Cuneiform and Devanagari test corrections with all six affected tests passing;
these retain exact native construction, frames, metrics and current cache proof.

Further diagnostic findings (still active): asteroid failure is a stale
contour-order pairing. The isolated role-aware correction preserves winding,
spatial containment, counts, bounds, shaping and 21 distinctions; both tests
pass and root inspected its local specimen. Geomantic centering is a genuine
14-glyph defect. B's extended Funky policy now preserves exactly those 14
already hand-inked native figures plus the harpoon: all 16 original geomantic
predicates, five harpoon constraints, 14 field checks and 26 combined policy
fixtures pass; the other 311 glyphs and layout/metrics are exact. Root inspected
and accepted both 22/44 specimens. The original centering/length bounds are
unchanged. Earlier single-harpoon staging is archived and its evidence rebound
historically. Neither policy is public. The diagnostic's complete terminal
failure list is still pending.

After diagnostic completion: resolve every failure, apply reviewed strict tests
and the minimal Music and Chemical policies, then run the normal transactional
builder and require only the Music and Funky fonts to change (379 others exact).
Review both actual final fonts and refresh their dependent catalog, versions
and audit evidence. Finally collect and
fingerprint the new state, run the entire Python suite from the beginning, and
complete the post-run fingerprint and 30-requirement audit. Existing scoped JS,
CJK, CFF, inventory/outline and local visual results remain separately recorded.
All current visual work uses the supplied local renderer; no browser, download
or approval action is needed.

### Earlier CFF correction checkpoint (historical, resolved above)


All92marked companions are built and their final font/base/inherited-dense hash
links pass. Combining catalog72510 is terminal0:1838drawings,2context records,
300sources,9,392,408bytes. Final inventory37100and routed-outline17124 audits
are terminal0;172365cmap-covered drawing requirements,172360positive routed
outlines plus5explicit exceptions,zero unexplained/routing gaps. All recorded
font SHAs match actual final files at that checkpoint.

Focused actual CFF domain23492 exposed a genuine Type2 width encoding bug:
1263adapted and5pre-existing retained charstrings report advances inconsistent
with hmtx. A/B own a width-operand-only correction with exact drawable-command
proof, explicit five-retained-glyph provenance, strict negative fixtures and
new content-addressed cache namespace. No public corrective build yet; do not
launch finalfulltests or claim completion until isolated correctedcandidate,
localfield inspection and ordinarytransactional rebuild pass. The existing380
other font caches should remain exact. RootCJKdomain session4018is still running
(`/tmp/unicode-final-cjk-domain-tests.log`), first3tests pass, complete92copyproof
pending. After correction:refresh affected CFF/atlas/audit evidence, assetversions,
currentJS/fullPython and final30requirement audit. Localrenderer only.

### Earlier primary-integration checkpoint (superseded by correction above)


The sole normal transactional primary build is terminal0:381shards,
181,304,236bytes. All145regular sources have accepted visual evidence tied to
actual final font bytes; sources45/50 were re-rendered and inspected after their
final hashes differed. All4final Cuneiform/Duployan/CFF fields pass384and1024guards
and22/44inspection (`docs/final-policy-production-review.json`). All123dense
public font and detailed report SHAs exactly match authenticated private accepted
candidates. Native invariants pass for146regular/CFF sources and97,679glyphs.
All17final atlas pages/199source samples were inspected locally
(`docs/final-source-style-review.json`). No browser/download/approval action was
used. CFF's new cache namespace is honestly recorded:onlynativeheadbit11 differs
from the isolated packaged input; all1301native drawings/order/metrics are exact,
and strict nativeSFNT reconstruction plus31negative/compatibility fixtures pass.

The final standalone CJK variation build is terminal0:1002pairs/902bases and
exactly the inspected prototype font SHA. Root owns the running92marked-companion
build session40463 (`/tmp/unicode-final-marked-cjk.log`). After actual terminal0,
run `tools/font/build_combining_outlines.py`, inventory/outline audits,
`tools/version_assets.py`, current `npm test` and one full terminal Python suite.
Do not reuse old1994/2063counts as current results. Reconcile all30requirements,
all199source production states and final file hashes only after checks pass;
then complete the goal. The goal remains active/incomplete until that work ends.

Primary build evidence:`output/font-review/final-builder-integration/public-after.json`;
regular continuity:`output/font-review/production-visual-match.json`;
dense continuity:`output/font-review/dense-production/public-continuity.json`;
native invariants:`output/font-review/supplemental-production/verification.json`.

### Earlier local staging milestone (retained history, superseded above)


- All 128 pen-adaptation findings now have explicit local sample acceptance in
  `docs/supplemental-acceptance-index.json`. All 199 source decisions reconcile
  in `docs/unicode-style-dispositions.json`; this is not full-glyph completion.
- First 15 pressure sources are built: 8,470 glyphs, 8,148 adapted, 141 blank,
  181 retained by guards. Native layout/identity/bounds checks pass, 17 fields
  pass, six final specimen pages and the 31 largest encoded retained cases were
  inspected. Frozen evidence: `docs/supplemental-production-first15-review.json`.
  Historical/source checks: 37 initial passes plus three strict UVS metadata
  rechecks, one CJK positioning pass, five cached catalog/native-path passes.
- Four optical-em sources are built, including Old Uyghur. Egyptian and
  Anatolian runtime ink changes remain accepted with current focused evidence.
- All three private regular warmers and four range helpers are terminal with
  frozen public fingerprint checks passed. All 130 planned source samples now
  have explicit production/rescue acceptance, with exact source-set equality:
  `docs/supplemental-private-production-review.json`. All 132 generated native
  guard-retention specimens have been inspected; Brahmi's isolated BNJ carrier
  is accepted only through actual numeric joining contexts, with two passing
  regressions (`docs/supplemental-private-retention-review.json`).
  Sources 45 and 50 require their separately audited Cuneiform and Duployan
  native-preservation wrappers at final integration. Private warm-stage fonts
  correctly predate those repairs and are not final field/style acceptance.
  B's initial full authentication proved 65 sources before a source9 retained
  representation mismatch. Only eight exact counted, isolated zero-ink point
  contours differed; every drawable command remains exact. The narrow verifier
  rule passes the actual410glyph source and30fixtures. Original aggregate
  exit1 is retained honestly. Resumed verification55140 is terminal0:
  130sources/87,908glyphs authenticated, plus all4auxiliary ranges/21,949selected
  GIDs. Earlier65proofs are explicitly bound to unchanged hashes; fresh group2
  handles only the two proven empty Mongolian wrappers as nonpainting.
  `output/font-review/supplemental-warm/verified.json` records the complete
  cache-stage scope. Private merge9496 is terminal0:167,641files merged,
  95duplicates byte-identical. Public fonts stay frozen.
  Public assets remain at the first-15 checkpoint until all six dense workers,
  all authentication gates and cache merge finish, followed by one normal
  production build. Do not edit frozen kernels or recipes under running jobs.
- Native CFF source 192 has an isolated 1,301-glyph accepted candidate: 1,263
  adapted, one blank, 37 retained. U+18F6C keeps its exact native charstring
  under `cubic_source_preservation.py`; both 384/1024 whole fields pass. All post-save identity/layout/bounds checks pass;
  maximum native bound error is 0.00545 design units (tolerance 0.01).
  Local visual review is complete; production integration remains.
- Source 9's narrow U+1262D connector needs its exact native component closure.
  `source_preservation.py` records the policy; independent 384/1024 fields pass.
  The first-15 kernel is unchanged. `docs/guarded-rescue-review.json` records
  all remaining specialist sample dispositions.
- The five-source dense native-curve kernel is ready, with conservative inward
  contrast reduction, smooth flex, native fallback and independent guards.
  Bulk source integration, retained-case triage and companion rebuilds remain.
  The isolated standardized CJK variant candidate in
  `build/dense-cjk-prototype` is terminal: all 1,002 mappings pass frozen/native
  lineage checks; 1,573 pen glyphs, 67 guarded flex, 264 native retentions, one
  blank. Representative 22/44 px comparisons were inspected; public variants
  remain unchanged. Three original private dense warmers run across 123 shards /
  146,617 retained glyphs: sessions 78814/89188/30117, logs
  `/tmp/dense-warm-group-{0,1,2}.log`. C owns terminal outcomes. Public assets
  must stay at the first-15 checkpoint while all dense workers run.
- All 37 standalone math variant pairs were inspected locally. Their naturally
  calligraphic letters and reviewed historical relations are retained;
  `docs/math-variant-style-review.json`. Native font bytes are unchanged.
- No new full Python suite has been launched. Preserve the terminal 1,994-test
  baseline and run current affected suites after stable integrated outputs.
  No further browser calls or manual approval requests are part of this run.

Dense ahead workers 21626/32028 cover 36 future shards / 37,708 glyphs;
logs `/tmp/dense-warm-ahead-group-{0,1}.log`. Tail helper55933 covers eight late
group0 shards /7,439glyphs under its own unchanged-mapping plan;
`/tmp/dense-warm-tail-group-0.log`. At10:52 all six owned handles were verified
live: conservative max-per-family/GID processed work118,118/146,617 (80.6%).
This is work progress, not unique Unicode/artwork/style coverage. Original,
ahead and tail completion, strong authentication and matching family-result
gates are required before integration; shared kernel and public files stay
frozen. C owns these outcomes.

### Scope and decisions to preserve

`docs/unicode-beta-brief.md` remains the agreed specification. Complete its full
Unicode typography and renderer scope, including assigned public characters,
standardised sequences, native shaping and joining, bidi, graphemes, line
breaking, marks, emoji, measurement, balloon sizing, and exports. The product
stays static, automatic, and free of language/font configuration.

Preserve the original Dad/Calvin art. Keep the approved expressive procedural
emoji treatment at strength 1.7 with fine-detail safeguards, 1.4× optical size,
and stronger ink. Prefer repeatable code-based treatment over further imagegen
batches. Preserve native letterforms, joining, marks, reading order, mathematical
alphabet distinctions, meaningful colour, and structural diagram geometry.
Native font coverage and lack of tofu do not establish completed comic styling.

Human playtesting and native-reader feedback may follow beta. Mandatory expert
approval, a full mathematics/music markup engine, every possible diagram
grammar, and an exhaustive browser/OS matrix are not additional beta gates.

### Current state

| Area | Current evidence | What remains |
| --- | --- | --- |
| Unicode inventory | Unicode 18.0.0 and authoritative data are pinned. Inventory: 172,873 assigned public points; 172,365 drawing requirements and 521 behaviour requirements overlap by 13 visible format signs. | Preserve and rerun affected inventory checks when sources/routing change. |
| Actual drawing reachability | Latest outline audit: 172,360 positive first-painted drawings plus five explicit blank/context exceptions; zero unexplained gaps and zero routing gaps. | Geometry is not identity or style proof. Re-audit affected routing and generated outputs after changes. |
| Emoji | 3,963 fully qualified sequences; 5,533 exact forms. Approved procedural finish, optical presence, and colour provenance are implemented. | Preserve existing treatment and category-specific detail guards during other work. |
| Variations and marks | 1,437 standardised pairs accounted for. All 128 contextual pairs checked in 512 contexts; native CGJ, spacing-mark tails, numeric enclosures, and positional mark repairs have focused evidence. | Guard these behaviours while adapting sources. Invalid cross-script syllables can legitimately retain native dotted-circle carriers. |
| Layout and script behaviour | Pinned bidi/grapheme/line-break conformance and application regressions pass. Recent fixes protect dictionary units and dependent vowels, proportional prose with structural symbols, and native format-sign fields. | Resolve concrete newly observed routing/layout defects; retain documented source-specific limitations. |
| Egyptian composition | All 982 enumerated native insertion candidates recovered, with zero unmatched. Earlier 910 entries remain unchanged; mirror helpers, alternates, damage, enclosures, and documented cell rules have focused source/runtime checks. | Thin mixed-dialogue ink is a visual gap. Enumerated source templates do not prove arbitrary expressions collision-free or linguistically correct. |
| Source-style triage | All 199 source files / 381 shards sampled at 22 px and 44 px beside Dad. Decisions: 128 need pen adaptation; 35 provisionally retain; 25 guarded; three optical, three weight, three mark-context, one structural, one nonvisible. | Implement and review the identified treatments. These are sample judgments, not all-glyph or language approvals. |
| Actual product smoke | Editing, copied link, PNG download, reset, shared-state restoration, reload/font wait, and image clipboard passed with mixed Unicode. Existing art and approved emoji presence remain. | Repeat affected integration checks after production changes; retain explicit visual findings rather than treating this pass as style completion. |
| Source/licence pipeline | Source hashes, derivative names, supplied notices, and Seal Sans source offer/rebuild have tests and manifests. | Check any newly modified source's terms and update provenance, output hashes, and source offers as applicable. |

Authoritative review records:

- `docs/unicode-beta-audit.json`: requirement-by-requirement evidence matrix.
- `docs/source-style-review.json`: exact source/sample hashes and visual triage.
- `output/font-review/source-style-atlas.json`: sampled source inventory.
- `docs/product-unicode-smoke-review.json` and
  `output/font-review/product-smoke-unicode.png`: actual product check and export.
- `docs/insertion-mirror-helper-review.json`: recovered Egyptian inventory.
- `docs/unicode-progress.md`: chronological implementation and test record.

The latest full Python run is **terminal: 1,994 passed, seven warnings in
7,526.40 seconds**, recorded in `/tmp/unicode-beta-full-python.log`. Its
collection predates the latest focused Egyptian regressions, which separately
passed nine current source tests. Latest full JavaScript result: **357 passed**;
latest Unicode browser corpus: **676 cases, no failures or geometry failures**;
last general browser corpus: **33 passed**. These are dated evidence for their
tested inputs, not a promise that later edits have already passed. There is no
unfinished Python run to poll or restart. Do not rerun the whole suite merely
to obtain a newer collection timestamp.

### Local visual review workflow

Use a local deterministic specimen renderer as the default for font and outline
iteration. The new entry point is `tools/font/render_specimen.py`; consult its
`--help` for the implemented CLI. It uses the existing FontTools, HarfBuzz, and
PyMuPDF dependencies to shape native glyphs and write local PNG/SVG specimens
with a JSON evidence record. It supports COLRv0 colour layers, decodes WOFF2,
rejects missing glyphs and unsupported COLRv1, and reserves full native ink
bounds. It needs no HTTP server, browser tab, account,
remote image-generation service, or localhost permission.

Verified entry points (run from the repository root):

```sh
.venv/bin/python tools/font/render_specimen.py --atlas-page 1 --output output/font-review/offline-source-style-01
.venv/bin/python tools/font/render_specimen.py --spec tools/font/specimens/unicode-groundwork.json --output output/font-review/offline-groundwork
.venv/bin/python -m pytest -q tests/test_render_specimen.py
```

`--atlas-page` is 1-based (1–17). `--spec` accepts a JSON `samples` array;
each sample has `label`, `font`, and `text`, or an explicitly ordered `runs`
array whose entries each have `font` and `text`. Runs may specify HarfBuzz
`direction`, `script`, and `language`. Font paths are absolute or repository
relative. Explicit run order is caller-provided; it is not a bidi paragraph
algorithm. The atlas mode reuses the project's grapheme segmentation and native
shaping aliases through a bounded local Node subprocess, without a server.
Verification: five focused tests passed in 35.27 seconds. Atlas pages 1 and
15 and the seven-row groundwork fixture were rendered locally; pages 1 and the
groundwork fixture were visually inspected. The page 15 artifact includes tall
stacked Khitan. No localhost access was used for this groundwork.

Output is three sibling files: `.png`, `.svg` (all text outlined), and `.json`
(source hashes, shaped glyphs, advances, offsets, bounds, and limitations).
The renderer does not fetch missing source files; use the pinned local assets.
The included groundwork fixture compares Greek sources and includes Arabic,
Egyptian source ink, meaningful colour, and a skin-tone ZWJ emoji. Separate
native-font samples do not reproduce the app's optical emoji finish.

For each experiment, render the unchanged source and candidate with the same
text and dialogue/detail sizes. Include original Dad lettering in comparisons,
preserve the sampled strings and source hashes, and inspect the saved PNG with
the local image viewer. Keep native shaping output, positions, bounds, selected
font, and any missing-glyph findings in the JSON evidence. Use conservative
script-specific samples as well as mixed-script text; isolated glyph inventories
alone miss joins, contextual alternates, and mark attachments. Save candidates
under distinct output directories, without replacing the accepted baseline.

This tool is a local image renderer, not a learned style model. It also does not
execute the application's JavaScript routing, bidi, line breaking, balloon
layout, canvas drawing, or clipboard/export actions. Local specimen success
cannot substitute for the final browser checks of those behaviours. Avoid
duplicating the app renderer and then claiming the duplicate proves the app.

Use the browser only for a bounded integration question that cannot be answered
by the local renderer and source/runtime tests. Keep each browser call short;
use finite event timeouts and save returned exports directly. The previous
share/download call returned successfully but took 1,245.94 seconds. The user
also encountered a localhost permission interruption. Do not repeatedly ask for
the same authorisation or attempt to bypass browser permission controls. Local
specimens allow independent font work to continue while any genuinely required
browser access is unavailable.

### Parallel work and ownership

The user explicitly requests more subagents. On resumption, the coordinator
should dispatch the first three tracks concurrently, using the available slots,
and assign the independent audit as a slot becomes free. Each task must carry
the brief, current findings, exact owned files, and expected evidence. Require
concrete artifacts or code and test results, not an open-ended investigation.

| Track | Initial subagent assignment | Owned work and deliverable | Dependencies and completion evidence |
| --- | --- | --- | --- |
| A: Greek/font routing | Diagnose and fix the observed wide Greek text. Inspect whole-word source preference, accents/marks, and mixed-script behaviour. | A narrowly scoped routing module or patch plus targeted regression tests and before/after local specimens. Coordinator assigns ownership of shared `js/fonts.js` before editing. | Current inspected metrics show KleeOne Greek advances of 1,000 units at 1,000 UPM, while WenKai Greek is about 500–570. This is a concrete lead, not an implemented fix. Verify chosen source is licensed, hand-lettered, and complete for the requested native field; preserve variation and mark routing. Confirm the actual exported Greek strip after integration. |
| B: Supplemental pen treatment | Prototype smooth variable pressure and contour variation for the 128 typeset-source findings, grouped by actual shape constraints. | New experimental treatment module, isolated candidate font outputs, local specimens, and a proposed per-source treatment list. Do not edit the production manifest or mass-rebuild sources concurrently. | Compare 22/44 px samples against approved studies and Dad. Preserve topology, counters, native joins/anchors, script identity, and distinctions; use finer treatment for dense scripts. Demonstrate the treatment visibly improves the sampled forms before scaling up. Edge noise alone is insufficient. |
| C: Egyptian optics | Prototype stronger mixed-dialogue ink and any necessary optical adjustment. | Isolated source/outline or measurement experiment, candidate specimens, focused geometry/source checks, and a proposed production patch. Coordinate ownership before editing shared `js/text-metrics.js` or `js/comic.js`. | Compare core Egyptian Text, UniHieroglyphica, grouped and ungrouped signs, mixed dialogue, damage, RTL, and enclosures. Protect internal detail and all 982 insertion templates. Measurement must reserve the same ink that painting/export uses. Do not silently replace source identities or apply emoji constants to all scripts. |
| D: Independent completion audit | Review the brief and evidence without writing production code. Start when a slot is free; update after integration. | A gap list mapped to every brief requirement and the current evidence matrix, with concrete verification commands and contradictory/stale claims identified. | Distinguish completed implementation, current targeted evidence, dated evidence, and missing evidence. Check licence/source obligations and all remaining visual categories, not just the three tracks above. Return unresolved items to the coordinator rather than narrowing scope. |

The coordinator owns integration, `docs/unicode-beta-audit.json`, this plan,
`docs/unicode-progress.md`, generated manifests/catalogs, and the final build
sequence. Agents may read all files but must not overwrite another track's
outputs. Allocate unique prototype output paths. No agent runs a mass font build
while another is changing its inputs. Only one owner updates a generated file
or performs the final source rebuild/hash refresh. Use existing checkout state;
do not reset the large dirty worktree or commit without instruction.

### Integration sequence and gates

1. Verify the local renderer's fixtures and outputs, and record its command and
   limitations. This groundwork can be completed while the overall goal stays
   paused. Resume implementation only when the goal is resumed.
2. Dispatch tracks A–C with disjoint ownership. The coordinator reviews their
   first concrete prototypes before any broad source adaptation. Reject both
   invisible treatments and treatments that damage native forms or fine detail.
3. Integrate accepted Greek routing and Egyptian optical changes one at a time.
   Run the affected source, native-shaping, measurement, and JavaScript tests.
   Keep prior artifacts available for comparisons.
4. Apply the accepted supplemental treatment in bounded source groups. Record
   which of the 199 source decisions each group resolves. Include the guarded,
   optical, weight, structural, and mark-context findings rather than assuming
   the 128-source prototype closes the entire style requirement. Confirm native
   shaped positions, joins/anchors, visible distinctions, open counters, and
   actual-size appearance. Rebuild dependent variants/catalogs only when needed.
5. The coordinator updates generated assets, required licences/source offers,
   coverage and provenance reports, and `tools/version_assets.py` outputs. Run
   meaningful focused checks first; broaden to documented project suites when
   the integrated change warrants it. Record terminal results and exact scope.
   Do not launch duplicate full suites or mutate build inputs under a live run.
6. Run final bounded browser integration on the current assets: general and
   Unicode harnesses, actual mixed-script comic edits, share restoration,
   font-wait/export behaviour, reset, PNG and clipboard actions, plus changed
   visual examples. Include native sentences, extreme marks/Zalgo, emoji,
   diagrams, dictionary scripts, variation sequences, and malformed/private or
   unassigned input. Reuse the existing corpus and add only relevant regressions.
7. Have track D reconcile every requirement with the integrated state. Recheck
   the remaining uncertainties directly. Refresh this plan and the evidence
   matrix, retain the playtesting corpus and provisional linguistic limits, and
   report any actual gaps. Mark the goal complete only when the full brief is
   achieved and no required work remains.

### Immediate handoff

The next production changes should address the observed Greek routing/spacing,
Egyptian weight, and supplemental source styling. Font reachability and broad
test coverage are already substantial; repeatedly re-auditing unchanged passing
paths is not a substitute for these visual changes. The saved
review records are the starting point, not a fresh implementation from scratch.


### Latest paused handoff (2026-11-03)

The user resumed and then explicitly paused this run. All three subagents were
interrupted. No production mass font build or final browser verification ran.
Do not treat intermediate edits as integrated completion.

- Track A changed `js/fonts.js` and added `tests/greek-fonts.test.mjs`:
  prefer complete proportional WenKai Greek fields, with complete native fallback
  for polytonic text. Agent reports 30 focused tests pass; its broader npm run
  was started with `/tmp/unicode-greek-js.log` (terminal outcome not yet checked).
  Local before/after `output/font-review/greek-routing/comparison.png` was
  inspected by both agent and coordinator. Final actual-strip/export check remains.
- Coordinator added `tools/font/source_optics.py`, optical-em size candidates for
  Aref Ruqaa/Gaegu (1.16) and Tolong (1.10), and wired recipes/output provenance
  into `tools/font/build_scripts.py`. **Production assets have not been rebuilt.**
  Four tests in `tests/test_source_optics.py` passed in 3.04s. Local candidates
  in `output/font-review/source-optics/` were visually inspected. These change
  the em only, preserving design-space curves, joins, anchors and advance ratios.
- `tools/font/specimens/nonpen-review.json` and
  `output/font-review/nonpen-review.{png,svg,json}` review nine remaining source
  categories. Coordinator inspected the PNG; attached Syriac/Khojki marks are
  coherent in these samples and structural geometry should stay exact.
  `docs/nonpen-source-review.json` records remaining optics/weight findings.
- Track B was prototyping isolated, topology-checked distance-field pressure
  candidates with native shaping tables retained. Check its files/artifacts and
  obtain terminal results before adopting anything; no broad treatment accepted.
- Track C proposed 0.014-em Egyptian optical stroke with matching bounds,
  including ungrouped mixed-dialogue signs, preserving insertion coordinates.
  It owns `js/egyptian-layout.js`, focused tests, and a small `js/comic.js`
  path-stroke branch; inspect any partial edits before continuing. No acceptance
  or terminal verification was received before interruption.
- Independent audit was requested from track A after its npm run, but no final
  audit was received. Existing main evidence matrix remains the prior baseline.
- Browser capability inventory only was inspected. No tab/server was opened.
- Asset URL version refresh, dependent outline catalogs, affected source tests,
  final browser checks and independent completion audit remain required after
  accepting and integrating candidates. Preserve the large pre-existing dirty
  checkout; do not reset or commit it without instruction.
