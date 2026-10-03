# Krakow hackathon landscape: organizers, recurring events, channels

Research date: **3 Oct 2026**. Scope: Krakow-held (or Krakow-run) hackathons, game jams, CTFs, datathons, roughly 2023 to Oct 2026, plus already-announced events.
Machine-readable version: `organizers.json` (38 entries, same content). Marks used below:
**[V]** verified on a primary page, **[P]** partial (search snippet / secondary source), **[U]** unverified or inferred.

## 0. Method and honest caveats

- Sources: web search + page fetches of official sites, Crossweb, Luma, Devpost, Global Game Jam, CTFtime, university/city/KPT news portals, LinkedIn posts surfaced by search.
- **Selection bias:** I found events through web search, so web-indexed events are over-represented. Facebook-, Discord-, Instagram- or Telegram-only events are by construction under-counted. Treat the volume figures as a lower bound.
- Several URLs (Crossweb, Devpost, GGJ, cybermadeinpoland.pl, krakhack.info, startup.pfr.pl) returned HTTP 403 to a plain scripted fetch (bot protection) but were visible in search results. Scrapers will need a browser UA, a headless browser, or an API/RSS route.
- Confirmed bad data in the wild: the blog `laczymybiznes.pl` lists HackYeah in "wrzesień" with "48 godzin" and NASA Space Apps in Krakow for Oct 2026; none of that matches the official sites. Do not use blog round-ups as a source. One search-engine summary also claimed HackYeah 2018 was in Krakow; sources conflict **[U]**.
- Crossweb mis-types: the March 2026 Blockchain Hack Krakow is listed as "Meetup", 1 day. GrowUp Hackathon is dated by its application deadline. Filtering by Crossweb type "Hackathon" alone misses events and keeps false positives (Hackerspace "Nighthack" shows up).

## 1. Announced / upcoming (from 3 Oct 2026)

| Event | Date | Where | Audience | Primary URL | Status |
|---|---|---|---|---|---|
| HackYeah 2026 (12th) | 3-4 Oct (in progress) | TAURON Arena Krakow | 18+, open | https://hackyeah.pl/ | [V] |
| EPICURE Hackathon (HPC/AI code optimisation, 5th ed.) | 7-9 Oct | ACK Cyfronet AGH + online | research/dev teams, registration on INESC TEC | https://www.cyfronet.pl/en/training/epicure-hackaton | [V] |
| European AI Hackathon (Cyfronet; hybrid, startups/SMEs/research) | 6-29 Oct | hybrid | EU teams | https://www.cyfronet.pl/en/training/european-ai-hackaton | [P] |
| Film Spring Open Hackathon (AI x film; Microsoft, Lenovo) | 16-18 Oct | Hotel Forest, Krakow / online | film-makers + devs | https://filmspringopen.eu/edukacja/hackathon-film-spring-open-2026/ | [V] |
| Blockchain Hack Krakow (Solana, Superteam Poland) | 17-18 Oct | Zablocie 20.22 | open | https://crossweb.pl/wydarzenia/blockchain-hack-krakow-pazdziernik-2026/ | [V] |
| AI in Pharma Student Hackathon | 25 Oct | AGH campus | students, free, English | https://www.aiinpharma.pl/hackathon-2026/ | [V] |
| GrowUp Hackathon (online; live final in Krakow) | apply to 20 Oct; online from 12 Nov; final 14 Jan 2027 | online + Krakow | 18-26 | https://growuphackathon.pl/ | [P] |
| AGH Cyber Kampus 4: CTF + conference | CTF 25 Nov, conf 26 Nov | AGH | students/pros | https://www.informatyka.agh.edu.pl/en/blog/save-the-date-agh-cyber-kampus-returns-this-november/ | [V] (agenda TBA) |
| "Mobilna pomoc - prosty robot ratunkowy" | 1-2 Dec | EXPO Krakow | vocational pupils only, 30 seats, apply by e-mail to 1 Nov | https://malopolskauczy.pl/festiwal-uczelni/hackathon | [V] (restricted) |
| Global Game Jam 2027 (Krakow sites TBD) | 25-31 Jan 2027 | TBD | open | https://globalgamejam.org/ | [P]; site registration opens 1 Nov |
| Hack4Krak V4 CTF (school students) | 20-21 Mar 2027 planned | Krakow | school students | https://hack4krak.pl/about_us | [P] |
| BITEhack IX | expected Jan 2027 | AGH area | students | https://best.krakow.pl/en/bitehack/ | [U] not announced |
| #SDG City Challenge 2026 (UJ) | expected Oct-Dec | UJ | UJ students | https://pkw.uj.edu.pl/aktualnosci | [U] not announced |
| EIT Health i-Days Krakow 2026 | expected Oct-Nov | Zablocie | students | https://idays.lifescience.pl/ | [U] not announced |

Adjacent, not hackathons: DevFest Krakow 10 Oct (https://devfestkrakow.pl/, conference); Hackerspace "Nighthack" every Friday (incl. 25 Dec).
Near but not Krakow: NASA Space Apps 14-15 Nov (Polish locals found: Poznan, Stalowa Wola; **no Krakow node found**), HackNation 21-22 Nov Bydgoszcz, CASSINI 12th 27-29 Nov Gdansk, Junction Warsaw (Nov), IBM Z Datathon 17-18 Oct (Krakow participation [U]).
Just finished: DATASPRINT by Visa 29-30 Sep (Klub Studio) [P]; Nokia FPGA Hackathon 26-27 Sep [V].

## 2. Recurring series (Krakow-held)

### 2.1 Universities and student groups

| Series | Organizer | Typical month | Past editions found | Channels | Canonical URL |
|---|---|---|---|---|---|
| **BITEhack** (BEST IT Extended), 24h | BEST AGH Krakow | Jan (VII was ~Dec 2024) | Jan 2022; Dec 2024; 10-11 Jan 2026 (Klub Studio); 2023 [U] | own site per edition (returned HTTP 500), best.krakow.pl, **Crossweb**, LinkedIn, FB [U] | https://best.krakow.pl/en/bitehack/ |
| **Hacknarok**, 24h, teams of 4 | EESTEC AGH Krakow | Apr | IX 12-13 Apr 2025 (KPT); X 18-19 Apr 2026 (Lubicz Park, 93 ppl) | hacknarok.pl, **Devpost**, **Crossweb**, FB group for team-finding | https://hacknarok.pl/ |
| **Kościuszkon**, hackathon+CTF+FPGA | Politechnika Krakowska (Faculty student council, Klub Kwadrat) | May/Jun | II 8-9 Jun 2024; III 31 May-1 Jun 2025; IV 9-10 May 2026 (theme cyber) | **Crossweb**, pk.edu.pl, FB, Instagram, LinkedIn | https://crossweb.pl/wydarzenia/kosciuszkon-iv-2026/ |
| **EnsembleAI**, ML 24h (rotating city) | KN BIT + KN Golem (AGH), KN Data Science (PW), KNUM (UW), MLinPL | Mar | 2024 Warsaw; **15-16 Mar 2025 AGH Krakow**; Mar 2026 Warsaw | ensembleaihackathon.pl, agh.edu.pl, LinkedIn | https://ensembleaihackathon.pl/ |
| **KN BIT AGH company hackathons** (DISKovery x ADATA 3 Dec 2025; AI hackathon with Upside 9 Jan 2026) | KN BIT | Dec/Jan | 2025, 2026 | **FB + LinkedIn only** found | LinkedIn page |
| **AI KrakHack** | KN AI Possibilities Lab, WSEI | Mar-Jun | Jun 2025; 27-28 Mar 2026 (48 ppl; numbering inconsistent) | krakhack.info (403 to scripts), LinkedIn | https://krakhack.info/ |
| **#SDG City Challenge** (semester hackathon) | UJ PKW + City of Krakow | Oct-Dec | 2024 (3rd), 2025 (4th; 17 Oct-13 Dec) | pkw.uj.edu.pl news; MS Forms | https://pkw.uj.edu.pl/aktualnosci |
| **Hackathon GBS** (business, non-coding) | UEK + City + GBS firms | Mar-Apr | 3rd ed. 27-28 Mar + 3-4 Apr 2025; no 2026 found | uek.krakow.pl, gbs.uek.krakow.pl | https://gbs.uek.krakow.pl/ |
| UEK online/international hackathons (D4PACK 22 Apr 2026; ENTEEF 20 May 2026) | UEK | Apr-May | 2026 | uek.krakow.pl | not Krakow-venue |
| **HackAGH**, 12h | URSS AGH + Capgemini Engineering | Apr | 22 Apr 2023 only | hack.samorzad.agh.edu.pl, LinkedIn | https://hack.samorzad.agh.edu.pl/ |
| **Hack4Krak CTF** (school students) | Fundacja Zerya / community | Feb-May; next Mar 2027 | Feb 2025; May 2025; 23-24 May 2026 (UKEN, 109+) | hack4krak.pl, **CTFtime**, GitHub, LinkedIn | https://hack4krak.pl/ |
| **AGH Cyber Kampus** CTF+conf | AGH Faculty of CS, #CyberMadeInPoland, KN Zero Day, Try IT | Nov | 3.0 on 26-27 Nov 2025 (CTF 82 ppl, 400+ attendees) | cybermadeinpoland.pl, informatyka.agh.edu.pl, **evenea**, FB event, LinkedIn | https://cybermadeinpoland.pl/agh_cyber_kampus/ |
| **AI in Pharma Student Hackathon** | ISPE Poland + AGH (+AWS) | Oct | 2025 (in Poznan); 25 Oct 2026 Krakow | aiinpharma.pl, eaiib.agh.edu.pl, LinkedIn | https://www.aiinpharma.pl/hackathon-2026/ |
| **EPICURE Hackathon** | Cyfronet AGH + INESC TEC | Oct (2026) | 5th ed. 2026; earlier venues not checked | cyfronet.pl | https://www.cyfronet.pl/en/training/epicure-hackaton |
| **HERE Krakow Hackathon** | HERE Technologies + AGH WGGiOS | Jun | 12-13 Jun 2025 only | innoagh.pl | https://www.innoagh.pl/en/wydarzenia/here-krakow-hackathon-2025/ |

Not hackathons but often confused: AGH "IT is ME!" competition (finals 12 May 2026 at AGH IT Future Day), AGH Science4Business open day, INNOAGH events.

### 2.2 Ecosystem, city and regional organizers

| Series | Organizer | Typical month | Past editions | Channels | URL |
|---|---|---|---|---|---|
| **HackYeah** (flagship, ~3000 registrants, 24h) | Proidea (Krakow) | late Sep / early Oct | 2022-2026 at TAURON Arena Krakow: 2024 28-29 Sep (10th, 13 tasks, 240k+ PLN); 2025 4-5 Oct (11th, 400+ projects); 2026 3-4 Oct (12th) | hackyeah.pl, **Crossweb**, **Eventory** (tickets), FB, Discord, LinkedIn, venue site, krakow.pl news | https://hackyeah.pl/ |
| **Blockchain Hack Krakow** (+ Solana Ideathon) | Superteam Poland + Klaster Zablocie | Mar and Sep/Oct | 19-20 Sep 2025 [P]; 28-29 Mar 2026 ($3k); 17-18 Oct 2026 | **Luma** (HACKKRAKOW, BlockchainHackKRK), **Crossweb**, Devpost, Telegram, klasterzablocie.um.krakow.pl | https://crossweb.pl/wydarzenia/blockchain-hack-krakow-pazdziernik-2026/ |
| **EUDIS Defence Hackathon Poland** | KPT / FORT Krakow (+AGH) | Mar-Jun | 31 May-2 Jun 2024; 9-11 May 2025; 26-28 Mar 2026 (118 ppl) | **Taikai**, media.kpt.krakow.pl, innoagh.pl, startup.pfr.pl, LinkedIn | https://media.kpt.krakow.pl/ |
| **Hackathon dla Malopolski** | Malopolska Voivodeship + KPT | Nov and May/Jun | Nov 2024; 7-8 Jun 2025 (Krakow); Nov 2025 (Tarnow); 30-31 May 2026 (Nowy Sacz); **5th not announced** | hackathon-dla-malopolski.kpt.krakow.pl, malopolska.pl, innowacyjna.malopolska.pl, LinkedIn | https://hackathon-dla-malopolski.kpt.krakow.pl/ |
| **EIT Health i-Days Krakow** | Klaster LifeScience Krakow + KMS | Oct-Nov | 3rd ed. 25 Oct 2025 | idays.lifescience.pl, lifescience.pl | https://idays.lifescience.pl/ |
| **KrakJam** (GGJ site) | KPT / Digital Dragons | late Jan | 2020-2024 (2023 in person at KPT); 2025 [U]; 30 Jan-1 Feb 2026 online | krakjam.digitaldragons.pl, **globalgamejam.org**, media.kpt.krakow.pl, Discord | https://krakjam.digitaldragons.pl/ |
| **Krakow Game Jam** + Junior | City of Krakow, Zablocie Space | Jan, Mar | 30 Jan-1 Feb 2026 (66 ppl); Junior 16-22 Mar 2026 | **globalgamejam.org**, klasterzablocie.um.krakow.pl, dlabiznesu.krakow.pl, Discord | https://globalgamejam.org/jam-sites/2026/krakow-game-jam-zablocie-space |
| **NASA Space Apps Krakow** | ThinkHackR + AGH + KPT | Oct | 5-6 Oct 2024 (AGH); none found 2025/2026 | spaceappschallenge.org, nasaspaceapps.pl, krakow.pl | https://www.spaceappschallenge.org/2026/ |
| **CASSINI Hackathon Poland** | KPT (organizer), now elsewhere | Apr, Nov | Krakow 6th ed. 3-5 Nov 2023; since then Wroclaw/Gdansk | cassini.eu, ChallengeRocket, media.kpt.krakow.pl | not Krakow now |
| **GrowUp Hackathon** | Fundacja DeepKind (+ KMS) | Nov-Jan | 2026 edition; earlier year [U] | growuphackathon.pl, Crossweb, allhackathons, LinkedIn | https://growuphackathon.pl/ |
| Re: Lacz Hackathon | unclear (venue Zablocie 20.22) | Mar | 6-8 Mar 2026, ~30 ppl | single non-obvious web page | https://axiosaccel.com/hackathony |
| Mlodziezowy Hackathon Biznesowy | Krakow Miastem Startupow / job fair | Mar | 11 Mar 2026 | LinkedIn only found | LinkedIn |
| "Mobilna pomoc" (vocational) | Malopolska Voivodeship | Dec | Dec 2026 first found | malopolskauczy.pl, e-mail | https://malopolskauczy.pl/festiwal-uczelni/hackathon |

### 2.3 Corporate

Public, Krakow-held: **Nokia FPGA Hackathon** (Nov 2022; 22-23 Apr 2023; 20-21 Apr 2024; 24-25 May 2025 at Hala Cracovii; 26-27 Sep 2026; own site fpgahackathon.com + nokiakrakow.pl + UJ page; application/selection) [V]. **Software Mansion Hackathon** (2024; 28 Mar 2026 "SWM x Gemini", hackathon.swmansion.com + AGH blog) [V]. **HERE** (above). **Visa DATASPRINT** (29-30 Sep 2026, visadatasprint.com) [P]. **Film Spring Open** sponsors Microsoft/Lenovo (above).
Sponsors/partners (not organizers): Aptiv, IBM, Sabre, UBS, Pega (BITEhack); Capgemini Engineering (HackAGH 2023); Honeywell, Akamai, Hitachi, IBM (Kościuszkon); ABB, Cisco, Jacobs, Genpact, Zurich (GBS); GR8 Tech, Deloitte, Luxoft, IBM (HackYeah).
Internal only (not joinable): **Motorola Solutions Open Innovation Hackathon** (Jul 2025; 2-3 Jun 2026, Krakow hub; LinkedIn posts) [P].
**No public Krakow hackathon found 2023-2026** (absence of evidence, not proof): Google, Comarch, Luxoft/DXC, Amazon, Shell, Ocado (hosts meetups), Goldman Sachs (Warsaw), Credit Suisse, State Street (Academy, not hackathon), HSBC, Tyro, ING, Philip Morris, Atlassian/Spartez, STX Next (Warsaw), 10Clouds, Netguru, Cisco (Splunk4Students workshop).

### 2.4 Communities / meetups (none found running hackathons)

Hackerspace Krakow (weekly Nighthack; Meetup 2.5k members, Telegram, FB; mirrored on Crossweb), Pykonik (meetup.com/pykonik, Tech Talks #86 on 24 Sep 2026), PyData Krakow, AWS User Group Krakow (#77 on 19 May 2026), GDG Krakow (DevFest, Build With AI, Eskadra Bielika workshops), Flutter Cracow, WomenTech Network Krakow. Not verified: Krakow JS, Node, Cracow Tech Meetup. Girls Who Code / Women Who Code: no Krakow hackathons found; "She Hacks" inside HackYeah is the women-in-tech hackathon track. Searched and found no Krakow tie: Hack4Good, Hack4Health, Hack the Hood, Ludum Dare Krakow, KrakowCTF, Venture Cafe Krakow, Startup Poland hackathons.

### 2.5 National programmes worth feeding a "widen" mode

HackNation (GovTech, Bydgoszcz, Nov), CASSINI (spring+Nov), NASA Space Apps (global, Nov 2026), Junction Warsaw, Warsaw.AI Hackathon (Nov 2025, Google for Startups Campus), AI Tinkerers Poland (application, Warsaw), Hack Heroes (online school contest, Nov), 4Developers/Infoshare/Devoxx (conferences, not hackathons).

## 3. Channel coverage: what covers >90%?

No single channel does. My tally over ~30 public Krakow-held events from Oct 2025 to Mar 2027 that I catalogued (rough, from n≈30, biased to web-visible events):

| Channel layer | Approx. share of events present | Notes |
|---|---|---|
| Crossweb (pl/en) | ~25-30% | HackYeah, BITEhack, Hacknarok, Kościuszkon, Blockchain Hack x2, GrowUp, Nighthack confirmed; most corporate/university/ecosystem events absent; mis-typed entries |
| Luma | ~7-10% | Superteam events; Zablocie Space; low overall |
| Devpost | ~7% | Hacknarok, Blockchain Hack |
| Global Game Jam registry | ~10% (all game jams) | single authoritative source for jams |
| CTFtime | ~5% | Hack4Krak (AGH Cyber Kampus not seen) |
| Taikai / ChallengeRocket | ~5% | EUDIS, CASSINI |
| University/city/KPT/region news pages (agh.edu.pl, informatyka.agh.edu.pl, eaiib.agh.edu.pl, innoagh.pl, cyfronet.pl, pk.edu.pl, uek.krakow.pl, pkw.uj.edu.pl, krakow.pl + dlabiznesu.krakow.pl, klasterzablocie.um.krakow.pl, media.kpt.krakow.pl, malopolska.pl, lifescience.pl, malopolskauczy.pl) | ~50-55% | institutional events are almost always here |
| Organizer's own site | ~80-85% | but heterogeneous (needs a seed list; many per-year domains) |
| LinkedIn | ~60-65% | often the only place for results/announcements |
| Facebook | ~35-40% (guess) | team-finding groups, student clubs |

**Practical conclusion (estimate, not measured):** the union of {Crossweb + Luma + Devpost + GGJ registry + CTFtime + Taikai/ChallengeRocket + ~14 institutional news pages + a maintained seed list of ~30 organizer sites} should cover about **85-92%** of Krakow events I'd consider feed-worthy. The last 8-15% needs LinkedIn/Facebook (or manual submission). Crossweb alone is not enough (~1 in 4).

## 4. Hard-to-scrape (social / invite / gated) events

- KN BIT AGH company hackathons (DISKovery, Upside): Facebook + LinkedIn, no persistent page.
- Mlodziezowy Hackathon Biznesowy (KMS): LinkedIn only.
- Re: Lacz: a single personal/consultant page.
- Corporate internal events (Motorola Open Innovation): LinkedIn employee posts only; not joinable anyway.
- Team-finding layer: Hacknarok Facebook group, HackYeah Discord, Superteam Telegram, Krakow Game Jam Discord, Hackerspace Telegram.
- Registration walled elsewhere: EPICURE (INESC TEC), #SDG City Challenge (MS Forms), "Mobilna pomoc" (e-mail), FPGA (application + selection), AI Tinkerers (application).
- Meetup events pages are JS-rendered (my fetch returned only a header); Crossweb/Devpost/GGJ/CTFtime return 403 to naive clients; BITEhack and krakhack.info flaky (500/403).
- LinkedIn post URLs are only reachable via search; no public API.

## 5. Volume and seasonality

Counted from what I verified (public, Krakow-held, includes game jams and CTFs, excludes internal events, restricted-school events counted separately):

- Calendar 2025: ~19 found (Jan 1, Feb 1, Mar 2, Apr 1, May 4, Jun 3, Jul 0, Aug 0, Sep 2, Oct 3, Nov 1, Dec 1).
- Oct 2025-Sep 2026: ~22 found (Oct 3, Nov 1, Dec 1, Jan 4, Feb 0, Mar 7, Apr 2, May 2, Jun-Aug 0, Sep 2).
- My estimate of the real figure including FB-only, small club and online-Krakow-hosted events: **roughly 25-35 per year, i.e. 2-3 per month on average**. Excluding school-only and tiny jams: ~12-18 "real" hackathons.

Seasonality: peaks in **March (5-7)** and **October (3-6)**, secondary bumps in **January** (BITEhack, GGJ, KrakJam) and **April-June** (Hacknarok, Kościuszkon, EUDIS, Hack4Krak, FPGA). Troughs: **July-August (~0)**, **February (~0-1)**, mid-Dec to early Jan. Weekends in Oct-Nov 2026 are reasonably full (HackYeah, EPICURE, Film Spring Open, Blockchain Hack, AI in Pharma, Cyber Kampus); Dec-Feb is thin (Mobilna pomoc, GrowUp final, GGJ Jan 25-31, BITEhack likely).

**Will a Krakow-only feed feel full?** No. At any random time there are usually 0-2 upcoming events inside a 3-week window, and several of those are audience-restricted (school pupils, UJ-only, research teams). Recommended defaults:
1. Krakow city (core), with an "audience" tag (open / students / school / pro).
2. Widen to Malopolska (Nowy Sacz, Tarnow, Hackathon dla Malopolski rotates).
3. Poland-wide on-site (Warsaw, Wroclaw, Gdansk, Bydgoszcz, Poznan, Katowice) and online/global feeds (Devpost, MLH, ChallengeRocket, Taikai, Crossweb online). Poland-wide volume is likely several times Krakow's [U].
4. Show recently-ended events with results (Krakow community value) so the page never looks empty.

## 6. Open items worth checking next (not done)

- Announcement of BITEhack IX, i-Days 2026, #SDG City Challenge 2026, GGJ 2027 Krakow sites (after 1 Nov), Space Apps Krakow node (re-check mid-Oct), Hackathon dla Malopolski V.
- Confirm HackYeah 2023 URL/archive, KrakJam 2025, AI KrakHack numbering, Solana Ideathon year.
- A direct count of Crossweb's Krakow + Hackathon feed over time (the fetch returned only a stub) to turn the estimates in section 3 into measured numbers.
