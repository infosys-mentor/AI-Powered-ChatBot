"""
Streamlit app for Milestone 1:
- choose a folder
- run scan
- view per-file metadata
- view generated docstrings (Google style)
- download the aggregate report JSON
"""

import json
import os
import streamlit as st
from core.parser.python_parser import parse_path
from core.docstring_engine.generator import generate_google_docstring
from core.reporter.coverage_reporter import compute_coverage, write_report

st.set_page_config(page_title="AI Code Reviewer - Milestone 1", layout="wide")

st.title("AI Code Reviewer — Milestone 1 (Parser & Baseline Docstrings)")
st.markdown(
    "Upload / select a project folder (or enter a path). Click **Scan** to run the AST parser and generate baseline Google-style docstrings (non-destructive)."
)

col1, col2 = st.columns([3, 1])

with col2:
    st.info("How to use\n1. Select folder path\n2. Click Scan\n3. Inspect results and download JSON")
    scan_path = st.text_input("Path to scan", value="examples")
    generate_docs = st.checkbox("Generate baseline docstrings (non-destructive)", value=True)
    out_path = st.text_input("Output JSON path", value="storage/review_logs.json")
    if st.button("Scan"):
        if not os.path.exists(scan_path):
            st.error(f"Path not found: {scan_path}")
        else:
            with st.spinner("Parsing files..."):
                results = parse_path(scan_path)
                # attach generated docs
                if generate_docs:
                    for f in results:
                        for fn in f.get("functions", []):
                            if not fn.get("has_docstring"):
                                fn["generated_docstring"] = generate_google_docstring(fn)
                report = compute_coverage(results)
                # ensure output dir exists
                out_dir = os.path.dirname(out_path)
                if out_dir and not os.path.exists(out_dir):
                    os.makedirs(out_dir, exist_ok=True)
                write_report(report, out_path)
                st.success(f"Scan complete — report written to {out_path}")
                st.session_state["last_scan_results"] = results
                st.session_state["last_report"] = report

# Show summary
report = st.session_state.get("last_report")
if report:
    st.subheader("Aggregate Coverage")
    agg = report["aggregate"]
    st.metric("Coverage %", f"{agg['coverage_percent']}%")
    st.write(f"Total files: {agg['total_files']}, Total functions: {agg['total_functions']}, Generated docs: {agg['generated_docstrings']}")

# Show per-file results table
results = st.session_state.get("last_scan_results")
if results:
    st.subheader("Per-file summary")
    rows = []
    for f in results:
        rows.append({
            "file": f.get("file_path"),
            "functions": len(f.get("functions", [])),
            "parsing_errors": len(f.get("parsing_errors", [])),
            "generated_docstrings": sum(1 for fn in f.get("functions", []) if fn.get("generated_docstring")),
        })
    st.table(rows)

    st.subheader("Files (expand to inspect)")
    for f in results:
        with st.expander(f.get("file_path")):
            st.write("Imports:", f.get("imports", []))
            st.write("Parsing errors:", f.get("parsing_errors", []))
            for fn in f.get("functions", []):
                fn_title = f"{fn.get('name')}  (lines {fn.get('start_line')}–{fn.get('end_line')})"
                st.markdown(f"**{fn_title}**")
                st.write(f"Has docstring: {fn.get('has_docstring')}")
                st.write(f"Args: {[a['name'] for a in fn.get('args', [])]}")
                st.write(f"Returns: {fn.get('returns')}")
                st.write(f"Complexity (heuristic): {fn.get('complexity')}, nesting: {fn.get('nesting_depth')}")
                if fn.get("has_docstring"):
                    st.code(fn.get("docstring") or "—")
                if fn.get("generated_docstring"):
                    st.subheader("Generated (Google-style) docstring")
                    st.code(fn.get("generated_docstring"))
    # Download button for report
    report_json = json.dumps(st.session_state.get("last_report", {}), indent=2)
    st.download_button("Download report JSON", data=report_json, file_name="review_report.json", mime="application/json")
else:
    st.info("No scan run yet. Enter a path and hit Scan.")
