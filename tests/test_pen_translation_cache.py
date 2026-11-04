"""Cached builds retain exact pen pixels and reports, including after corruption."""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]


def test_real_translation_cache_is_exact_and_reports_are_not_shared(tmp_path,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from pen_translate import translate,Settings
 from pen_translation_cache import cached_translation
 uncached=getattr(translate,'__wrapped__',translate)
 mask=np.zeros((64,64),dtype=bool);mask[10:54,10:54]=True;mask[20:44,20:44]=False
 calls=[]
 def compute(mask,settings=Settings()):
  calls.append(1);return uncached(mask,settings)
 cached=cached_translation(compute,ROOT/'tools/font/pen_translate.py',tmp_path)
 settings=Settings(strength=1.7,seed=19)
 expected_image,expected_report=uncached(mask,settings)
 image,report=cached(mask,settings)
 assert np.array_equal(image,expected_image) and report==expected_report
 report['settings']['seed']=-1;image.paste(0,(0,0,image.width,image.height))
 image,report=cached(mask,settings)
 assert len(calls)==1 and np.array_equal(image,expected_image) and report==expected_report
 monkeypatch.setenv('DAD_DISABLE_PEN_CACHE','1')
 image,report=cached(mask,settings)
 assert len(calls)==2 and np.array_equal(image,expected_image) and report==expected_report


def test_cache_invalidates_for_pixels_settings_and_implementation(tmp_path,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from pen_translate import Settings
 from pen_translation_cache import cached_translation
 from dataclasses import asdict
 calls=[];implementation=tmp_path/'implementation.py';implementation.write_text('version1')
 def compute(mask,settings=Settings()):
  calls.append(1);return Image.fromarray(np.uint8(~mask)*255),{'settings':asdict(settings)}
 mask=np.eye(8,dtype=bool);cached=cached_translation(compute,implementation,tmp_path/'cache')
 cached(mask);cached(mask.copy());assert len(calls)==1
 cached(np.flip(mask,axis=1));assert len(calls)==2
 cached(mask,Settings(seed=22));assert len(calls)==3
 implementation.write_text('version2');cached=cached_translation(compute,implementation,tmp_path/'cache')
 cached(mask);assert len(calls)==4


def test_corrupted_or_unwritable_cache_recomputes(tmp_path,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from pen_translate import Settings
 from pen_translation_cache import cached_translation
 from dataclasses import asdict
 calls=[]
 def compute(mask,settings=Settings()):
  calls.append(1);return Image.fromarray(np.uint8(~mask)*255),{'settings':asdict(settings)}
 cached=cached_translation(compute,__file__,tmp_path/'cache');mask=np.eye(8,dtype=bool)
 cached(mask);entry=next((tmp_path/'cache').rglob('*.npz'))
 entry.write_bytes(b'interrupted download')
 cached(mask);assert len(calls)==2
 with np.load(entry,allow_pickle=False) as data:
  pixels=data['pixels'].copy();report=data['report'];digest=data['digest']
 pixels[0,0]^=255
 np.savez_compressed(entry,pixels=pixels,report=report,digest=digest)
 cached(mask);assert len(calls)==3
 entry.write_bytes(entry.read_bytes()[:50])
 cached(mask);assert len(calls)==4
 blocked=tmp_path/'not-a-directory';blocked.write_text('occupied')
 cached=cached_translation(compute,__file__,blocked)
 image,_=cached(mask);assert len(calls)==5 and np.array_equal(image,np.uint8(~mask)*255)


# A narrowly pinned equivalence transition may read, never rewrite, legacy NPZs.
import importlib.util
import sys
import hashlib
import json
from dataclasses import asdict
import pytest
sys.path.insert(0,str(ROOT/'tools/font'))
import pen_translation_cache as newcache
import pen_translate as newpen
STAGE=ROOT/'output/font-review/final-checks/cropped-holes-staging'

def _load_archived_pen_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module
 spec.loader.exec_module(module);return module

oldcache=_load_archived_pen_module('archived_pen_cache_for_equivalence',STAGE/'original-pen_translation_cache.py')
oldpen=_load_archived_pen_module('archived_pen_kernel_for_equivalence',STAGE/'original-pen_translate.py')
oldcompute=oldpen.translate.__wrapped__
newcompute=newpen.translate.__wrapped__
pins=json.loads((STAGE/'pins.json').read_text())
assert hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest()==pins['newPenSha256']
assert hashlib.sha256((ROOT/'tools/font/pen_translation_cache.py').read_bytes()).hexdigest()==pins['newCacheModuleSha256']
assert hashlib.sha256((STAGE/'original-pen_translate.py').read_bytes()).hexdigest()==pins['oldPenSha256']
assert hashlib.sha256((STAGE/'original-pen_translation_cache.py').read_bytes()).hexdigest()==pins['oldCacheModuleSha256']
@pytest.fixture(autouse=True)
def empty_receipts():
 newcache._MIGRATION_RECEIPTS.clear()
 yield
 newcache._MIGRATION_RECEIPTS.clear()


@pytest.fixture
def pair(tmp_path,monkeypatch):
 monkeypatch.delenv('DAD_DISABLE_PEN_CACHE',raising=False)
 calls=[]
 def compute(mask,settings=newpen.Settings()):
  calls.append(1);return newcompute(mask,settings)
 old=oldcache.cached_translation(oldcompute,STAGE/'original-pen_translate.py',tmp_path)
 new=newcache.cached_translation(compute,ROOT/'tools/font/pen_translate.py',tmp_path)
 mask=np.zeros((48,48),bool);mask[5:43,5:43]=True;mask[16:32,16:32]=False
 return old,new,mask,calls,tmp_path,compute


def test_migration_exact_npz_fresh_results_and_receipt(pair):
 old,new,mask,calls,directory,_=pair
 before=old(mask);legacy=next(directory.rglob('*.npz'));raw=legacy.read_bytes()
 image,report=new(mask)
 assert calls==[] and np.array_equal(image,before[0]) and report==before[1]
 paths=list(directory.rglob('*.npz'));assert len(paths)==1 and paths[0].read_bytes()==raw
 receipts=newcache.migration_receipts();assert len(receipts)==1
 receipt=next(iter(receipts.values()))
 assert receipt['oldSourceSha256']==pins['oldPenSha256'] and receipt['newSourceSha256']==pins['newPenSha256']
 assert receipt['oldCacheModuleSha256']==pins['oldCacheModuleSha256']
 assert receipt['newCacheModuleSha256']==pins['newCacheModuleSha256']
 assert receipt['npzSha256']==hashlib.sha256(raw).hexdigest()
 report['settings']['seed']=-1;image.paste(0,(0,0,image.width,image.height))
 image,report=new(mask);assert np.array_equal(image,before[0]) and report==before[1] and calls==[]
 assert legacy.read_bytes()==raw
 receipts[receipt['newKey']]['environment']['libraries']['numpy']='poison'
 assert newcache.migration_receipts()[receipt['newKey']]['environment']['libraries']['numpy']!='poison'
 assert len(list(directory.rglob('*.npz')))==1 and not (directory/'migration-receipts').exists()


def test_future_source_hash_cannot_migrate(pair):
 old,_,mask,calls,directory,compute=pair;old(mask)
 source=directory/'future.py';source.write_bytes((ROOT/'tools/font/pen_translate.py').read_bytes()+b'\n')
 newcache.cached_translation(compute,source,directory)(mask)
 assert calls==[1] and not (directory/'migration-receipts').exists() and newcache.migration_receipts()=={}


@pytest.mark.parametrize('mutation',['mask','settings','platform','library','old-source','old-cache'])
def test_namespace_mismatch_never_migrates(pair,monkeypatch,mutation):
 old,new,mask,calls,directory,compute=pair
 if mutation=='old-source':
  p=directory/'old-source.py';p.write_bytes((STAGE/'original-pen_translate.py').read_bytes()+b'\n');old=oldcache.cached_translation(oldcompute,p,directory)
 if mutation=='old-cache':
  p=directory/'old-cache.py';p.write_bytes((STAGE/'original-pen_translation_cache.py').read_bytes()+b'\n');other=_load_archived_pen_module('cropped_different_old_cache',p);old=other.cached_translation(oldcompute,STAGE/'original-pen_translate.py',directory)
 old(mask)
 if mutation=='mask':mask=mask.copy();mask[1,1]=True
 if mutation=='platform':
  monkeypatch.setattr(newcache.sys,'platform','unmatched-platform');new=newcache.cached_translation(compute,ROOT/'tools/font/pen_translate.py',directory)
 if mutation=='library':
  version=newcache.version;monkeypatch.setattr(newcache,'version',lambda name:version(name)+'-different');new=newcache.cached_translation(compute,ROOT/'tools/font/pen_translate.py',directory)
 if mutation=='settings':new(mask,newpen.Settings(seed=999))
 else:new(mask)
 assert calls==[1] and not (directory/'migration-receipts').exists() and newcache.migration_receipts()=={}


@pytest.mark.parametrize('mutation',['truncated','digest','settings'])
def test_invalid_legacy_recomputes_without_rewriting_legacy(pair,mutation):
 old,new,mask,calls,directory,_=pair;old(mask);legacy=next(directory.rglob('*.npz'))
 if mutation=='truncated':legacy.write_bytes(legacy.read_bytes()[:40])
 else:
  with np.load(legacy,allow_pickle=False) as stored:pixels=stored['pixels'];report=str(stored['report'].item());digest=str(stored['digest'].item())
  if mutation=='digest':pixels=pixels.copy();pixels[0,0]^=255
  else:
   r=json.loads(report);r['settings']['seed']=999;report=newcache.canonical(r);digest=hashlib.sha256(pixels.tobytes()+report.encode()).hexdigest()
  np.savez_compressed(legacy,pixels=pixels,report=report,digest=digest)
 raw=legacy.read_bytes();image,report=new(mask)
 assert calls==[1] and legacy.read_bytes()==raw and not (directory/'migration-receipts').exists() and newcache.migration_receipts()=={}
 expected,expected_report=newcompute(mask);assert np.array_equal(image,expected) and report==expected_report


def test_disabled_cache_cannot_migrate(pair,monkeypatch):
 old,new,mask,calls,directory,_=pair;old(mask)
 monkeypatch.setenv('DAD_DISABLE_PEN_CACHE','1');new(mask)
 assert calls==[1] and len(list(directory.rglob('*.npz')))==1 and not (directory/'migration-receipts').exists() and newcache.migration_receipts()=={}


def test_legacy_readthrough_never_writes_files(pair,monkeypatch):
 old,new,mask,calls,directory,_=pair;old(mask);legacy=next(directory.rglob('*.npz'));raw=legacy.read_bytes()
 def forbidden(*args,**kwargs):raise AssertionError('legacy hit attempted file write')
 monkeypatch.setattr(newcache.os,'replace',forbidden)
 monkeypatch.setattr(newcache.tempfile,'NamedTemporaryFile',forbidden)
 image,report=new(mask);expected,expected_report=newcompute(mask)
 assert calls==[] and legacy.read_bytes()==raw
 assert np.array_equal(image,expected) and report==expected_report
 assert len(list(directory.rglob('*.npz')))==1 and len(newcache.migration_receipts())==1


def test_true_cache_miss_writes_current_namespace(pair):
 _,new,mask,calls,directory,_=pair
 image,report=new(mask)
 assert calls==[1] and newcache.migration_receipts()=={}
 entries=list(directory.rglob('*.npz'));assert len(entries)==1
 environment=dict(source=pins['newPenSha256'],cache=pins['newCacheModuleSha256'],
  python=newcache.sys.version,platform=newcache.sys.platform,
  libraries={name:newcache.version(name) for name in ('numpy','scipy','scikit-image','Pillow')})
 parameters=newcache.canonical(dict(shape=mask.shape,settings=asdict(newpen.Settings()))).encode()
 key=hashlib.sha256(newcache.canonical(environment).encode()+b'\0'+parameters+b'\0'+np.packbits(mask).tobytes()).hexdigest()
 assert entries[0]==directory/key[:2]/(key+'.npz')
 again,again_report=new(mask);assert calls==[1] and np.array_equal(image,again) and report==again_report


def test_cached_base_report_has_no_engine_hash(pair):
 old,new,mask,calls,directory,_=pair;_,before=old(mask);_,after=new(mask)
 assert before==after
 assert not any('sha' in key.lower() or 'engine' in key.lower() or 'cache' in key.lower() for key in before)
