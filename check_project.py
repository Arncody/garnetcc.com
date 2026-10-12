"""Lightweight project sanity checker that does not require Django to be installed.
Run with: python check_project.py
"""
from pathlib import Path
import ast, sys

ROOT = Path(__file__).resolve().parent
errors=[]
for path in ROOT.rglob('*.py'):
    if any(part in {'.venv','__pycache__'} for part in path.parts):
        continue
    try:
        ast.parse(path.read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'{path}: {exc}')

required = [
    ROOT/'manage.py', ROOT/'config'/'settings.py', ROOT/'website'/'models.py',
    ROOT/'website'/'views.py', ROOT/'website'/'forms.py', ROOT/'templates'/'website'/'base.html',
    ROOT/'static'/'css'/'style.css', ROOT/'static'/'js'/'main.js'
]
for p in required:
    if not p.exists(): errors.append(f'Missing required file: {p}')

if errors:
    print('PROJECT CHECK: FAILED')
    print('\n'.join(errors))
    sys.exit(1)
print('PROJECT CHECK: OK')
print('Python AST: OK')
print('Required files: OK')
print('For the full Django check run: python manage.py check')
