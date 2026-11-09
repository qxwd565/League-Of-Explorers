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
 print(json.dumps({'migrated':changed,'catalogCards':len(current),'sourceCommit':SOURCE}))
if __name__=='__main__':main()
