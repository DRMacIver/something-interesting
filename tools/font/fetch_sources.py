"""Restore the pinned licensed source cache; never use an unverified download.

Run before build_scripts.py or extend_latin.py on a fresh checkout. All URLs,
licences and hashes are recorded in data/font-sources/*.json. --check verifies
cached files without accessing the network.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen
import tarfile
import zipfile
import stat

ROOT = Path(__file__).resolve().parents[2]


def allowed_target(path):
    return any(path.is_relative_to(ROOT / folder)
               for folder in ('build/unicode-sources', 'assets/fonts/licenses'))


def valid(raw, entry):
    blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
    return (hashlib.sha256(raw).hexdigest() == entry['sha256']
            and hashlib.sha1(blob).hexdigest() == entry['git_blob_sha1'])


def restore_archive(source):
    """Extract only named, hash-verified regular files; never run archive code."""
    spec = source['archive']
    path = (ROOT / spec['path']).resolve()
    if not path.is_relative_to(ROOT / 'build/unicode-sources'):
        raise ValueError('Unexpected archive cache path')
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != spec['sha256']:
        if not spec['url'].startswith('https://'):
            raise ValueError('Source downloads must use HTTPS')
        with urlopen(spec['url'], timeout=90) as response:
            raw = response.read()
        if hashlib.sha256(raw).hexdigest() != spec['sha256']:
            raise ValueError('Source archive hash mismatch')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    zipped = zipfile.is_zipfile(path)
    with (zipfile.ZipFile(path) if zipped else tarfile.open(path)) as archive:
        for entry in source['files']:
            target = (ROOT / entry['path']).resolve()
            if not allowed_target(target):
                raise ValueError('Unexpected archive target path')
            name = entry['archive_member']
            if zipped:
                member = archive.getinfo(name)
                mode = stat.S_IFMT(member.external_attr >> 16)
                if member.is_dir() or mode not in (0, stat.S_IFREG):
                    raise ValueError('Only regular source files may be restored')
                raw = archive.read(member)
            else:
                member = archive.getmember(name)
                if not member.isfile():
                    raise ValueError('Only regular source files may be restored')
                raw = archive.extractfile(member).read()
            if not valid(raw, entry):
                raise ValueError(f'Archive member hash mismatch: {name}')
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_suffix(target.suffix + '.download')
            temporary.write_bytes(raw)
            temporary.replace(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    errors = []
    total = 0
    for manifest in sorted((ROOT / 'data/font-sources').glob('*.json')):
        source = json.loads(manifest.read_text())
        if not args.check and source.get('archive'):
            if any(not (ROOT / e['path']).exists() or not valid((ROOT / e['path']).read_bytes(), e) for e in source['files']):
                restore_archive(source)
        for entry in source.get('files', []):
            total += 1
            path = (ROOT / entry['path']).resolve()
            if not allowed_target(path):
                raise ValueError(f'Unexpected cache path: {path}')
            if path.exists() and valid(path.read_bytes(), entry):
                continue
            if args.check:
                errors.append(entry['path'])
                continue
            if not entry['url'].startswith('https://'):
                raise ValueError('Source downloads must use HTTPS')
            print('Fetching', entry['path'], flush=True)
            with urlopen(entry['url'], timeout=90) as response:
                raw = response.read()
            if not valid(raw, entry):
                raise ValueError(f'Upstream bytes no longer match pinned hashes: {entry["url"]}')
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(path.suffix + '.download')
            temporary.write_bytes(raw)
            temporary.replace(path)
    if errors:
        raise SystemExit('Missing or invalid sources:\n' + '\n'.join(errors))
    print(f'{total} source files verified')


if __name__ == '__main__':
    main()
