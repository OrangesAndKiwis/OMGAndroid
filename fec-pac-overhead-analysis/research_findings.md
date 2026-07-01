# External Research: Corroboration of Flagged PACs

Cross-checking the top quantitative leads against journalism, FEC enforcement,
and watchdog reporting. Verdicts: **CORROBORATED** (external evidence supports
the concern), **MIXED**, **EXONERATED** (evidence it's legitimate / flag is an
artifact). This is *lead corroboration*, not legal adjudication.

## The headline: the pipeline independently rediscovered documented scam PACs

Four of our top leads are already documented as scam / donor-deceiving operations
by independent journalists — one with a **criminal fraud conviction** of its
principal. We surfaced them purely from FEC financial ratios, blind to the reporting.

| PAC | Our flag | External corroboration | Verdict |
|---|---|---|---|
| **Law Enforcement for a Safer America** (C00681825) | 75% cost-to-raise, $8.4M | CNN "scam" investigation; Jacobin; principal telemarketer **Richard Zeitlin convicted of wire fraud (121 months)** | **CORROBORATED (proven fraud connection)** |
| **American Coalition for Crisis Relief** (C00709113) | 83% cost-to-raise | Multiple outlets call it a "scam PAC"; 90–98% overhead; insider vendor "Crisis Relief Consultants"; ties to sanctioned fundraiser Mark Gelvan | **CORROBORATED** |
| **SEAL PAC** (C00570226) | 68% cost-to-raise + treasurer link | Roll Call "Ethical questions cloud Zinke's SEAL PAC"; active FEC inquiry; treasurer routes fees to his own firm across many PACs | **CORROBORATED** |
| **Defending the Republic** (C00771139, Sidney Powell) | $20k self-dealing | Dominion filing alleges fund redirection to her law firm; Florida $10k fine for deceptive solicitation; federal grand-jury subpoena | **CORROBORATED (org level)** |

## The vendor cluster caught a real high-overhead fundraiser

Cluster 1 (Conservative Action Fund, **Red Renaissance**, Nine PAC) linked via
shared vendor **Olympic Media** — a firm mainstream reporting (Washington Post,
Axios, Baltimore Sun) documents taking **70–80% commissions** ("a racket," per a
former client). Red Renaissance is Kim Klacik's PAC (≈100% operating spend every
cycle, ~$500 lifetime to candidates), a *documented* Olympic Media client. So
distinctive-vendor clustering surfaced a genuine high-overhead fundraising
relationship. (TMA Direct, another cluster vendor, is a legitimate conservative
mail firm with no scam reporting.)

Stronger still: a *second* Cluster 1 vendor, **Reach Right Digital Marketing**,
is the firm of **Jack Daly — criminally convicted in 2023 of scam-PAC fraud**
(the "Draft PAC"/Draft David Clarke scheme: $1.6M raised, targeting elderly and
Alzheimer's-afflicted victims; 4 months prison + restitution). So the cluster is
linked by *two* documented high-overhead fundraising vendors, one owned by a
convicted fraudster. That is exactly the "coordinated fundraising ecosystem"
signal the vendor layer was designed to surface.

Caveats on the cluster: no source labels any of the three PACs themselves a
"scam PAC" outright; Red Renaissance's one formal fraud-type complaint (FEC
**MUR 7944**) was **dismissed** ("no reason to believe"); and Reach Right's
*largest* clients are mainstream committees (NRCC, Rand Paul, McCarthy) — using
the vendor doesn't by itself make a PAC a scam. Also, the three don't share one
treasurer: Red Renaissance and Nine PAC are Crate/Red Curve, but **Conservative
Action Fund is Charles Gantt / Bulldog Compliance** — a *second* high-volume GOP
compliance shop (reportedly behind 500+ dark-money groups). The cluster is real
because of the shared *fundraising vendors*, not a shared treasurer.

## False positives the research confirmed (and why)

| PAC | Our flag | Why it's a false positive |
|---|---|---|
| **Zinc Collective** (C00767749) | 286% cost-to-raise | Legitimate Democratic talent org (merged into Arena). >100% ratio is a **termination artifact** — a winding-down committee spending reserves. Exactly the >100% caveat we noted. |
| **Napoleon PAC** (C00627836) | 86% cost-to-raise | Real Louisiana Democratic **direct-mail PAC** (Trey Ourso). High overhead is inherent to a mail operation. |
| **Wolf PAC** (C00485102) | $79k self-dealing | Cenk Uygur's **Article V constitutional-convention** movement — mission is state-legislature organizing, not candidates, so ~0% candidate spend is by design. No source alleges self-dealing. |
| **Black Men Vote** (C00528950) | 100% overhead | Super PAC (0%-to-candidates is structural). External scrutiny is about *straw donors* (Pras Michel), and the FEC **deadlocked and dismissed** it — not an overhead scam. |

## Methodological lessons for the next iteration

1. **Treasurer-clustering has a ubiquity problem — same as WinRed/ActBlue.**
   The cluster PACs run through *two* mega-compliance treasurers — Bradley Crate
   (Romney CFO → Trump committees, treasurer of record for **200+ committees**)
   and Charles Gantt / Bulldog Compliance (500+ groups). Both are innocent shared
   service providers. High-volume treasurers must be stoplisted from
   treasurer-based clustering, exactly as we stoplisted payment processors — the
   real signal is the shared *fundraising vendor* (Olympic Media), not the treasurer.

2. **The self-dealing flag conflates roles.** For ALIPAC our name-match fired,
   but the public record shows the insider being paid is the **president**
   (William Gheen), not the treasurer — and one formal FEC diversion complaint
   was *retracted and closed*. The treasurer-name match should distinguish
   treasurer-vendors from officers and shared-address vendors to cut false hits.

3. **Two structural false-positive classes remain** beyond JFCs/party/union:
   **issue-advocacy PACs** (Wolf PAC — legitimately ~0% to candidates) and
   **IE-only Super PACs** measured in a period with $0 IEs (Black Men Vote).
   Consider a "does any express-advocacy or IE activity exist at all?" gate.

4. **>100% cost-to-raise = termination artifact**, not a super-scam. Flag
   separately or require the committee to be active (non-terminated) that cycle.

5. **Build a known-bad-fundraiser watchlist** — the highest-value enhancement
   this research suggests. Several vendors recur across documented scam
   operations: **Cloud Data Services / Richard Zeitlin** (convicted), **Reach
   Right Digital Marketing / Better Mousetrap Digital** (Jack Daly, convicted),
   **Olympic Media** ("racket" commissions), **Crisis Relief Consultants**, and
   **Mark Gelvan / Outreach Calling** (court-barred). Flagging any PAC that pays
   a watchlisted vendor would catch scams the ratios miss, and corroborate the
   ones they don't. (Guard against over-reach: some of these vendors also serve
   mainstream clients — the vendor is a signal, not a verdict.)

## Data caveats
- Fetches to OpenSecrets / major outlets frequently returned HTTP 403; several
  findings rest on search-indexed snippets of those sources plus primary FEC data.
- LEFSA treasurer of record: our FEC pull shows "Mark Nelson"; some journalism
  cites "Jeremy Kevitt." Verify against the current FEC Form 1 before publishing.
- No completed FEC enforcement (MUR) confirmed against American Coalition for
  Crisis Relief or SEAL PAC — the concern is journalistic/factual, not adjudicated.
  Only LEFSA's telemarketer (Zeitlin) has an actual criminal conviction.

## Bottom line
The screen works: run blind on FEC ratios, it rediscovered four independently
documented scam/misuse operations (including a criminally-convicted one) and its
false positives all fall into explainable structural classes. It is a strong
*lead generator* for review — not a fraud adjudicator.
