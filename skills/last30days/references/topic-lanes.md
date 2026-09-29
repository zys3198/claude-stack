<!-- Step 0.5d-f: optional source lanes
     2026-09-25 本地化裁剪时由 SKILL.md 移入；原行 1065-1147。 -->

### Step 0.5d: Resolve Trustpilot Domain (if topic is a company/brand)

When TOPIC is a company, brand, or service and you want Trustpilot review evidence, resolve its Trustpilot review-page domain. Trustpilot pages are keyed by domain (`www.thriftbooks.com`), not company name — a bare name 404s. Passing `--trustpilot-domain` (or a per-entity `trustpilot_domain` in `--competitors-plan`) auto-activates the opt-in Trustpilot source for that run — you do not also need `INCLUDE_SOURCES=trustpilot`.

**You usually already have it.** Step 0.55 item 6 (first-party positioning) fetches the official site — capture the bare hostname while you're there. When positioning wasn't fetched, one lookup covers it:

```
WebSearch("{TOPIC} official site")
```

Pass to the CLI: `--trustpilot-domain={domain}` (e.g., `--trustpilot-domain=www.thriftbooks.com`)

The flag is used verbatim, bypasses the engine's brand-shape gate, and auto-activates Trustpilot for the run, so it also unlocks Trustpilot for multi-word company names ("Stanley Steemer carpet cleaning"). For comparisons, put a per-entity `trustpilot_domain` in each PEER entity's `--competitors-plan` entry; the MAIN topic's domain must ride the outer `--trustpilot-domain` flag (the engine does not read a main-topic entry out of the plan).

**A miss is not fatal.** When the flag is absent, the engine resolves name → domain itself via the CLI's search **only when Trustpilot is already active** (`INCLUDE_SOURCES=trustpilot` or `--search` includes it); headless `--auto-resolve` fills a hint the engine verifies, but that hint alone does not activate the source. Resolve the flag when the domain is already in hand or the company name is ambiguous (lookalike or same-named companies) — an explicit domain is the only way to guarantee the right company *and* turn the source on.

**Skip this step if:**
- TOPIC is a person, event, or abstract concept (no company reviews to fetch)
- You intentionally want Trustpilot off for this run (`EXCLUDE_SOURCES=trustpilot`)

Store: `RESOLVED_TRUSTPILOT_DOMAIN = {domain or empty}`

---

### Step 0.5e: Decide the Amazon Buyer-Signal Lane (if `brightdata` is available)

**Availability first.** This lane exists only when the Bright Data CLI is on PATH and logged in (`--diagnose` reports `brightdata_installed` and `brightdata_authenticated`). If either is false the source does not exist, nothing changes, and you should skip this step entirely — do not mention it, do not suggest installing it mid-run.

**The one question to ask:** *would recent Amazon buyer sentiment materially inform this report?* Not "is this shopping" — the test is whether buyer evidence is real evidence for this topic.

| Topic | Fires? | `--amazon-query` |
|---|---|---|
| "Weber Grills" | Yes — brand topic where review signal is core evidence | `Weber grill` |
| "best bluetooth speaker under $100" | Yes — buying question, the whole point | `bluetooth speaker` |
| "Bentgo Box" | Yes — brand line | `Bentgo lunch box` |
| "Matt Van Horn" (CEO of June) | Yes — **and the keyword is the company's product, not the person** | `June Oven` |
| "Kanye West" | No — person/culture topic, buyer reviews are noise | — |
| "the 2026 election" | No — nothing to buy | — |

**Two mechanics that matter:**

1. **The keyword is yours to choose and is often not the topic.** Map person → company → product line using what you know plus what Step 0.55 surfaced. A "Matt Van Horn" run that searches Amazon for his name returns nothing; searching `June Oven` returns his company's product reviews, which is the actual signal.
2. **Phrase it as brand plus category, never bare brand.** A bare brand keyword lands on Amazon's ad-heavy page 1 and can miss the brand's own bestsellers — a live `Bentgo` search returned 57 competitor ads and missed the flagship, while `Bentgo lunch box` surfaced it. Say `Weber grill`, not `Weber`.

**`--search` is replace-not-add.** Passing `--search` narrows the run to exactly the sources listed, so include the full intended set: `--search reddit,x,youtube,amazon` — never a bare `--search amazon`, which would silently drop every other source.

**Cost and latency, so you can set expectations:** one credit for the product search plus one per review pull, 4 per typical run against a 5,000/month free tier. Review sampling adds roughly 30 seconds to 2 minutes at default depth. Quick depth pulls no reviews at all.

Store: `AMAZON_QUERY = {product keyword or empty}` — pass as `--amazon-query="{AMAZON_QUERY}"` and add `amazon` to `--search`.

**Skip this step if:** the CLI is unavailable, the topic has no consumer-product dimension, or the user set `EXCLUDE_SOURCES=amazon`.

---

### Step 0.5f: Decide the Meta Ads Lane (if a ScrapeCreators key is set)

**Availability first.** This lane exists only when `SCRAPECREATORS_API_KEY` is configured (`--diagnose` reports `has_scrapecreators`). Without it the source does not exist, nothing changes, and you should skip this step entirely — do not mention it, do not suggest signing up mid-run.

**The one question to ask:** *is there a brand here whose own paid message is evidence?* This lane answers "what is this company paying to say right now" — its live creatives, the products it is pushing, the promo codes it is running, and what its video ads say out loud. It is not a conversation source: nothing here is what people think about the brand, only what the brand is telling them.

| Topic | Fires? | Why |
|---|---|---|
| A consumer-brand topic | Yes — the brand's own campaign is first-party evidence | Paid message next to customer reaction |
| A retailer or membership warehouse | Yes — current promotions and seasonal push | Live offers are the story |
| A direct-to-consumer startup | Yes — positioning shows up in ad copy first | Often the earliest signal of a repositioning |
| A person, an executive, a creator | No — people do not run Ad Library campaigns | Their company might; use the company as the topic |
| An AI tool, a framework, a developer product | No — resolution returns unrelated advertisers | A live check on one such topic returned 1,467 wrong-entity ads |
| A news, politics, or culture topic | No — nothing to resolve | The lane ends unresolved and spends a credit finding that out |

**Three mechanics that matter:**

1. **Resolution can pick the wrong company, and the footer tells you when it did.** The lane resolves the advertiser page by name from an ad search. The 📣 footer line always names the page it resolved, and says `matched by partial name` when it fell back to the weakest match, so check it. If the advertiser is not the brand you meant, find the real page id and re-run with `--meta-ads-page`: `WebSearch("{TOPIC} facebook ad library")`, open the Ad Library result, and take the digits from its `view_all_page_id=` parameter. A `facebook.com/<name>` vanity URL is not a page id and the flag rejects it.
2. **A brand that advertises under product-line names still resolves.** Matching works in both directions, so an umbrella topic finds a product-named page and vice versa. What does not resolve is a brand whose pages share no word with the topic; that is the override's main use.
3. **The window means launched, not running.** Items are creatives that *started* inside the last 30 days. Long-running creatives from before are counted on the footer but never ranked, because "still advertising" is not news and "just launched this" is.

**`--search` is replace-not-add.** Passing `--search` narrows the run to exactly the sources listed, so include the full intended set: `--search reddit,x,youtube,meta_ads` — never a bare `--search meta_ads`, which would silently drop every other source.

**Cost and latency, so you can set expectations:** one or two credits to resolve the advertiser (a second only when the first search finds no name match), up to two more for its creatives, and up to three for video transcripts — at most seven per default-depth run against a 10,000-call free tier. Transcripts add roughly 15 to 45 seconds. Quick depth pulls no transcripts at all, though it still spends the resolve and one page.

Store: `META_ADS_PAGE = {page id or empty}` — add `meta_ads` to `--search`, and pass `--meta-ads-page="{META_ADS_PAGE}"` only when you have a page id.

**Skip this step if:** no ScrapeCreators key is set, the topic has no brand whose advertising is evidence, or the user set `EXCLUDE_SOURCES=meta_ads`.
