"""Recreate the 1,500 IDs from the frozen official metadata, using only Python 3.
Run from any directory: python3 checks/draw_audit.py
"""
import csv
import hashlib
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 'nwerc-dp-random-audit-2026-11-23-v1'
EXPECTED = '161a0e0a2e3b953d845b780ae36a276c34d99232486d73ac1e71533aa0728fb8'

def priority(stage, problem_id):
    return hashlib.sha256(f'{SEED}|{stage}|{problem_id}'.encode()).hexdigest()

def family_name(title):
    title = title.casefold().strip()
    version = r'\s*\((?:the )?(?:very |extra |super )?(?:easy|medium|normal|hard|simplified|advanced)(?:er|est)?(?:[^()]*(?:version|edition)|\s*)\)\s*$'
    return ' '.join(re.sub(version, '', title).split())

def draw():
    families = defaultdict(list)
    with (ROOT/'assets/audit-frame.csv').open(encoding='utf-8') as f:
        for row in csv.DictReader(f):
            assert 'dp' in row['official_tags'].split('|') and 800 <= int(row['rating']) <= 3000
            families[(row['start_utc_seconds'],family_name(row['title']))].append(row)
    bands = defaultdict(list)
    for family in families.values():
        rep = min(family,key=lambda row:priority('representative',row['id']))
        bands[int(rep['rating'])].append(rep['id'])
    count = 1500
    size = len(families)
    quotas = {r:count*len(b)//size for r,b in bands.items()}
    by_remainder = sorted(bands,key=lambda r:(-(count*len(bands[r])%size),r))
    for r in by_remainder[:count-sum(quotas.values())]:
        quotas[r] += 1
    return [k for r in sorted(bands) for k in sorted(bands[r],key=lambda k:priority('draw',k))[:quotas[r]]]

if __name__ == '__main__':
    ids = draw()
    with (ROOT/'assets/dp-audit.csv').open(encoding='utf-8') as f:
        published = [row['problem'] for row in csv.DictReader(f)]
    digest = hashlib.sha256('\n'.join(ids).encode()).hexdigest()
    assert ids == published and len(set(ids)) == 1500 and digest == EXPECTED
    print(f'{len(ids)} published IDs match the seeded draw. SHA-256 {digest}')
