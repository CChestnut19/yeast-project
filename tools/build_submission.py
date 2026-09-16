"""Build a traceable DRAFT submission ZIP from an explicit file inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(content):
    return hashlib.sha256(content).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8')


def selected_files(root):
    root = Path(root).resolve()
    config = json.loads((root / 'submission/package_files.json').read_text(encoding='utf-8'))
    files = config['files']
    if not isinstance(files, list) or not files or len(files) != len(set(files)):
        raise ValueError('The package inventory must contain unique file paths')
    for name in files:
        if not isinstance(name, str) or '\\' in name or ':' in name:
            raise ValueError(f'Unsafe package path: {name!r}')
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or str(relative) != name:
            raise ValueError(f'Unsafe package path: {name!r}')
        if (name.endswith(('.ipynb', '.pyc', '.pyo')) or name == 'tests/test_legacy_notebooks.py'
                or any(part.lower() in {'output', '__pycache__', 'tmp'} or part.startswith('.') for part in relative.parts)):
            raise ValueError(f'Development or generated file cannot enter submission: {name}')
        path = root / name
        if root not in path.resolve().parents or any(parent.is_symlink() for parent in [path, *path.parents] if parent != root):
            raise ValueError(f'Linked or outside package path: {name}')
        if not path.is_file():
            raise FileNotFoundError(f'Missing package input: {name}')
    if not {'submission/metadata.json', 'submission/package_files.json'}.issubset(files):
        raise ValueError('Package metadata and file inventory must be included')
    return sorted(files)


def source_info(root, allow_dirty=False):
    root = Path(root).resolve()
    if (root / '.git').exists():
        def git(*args):
            return subprocess.check_output(['git', '-C', str(root), *args], text=True, encoding='utf-8').strip()
        revision = git('rev-parse', 'HEAD')
        dirty = bool(git('status', '--porcelain', '--untracked-files=normal'))
        if dirty and not allow_dirty:
            raise ValueError('Working tree is dirty; commit first or use --allow-dirty for a draft validation build')
        return {'revision': revision, 'dirty': dirty, 'kind': 'git'}
    manifest_path = root / 'PACKAGE_MANIFEST.json'
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        files = selected_files(root)
        if set(files) != set(manifest['sha256']):
            raise ValueError('Extracted package inventory differs from its manifest')
        for name in files:
            if digest((root / name).read_bytes()) != manifest['sha256'][name]:
                raise ValueError(f'Extracted package file changed: {name}')
        return manifest['source']
    raise ValueError('Build from a Git checkout or a verified extracted submission archive')


def build_archive(root, output_dir, source):
    root, output_dir = Path(root).resolve(), Path(output_dir).resolve()
    files = selected_files(root)
    metadata = json.loads((root / 'submission/metadata.json').read_text(encoding='utf-8'))
    if metadata.get('status') != 'DRAFT':
        raise ValueError('This builder only produces DRAFT packages; final publication requires author review')
    version = metadata['version']
    if not re.fullmatch(r'\d+\.\d+\.\d+-draft\.\d+', version):
        raise ValueError('Use a draft version such as 0.1.0-draft.1')
    if not re.fullmatch(r'[0-9a-f]{40}', source.get('revision', '')) or not isinstance(source.get('dirty'), bool):
        raise ValueError('Source must identify a full Git revision and explicit dirty state')
    contents = {name: (root / name).read_bytes() for name in files}
    manifest = {
        'status': 'DRAFT', 'version': version, 'source': source,
        'license_status': metadata.get('license', {}).get('status', 'not_declared'),
        'sha256': {name: digest(content) for name, content in contents.items()},
    }
    suffix = '-working' if source['dirty'] else ''
    path = output_dir / f'yeast-project-{version}-DRAFT-{source["revision"][:7]}{suffix}.zip'
    checksum_path = path.with_suffix('.zip.sha256')
    if path.exists() or checksum_path.exists():
        raise FileExistsError(f'Archive or checksum already exists: {path}')
    output_dir.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, content in sorted({**contents, 'PACKAGE_MANIFEST.json': json_bytes(manifest)}.items()):
                entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, content, compresslevel=9)
    checksum_path.write_text(f'{digest(path.read_bytes())}  {path.name}\n', encoding='ascii')
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--allow-dirty', action='store_true', help='Identify a development snapshot explicitly as dirty')
    args = parser.parse_args(argv)
    try:
        source = source_info(ROOT, args.allow_dirty)
        print(build_archive(ROOT, args.output_dir, source))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(2, f'Submission packaging failed: {error}\n')


if __name__ == '__main__':
    main()
