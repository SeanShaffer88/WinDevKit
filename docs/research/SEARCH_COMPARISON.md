# Search comparison — October 21, 2026

Target receiving library: [FastSearch](https://github.com/SeanShaffer88/FastSearch).
Research targets below are adjacent search/launcher products, not proof that
FastSearch should become a launcher or use an Electron runtime.

## Source identities and REA result

| Target | Official source snapshot | Inspection |
|---|---|---|
| Ueli | [2f8d665](https://github.com/oliverschwendener/ueli/tree/2f8d665a53588da8b1021465567490b7b0359885) | Selected `src/common/Core/Search/fuzzySortFilter.ts` and `fuseJsSearchFilter.ts` for REA; directly reviewed those sources and Simple File Search documentation. |
| Cerebro | [6283050](https://github.com/cerebroapp/cerebro/tree/62830502cd287d69c08c6da7a07d875710425615) | Selected `app/main/actions/search.js` for REA; directly reviewed that source. |

REA 6.7.0 returned `capability_unavailable` because `ps` fails with
`fatal library error, lookup self` in Node's child environment here. Shell `ps`
works, but an independent Node `execFile('ps', ...)` reproduces the same failure.
No provider check was bypassed. REA returned digest-bearing **partial inventory**
evidence, not a completed semantic or runtime analysis. The compact
[Ueli summary](rea-ueli-summary.json) and [Cerebro summary](rea-cerebro-summary.json)
retain evidence IDs, subject digests, selection and limitations. Full temporary
reports were 16.2 MB and 1.4 MB and are not committed as application source.

The feature facts below come from **direct official source/documentation review**,
not from an unavailable REA relationship graph. No paid-tier, current-price,
full-product coverage or runtime verification claim is made.

## Individual feature decisions

| Verified behavior and source | User benefit | Decision for FastSearch/shared tools |
|---|---|---|
| Ueli [Simple File Search](https://github.com/oliverschwendener/ueli/blob/2f8d665a53588da8b1021465567490b7b0359885/docs/Extensions/SimpleFileSearch/README.md) lets users select files, folders or both. | Avoid irrelevant results for the current task. | Matches the new explicit type filter. Filter before the result cap; preserve existing unfiltered semantics. Implemented in the FastSearch PR. |
| The same documentation supports specific folder locations. | Restrict results to a useful scope. | Full-path substring filter is implemented; multiple independently configurable roots remain future work and must deduplicate overlapping roots. |
| The same documentation makes recursion configurable and warns about large recursive scans. | Control startup cost and responsiveness. | Existing FastSearch builds are recursive snapshots. Recommend a future explicit walk policy/progress/cancel API; do not overload the contractual name-query syntax. Not implemented in this batch. |
| Ueli [fuzzysort filter](https://github.com/oliverschwendener/ueli/blob/2f8d665a53588da8b1021465567490b7b0359885/src/common/Core/Search/fuzzySortFilter.ts) uses a configurable threshold and caps results. | Find approximate names while controlling result volume. | Recommend opt-in ranked fuzzy search with documented scores and quality fixtures. Keep deterministic exact/glob mode as the default. A JS fuzzy package is not a reason to change this Rust library's runtime. Not implemented here. |
| Ueli [Fuse filter](https://github.com/oliverschwendener/ueli/blob/2f8d665a53588da8b1021465567490b7b0359885/src/common/Core/Search/fuseJsSearchFilter.ts) uses an alternative engine with its own threshold semantics. | Tune search quality to different workflows. | Engine interchangeability is valuable at the host boundary. Before adopting a Rust fuzzy crate, benchmark recall/ranking and latency against an original std-only prototype; an engine name alone proves neither. Deferred pending an actual consumer. |
| Cerebro [search actions](https://github.com/cerebroapp/cerebro/blob/62830502cd287d69c08c6da7a07d875710425615/app/main/actions/search.js) dispatch queries to plugins and catch plugin exceptions. | One provider failure need not stop other results. | Preserve an explicit error boundary in shared FFI templates and avoid holding global registry locks during provider work. These infrastructure fixes are implemented; no plugin runtime is added to FastSearch. |
| The same actions attach the originating search term to incoming results. | A UI can distinguish results from different queries. | Recommend host-side query generation IDs/cancellation for asynchronous search. Snapshot pinning is implemented; stale-result UI suppression is outside a synchronous DLL's responsibility. |
| The same actions offer open, reveal, clipboard and result-update/hide actions. | Act on results without manually navigating. | Put these in the consuming UI's command layer, with keyboard/accessibility tests. A search DLL should return data and not launch programs as a side effect. Not added to FastSearch. |
| Cerebro source contains a TODO about ordering by frequency. | Potential personalized ranking. | This is explicitly **not verified as an offered feature** in this source. Consider only as a future opt-in host feature with local history/reset controls. |

## Implementation connection

[FastSearch PR](https://github.com/SeanShaffer88/FastSearch/pull/1) adds type/path/
extension filters, snapshot concurrency and measured prefix seeking. These
changes were already being implemented when the comparison was requested;
the review corroborates some design choices rather than claiming to have
originally discovered all of them through REA.

WinDevKit now records partial-analysis failures honestly and provides a repeatable
review workflow. Complete REA semantic analysis on a supported process environment
before claiming deeper implementation evidence from either inspected product.
