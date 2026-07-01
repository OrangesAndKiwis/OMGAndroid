# The Un-Haircut: How Big Is the Shared-Vendor Finding, Really?

*Resolving the methodology question — "is the shared-vendor thing small only
because you're checking for scam vendors?" Written 2026-07-01. Not legal advice;
"scam-profile" is descriptive of a financial pattern, not a legal conclusion.*

## The question

Earlier passes gave three very different numbers for "how many of the ~205
scam-profile PACs are tied together by a shared vendor," and the spread was a
methodology artifact, not a fact about the world:

| Number | How it was computed | Why it was wrong |
|--------|--------------------|------------------|
| **13%** | shared a vendor **I had hand-labeled** "scam-concentrated" (~25 vendors) | a *haircut* — it can only find rings through vendors I already knew about |
| **90%** | shared **any** vendor with another scam PAC | counted ubiquitous mail houses (DonorBureau) **and** non-vendors (candidate committees, IRS, airlines) — links everyone, means nothing |
| **~28–29%** | shared a **distinctive** (rare) **commercial vendor** | the honest middle — see below |

The 13% was small *because of the hand-labeling*, exactly as suspected. The 90%
was big because it counted noise. Neither is the real answer.

## The un-haircut method (no hand-labeling)

A vendor is a coordination link if it is **rare and shared** — not because it
appears on any watchlist. So for every vendor paid by **≥3** scam-profile PACs,
we pulled its **total client count across the entire FEC universe** and split:

- **distinctive** = ≤12 total clients → a real, narrow coordination link
- **generic** = many clients → an industry mail house everyone uses (noise)

228 vendors were shared by ≥3 scam PACs. 76 were distinctive.

Then — transparently, with every recipient shown — we removed the distinctive
"recipients" that **aren't commercial vendors at all** but are rare for
structural reasons:

- **PROCESSOR/BANK** (ActBlue/WinRed Technical Services, Amalgamated Bank) — conduits
- **COMMITTEE** (Nick Brown for Attorney General, Trump 47, Progressive Turnout
  Project, CULAC) — PAC-to-PAC transfers and earmarks, not vendors
- **PERSON** (individual treasurers paid directly) — one human, few committees

## The honest answer

| Measure | Result |
|---------|--------|
| Distinctive recipient of any kind (raw) | **110 / 205 = 54%** |
| **Distinctive genuine commercial vendor (clean)** | **60 / 205 = 29%** |

**~29% of scam-profile PACs are wired to at least one other scam-profile PAC
through a rare, shared commercial fundraising/telefund/mail/data vendor** — with
zero hand-labeling. This is a conservative floor (a few real firms were bucketed
as "person" to avoid overcounting). The true figure sits between 29% and 54%.

## What the 45 distinctive vendors actually are

They are **not** a random assortment — they are the recognizable fraud-adjacent
fundraising infrastructure the screen was built to find:

- **Zeitlin (convicted) data shops:** Cloud Data Services (11 PACs), Wired4Data
  (9), LAV Services (9), Standard Data Services (9), Paction Data (7), ECG Data
  Center (6), Sterling Data (3)
- **Telemarketing / phone rooms:** Pro Speaking (4), DS3 Marketing (3), Office
  Edge (4), Contact Logistics (3), Avery Services (3), Political Response (3)
- **Mail + caging houses:** Excel Mailing (6), Image Direct Group (6), Capitol
  Caging (3), North American Fulfillment (5), Fulfillment House (3), CP Direct
  (4), DirectMail.com (3), Moore RMG / Moore Response Management Group (5+3)
- **Media/digital & consulting fronts:** North Star Multimedia (5), Keystone
  Media Resources (4), Advance Creative Media (3), Next Level Digital (4),
  EngageUSA (3), Sapphire/Windward/Praxis/Dragonfly Strategies, RWT Production

Full bucketed list (every recipient, in/out flag): `distinctive_clusters.csv`.

## Bottom line

The shared-vendor finding was small **only because of the hand-labeling haircut.**
Removed, it is not a fringe of pre-known scammers — roughly **a third** of the
scam-profile universe (and up to half on the raw measure) is tied together by a
handful of rare fundraising vendors, and those vendors are exactly the telefund /
caging / data shops (led by the convicted Zeitlin network) that define the
pattern. The clusters are real, they are dominated by known-bad infrastructure,
and the method finds them without being told what to look for.

### Method files
- `shared_vendor_footprint.py` — pulls each shared vendor's total client count
  (resumable, checkpoints to `footprint_cache.csv`)
- `reclassify.py` — offline bucketing of the 76 distinctive recipients into
  VENDOR / COMMITTEE / PROCESSOR / PERSON; emits `distinctive_clusters.csv`
