# SlideSynth

## Tests

Integration test for the Docling parser:

```bash
export SLIDESYNTH_TEST_PDF=/absolute/path/to/sample.pdf
python -m unittest discover -s tests -p "test_*.py"
```

Notes:
- The integration test is skipped if `SLIDESYNTH_TEST_PDF` is not set.
- This avoids committing a binary PDF fixture into the repo.
