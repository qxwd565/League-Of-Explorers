# Date-first League of Explorers API

Pinned original main: ea2983bcc83c00fcf74ae4d4531d1fce4301e6b1. All 62 existing data files are actual cards: 60 catalog cards (45 collectible) and two source-only records, HERO_11bp and HERO_11bpt. All 62 now have date-first timelines and immutable metadata sidecars. All six root endpoints retain exactly the original 60 runtime IDs. No invented catalog row, unrelated expansion, plugin, site or database change.

## Source and reconstruction provenance

Original data files were schemaVersion 1 wrappers with 17 forward patch events. Root cards.json/render.json were schema 1 current catalogs, and root history.json already contained sparse reverse history. There is no data/history.json aggregate in this repository. The two extra files are real Death Knight power/token records, not an aggregate.

metadata/<ID>.json keeps originalSource exactly equal to pinned Git data and currentCatalog exactly equal to the original catalog row. Source-only records have currentCatalog null. Full raw native tags, text, assets, relationships and original metadata survive. tools/supplemental-audit contains separately labeled reconstructed inputs; these are not falsely attributed to the pinned source. Clean migration regenerates all 130 card/sidecar/bundle files from pinned originals plus committed evidence.

## Canonical dates and fields

Each data/<ID>.json has the first known full gameplay state, then sparse changes. Missing fields inherit; __remove deletes. Null, zero, false, empty values and absence remain distinct. Source chooseOne booleans and unknown rarity null survive. Spells and powers get no invented combat stats. The weapon uses durability, not health; the old transport alone retains its health mirror. Display line breaks are exactly <br></br>; raw evidence stays verbatim.

32 later events retain and correct the original 17 events while adding 15 missing events. Known numeric, type, race and school values match 52 exact original-ID client archives, comprising 3,162 observations. This bounded sample is not every patch or a complete rule-engine audit.

Main corrections include Ethereal Conjurer health, five 27.2 card changes (Museum Curator, Tomb Pillager, Keeper of Uldaman, Dark Peddler and Explorer's Hat), Gorillabot cost and later Beast type, Scarab Beast, Jungle Moonkin Beast removal, Djinni Elemental timing, Mummy Zombie Undead timing, Ancient Curse cost/manual casting and named Casts When Drawn text, and Raven Idol option costs. Undead/Beast dual types on Unearthed Raptor and Fossilized Devilsaur no longer appear at release. The latter's other-Beast condition wording follows its own type addition.

Korean ordinary-match availability is the date rule. Original 45 collectible wing mappings remain November 13, November 20, December 4 and December 11, 2015. The week-long hiatus is preserved. Generated cards follow their actual source, including Elise's deceptively prefixed LOE_019t/t2. After the 2026-11-14 first-use-only audit, all 15 generated/choice card first possible gameplay days are verified by their originating playable parents plus the matching original 2015 CardID and DBF; their complete baseline stats/text remain partially verified. The 2 unrelated source-only DK records remain estimated. The two source-only DK records use an estimated November 30, 2022 generation date from prelaunch Finley evidence, not an asserted class unlock or verified Korean replay.

Important corrected dates: Naga type April 6, 2022, not expansion launch April 13; Djinni Elemental July 11, 2017, not April 5; Jungle Moonkin Beast removal July 11, 2018, not the US July 10 header. Ancient Curse manual-cast/cost change is December 7, 2017 and named keyword October 3, 2018. Exact patch-date evidence and qualifications are in tools/loe-date-recheck.json.

## Abilities and uncertainty

The bounded intrinsic vocabulary distinguishes own keywords from references/grants. Museum Curator is not a Deathrattle minion. Brann and Rumbling Elemental do not themselves have Battlecry. Tunnel Trogg does not Overload. Explorer's Hat grants another card Deathrattle. Fossilized Devilsaur only conditionally gains Taunt. The DK power creates a Charge ghoul but does not itself have Charge. Jungle Moonkin's symmetric Spell Damage aura is proven by own text despite referenced rather than actual tag. Choose One is present from Raven Idol's own release text. Discover and other free-text effects remain in text; empty mechanics does not mean effectless. Implementation AURA/TRIGGER_VISUAL stay separate.

All 62 baselines remain partially verified. There are 36 unresolved initial Korean display/name differences; modern display is retained where the exact historical transition date is unverified, while raw observations are preserved. Naga rule-order timing is unresolved, not given a guessed 9.1 date. Early class/rarity implementation differences are not promoted to dated gameplay facts. Strict resolution rejects partial history; ordinary consumers get no new default visibility gate. See tools/loe-known-unmodeled-intervals.json.

## Compatibility and validation

cards.json, render.json and history.json remain schema 1 for unchanged clients. The current catalog changes only 27 text newline forms. All current numbers, types, IDs, DBFs, races, mechanics conventions, relationships and assets match pinned originals. Endpoint field presence is preserved rather than freezing all current values; future approved cost/keyword changes propagate.

cards-date.json, render-date.json and history-date.json are precise root siblings. They expose exact typed states, historySchema 2, disjoint reverse intervals and explicit removals. All retain original art/<ID> bases. Source-only records remain independently reconstructable but intentionally absent from these 60-card bundles.

Checks cover 62 immutable originals, 386 unchanged artwork/golden files, all date boundaries, 3,540 precise cases, 3,540 old parser cases, 360 sibling art URL checks, typed-presence fixtures, future propagation, 130-file clean regeneration and repeated-build idempotence. The unchanged pinned PHP plugin passed 60 imports and 3,541 checks under PHP 8.5.12. Old whitelist/native-tag/sentinel limitations remain; offline tests do not prove live UI or authorize plugin import changes.

Run python3 tools/migrate-date-schema.py, python3 tools/build-api.py, then all test-*.py scripts. CI uses only local committed tools, full Git history and persist-credentials:false. The old wrapper writer is disabled. Optional extract-client-evidence.py --archive-dir <directory> verifies full-file SHA256 and re-extracts each pinned original-ID observation from supplied XML archives. Do not infer server-live dates from archive commit timestamps.

## First-use provenance audit (2026-11-14)

Original 2015 client build 4.0.0.10833 (HearthSim/hsdata commit af481578003cb5dae70b672353d33e298f9ab128) matches 60/60 source CardID/DBF pairs. Actual regional release days 2015-11-13 / 2015-11-20 / 2015-12-04 / 2015-12-11 are established separately from client patch import; November 27 was a hiatus. Parents, token generation and source URLs are independently recorded in tools/loe-first-use-evidence.json. All 45 collectible releases were already verified; the 15 token/choice release confidence statuses have now been promoted with original date keys preserved. Source-only BASIC DK HERO_11bp and HERO_11bpt are untouched. Build + compatibility and pinned-source reproducibility tests guard against gameplay/history/art drift.
