"""Tests-only lossless WOFF2 table decoding; never caches finished fonts.

FreeType supplies native decoded coordinates. FontTools canonically serializes
all expanded glyphs; original source head bytes and other tables stay exact.
Every caller receives a fresh TTFont over immutable bytes. Unsupported inputs or
changed/unavailable native libraries retain the original FontTools reader.
"""
import ctypes as C
from functools import lru_cache
import hashlib
import io
from pathlib import Path
import struct
import PIL._imagingft
from fontTools.ttLib import TTFont as _TTFont, TTLibError
from fontTools.ttLib.sfnt import SFNTWriter, SFNTReader
from fontTools.ttLib.woff2 import WOFF2LocaTable

LIBRARY_PATH=Path(PIL._imagingft.__file__).parent/'.dylibs/libfreetype.6.dylib'
# otool-confirmed bundled dependency closure; systemlib versions belong to the
# recorded platform. Match bundledversion suffixes instead ofhardcoding them.
LIBRARY_DEPENDENCIES=tuple(sorted({path for pattern in ('libfreetype*.dylib','libharfbuzz*.dylib','libbrotli*.dylib','libpng*.dylib','libz.*.dylib') for path in LIBRARY_PATH.parent.glob(pattern)}))

def _identity(path):
    try:s=Path(path).stat()
    except FileNotFoundError:return None
    return (s.st_dev,s.st_ino,s.st_ctime_ns,s.st_mtime_ns,s.st_size)

_INITIAL_LIBRARY_ID=_identity(LIBRARY_PATH)
_INITIAL_DEPENDENCY_IDS=tuple(_identity(path) for path in LIBRARY_DEPENDENCIES)
_stats={'native':0,'fallback':0}


def _watch(path):
    from font_proof_session import record_evidence
    record_evidence(path)
    # Loading is also used outside the read recorder in a catalog batch.
    import font_baseline_checks as checks
    checks.watch_evidence(path,required=False)


@lru_cache(maxsize=1)
def _library(identity):
    lib=C.CDLL(str(LIBRARY_PATH));p=C.c_void_p
    lib.FT_Init_FreeType.argtypes=[C.POINTER(p)];lib.FT_Init_FreeType.restype=C.c_int
    lib.FT_New_Memory_Face.argtypes=[p,C.POINTER(C.c_ubyte),C.c_long,C.c_long,C.POINTER(p)];lib.FT_New_Memory_Face.restype=C.c_int
    lib.FT_Load_Sfnt_Table.argtypes=[p,C.c_ulong,C.c_long,C.POINTER(C.c_ubyte),C.POINTER(C.c_ulong)];lib.FT_Load_Sfnt_Table.restype=C.c_int
    lib.FT_Done_Face.argtypes=[p];lib.FT_Done_FreeType.argtypes=[p]
    return lib


def _native_sfnt(raw,identity):
    lib=_library(identity);library=C.c_void_p();face=C.c_void_p();buffer=(C.c_ubyte*len(raw)).from_buffer_copy(raw)
    if lib.FT_Init_FreeType(C.byref(library)):raise ValueError('FreeType init failed')
    try:
        if lib.FT_New_Memory_Face(library,buffer,len(raw),0,C.byref(face)):raise ValueError('Unsupported native face')
        length=C.c_ulong(0)
        if lib.FT_Load_Sfnt_Table(face,0,0,None,C.byref(length)):raise ValueError('No native SFNT stream')
        data=(C.c_ubyte*length.value)()
        if lib.FT_Load_Sfnt_Table(face,0,0,data,C.byref(length)):raise ValueError('Native SFNT read failed')
        return bytes(data)
    finally:
        if face:lib.FT_Done_Face(face)
        lib.FT_Done_FreeType(library)


@lru_cache(maxsize=8)
def _canonical_sfnt(raw,source_sha,library_identity):
    assert hashlib.sha256(raw).hexdigest()==source_sha
    reference=_TTFont(io.BytesIO(raw),recalcBBoxes=False,recalcTimestamp=False)
    tags=set(reference.reader.keys())
    if 'glyf' not in tags or {'CFF ','CFF2','fvar','gvar'}&tags:return None
    if any(entry.transformed for tag,entry in reference.reader.tables.items() if tag not in {'glyf','loca'}):return None
    if not reference.reader.tables['glyf'].transformed:return None
    native=_TTFont(io.BytesIO(_native_sfnt(raw,library_identity)),recalcBBoxes=False,recalcTimestamp=False)
    if set(native.reader.keys())!=tags:raise ValueError('Native table inventory changed')
    original_head=reference.reader['head'];native_head=native.reader['head']
    if original_head[:8]+original_head[12:]!=native_head[:8]+native_head[12:]:raise ValueError('Native head changed outside checksum')
    tables={}
    for tag in tags-{'glyf','loca','head'}:
        tables[tag]=reference.reader[tag]
        if tables[tag]!=native.reader[tag]:raise ValueError('Native unchanged table differs: '+tag)
    # FreeType's exported stream may put the absolute glyf end in the final
    # loca sentinel. Only this exactly identified offset form is normalized.
    length=len(native.reader['glyf']);locations=native['loca'].locations
    if locations[-1]!=length:
        if locations[-1]-length!=native.reader.tables['glyf'].offset:raise ValueError('Unrecognized native loca sentinel')
        locations[-1]=length
    if any(a>b for a,b in zip(locations,locations[1:])) or any(x>length for x in locations):raise ValueError('Invalid native glyph offsets')
    native['glyf'].ensureDecompiled();native['glyf'].padding=1
    native['glyf'].indexFormat=reference['head'].indexToLocFormat
    loca=WOFF2LocaTable('loca');loca.set(locations);native['loca']=loca
    tables['glyf']=native['glyf'].compile(native);tables['loca']=native['loca'].compile(native);tables['head']=original_head
    stream=io.BytesIO();writer=SFNTWriter(stream,len(tables),reference.sfntVersion)
    for tag in sorted(tables):writer[tag]=tables[tag]
    writer.close();data=bytearray(stream.getvalue())
    # SFNTWriter adjusts the master checksum. Match the original WOFF2 reader's
    # exact head table; normal TTFont.save still computes its usual checksum.
    reader=SFNTReader(io.BytesIO(data));offset=reader.tables['head'].offset;data[offset:offset+len(original_head)]=original_head
    result=bytes(data);reader=SFNTReader(io.BytesIO(result))
    if any(reader[tag]!=value for tag,value in tables.items()):raise ValueError('Canonical table serialization changed')
    _stats['native']+=1
    return result


def evidence_ttfont(file=None,*args,**kwargs):
    # CFF/variables/collections/rawfonts/builders and stream callers retain the
    # original loader. This wrapper is imported only by assertion helpers.
    if not isinstance(file,(str,Path)) or Path(file).suffix.lower()!='.woff2' or args or kwargs.get('fontNumber',-1)!=-1:
        return _TTFont(file,*args,**kwargs)
    path=Path(file);_watch(path);before=_identity(path)
    for dependency in LIBRARY_DEPENDENCIES:_watch(dependency)
    library_before=tuple(_identity(dependency) for dependency in LIBRARY_DEPENDENCIES)
    if _identity(LIBRARY_PATH)!=_INITIAL_LIBRARY_ID or library_before!=_INITIAL_DEPENDENCY_IDS or any(value is None for value in library_before):
        _stats['fallback']+=1;return _TTFont(file,**kwargs)
    raw=path.read_bytes();assert _identity(path)==before,'Font changed during decode read'
    if raw[:4]!=b'wOF2' or raw[4:8]==b'OTTO':return _TTFont(file,**kwargs)
    try:data=_canonical_sfnt(raw,hashlib.sha256(raw).hexdigest(),library_before)
    except (OSError,ValueError,TTLibError,struct.error):data=None
    assert _identity(path)==before and tuple(_identity(dependency) for dependency in LIBRARY_DEPENDENCIES)==library_before,'Font/native library changed during decode'
    if data is None:
        _stats['fallback']+=1;return _TTFont(file,**kwargs)
    font=_TTFont(io.BytesIO(data),**kwargs);font.flavor='woff2'
    return font


def metrics():return dict(_stats,cache=_canonical_sfnt.cache_info()._asdict())
