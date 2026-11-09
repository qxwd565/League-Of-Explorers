#!/usr/bin/env python3
"""Cross-check canonical state against original IDs in every committed archive."""
import json,copy
from pathlib import Path
from date_schema import *
r=Path(__file__).resolve().parents[1];e=load(r/'tools/loe-client-evidence.json');a=load(r/'tools/loe-event-builds.json')
def ver(b):return tuple(map(int,b.split('.')))
tribes={'11':'UNDEAD','14':'MURLOC','17':'MECHANICAL','18':'ELEMENTAL','20':'BEAST','92':'NAGA'}
schools={'1':'ARCANE','2':'FIRE','3':'FROST','4':'NATURE','5':'HOLY','6':'SHADOW','7':'FEL'}
types={'4':'MINION','5':'SPELL','7':'WEAPON','10':'HERO_POWER'}
observations=0;mechanics=0
for b in e['builds']:
 assert len(b['xmlSha256'])==64 and '/blob/' in b['source']
 for cid,c in b['cards'].items():
  t,m=read_card(r,cid);state=copy.deepcopy(next(iter(t.values())))
  for day,changes in list(t.items())[1:]:
   if ver(a[cid][day])<=ver(b['build']):state=apply(state,changes)
  tags=c['Tag'];kind=types[tags['202']];assert state['type']==kind,(cid,b['build'])
  fieldtags={'cost':'48'}
  if kind=='MINION':fieldtags.update({'attack':'47','health':'45'})
  if kind=='WEAPON':fieldtags.update({'attack':'47','durability':('187' if '187' in tags else '45')})
  for field,tag in fieldtags.items():assert state[field]==int(tags.get(tag,0)),(cid,b['build'],field,state[field],tags.get(tag))
  races=([tribes[tags['200']]] if tags.get('200') in tribes else [])+(['BEAST'] if tags.get('2542')=='1' else [])
  assert state.get('races',[])==races,(cid,b['build'],races,state.get('races'))
  assert state.get('spellSchool')==schools.get(tags.get('1635')),(cid,b['build'],'school')
  observations+=1
  # Only stable intrinsically owned tag semantics are compared directly.
  # Conditional Taunt and referenced Deathrattle/Charge/Overload are excluded.
  for tag,kw in {'218':'BATTLECRY','217':'DEATHRATTLE','219':'SECRET','363':'POISONOUS'}.items():
   if tags.get(tag)=='1':assert kw in state['mechanics'],(cid,b['build'],kw)
  assert not set(state['mechanics'])&{'AURA','TRIGGER_VISUAL'}
  if cid in ['LOE_009','LOE_016','LOE_018','LOE_077','LOE_105','HERO_11bp']:assert state['mechanics']==[],cid
  if cid=='LOE_051':assert state['mechanics']==['SPELLPOWER']
  if cid=='LOE_115':assert state['mechanics']==['CHOOSE_ONE']
  if cid=='LOE_006':assert 'DEATHRATTLE' not in state['mechanics']
  if cid=='LOE_073':assert 'TAUNT' not in state['mechanics']
  mechanics+=1
report={'result':'pass','archiveBuilds':len(e['builds']),'numericTypeRaceSchoolObservations':observations,'abilityObservations':mechanics,'scope':'Overlapping bounded observations, not every historical build or server rule. Missing numeric tags in existing typed entities encode known zero defaults; they do not invent combat fields for spells/powers.'}
put(r/'tools/loe-archive-validation.json',report);print(json.dumps(report))
