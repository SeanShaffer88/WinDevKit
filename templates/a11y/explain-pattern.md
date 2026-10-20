# The `explain` Pattern — tooltips & accessible names

Distilled from InstallScope's P0-1 work (tooltip coverage was ~33% and
hover-only — the worst a11y gap in the quality audit) and the production
polish standard:

- Every interactive control gets a short explanation: what it does, when
  to use it, and its important effects — especially destructive ones.
- One helper, one voice: route every explanation through a single
  `a11y::explain(control, text)` (or framework equivalent) so wording,
  delay, and accessible-name wiring stay consistent and auditable.
- The explanation must reach ALL input modes: mouse hover, keyboard
  focus, assistive technology (it doubles as / feeds the accessible
  name), and touch (long-press or an adjacent info affordance).
- A tooltip is NEVER the only carrier of essential information — labels,
  inline help, and error text carry the essentials; tooltips enrich.
- Coverage is measurable: count interactive controls vs. explained
  controls per page and record the number (InstallScope tracked this per
  phase). Ship-blocker threshold for new pages: 100% of interactive
  controls, or a named exception list.
- Destructive/irreversible controls explain risks, limitations, and the
  recovery path (undo/backup/preview) before the action, not after.
