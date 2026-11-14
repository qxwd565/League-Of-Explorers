#!/usr/bin/env python3
import argparse,copy,json,subprocess
from pathlib import Path
from datetime import date,timedelta
from urllib.parse import urljoin
from date_schema import *
from legacy_projection import PHP_FIELDS,project_legacy
ROOT=Path(__file__).resolve().parents[1];SOURCE='ea2983bcc83c00fcf74ae4d4531d1fce4301e6b1';BASE_URL='https://raw.githubusercontent.com/qxwd565/League-Of-Explorers/main/'
def main(fixture=None):
 original=json.loads(subprocess.check_output(['git','show',SOURCE+':cards.json'],cwd=ROOT));catalog=load(ROOT/'cards.json');history=load(ROOT/'history.json');render=load(ROOT/'render.json');expected=copy.deepcopy(original);normalized=[]
 for c in expected['cards']:
  text=BREAK.sub('<br></br>',c['text'])
  if text!=c['text']:normalized.append(c['id'])
  c['text']=text
 # Only the 15 source-backed generated-card release confidence flags may differ
 # from the immutable pre-migration catalog; original fields remain unchanged.
 audit=load(ROOT/'tools/loe-first-use-evidence.json')
 reviewed={row['id']:row for row in audit['tokens']}
 assert len(reviewed)==15
 for c in expected['cards']:
  if c['id'] not in reviewed:continue
  record=reviewed[c['id']]
  assert c['releasedAt']==record['firstUseKst'] and c['releaseStatus']=='estimated'
  c['releaseStatus']='verified'
 assert all(row['releaseStatus']=='verified' for row in catalog['cards'])
 assert json_equal(catalog,expected),'Unreviewed current catalog changes'
 assert all(x['schema']==1 and 'historySchema' not in x for x in (catalog,history,render))
 for name in ['cards.json','history.json','render.json']:assert '__remove' not in (ROOT/name).read_text()
 dates={'1900-01-01','2099-12-31'}
 for c in catalog['cards']:
  for d in load(ROOT/'data'/f"{c['id']}.json"):dates.update((date.fromisoformat(d)+timedelta(days=n)).isoformat() for n in [-1,0,1])
 cases=[];rh={c['id']:c for c in render['cards']}
 for c in catalog['cards']:
  cid=c['id'];t,m=read_card(ROOT,cid)
  for name in ['cards.json','render.json','history.json','cards-date.json','render-date.json','history-date.json']:assert urljoin(BASE_URL+name,c['art'])==BASE_URL+c['art']
  rows=history['cards'].get(str(c['dbfId']),{}).get('history',[]);assert rows==rh[cid].get('history',[])
  for d in sorted(dates):
   want=copy.deepcopy(c);s=fold(t,d)
   if s is not None:want.update(project_legacy(s,m))
   actual=copy.deepcopy(c)
   for row in rows:
    if row.get('from','0001-01-01')<=d<row['before']:
     actual.update({k:v for k,v in row['changes'].items() if k in PHP_FIELDS})
   want={k:v for k,v in want.items() if k in PHP_FIELDS}
   assert json_equal({k:v for k,v in actual.items() if k in PHP_FIELDS},want),(cid,d)
   cases.append({'id':cid,'dbfId':c['dbfId'],'date':d,'expected':want})
 report={'result':'pass','cards':60,'approvedTextNormalizations':len(normalized),'approvedReleaseMetadata':len(reviewed),'otherCurrentChanges':0,'legacyDateCases':len(cases),'artURLChecks':360,'visibility':'Before-release old-parser fallback retained; no strict/default gating. Precise/source-only scopes remain distinct.'}
 put(ROOT/'tools/legacy-compatibility-validation.json',report)
 if fixture:put(fixture,{'catalog':catalog,'history':history,'cases':cases,'allowed':list(PHP_FIELDS),'originalCatalog':expected,'baseUrl':BASE_URL,'expectedCards':60,'originalComparison':'Pinned current source with only reviewed display newline normalization'})
 print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path);main(p.parse_args().fixture)
