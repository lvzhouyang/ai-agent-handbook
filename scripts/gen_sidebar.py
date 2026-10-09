#!/usr/bin/env python3
"""根据目录结构生成 Docsify 侧边栏 _sidebar.md。"""
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = [
    ("00-preface", "前言"),
    ("01-architecture", "架构篇"),
    ("02-build", "构建篇"),
    ("03-run", "运行篇"),
    ("04-governance", "治理篇"),
    ("05-optimization", "调优篇"),
    ("06-case-study", "实践篇"),
    ("07-conclusion", "总结与展望篇"),
]
INTRO_NAMES = {"README.md"}


def chapter_no(name: str) -> int:
    match = re.search(r"第\s*(\d+)\s*章", name)
    return int(match.group(1)) if match else 0


def is_intro(path: Path) -> bool:
    return path.name in INTRO_NAMES or "导读" in path.stem


def link(path: Path, title: str, indent: int) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return f"{'  ' * indent}- [{title}](/{quote(rel)})"


def title_of(path: Path) -> str:
    if path.name == "README.md":
        return "导读"
    if not chapter_no(path.name):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return re.sub(r"\s+", " ", path.stem).strip()


def section_lines(directory: Path, indent: int) -> list[str]:
    files = sorted(directory.glob("*.md"), key=lambda p: (not is_intro(p), chapter_no(p.name), p.name))
    subdirs = sorted((d for d in directory.iterdir() if d.is_dir()), key=lambda d: chapter_no(d.name))
    lines = [link(f, title_of(f), indent) for f in files if is_intro(f)]
    for sub in subdirs:
        lines.append(f"{'  ' * indent}- {sub.name}")
        lines.extend(section_lines(sub, indent + 1))
    lines.extend(link(f, title_of(f), indent) for f in files if not is_intro(f))
    return lines


def main() -> None:
    lines = [
        "- [首页](/)",
        link(ROOT / "2026-agent-survey-report.md", "2026 Agent 开发者调研报告", 0),
    ]
    for dirname, label in SECTIONS:
        directory = ROOT / dirname
        if not directory.is_dir():
            continue
        lines.append(f"- {label}")
        lines.extend(section_lines(directory, 1))
    (ROOT / "_sidebar.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"生成 _sidebar.md，共 {len(lines)} 行")


if __name__ == "__main__":
    main()
