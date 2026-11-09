#!/usr/bin/env python3
"""Reproduce committed evidence from local exact CardDefs archives; never infer dates."""
import argparse,pathlib,json,hashlib,re,xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('--archive-dir',action='append',type=pathlib.Path,required=True);args=p.parse_args()
r=pathlib.Path(__file__).resolve().parents[1];dst=r/'tools/loe-client-evidence.json';expected=json.loads(dst.read_text());ids={p.stem for p in (r/'data').glob('*.json')};files={}
for folder in args.archive_dir:
 for path in folder.glob('*CardDefs.xml'):
  with path.open() as f:head=f.read(300)
  m=re.search(r'build="(\d+)"',head)
  if m:files[m[1]]=path
count=0
for build in expected['builds']:
 path=files[build['build'].split('.')[-1]];assert hashlib.sha256(path.read_bytes()).hexdigest()==build['xmlSha256']
 cards={}
 for e in ET.parse(path).getroot():
  cid=e.get('CardID')
  if cid not in ids:continue
  cards[cid]={'name':e.findtext('./Tag[@enumID="185"]/koKR'),'rawText':e.findtext('./Tag[@enumID="184"]/koKR'),'enText':e.findtext('./Tag[@enumID="184"]/enUS')}
  for kind in ['Tag','ReferencedTag']:cards[cid][kind]={t.get('enumID'):t.get('value') for t in e if t.tag==kind and t.get('value') is not None}
 assert cards==build['cards'],build['build'];count+=len(cards)
print(json.dumps({'result':'pass','builds':len(expected['builds']),'originalIdObservations':count,'sha256Verified':True}))
