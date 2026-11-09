"""Explicit lossy schema-1 boundary for the unchanged installed plugin.

Never write this projection back to canonical data or confidence sidecars.
"""
from __future__ import annotations
import copy
from date_schema import SPECS, apply, json_equal, resolve

LEGACY_FIELDS = ("name", "type", "cardClass", "classes", "rarity", "collectible",
                 "cost", "attack", "health", "durability", "armor", "text",
                 "races", "race", "spellSchool", "mechanics", "legacyArt")
RENDER_FIELDS = ("id", "dbfId", "name", "type", "cardClass", "rarity", "collectible",
                 "cost", "text", "attack", "health", "durability", "armor", "art",
                 "races", "race", "spellSchool", "set", "nativeTags", "mechanics",
                 "watermark", "classes", "releasedAt", "releaseStatus")
PHP_FIELDS = ("name", "cost", "text", "attack", "health", "durability", "armor",
              "race", "spellSchool", "art", "legacyArt", "type", "cardClass",
              "rarity", "watermark", "mechanics", "nativeTags")


def project_legacy(state, meta):
    """Represent exact state using documented old wire sentinels only."""
    original = meta['currentCatalog'] or meta['originalSource']['card']
    managed = set(meta.get('canonicalFields', [])) | set(original)
    result = {k:copy.deepcopy(v) for k,v in state.items() if k in LEGACY_FIELDS}
    for key in ('cost','attack','health','durability','armor'):
        if key not in result:
            # The old renderer/exporter used health as the weapon's mirror.
            # Preserve that legacy representation only at this output boundary.
            if key == 'health' and state.get('type') == 'WEAPON':
                result[key] = state.get('durability',0)
            else:
                result[key] = 0
    for key,empty in (('text',''),('race',''),('races',[]),('spellSchool',''),('mechanics',[]),('classes',[])):
        if key not in result and (key == 'text' or key in managed):
            result[key] = copy.deepcopy(empty)
    # Preserve the pinned endpoint's annotation convention, not a frozen card.
    # Implementation markers and referenced-keyword annotations remain confined
    # to schema1. Future canonical keyword changes still flow through.
    convention = meta['legacyMechanicsConvention']
    owned = state.get('mechanics', [])
    baseline = convention['canonicalBaseline']
    previous = convention['original']
    legacy = [m for m in previous if m not in baseline or m in owned]
    legacy += [m for m in owned if m not in baseline and m not in legacy]
    if convention['present'] or legacy:
        result['mechanics'] = legacy
    else:
        result.pop('mechanics', None)
    # Old JSON always has these required common fields in this League corpus.
    # Do not invent unsupported data for a different expansion silently.
    for field in ('name','type','cardClass','rarity','collectible'):
        if field not in result:
            raise ValueError(f"Schema-1 compatibility cannot supply missing {field}: {state.get('id')}")
    return result


def compile_legacy(timeline, meta, precise_record):
    record = copy.deepcopy(meta['currentCatalog'])
    record.pop('history', None)
    latest = resolve(timeline,meta)
    current = project_legacy(latest,meta)
    for field in LEGACY_FIELDS:
        if field == 'legacyArt':
            continue  # old current catalogue never advertised this flag
        if field in current:
            if field in ('race','races') and field not in record and not current[field]:
                continue
            record[field] = copy.deepcopy(current[field])
    record['releasedAt'] = meta['release']['date']
    record['releaseStatus'] = meta['release']['status']
    if timeline:
        points=list(timeline.items())
        start,state=points[0]
        events=[{'date':d,'changes':c} for d,c in points[1:]]
    else:
        start=None
        state=copy.deepcopy(meta['undated']['baseline'])
        events=meta['undated']['patches']
    revisions=[]
    for event in events:
        old=project_legacy(state,meta)
        changes={k:copy.deepcopy(v) for k,v in old.items()
                 if k not in current or not json_equal(v,current[k])}
        # Every old field is representable or normalized to the legacy
        # sentinel. No __remove operation reaches an old parser.
        if changes:
            revision={'before':event['date'],'changes':changes}
            if start:revision['from']=start
            revisions.append(revision)
        state=apply(state,event['changes'])
        start=event['date']
    return record,revisions


def loss_report():
    return {
        'schema':1,
        'scope':'Only old schema1 endpoints; canonical and precise endpoints retain exact presence.',
        'legacyConsumer':'qxwd565/HSdeck-plugin 78ce6fdc4e70f689880a70d6f22aa77a6c75e337 (unmodified)',
        'rules':[
            'Absent combat stats use old zero sentinels only at the compatibility boundary; one weapon retains its health/durability mirror.',
            'Original endpoint mechanics annotations and field presence are preserved, while future canonical cost and keyword edits propagate.',
            '27 current text fields normalize newlines to <br></br>. No other current catalog differences.',
            '60 existing catalog IDs remain in all root bundles. Two source-only card files have separate timelines but no fabricated catalog rows.',
            'Before-release fallback remains unchanged; no strict/default hiding is enabled.'
        ],
        'limitations':[
            'Old numeric sentinels cannot distinguish zero from absent attributes or represent general removals.',
            'Old PHP whitelist omits races/classes/collectible and arbitrary fields; current native tags can leak into historical rendering.',
            'Undated Korean wording/name/class/rarity changes and Naga rule-order timing remain explicitly qualified.',
            'Offline parser checks are not live site/import/rendering proof. No plugin or live setting was changed.'
        ],
        'preciseEndpoints':{'cards':'cards-date.json','render':'render-date.json','history':'history-date.json'},
        'artRule':'All six endpoints remain root siblings with original art/<ID> links.'
    }
