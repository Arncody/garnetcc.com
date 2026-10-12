# Garnet V13 — Stability Patch

## Fixed
- Mobile menu no longer shows a second large consultation button in the header area. The header has one CTA; consultation remains available as a normal menu action.
- Mobile menu background is now nearly opaque frosted white so Hero text/images cannot bleed through.
- Mobile RTL/LTR header alignment is deterministic: Persian brand is right, controls are left; English mirrors the layout.
- Consultation modal uses stronger white glass and a controlled backdrop so page content does not bleed through the form.
- Removed the mobile horizontal overflow caused by 3 × `78vw` / `84vw` card tracks. Compact project and showcase grids now use one/two columns within the viewport.
- Added `overflow-x:hidden` safety and responsive media constraints to prevent intrinsic images/cards from widening the page.
- Added a lightweight `check_project.py` that validates Python AST and required project files without requiring Django to be installed.

## Validation
- Python AST: OK
- `compileall`: OK
- ZIP integrity: checked when packaging
- Full Django runtime check still requires the project's virtual environment with dependencies installed; run `python manage.py check` locally.
