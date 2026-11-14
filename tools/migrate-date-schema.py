#!/usr/bin/env python3
"""Deterministic pinned originals plus separately labeled audited reconstruction."""
import copy,json,subprocess
from pathlib import Path
from date_schema import *
ROOT=Path(__file__).resolve().parents[1]
SOURCE='ea2983bcc83c00fcf74ae4d4531d1fce4301e6b1'
def original(path):
 try:return json.loads(subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT))
 except subprocess.CalledProcessError:raise RuntimeError('Pinned source missing; require checkout fetch-depth: 0')
def main():
 current={c['id']:c for c in original('cards.json')['cards']};evidence=load(ROOT/'tools/loe-client-evidence.json');changed=0
 for path in sorted((ROOT/'data').glob('*.json')):
  cid=path.stem;doc=load(path)
  if 'card' not in doc:
   validate_timeline(doc);assert (ROOT/'metadata'/path.name).exists();continue
  source=original('data/'+path.name);assert doc==source
  supplemental=load(ROOT/'tools/supplemental-audit'/path.name)
  timeline,meta=migrate_document(supplemental,current.get(cid),SOURCE)
  meta['originalSource']=source
  now=fold(timeline);old=current.get(cid,source['card'])
  meta['legacyMechanicsConvention']={'present':'mechanics' in old,'original':old.get('mechanics',[]),'canonicalBaseline':now['mechanics']}
  meta['supplementalAudit']={'status':'unpublished-reconstruction','source':'tools/supplemental-audit/'+path.name,'document':supplemental,'meaning':'Explicit source-backed reconstruction input, not the pinned original.'}
  meta['catalogMembership']=cid in current
  meta['currentOnlyFields']=sorted(set(old)-set(meta['canonicalFields'])-{'releasedAt','releaseStatus'})
  meta['availabilityScope']='Korean ordinary constructed-match use, including generated powers; excludes preload and adventure-only use.'
  meta['confidenceNote']='Partial verification: numeric/taxonomy and listed gameplay changes verified against bounded archives; undated Korean display/name/rarity/class changes are retained as observations, not invented dates. No strict/default hiding.'
  meta['dateRecheckEvidence']='tools/loe-date-recheck.json'
  meta['undatedEvidence']={'source':'tools/loe-client-evidence.json','limitations':'tools/loe-known-unmodeled-intervals.json'}
  meta['historicalObservations']=[];prior=None
  for b in evidence['builds']:
   if cid not in b['cards']:continue
   value=b['cards'][cid]
   if value!=prior:meta['historicalObservations'].append({'build':b['build'],'source':b['source'],**value,'dateStatus':'Client observation only; not asserted Korean server-live date'});prior=value
   else:meta['historicalObservations'][-1]['lastObservedBuild']=b['build']
  if source['card'].get('rarity','ABSENT') is None:meta['rarityPresenceEvidence']={'status':'unknown','value':None}
  put(ROOT/'metadata'/path.name,meta);put(path,timeline);changed+=1

 # Release-day audit is separately sourced and must be reproducible even
 # when this script starts from pinned original wrappers in a clean clone.
 # Never rewrite the pinned originalSource/currentCatalog or any gameplay data.
 audit=load(ROOT/'tools/loe-first-use-evidence.json')
 assert audit['schema']==1 and audit['timezone']=='Asia/Seoul'
 assert audit['archive']['build']=='4.0.0.10833'
 assert len(audit['archivedIdentity'])==60 and len(audit['tokens'])==15
 identifiers={row['id']:row for row in audit['archivedIdentity']}
 assert set(identifiers)==set(current)
 tokens={row['id']:row for row in audit['tokens']}
 assert len(tokens)==15 and set(tokens)<=set(identifiers)
 assert set(tokens)=={cid for cid,c in current.items() if not c['collectible']}
 wing_dates={v['date']:v['sources'] for v in audit['releaseSources'].values()
             if isinstance(v,dict) and 'date' in v}
 assert set(wing_dates)=={'2015-11-13','2015-11-20','2015-12-04','2015-12-11'}
 for cid in sorted(identifiers):
  row=identifiers[cid];original_card=current[cid]
  assert row['dbfId']==original_card['dbfId'] and row['collectible']==original_card['collectible'],cid
  assert row['firstUseKst']==original_card['releasedAt'],cid
  assert row['firstUseKst'] in wing_dates,cid
  path=ROOT/'metadata'/f'{cid}.json'
  meta=load(path)
  assert meta['currentCatalog']==original_card and meta['sourceCommit']==SOURCE,cid
  timeline=load(ROOT/'data'/f'{cid}.json')
  assert list(timeline)[0]==row['firstUseKst'],cid
  assert meta['release']['date']==row['firstUseKst'],cid
  assert meta['baselineStatus']=='partially-verified',cid
  if cid in tokens:
   token=tokens[cid]
   assert meta['release']['status'] in ('estimated','verified'),cid
   assert token['statusBefore']=='estimated' and token['statusAfter']=='verified'
   assert token['dbfId']==row['dbfId'] and token['firstUseKst']==row['firstUseKst'],cid
   assert token['rootCollectibleId'] in identifiers and token['parentId'] in identifiers,cid
   parent=identifiers[token['parentId']]
   root=identifiers[token['rootCollectibleId']]
   assert root['collectible'] and not row['collectible'],cid
   assert parent['firstUseKst']==root['firstUseKst']==row['firstUseKst'],cid
   meta['release']['status']='verified'
   meta['releaseEvidence']={
    'firstUseKst':row['firstUseKst'],
    'timezone':'Asia/Seoul',
    'evidenceType':'In-game generation/selection from wing-unlocked original parent',
    'originalClientBuild':'4.0.0.10833',
    'originalClientCardId':cid,
    'originalClientDbfId':row['dbfId'],
    'clientArchive':'tools/loe-first-use-evidence.json',
    'clientArchiveSha':'c56bf29b116e57fd8cdf4382e27d109b72b29e12',
    'parentId':token['parentId'],
    'rootCollectibleId':token['rootCollectibleId'],
    'parentAction':token['relation'],
    'wingReleaseSources':wing_dates[row['firstUseKst']],
    'cardAndParentSources':[audit['tokenSources'][key] for key in token['sourceRefs']],
    'criterion':'Earliest playable or generatable on Korean wing opening, never client import',
    'limitations':'Actual generating effect/parent unlock and CardID verified; entire first stats and text not fully certified.'
   }
   meta['confidenceNote']='First possible generated-card use date corroborated against Korean wing unlock, parent generation and original 2015 CardID/DBF. Baseline gameplay stats remain partially verified.'
  else:
   assert meta['release']['status']=='verified' and row['collectible'],cid
   meta['releaseEvidence']={
    'firstUseKst':row['firstUseKst'],
    'timezone':'Asia/Seoul',
    'evidenceType':'Korean adventure wing unlock and collectible/class-challenge reward',
    'originalClientBuild':'4.0.0.10833',
    'originalClientCardId':cid,
    'originalClientDbfId':row['dbfId'],
    'clientArchive':'tools/loe-first-use-evidence.json',
    'clientArchiveSha':'c56bf29b116e57fd8cdf4382e27d109b72b29e12',
    'wingReleaseSources':wing_dates[row['firstUseKst']],
    'rewardMappingSources':audit['releaseSources']['rewardMapping'],
    'criterion':'First collectible availability on Korean release date; not prior client preload',
    'limitations':'First available date only; baseline gameplay stats and wording remain partially verified.'
   }
   meta['confidenceNote']='First Korean collectible use date and 2015 CardID/DBF independently cross-checked. Original stat and text baselines remain partially verified.'
  put(path,meta)
 assert all(load(ROOT/'metadata'/f'{cid}.json')['release']['status']=='verified' for cid in identifiers)
 for cid in audit['sourceOnlyExcluded']:
  assert cid not in identifiers and load(ROOT/'metadata'/f'{cid}.json')['release']['status']=='estimated',cid
 
 print(json.dumps({'migrated':changed,'catalogCards':len(current),'sourceCommit':SOURCE}))
if __name__=='__main__':main()
