#!/usr/bin/env python3
"""Actual full-input host controls with fixed public 8.3 tiler, not CANN9."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
code = (ROOT / 'tools/validate_c9_packages_public_tiler.py').read_text()
code = code.replace('tools/validate_c9_packages.py', 'tools/validate_c7_full_inputs.py')
code = code.replace("+ ns['host'] + ns['hostmain']", "+ 'namespace Parent{' + ns['parenthost'] + '}namespace Candidate{' + ns['host'] + '}' + ns['hostmain']")
exec(compile(code, str(ROOT/'tools/validate_c9_packages_public_tiler.py'), 'exec'))
