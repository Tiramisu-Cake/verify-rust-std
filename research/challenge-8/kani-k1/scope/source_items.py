"""Narrow top-level Rust item scan for cfg/helper forecasts, never compiler evidence."""
import re

from source_inventory import attributes, gated, predict

CFG = "#[cfg(kani_smallsort_controls)]"


def imports(body, prefix=""):
    """Expand this source's brace imports into canonical paths (no glob binding forecast)."""
    body = body.removeprefix("use ").removesuffix(";").strip()
    for part in predict.split_args(body):
        part = part.strip()
        if "{" in part:
            at = part.index("{")
            yield from imports(part[at + 1:part.rindex("}")], prefix + part[:at])
        else:
            yield prefix + part


def items(text):
    masked = predict.mask_comments_strings(text)
    result, pos = [], 0
    while pos < len(masked):
        while pos < len(masked) and (masked[pos].isspace() or masked[pos] == ";"):
            pos += 1
        if pos == len(masked):
            break
        if masked.startswith("#![", pos):
            pos = predict.matching(masked, pos + 2, "[", "]") + 1
            continue
        start = pos
        while masked.startswith("#[", pos):
            pos = predict.matching(masked, pos + 1, "[", "]") + 1
            while pos < len(masked) and masked[pos].isspace():
                pos += 1
        content = pos
        while pos < len(masked):
            char = masked[pos]
            if char in "([":
                pos = predict.matching(masked, pos, char, {"(": ")", "[": "]"}[char]) + 1
            elif char == "{":
                pos = predict.matching(masked, pos, "{", "}") + 1
                if masked[content:content + 4] == "use ":
                    continue
                if masked[pos:pos + 1] == ";":
                    pos += 1
                break
            elif char == ";":
                pos += 1
                break
            else:
                pos += 1
        body = masked[content:pos]
        macro = re.match(r"macro_rules!\s*(\w+)", body)
        fn = re.match(r"(?:pub(?:\([^)]*\))?\s+)?(?:unsafe\s+)?fn\s+(\w+)", body)
        call = re.match(r"(\w+)\s*!\s*\(", body)
        kind, name = "other", " ".join(body.split())
        if macro:
            kind, name = "macro", macro[1]
        elif fn:
            kind, name = "fn", fn[1]
        elif body.startswith("use "):
            kind, name = "use", "|".join(imports(body))
        elif call:
            kind, name = "call", "".join(body.split())
        result.append(dict(start=start, content=content, end=pos, body=body,
                           attrs=masked[start:content], kind=kind, name=name,
                           gated=gated(masked[start:content]),
                           line=text.count("\n", 0, start) + 1))
    return result


def key(item):
    return item["kind"], item["name"]


def without_cfg(text):
    return text.replace(CFG + "\n", "")


def fingerprints(text):
    """Exact non-import bodies/attrs, including literals; permit top-level comments/import regrouping."""
    tokens, leaves = [], []
    for item in items(text):
        attrs = without_cfg(text[item["start"]:item["content"]]).strip()
        if item["kind"] == "use":
            leaves.extend((x, "".join(attrs.split())) for x in imports(item["body"]))
        else:
            tokens.append((attrs, text[item["content"]:item["end"]]))
    return tokens, sorted(leaves)
