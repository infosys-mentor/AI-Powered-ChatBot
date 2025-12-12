"""
core.docstring_engine.generator
Generate Google-style baseline docstrings given parser metadata.

Generator is non-destructive: returns docstring text but does not modify code files.
"""

from typing import Dict, List, Optional


def _arg_type_str(arg: Dict) -> str:
    ann = arg.get("annotation")
    if ann:
        return ann
    return "TYPE"


def _format_args_section(args: List[Dict]) -> str:
    if not args:
        return ""
    lines = ["Args:"]
    for a in args:
        name = a.get("name")
        typ = _arg_type_str(a)
        lines.append(f"    {name} ({typ}): DESCRIPTION.")
    return "\n".join(lines)


def _format_returns_section(returns: Optional[str], has_return_statements: bool) -> str:
    if returns:
        typ = returns
    elif has_return_statements:
        typ = "TYPE"
    else:
        return ""
    return f"Returns:\n    {typ}: DESCRIPTION."


def _format_raises_section(raises: List[str]) -> str:
    if not raises:
        return ""
    lines = ["Raises:"]
    for r in raises:
        lines.append(f"    {r}: DESCRIPTION.")
    return "\n".join(lines)


def generate_google_docstring(func_meta: Dict) -> str:
    """
    Given metadata for a function (from parser), produce a Google-style docstring string.
    """
    name = func_meta.get("name", "<func>")
    short_summary = f"Short description of `{name}`."
    args = func_meta.get("args", [])
    returns = func_meta.get("returns")
    raises = func_meta.get("raises", [])
    yields = func_meta.get("yields", False)

    # Quick heuristic: if returns annotation or presence of return-related nodes exist
    has_return = bool(returns) or func_meta.get("complexity", 0) >= 0 and True  # keep safe
    # Better: check original docstring presence of return is not available here, so use returns + yields flag
    if yields:
        returns_text = "Yields:\n    TYPE: DESCRIPTION."
    else:
        returns_text = _format_returns_section(returns, has_return)

    parts = [short_summary, ""]
    args_section = _format_args_section(args)
    if args_section:
        parts.append(args_section)
        parts.append("")

    if returns_text:
        parts.append(returns_text)
        parts.append("")

    raises_section = _format_raises_section(raises)
    if raises_section:
        parts.append(raises_section)
        parts.append("")

    # join and ensure trailing newline
    doc = "\n".join(parts).strip() + "\n"
    # Wrap with triple quotes
    return '"""' + doc + '"""'
