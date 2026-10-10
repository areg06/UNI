# Kursayin ashxatanq — TMM (Theory of Machines and Mechanisms), Variant 1

University coursework: kinematic analysis of a six-link linkage (synthesis, positions,
velocity & acceleration plans, A3 drawings). All user-facing text is in **Armenian**;
keep it Armenian when editing. The owner often requests changes from a phone via GitHub,
so make the change, rebuild, and commit the regenerated outputs in the same commit.

Live site (GitHub Pages, branch `main`, root): https://areg06.github.io/kursayin/

## Layout

| Path | What it is |
|---|---|
| `TMM_Variant1.html` | Main page (generated — do not hand-edit) |
| `bacatrutyun.html` | Step-by-step explanation page (generated — do not hand-edit) |
| `chertej_A3_1.*`, `chertej_A3_2.*` | The two A3 drawing sheets as SVG / PNG / PDF (generated) |
| `index.html` | Hand-written home page: choose the work (`TMM_Variant1.html`) or the explanation (`bacatrutyun.html`) |
| `source/model.py` | Task data (`DATA` dict), chosen constants (scales μ, β, α…), geometry + kinematics |
| `source/calc.py` | Rounded values "as a student writes them in the notebook" (`n()` formats with a comma decimal) |
| `source/sheet.py` | SVG of the A3 sheets: `build()` = sheet 1, `build2()` = sheet 2 (velocity plans) |
| `source/notebook.py` | Notebook (copybook) pages 10–16 filled in for this variant |
| `source/build.py` | Assembles `TMM_Variant1.html` (uses model, calc, sheet, notebook) |
| `source/explain.py` | Builds `bacatrutyun.html` |
| `source/export.py` | Exports `chertej_A3_*.svg/.png/.pdf` |

## Rebuilding (Python 3, standard library only)

```sh
cd source
python3 build.py      # -> ../TMM_Variant1.html (also writes source/variant1.html, gitignored)
python3 explain.py    # -> ../bacatrutyun.html
python3 export.py     # -> ../chertej_A3_{1,2}.svg (+ .png/.pdf only on the owner's Mac)
```

- Always edit the Python sources, never the generated HTML, then rerun the relevant script(s).
- If you change anything in `model.py`, `calc.py` or `sheet.py`, rerun **all** scripts that use it
  (build + explain, and export if the drawing changed).
- `export.py` needs Google Chrome at the macOS path for PNG/PDF. In a cloud/phone session only
  the SVGs get regenerated — say so, and tell the owner to run `python3 export.py` on the Mac
  to refresh the PNG/PDF.
- Numbers shown to the reader use a comma decimal separator (Armenian convention) via `calc.n()`.
