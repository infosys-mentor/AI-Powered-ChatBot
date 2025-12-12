"""
Compute docstring coverage and write report to JSON.
"""

import json
from typing import List, Dict, Any


def compute_coverage(per_file_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    per_file_results: list from python_parser.parse_path
    returns coverage dict with per-file and aggregate stats.
    """
    report = {"files": [], "aggregate": {}}
    total_funcs = 0
    total_with_doc = 0
    total_generated = 0
    total_files = len(per_file_results)
    parsing_errors_total = 0

    for f in per_file_results:
        funcs = f.get("functions", [])
        file_total = len(funcs)
        file_with_doc = sum(1 for fn in funcs if fn.get("has_docstring"))
        # for baseline: include generated docstrings if present in metadata
        file_generated = sum(1 for fn in funcs if fn.get("generated_docstring"))
        total_funcs += file_total
        total_with_doc += file_with_doc + file_generated
        total_generated += file_generated
        parsing_errors_total += len(f.get("parsing_errors", []))
        coverage = 0.0
        if file_total:
            coverage = (file_with_doc + file_generated) / file_total * 100.0
        report["files"].append(
            {
                "file_path": f.get("file_path"),
                "total_functions": file_total,
                "functions_with_docstring": file_with_doc,
                "generated_docstrings": file_generated,
                "coverage_percent": round(coverage, 2),
                "parsing_errors": f.get("parsing_errors", []),
            }
        )

    aggregate_coverage = 0.0
    if total_funcs:
        aggregate_coverage = total_with_doc / total_funcs * 100.0

    report["aggregate"] = {
        "total_files": total_files,
        "total_functions": total_funcs,
        "functions_with_docstring": total_with_doc,
        "generated_docstrings": total_generated,
        "coverage_percent": round(aggregate_coverage, 2),
        "parsing_errors_total": parsing_errors_total,
    }
    return report


def write_report(report: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
