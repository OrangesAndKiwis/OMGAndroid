# Scam-PAC Investigation — Synthesis & Case Assessment

*2026-07-01. Factual/analytical synthesis to support counsel — **not legal advice**.
"Scam PAC" is used descriptively; nothing here is an adjudication.*

---

## Q1 — Has anyone done this analysis before? Yes — extensively.

Our core method is **well-trodden**, and we should be honest about that:

- **Published overhead-ratio screens.** OpenSecrets runs a standing screen —
  committees that spent **>$100k AND ≥50% of itemized spending on "fundraising"**
  (86 PACs flagged for 2022; it explicitly names Law Enforcement for a Safer
  America and American Alliance for Disabled Children). Issue One / Center for
  Fiscal Policy publish the aggregates ($344M cumulative). Rob Pyers (CA Target
  Book) and ThinkingOregon run recurring per-PAC teardowns.
- **Shared-vendor / treasurer clustering.** The Daily Beast used exactly this to
  expose the **$140M Zeitlin network** (43 PACs, one call center). Campaign Legal
  Center and Documented trace officer-controlled vendors and file FEC/DOJ referrals.
- **Academic — the real prior art.** **Zhao Li (Princeton), "Lemons in the
  Political Marketplace,"** already built a **supervised ML classifier** on FEC
  data using **donor-age, small-dollar/itemization, and donor/treasurer/vendor
  network features** (incl. "PAC address = vendor's home address"). Adam Bonica
  (Stanford/DIME) documents elderly-donor exploitation. This combines nearly every
  signal we used.
- **Government.** The FEC's 2021 Scam PACs Working Group proposed the exact
  disclosure metrics we compute (direct-candidate-support %, per-vendor
  concentration) but didn't adopt them; Congress's **SCAM PAC Act** defines the
  behavioral test; Rep. Porter's "Political Parasites" report and DOJ/FBI/state-AG
  actions round it out.
- **Tools.** PACSpam.org (message/UTM provenance — a genuinely different angle),
  AARP red-flags, ProPublica's FEC Itemizer.

**What we actually added (incremental, not novel):** (1) a **known-bad-vendor
watchlist** tying PACs to *criminally convicted* operators as a scored signal;
(2) an integrated composite score; (3) explicit **charity-impersonation targeting
oriented to a legal theory**. **Genuinely underexplored** (if anyone wanted to go
further): message-level provenance at scale, a live dashboard/API, cross-linking
FEC → 501(c)(4)/IRS and telemarketing-vendor layers, and temporal "burn-and-churn"
modeling. Bottom line: this is a solid *synthesis for a legal purpose*, not new science.

---

## Q2 — If I were the scammer, what would I do to hide? (and what we should add)

Adversarial view — evasion tactics, several **already visible in our data**:

1. **Relabel fundraising as "independent expenditures."** *Proven here:* the
   breast-cancer and police PACs book their own telemarketer's costs as IEs
   ("phonebank," "caging," "database services") **supporting candidates — and
   split them trivially across BOTH parties** (Ernst *and* Klobuchar; Issa *and*
   Tester). That inflates "% to candidates" and **games the mission-ratio our
   screen (and OpenSecrets') relies on.** → *Detect:* flag IE payees that are the
   fundraising vendor; IE purposes reading phonebank/caging/database; both-party
   micro-splits.
2. **Vendor shell-shuffle.** Zeitlin spun up **LAV / Wired4Data / Standard Data**
   to fragment "Cloud Data," so no single vendor dominates and name-clustering
   splinters. → *Detect:* entity-resolve on **vendor address/email**, not names;
   maintain operator-network maps.
3. **Hide behind a high-volume compliance treasurer.** Watkins (246 committees),
   Crate/Red Curve (200+) make the *operator invisible* — the treasurer signal is
   defeated (we proved this). → *Detect:* operator ≠ treasurer; trace via vendor +
   PO-box address + email domain.
4. **Alias/DBA under several charity names.** "Disabled Children" also solicits as
   "American Coalition for Autistic Children" and "Children's Cancer Coalition." →
   *Detect:* cross-reference aliases by shared address/email/vendor.
5. **Move the real money to a 501(c)(4).** The biggest blind spot — dark-money
   nonprofits don't itemize donors/vendors to the FEC at all. → *Detect:* link
   committees to IRS 990 nonprofits sharing address/treasurer.
6. **Rotate/terminate & re-form committee IDs each cycle** to dodge persistence
   analysis. → *Detect:* multi-cycle operator tracking by vendor/address/email.
7. **Recurring-donation dark patterns** (pre-checked boxes, money multipliers).
   *We tested refund/chargeback rate:* modest, but higher for the digital
   Democratic small-dollar PACs (~2%) than the elderly-telemarketing PACs (~0%) —
   so **refund rate flags the dark-pattern subtype specifically.**
8. **Token candidate gift** to clear a threshold or the SCAM PAC Act safe harbor.
9. **Robocalls/spoofed area codes & sub-$200 unitemized fragmentation** — largely
   invisible to FEC; needs FCC complaint data and message-provenance tools.

**Highest-value additions:** IE-payee scrutiny (closes the #1 gaming hole),
vendor-address entity resolution, multi-cycle operator persistence, alias/501(c)(4)
cross-linking, and message provenance.

### The vendor-BACK view (the biggest missing angle — now built)

The whole pipeline was **PAC-back** (PAC → its vendors). Inverting it — **vendor →
every client PAC** (`vendor_back.py`) — is how the Daily Beast mapped the Zeitlin
network, and it is the frame the legal case needs (vendor = enterprise/defendant).
Mapping each convicted/banned operator across 2022–2026 and grading by
**scam-concentration** (share of client money going to scam-profile PACs):

| Operator | Client PACs | Total paid | % $ to scam PACs | Read |
|---|--:|--:|--:|---|
| **Gelvan** (banned) | 33 | $11.8M | **76%** | real enterprise |
| **Zeitlin** (convicted) | 27 | **$36.8M** | ~63%* | real enterprise |
| Daly (convicted) | 239 | $22.5M | **5%** | noise (mainstream clients) |
| Olympic Media | 145 | $9.4M | **2%** | noise |
| RetroMedia | 1 | $0.4M | bespoke | single-PAC shell |

*\*Zeitlin's 27-PAC roster is entirely police/veteran-themed (Honoring American
Law Enforcement $5.9M, Police Coalition $4.3M, Police & Trooper Support $3.6M…);
the 63% is a floor from the exact small-dollar filter, substance is ~100%.*

**Two payoffs:** (1) it **corrects the watchlist** — a convicted operator is only
a strong signal if its *clientele is concentrated in scam PACs* (Zeitlin/Gelvan),
not if it went mainstream post-conviction (Daly's 239 clients are 95% NRSC/RNC/
Trump/NRCC; Olympic serves real campaigns). Weight the watchlist by
scam-concentration. (2) It hands the case its **cleanest defendants**: the Zeitlin
call-center enterprise ($36.8M, 27 police/veteran PACs, convicted → collateral
estoppel) and the Gelvan enterprise ($11.8M, 76% charity-name scams). See
`vendor_networks.csv` / `vendor_network_clients.csv`.

---

## Q3 — What we learned: the case, structured

### Context & problem statement
Scam PACs adopt **charitable or emotive names** (breast cancer, disabled children,
veterans, police) and use **deceptive small-dollar solicitation** — robocalls,
texts, emails — to harvest money **disproportionately from elderly and fixed-income
Americans**, then keep **~85–95% as fundraising/overhead** (often paid to the
operator's own firms) and pass **almost nothing to candidates or the named cause.**
Our 2024 FEC screen: **1,548 flagged PACs**; **206 harvested ~$354M from small
donors** while giving <20% to candidates (net of union/advocacy false positives,
**174 PACs / ~$289M**); a **tight tier of ~11 (~$27M)** carries charity names *and*
convicted-operator vendors. The harm is large, growing (7 → 86 PACs since 2001),
bipartisan, elder-targeted, and **barely recovered** (Zeitlin restitution $8.9M vs.
$133M kept). This is a real consumer-fraud problem, not a phantom.

### Categories with the most legal potential (ranked)

**A. Charity/cause-impersonation PACs** — *strongest.* The **name itself is the
affirmative misrepresentation**, which sidesteps the "high overhead is legal" wall.

**B. Convicted-operator vendor networks** — sue the **vendor** (deep pocket, no
speech shield, common enterprise); fraud already **adjudicated** (collateral estoppel).

**C. Recurring-donation dark-pattern operations** — the *WinRed v. Ellison* path;
uniform deceptive UX = the **best class-certification** posture.

**D. Generic high-overhead small-dollar PACs** — *weak; don't pursue alone.*
Protected inefficiency (Schaumburg/Riley). **This is where the Animal PAC sits.**

### Deep dive — if I were the lawyer

**A. Charity-impersonation**
- **Who I'd sue:** the committee + operator + telemarketing vendor. Best anchors:
  **American Police & Troopers Coalition** (Jacobin-named; four Zeitlin vendors;
  treasurer self-pay), **United Breast Cancer Support** (four Zeitlin vendors;
  name collides with the real UBCF charity), **American Alliance for Disabled
  Children** ($3.4M; Gelvan cluster; press-named; aliases as autism/cancer).
- **Basis:** common-law fraud + **state UDAP** + charitable-solicitation fraud +
  unjust enrichment (+ possible Lanham/passing-off on the UBCF name), anchored in
  ***Madigan v. Telemarketing Associates*** (affirmative misrepresentation is
  unprotected).
- **What I'd need to believe/prove:** donors were **told** (via the name + scripts)
  their money supports the cause/patients; **it didn't** (~0 to cause); the
  deception was **material and classwide-relied-upon**; the operator **knew**.
- **Biggest defenses:** First Amendment (*Schaumburg/Riley* — no suing on the
  ratio); the "not a charity/not tax-deductible" **disclaimers**; **FECA-preemption
  re-characterization** ("really an attack on expenditure allocation"); **the
  treasurers weren't criminally charged** (2017–2020 window vs. 2022–2024 filings)
  → knowledge is inferred; **individualized reliance** at certification.

**B. Convicted-operator vendors**
- **Who:** Zeitlin's entities, Gelvan/Market Process Group, Daly/Better Mousetrap —
  civil follow-on to the convictions.
- **Basis:** fraud, unjust enrichment, **RICO** (enterprise), UDAP; leverage
  **collateral estoppel** from the criminal record.
- **Prove:** the enterprise's deception (largely established for Zeitlin); **each
  class member's calls trace to the enterprise** (the hard part); damages.
- **Defenses:** **collectibility** (Zeitlin imprisoned/forfeited; Gelvan's $56M
  judgment suspended as uncollectable — *the deepest pockets may be empty*); the
  **dismissed** M.D. Pa. Zeitlin TCPA class action; tracing/standing; arbitration.

**C. Dark-pattern recurring-donation**
- **Who:** the PAC + the platform/texting vendor; the digital small-dollar cluster
  (higher refund rates) is the pool.
- **Basis:** state UDAP (deceptive pre-checked/recurring/multiplier UX), unjust
  enrichment; ***WinRed v. Ellison* (8th Cir. 2023)** shows this survives preemption.
- **Prove:** the UX **deceptively enrolled** donors in recurring/inflated charges;
  harm is **uniform** (→ presumed classwide reliance).
- **Defenses:** **consent** ("they clicked"), **arbitration/class-waiver** in the
  donation terms, First Amendment, preemption re-characterization.

### Final assessment — magnitude and benefit to the American people

**Is the problem real and of magnitude? Yes, unambiguously.** Hundreds of millions
cumulatively; multiple $100M+ networks; **systematic targeting of elderly and
fixed-income Americans**; ~20x growth in two decades; recognized by DOJ, FBI, state
AGs, and Congress; and **recovery has captured only pennies on the dollar** — a
large, under-addressed harm to vulnerable people.

**Is a private class action the right instrument? Hard, and eyes-open honest:**
- Every accountability **win so far is a government actor** (DOJ criminal; state
  AG/FTC civil) under a **scienter or clear-and-convincing** standard.
- The **only on-point private class action (Zeitlin TCPA) was dismissed.**
- **Class certification** is threatened by individualized reliance; **First
  Amendment + FECA-preemption** re-characterization are live; and the **strongest
  defendants are judgment-proof.**
- The underlying **analysis is not a differentiator** (Zhao Li/OpenSecrets already
  do it) — the *value is the legal framing and target selection*, not the screen.

**Where the genuine public benefit lies — my recommendation:**
1. **Anchor on charity-impersonation** (breast-cancer / disabled-children / police
   "support" PACs). It best clears the First Amendment (name = misrepresentation),
   protects the most sympathetic victims, and maps onto conduct DOJ already proved.
2. **Aim at the for-profit vendors + operators**, not just the PAC shells.
3. **Force-multiply with the proven winners:** package the ranked targets +
   evidence as **referrals to state AGs** (*WinRed v. Ellison* shows they win on
   preemption) and the **FTC** (jurisdiction over the vendors), and coordinate with
   **CLC/Documented** (who already file FEC/DOJ referrals). A private UDAP/dark-
   pattern class can ride alongside.
4. **Set expectations on recovery** (collectibility is the real ceiling) — but the
   **deterrence, exposure, and regulatory-referral value is high and real.**

**Bottom line for your friend (class-action + constitutional-law specialist — the
right profile):** This is a genuine, large-scale fraud on vulnerable Americans with
a **viable-but-difficult** litigation path. The case lives or dies on the First
Amendment line from *Madigan / Schaumburg / Riley*, which is precisely their
expertise. The single most winnable, highest-benefit case is a **charity-
impersonation anchor** (e.g., the Zeitlin-vendor breast-cancer/police PACs or the
Gelvan-linked disabled-children PAC) against the **vendor + operators**, filed in a
**donor-friendly UDAP jurisdiction**, ideally **in tandem with a state AG** — with
realistic expectations about certification and collectibility.

*Targets, financials, corroboration, and sources: `case_candidates.csv`,
`scored_leads.csv`, `research_findings.md`, `CASE_MEMO.md`.*
