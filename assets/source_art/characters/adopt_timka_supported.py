#!/usr/bin/env python3
"""Explicit reviewed schema2 migration; never approves art or a combat fixture."""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image
from compact_timka import ROOT, PROFILE, SOURCE_COLUMNS, require, sha, validate


def relative_file(base, relative):
    require(isinstance(relative, str), 'Expected relative file path')
    path = (base / relative).resolve()
    require(not Path(relative).is_absolute() and path.is_relative_to(base.resolve()) and path.is_file(), 'File outside evidence root or missing: ' + relative)
    return path


def adopt(kind, version, review_relative):
    require(kind in SOURCE_COLUMNS and isinstance(version, str) and 0 < len(version) <= 64 and all(c.isascii() and (c.isalnum() or c == '_') for c in version), 'Unknown kind or invalid version')
    source = ROOT / 'assets/source_art/characters/timka'
    native = source / f'{kind}_native_{version}.png'
    metadata = source / f'{kind}_manifest_{version}.json'
    review_path = relative_file(ROOT, review_relative)
    require(review_path.is_relative_to(ROOT / 'reports/phases/P06/art-preflight'), 'Review outside ART evidence directory')
    review = json.loads(review_path.read_text())
    count = len(SOURCE_COLUMNS[kind]) * 4
    require(review.get('schema') == 2 and review.get('layout_profile') == PROFILE, 'Fresh supported-layout review required')
    require(review.get('status') == 'ACCEPTABLE_SUPPORTED_LAYOUT_SOURCE_CANDIDATE', 'Source review did not accept this layout')
    require(review.get('actor_id') == 'timka' and review.get('kind') == kind, 'Wrong reviewed actor/kind')
    require(review.get('independent_of_author') is True and isinstance(review.get('reviewer'), str) and bool(review['reviewer']), 'Explicit independent reviewer required')
    require(review.get('source_only_acceptance') is True and review.get('all_required_cells_freshly_reviewed') is True, 'Fresh whole required set not reviewed')
    indices = review.get('reviewed_cell_indices')
    require(isinstance(indices, list) and all(type(x) is int for x in indices) and indices == list(range(count)), 'Wrong reviewed cell set')
    require(type(review.get('source_cells')) is int and review['source_cells'] == count, 'Wrong reviewed count')
    require('all32_freshly_reviewed' not in review, 'Legacy all32 flag cannot approve this profile')
    require(review.get('must_fix') == [], 'Unresolved source findings')
    require(all(review.get(k) is False for k in ['runtime_approval', 'phase_approval', 'full_phase_approval']), 'Source acceptance must not imply runtime/phase approval')
    for key, base in [('source_inventory_sha256', ROOT), ('review_artifacts_sha256', review_path.parent)]:
        inventory = review.get(key)
        require(isinstance(inventory, dict) and bool(inventory), 'Missing inventory ' + key)
        for relative, digest in inventory.items():
            require(sha(relative_file(base, relative)) == digest, 'Reviewed input/artifact changed: ' + relative)
    require(sha(review_path.with_suffix('.md')) == review.get('report_sha256'), 'Report changed')
    require(sha(review_path.with_name(review_path.stem + '_metrics.json')) == review.get('metrics_sha256'), 'Metrics changed')
    manifest = json.loads(metadata.read_text())
    validate(manifest, Image.open(native).convert('RGBA'))
    require(manifest.get('status') == 'CANDIDATE_SOURCE_NOT_IN_RUNTIME', 'Not a source candidate')
    require(sha(native) == manifest['sha256'] == review.get('native_sha256'), 'PNG review binding failed')
    require(sha(metadata) == review.get('manifest_sha256'), 'Manifest review binding failed')
    master = relative_file(ROOT, manifest['master'])
    require(sha(master) == manifest['master_sha256'] == review.get('master_sha256'), 'Master review binding failed')
    compaction = manifest['source_compaction']
    script = relative_file(ROOT, compaction['script'])
    require(script == (ROOT / 'assets/source_art/characters/compact_timka.py').resolve(), 'Unexpected compaction script')
    require(sha(script) == compaction.get('script_sha256'), 'Recorded compaction script digest changed')
    original_png = relative_file(ROOT, compaction['input_native'])
    original_manifest = relative_file(ROOT, compaction['input_manifest'])
    require(sha(original_png) == compaction['input_native_sha256'] and sha(original_manifest) == compaction['input_manifest_sha256'], 'Original compaction inputs changed')
    require(compaction.get('whole_cell_RGBA_unchanged') is True and compaction.get('anatomical_edit') is False, 'Whole-cell-only provenance required')
    original_image = Image.open(original_png).convert('RGBA')
    require(original_image.size == (384, 256), 'Original sheet size changed')
    for frame in manifest['frames']:
        row = frame['index'] // len(SOURCE_COLUMNS[kind])
        col = frame['source_column']
        cell = original_image.crop((col * 48, row * 64, col * 48 + 48, row * 64 + 64))
        require(hashlib.sha256(cell.tobytes()).hexdigest() == frame['rgba_sha256'], 'Selected cell differs from original whole figure')
    if kind == 'world':
        require(sha(native) == sha(original_png), 'WORLD PNG must remain byte-exact')
    for path in [native, metadata, master, original_png, original_manifest, script, relative_file(ROOT, compaction['owner_decision'])]:
        require(review['source_inventory_sha256'].get(str(path.relative_to(ROOT))) == sha(path), 'Required source missing from review inventory')
    owner = relative_file(ROOT, compaction['owner_decision'])
    require(owner == (ROOT / 'automation/decisions/P06_TIMKA_SUPPORTED_ANIMATIONS.json').resolve(), 'Canonical owner decision required')
    require(sha(owner) == compaction['owner_decision_sha256'], 'Owner decision changed')
    permission = json.loads(owner.read_text())
    require(permission.get('status') == 'APPROVED' and permission.get('kind') == 'OWNER_APPROVED_SCOPE_EXCEPTION_NOT_PHASE_ACCEPTANCE', 'Scoped owner approval required')
    require(permission.get('phase') == 'P06' and permission.get('actor_id') == 'timka' and permission.get('profile') == PROFILE, 'Owner approval does not cover this phase/actor/profile')
    budget = permission.get('source_cells')
    require(isinstance(budget, dict) and budget == {'world':32, 'action':28, 'finisher':24} and all(type(v) is int for v in budget.values()), 'Owner approval does not cover this cell budget')
    require(type(permission.get('total_source_cells')) is int and permission['total_source_cells'] == 84, 'Owner total budget differs')
    require(permission.get('excluded') == ['finish_sharp', 'finish_firearm', 'fire'], 'Owner excluded actions differ')
    require(permission.get('required_contexts') == {'peaceful_present':['world','action','implemented_disengage'], 'athletic_prime':['world','action','finisher_unarmed_blunt_environmental','implemented_clinch']}, 'Owner context requirements differ')
    require(permission.get('phase_approval') is False and permission.get('merge_approval') is False, 'Scope approval cannot substitute for phase acceptance')
    destination = ROOT / 'game/assets/art/characters/timka'
    target = destination / (kind + '_sheet.png')
    target_meta = destination / (kind + '.json')
    require(target.exists() == target_meta.exists(), 'Partial old runtime must be reconciled first')
    require(not (destination / (kind + '.sockets.json')).exists(), 'Explicit old socket migration required; never reuse stale annotations')
    backup = source / 'runtime_before_supported_v1'
    if target.exists():
        old = json.loads(target_meta.read_text())
        require(old.get('schema') == 1 and old.get('actor_id') == 'timka' and old.get('kind') == kind, 'Only explicit legacy Timka migration is supported')
        require(sha(target) == old.get('sha256') == compaction['input_native_sha256'], 'Runtime differs from selected source baseline')
        require(not (backup / target.name).exists() and not (backup / target_meta.name).exists(), 'Preserve existing migration snapshot')
    output = copy.deepcopy(manifest)
    output.update(file=target.name, status='SOURCE_ACCEPTED_RUNTIME_VALIDATION_PENDING')
    output['source_adoption'] = {'native': str(native.relative_to(ROOT)), 'sha256': sha(native),
        'manifest': str(metadata.relative_to(ROOT)), 'manifest_sha256': sha(metadata),
        'independent_source_review': str(review_path.relative_to(ROOT)), 'review_sha256': sha(review_path),
        'report_sha256': review['report_sha256'], 'packing': 'exact reviewed PNG copy; whole selected cells only'}
    output['review'] = {'independent_source_art': review['status'], 'actual_animation': 'PENDING', 'runtime_approval': False, 'phase_approval': False}
    # All validation completes before any runtime write; no live engine is used
    # during migration. Original PNG/JSON are preserved before atomic replacements.
    backup.mkdir(exist_ok=True)
    if target.exists():
        shutil.copyfile(target, backup / target.name)
        shutil.copyfile(target_meta, backup / target_meta.name)
    destination.mkdir(parents=True, exist_ok=True)
    png_temp = target.with_suffix('.png.migrating')
    json_temp = target_meta.with_suffix('.json.migrating')
    require(not png_temp.exists() and not json_temp.exists(), 'Interrupted migration must be inspected, not overwritten')
    shutil.copyfile(native, png_temp)
    json_temp.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    png_temp.replace(target)
    json_temp.replace(target_meta)
    require(sha(target) == manifest['sha256'], 'Post-migration PNG changed')
    print(json.dumps({'kind': kind, 'cells': count, 'sha256': sha(target), 'source_review_sha256': sha(review_path), 'runtime_approval': False, 'phase_approval': False}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=SOURCE_COLUMNS)
    parser.add_argument('--version', required=True)
    parser.add_argument('--review', required=True)
    args = parser.parse_args()
    adopt(args.kind, args.version, args.review)
