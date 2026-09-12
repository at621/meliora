# Contributing

From the repository root:

```bash
python -m pip install -e ".[test]"
python -m pytest --doctest-modules meliora tests
```

Input checks and calculations live in `meliora/core.py`. Keep each method's
implementation, docstring, Markdown reference and notebook
example consistent. Update the corresponding numerical or input test when its
behavior changes. The reference index is `docs/README.md`; these are ordinary
Markdown files edited directly.

The book relies on the 29 public functions. Preserve
their argument names, defaults and return forms unless a change is intentional
and the book is updated with it. Run the checks above after changing a calculation.
Run the notebook's cells when changing its examples.
