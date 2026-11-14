#!/usr/bin/env python3
import copy,json,subprocess,hashlib
from pathlib import Path
from datetime import date,timedelta
from collections import Counter
from date_schema import *
from legacy_projection import project_legacy
ROOT=Path(__file__).resolve().parents[1];SOURCE='ea2983bcc83c00fcf74ae4d4531d1fce4301e6b1'
def require_source_commit(root,commit):
 if subprocess.run(['git','cat-file','-e',commit+':data'],cwd=root,capture_output=True).returncode:raise RuntimeError('Pinned source unavailable; use checkout fetch-depth: 0')
def original(p):return json.loads(subprocess.check_output(['git','show',SOURCE+':'+p],cwd=ROOT))
def reverse(record,day):
 if day<record['releasedAt']:return None
 s=copy.deepcopy(record['current']);s.pop('art',None)
 matches=[e for e in record['history'] if e.get('from','0001-01-01')<=day<e.get('before','9999-12-31')];assert len(matches)<=1
 for e in matches:s=apply(s,e['changes'])
 return s

def main():
 require_source_commit(ROOT,SOURCE);current={c['id']:c for c in original('cards.json')['cards']};precise={c['id']:c for c in load(ROOT/'cards-date.json')['cards']};h=load(ROOT/'history-date.json');assert h['historySchema']==2
 ids={p.stem for p in (ROOT/'data').glob('*.json')};assert set(current)==set(precise) and len(current)==60 and len(ids)==60
 assert ids=={p.stem for p in (ROOT/'metadata').glob('*.json')};assert ids-set(current)==set()
 dates={'1900-01-01','2099-12-31'};maps={};metas={};events=0;checks=0
 for cid in sorted(ids):
  t,m=read_card(ROOT,cid);maps[cid]=t;metas[cid]=m;validate_timeline(t)
  assert m['originalSource']==original('data/'+cid+'.json')
  assert m['currentCatalog']==current.get(cid) and m['sourceCommit']==SOURCE
  doc=load(ROOT/'tools/supplemental-audit'/f'{cid}.json');assert m['supplementalAudit']['document']==doc and m['supplementalAudit']['status']=='unpublished-reconstruction'
  for d,s in projected_states(doc):assert json_equal(fold(t,d),s),(cid,d);checks+=1
  if cid in precise:assert json_equal(fold(t),{k:precise[cid][k] for k in m['canonicalFields'] if k in precise[cid]})
  events+=len(t)-1
  for d in t:dates.update((date.fromisoformat(d)+timedelta(days=n)).isoformat() for n in (-1,0,1))
  try:resolve(t,m,'2025-01-01',strict=True)
  except UncertainHistory:pass
  else:raise AssertionError('Partial baseline silently verified')
  for day,state in [(d,fold(t,d)) for d in t]:
   assert '\n' not in state.get('text','') and '<br/>' not in state.get('text','')
 cases=0;oldcases=0;old={c['id']:c for c in load(ROOT/'cards.json')['cards']};lh=load(ROOT/'history.json')['cards']
 for cid in current:
  t=maps[cid];m=metas[cid]
  for d in sorted(dates):
   assert json_equal(fold(t,d),reverse(h['cards'][str(current[cid]['dbfId'])],d)),(cid,d);cases+=1
   if d<next(iter(t)):continue
   state=copy.deepcopy(old[cid]);revs=lh.get(str(current[cid]['dbfId']),{}).get('history',[])
   matches=[e for e in revs if e.get('from','0001-01-01')<=d<e['before']];assert len(matches)<=1
   for event in matches:state.update(event['changes']);assert '__remove' not in event['changes']
   expected=project_legacy(fold(t,d),m)
   for k,v in expected.items():
    if k in state:assert json_equal(state[k],v),(cid,d,k,state[k],v)
   oldcases+=1
 # Audit every original CardID and DBF, and separately verify actual first-use
 # date plus producer for all tokens. Legacy stats stay partially verified.
 audit=load(ROOT/'tools/loe-first-use-evidence.json')
 originals={row['id']:row for row in audit['archivedIdentity']}
 tokens={row['id']:row for row in audit['tokens']}
 assert audit['schema']==1 and audit['timezone']=='Asia/Seoul'
 assert len(originals)==60 and len(tokens)==15 and set(originals)==set(current)
 assert set(tokens)=={cid for cid,x in current.items() if not x['collectible']}
 for cid,row in originals.items():
  meta=metas[cid]; timeline=maps[cid]
  assert row['dbfId']==current[cid]['dbfId'],cid
  assert row['firstUseKst']==current[cid]['releasedAt']==next(iter(timeline)),cid
  assert meta['release']=={'date':row['firstUseKst'],'status':'verified'},cid
  assert meta['releaseEvidence']['firstUseKst']==row['firstUseKst'],cid
  assert meta['releaseEvidence']['originalClientCardId']==cid,cid
  assert meta['releaseEvidence']['originalClientDbfId']==row['dbfId'],cid
  assert meta['releaseEvidence']['originalClientBuild']=='4.0.0.10833',cid
  assert meta['baselineStatus']=='partially-verified',cid
  assert resolve(timeline,meta,(date.fromisoformat(row['firstUseKst'])-timedelta(days=1)).isoformat()) is None,cid
 for cid,token in tokens.items():
  p=token['parentId'];root=token['rootCollectibleId']
  assert originals[p]['firstUseKst']==originals[root]['firstUseKst']==token['firstUseKst'],cid
  assert originals[root]['collectible'] and not originals[cid]['collectible'],cid
  assert metas[cid]['releaseEvidence']['parentId']==p,cid
  assert metas[cid]['releaseEvidence']['rootCollectibleId']==root,cid
  assert metas[p]['release']['status']=='verified',cid
 for cid in audit['sourceOnlyExcluded']:
  assert cid in metas and cid not in originals,cid
  assert metas[cid]['release']['status']=='estimated',cid
 
 # Endpoint differences are explicit, narrow and independently counted.
 differences=Counter()
 for cid,c in old.items():
  for k in set(c)|set(current[cid]):
   if not json_equal(c.get(k),current[cid].get(k)):
    assert k in {'text','releasedAt','releaseStatus'},(cid,k,current[cid].get(k),c.get(k))
    if k=='text':assert c[k]==BREAK.sub('<br></br>',current[cid][k])
    differences[k]+=1
 # Every original asset remains byte-identical; no path or relationship is replaced.
 assets=subprocess.check_output(['git','ls-tree','-r','--name-only',SOURCE,'art','golden'],cwd=ROOT,text=True).splitlines()
 transferred={'art/HERO_11bp.png','art/HERO_11bpt.png',
              'golden/cards/HERO_11bp.json','golden/cards/HERO_11bpt.json'}
 for path in assets:
  if path in transferred:
   assert not (ROOT/path).exists(),('source-only BASIC asset retained in LOE',path)
  else:
   assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT)
 for cid in current:
  assert old[cid]['art']==current[cid]['art']==precise[cid]['art'] and (ROOT/old[cid]['art']).is_file()
 report={'result':'pass','sourceCards':60,'firstUseVerified':60,'generatedFirstUseVerified':15,'runtimeCards':60,'sourceOnlyCards':0,'preciseGlobalDateCases':cases,'oldConsumerCases':oldcases,'globalDates':len(dates),'sparseEvents':events,'supplementalStateChecks':checks,'originalAssets':len(assets)-len(transferred),'currentCatalogDifferences':dict(differences),'partiallyVerifiedBaselines':60,'currentTypes':dict(Counter(fold(t)['type'] for t in maps.values()))}
 put(ROOT/'tools/date-schema-validation.json',report);print(json.dumps(report))
if __name__=='__main__':main()
