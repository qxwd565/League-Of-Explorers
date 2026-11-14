#!/usr/bin/env python3
"""Strict first-playable-day-only audit, independent of unrelated old stat defects."""
import json
import subprocess
from datetime import date,timedelta
from pathlib import Path
from date_schema import read_card, resolve, load
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL='ea2983bcc83c00fcf74ae4d4531d1fce4301e6b1'
audit=load(ROOT/'tools/loe-first-use-evidence.json')
assert audit['schema']==1 and audit['timezone']=='Asia/Seoul'
archive=audit['archive']
assert archive['build']=='4.0.0.10833'
assert archive['cardDefsBlobSha']=='c56bf29b116e57fd8cdf4382e27d109b72b29e12'
rows={c['id']:c for c in audit['archivedIdentity']}
tokens={t['id']:t for t in audit['tokens']}
assert len(rows)==60 and len(tokens)==15
assert sum(c['collectible'] for c in rows.values())==45
source=json.loads(subprocess.check_output(['git','show',ORIGINAL+':cards.json'],cwd=ROOT))['cards']
source={c['id']:c for c in source}
assert rows.keys()==source.keys()
for cid,record in rows.items():
    src=source[cid]
    assert src['id']==record['id'] and src['dbfId']==record['dbfId'],cid
    assert src['releasedAt']==record['firstUseKst'],cid
    assert src['collectible']==record['collectible'],cid
    timeline,meta=read_card(ROOT,cid)
    assert list(timeline)[0]==record['firstUseKst'],cid
    assert meta['release']=={'date':record['firstUseKst'],'status':'verified'},cid
    assert meta['currentCatalog']==src,cid
    assert meta['baselineStatus']=='partially-verified',cid
    proof=meta['releaseEvidence']
    assert proof['firstUseKst']==record['firstUseKst'],cid
    assert proof['originalClientCardId']==cid,cid
    assert proof['originalClientDbfId']==record['dbfId'],cid
    assert proof['originalClientBuild']=='4.0.0.10833',cid
    before=(date.fromisoformat(record['firstUseKst'])-timedelta(days=1)).isoformat()
    assert resolve(timeline,meta,before) is None,cid
for cid,record in tokens.items():
    parent=record['parentId']; root=record['rootCollectibleId']
    assert parent in rows and root in rows and parent in source,cid
    assert rows[root]['collectible'] and not rows[cid]['collectible'],cid
    assert rows[cid]['firstUseKst']==rows[parent]['firstUseKst']==rows[root]['firstUseKst'],cid
    proof=load(ROOT/'metadata'/f'{cid}.json')['releaseEvidence']
    assert proof['parentId']==parent and proof['rootCollectibleId']==root,cid
    assert record['statusBefore']=='estimated' and record['statusAfter']=='verified',cid
for cid in audit['sourceOnlyExcluded']:
    assert cid not in rows
    _,meta=read_card(ROOT,cid)
    assert meta['release']['status']=='estimated',cid

for name in ('cards.json','render.json','cards-date.json','render-date.json'):
    bundle=load(ROOT/name)['cards']
    byid={c['id']:c for c in bundle}
    assert set(byid)==set(rows),(name,'catalog ids differ')
    for cid,record in rows.items():
        c=byid[cid]
        assert c['dbfId']==record['dbfId'] and c['releasedAt']==record['firstUseKst'],(name,cid)
        assert c['releaseStatus']=='verified' and c['collectible']==record['collectible'],(name,cid)
    assert {c['art'] for c in bundle}=={source[cid]['art'] for cid in source}
h=load(ROOT/'history-date.json')['cards']
assert len(h)==60
for cid,record in rows.items():
    obj=h[str(record['dbfId'])]
    assert obj['id']==cid and obj['releasedAt']==record['firstUseKst'],cid
    assert obj['releaseStatus']=='verified' and obj['baselineStatus']=='partially-verified',cid
policy=load(ROOT/'release-policy.json')
assert policy['timezone']=='Asia/Seoul'
assert all(policy['cards'][cid]['status']=='verified' and policy['cards'][cid]['date']==row['firstUseKst'] for cid,row in rows.items())
# No change to gameplay JSON timelines, artwork, golden assets or frame files.
diff=subprocess.check_output(['git','diff','--name-only','--','data','art','golden','frame'],cwd=ROOT,text=True).strip()
assert not diff,('unapproved gameplay or art modification',diff)
print(json.dumps({'result':'pass','catalog':60,'collectibleFirstUse':45,'tokenFirstUse':15,
                  'undatedBaselineVerified':0,'sourceOnlyNotBackdated':0,
                  'noGameplayOrAssetChanges':True}))
