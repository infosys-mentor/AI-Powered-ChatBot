import os
from core.parser.python_parser import parse_path


def test_parse_examples():
    here = os.path.join(os.path.dirname(__file__), "..", "examples")
    results = parse_path(here)
    assert isinstance(results, list)
    # at least two files present
    assert len(results) >= 2
    # total functions >= 3 (depends on example files)
    total_funcs = sum(len(f.get("functions", [])) for f in results)
    assert total_funcs >= 3
    # check fields exist
    for f in results:
        assert "file_path" in f
        for fn in f.get("functions", []):
            assert "name" in fn
            assert "has_docstring" in fn
            assert "complexity" in fn
