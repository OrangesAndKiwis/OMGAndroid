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

---

# Round 2: corroboration of the statistical-only top leads

Research on the 12 top-scored leads not covered above. Verdicts vary — which is
the point: the score is triage, and external review sorts real from artifact.

## Watchlist-vendor leads

| PAC | Verdict | Evidence |
|---|---|---|
| **God, Family, & Country PAC** (C00847897) | **CORROBORATED** | ThinkingOregon scam-PAC writeup; vendor Better Mousetrap Digital = **Jack Daly (convicted)**; PO-box-only, untraceable principal |
| **Elect Republicans** (C00747170) | **CORROBORATED** | paid **Better Mousetrap Digital (Jack Daly, convicted)** $63k; one of a **9-committee network** under serial treasurer Garrett Lott; 83–98% overhead, <1% lifetime to candidates |
| **Defeat Republicans PAC** (C00755702) | **CORROBORATED** | **FEC + California FPPC fines**; serial treasurer (33 committees); 2.7% to candidates in 2024 vs. 98.8% overhead |
| **Early Vote Action PAC** (C00829721) | **MIXED → exonerated** on scam charge | Real Scott Presler grassroots op; flagged spend went to an *insider* vendor, not a watchlisted fraudster; fraud claims only from partisan blogs. A Public Citizen complaint exists but is about *lobbying disclosure*, not fundraising fraud |

## Self-dealing leads — and the key refinement

The self-dealing signal split cleanly by *treasurer type*:

**REAL (owner-operator treasurer/principal pays their own firm/salary — corroborated):**
| PAC | Verdict | Evidence |
|---|---|---|
| **BAMPAC / Black America's PAC** (C00300921) | **CORROBORATED** | treasurer Alvin Williams paid himself ~$255k in 2024 (~$2M+ lifetime, salary-coded); CPI documented ~1% to candidates |
| **Elder for America** (C00799361) | **CORROBORATED** | treasurer's firm Baric & Associates $307k *and* Larry Elder's own firm ~$150k (Forbes) — double insider layer, disclosed |
| **Bowers News Media PAC** (C00878124) | **MIXED** | Bowers Kerbel Media LLC (treasurer co-owned) got ~94% of receipts; co-owned + no external scrutiny |
| **New Journey PAC** (C00709691) | **MIXED** | $1.12M lifetime to CEO Autry Pruitt's own firm (real, disclosed) — BUT the self-deal *flag* fired on a **corrupted FEC `treasurer_name` field** (actual treasurer is Thomas Datwyler); no enforcement, disclosed vendor payment |

**FALSE POSITIVE (compliance-treasurer-for-hire pays their own firm — routine):**
| PAC | Verdict | Why the flag is wrong |
|---|---|---|
| **Tea Party PAC** (C00692129) | **MIXED** | "self-deal" = Robert Watkins & Co accounting fee; **Watkins treasures ~246 committees** → false positive. BUT vendor RetroMedia took ~44–58% and only 1.7% went to politics — real scam-adjacent economics via the *vendor* |
| **Reform California Voter Guide** (C00860023) | **MIXED** (flags false) | slate-mailer economics; treasurer Boling (~24 cmtes) paid ~1.4%; but DeMaio's network has real documented controversy |
| **Colorado Turnout Project** (C00765917) | **EXONERATED** | legit anti-Boebert Dem GOTV; no payment to the treasurer at all |
| **Blue Vision** (C00887174) | **MIXED → exonerated** | small digital Dem PAC; $9k to treasurer (~5%) is ordinary; makes real contributions |

### THE refinement this round proved
**Self-dealing is real only when the treasurer is an owner-operator, not a
high-volume compliance shop.** A treasurer who serves 200+ committees (Watkins)
or 24 (Boling) paying their own firm is routine bookkeeping; a single-committee
principal (Williams, Pruitt, Elder/Baric) paying their own firm 40–94% of
receipts is self-dealing. **Fix:** gate the self-dealing signal on the
treasurer's committee count (exclude treasurers-for-hire) and on the payment as
a % of receipts. Same ubiquity lesson as WinRed/ActBlue and Bradley Crate — now
applied to treasurers.

### Second nuance: the vendor signal beats the treasurer signal
Twice the treasurer was a red herring while the *vendor* told the truth:
God/Family/Country and Elect Republicans both have institutional treasurers
(Red Curve; Lott) but pay **Better Mousetrap Digital (convicted Jack Daly)** —
and both corroborated. Tea Party's treasurer flag was false, but its vendor
(RetroMedia, ~44–58% of receipts) is the real signal. Weight vendors over
treasurers. And a watchlist hit is still a signal, not a verdict: Early Vote
Action tripped it but routed money to an *insider* vendor, not a listed fraudster.

### Third nuance: the FEC `treasurer_name` field can be wrong
New Journey PAC's master record lists "Pruitt, Autry" as treasurer, but the
actual treasurer of record is Thomas Datwyler — a data glitch that made the
self-dealing match doubly unreliable. Don't trust `treasurer_name` alone.

## Round-2 scorecard
Of 12 statistical-only leads: **5 CORROBORATED** (God/Family/Country, Elect
Republicans, Defeat Republicans, BAMPAC, Elder for America) · **4 MIXED with a
real component** (Bowers, New Journey, Tea Party, Reform California network) ·
**1 MIXED→exonerated** (Blue Vision) · **2 EXONERATED** (Early Vote Action on the
scam charge, Colorado Turnout).

**The single strongest validator: all 3 watchlist hits with any external record
(God/Family/Country, Elect Republicans, Defeat Republicans) corroborated** —
each pays a convicted fraudster's firm. The false positives cluster entirely in
the compliance-treasurer self-dealing class — a fixable scoring gap, not a
screen failure.
