import re
from pathlib import Path

import jinja2

REPO_ROOT = Path(__file__).resolve().parents[2]
README = REPO_ROOT / "readme.md"
TEMPLATE_DIR = REPO_ROOT / "latex"
TEMPLATE_NAME = "resume_template.tex.j2"
OUTPUT = TEMPLATE_DIR / "resume.tex"

LATEX_SPECIAL_CHARS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
LATEX_SPECIAL_RE = re.compile("|".join(re.escape(c) for c in LATEX_SPECIAL_CHARS))


def escape_latex(text):
    return LATEX_SPECIAL_RE.sub(lambda m: LATEX_SPECIAL_CHARS[m.group()], text)


def inline_markdown_to_latex(text):
    """Escape LaTeX specials, then translate the small set of Markdown
    inline syntax used in readme.md (bold, trailing hard line breaks)."""
    text = escape_latex(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r" {2,}$", r"\\\\", text, flags=re.MULTILINE)
    return text


def split_sections(body, level_marker):
    """Split body into (heading_text, section_body) chunks on lines that
    start with the given Markdown heading marker (e.g. '### ')."""
    pattern = re.compile(rf"^{re.escape(level_marker)}(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(body))
    sections = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections.append((m.group(1).strip(), body[start:end]))
    return sections


def strip_hr_and_blank(text):
    lines = [l for l in text.split("\n") if l.strip() != "---"]
    return "\n".join(lines).strip("\n")


def markdown_block_to_latex(text):
    """Render a free-form Markdown block as LaTeX paragraphs, turning each
    blank-line-delimited paragraph's internal line breaks into \\\\ so
    lines that are visually distinct in readme.md stay distinct in the PDF."""
    paragraphs = re.split(r"\n\s*\n", text.strip("\n"))
    rendered = []
    for para in paragraphs:
        lines = [inline_markdown_to_latex(l.strip()) for l in para.split("\n") if l.strip()]
        rendered.append(r"\\".join(lines))
    return "\n\n".join(rendered)


PERIOD_RE = re.compile(r"(.*?)[　\s]+((?:\d.*)?\d.*)$")


def split_name_and_period(heading):
    """'I社　2026年4月 - 現在' -> ('I社', '2026年4月 - 現在')"""
    m = PERIOD_RE.match(heading.strip())
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return heading.strip(), ""


PROJECT_TITLE_RE = re.compile(r"^(.*?)\s*\(([^()]+)\)\s*$")


def split_project_title_and_period(heading):
    """'ECサイト向け...開発 (2026年5月 - 現在)' -> (title, period)"""
    m = PROJECT_TITLE_RE.match(heading.strip())
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return heading.strip(), ""


ROLE_RE = re.compile(r"^_(.+)_$")
LABEL_LINE_RE = re.compile(r"^\*\*(.+?):\*\*\s*(.*)$")


def parse_project_body(body):
    """Turn a project's body into a list of (label, text) bullet items.
    Lines like '**課題:** ...' become labelled bullets; any remaining
    freeform lines become unlabelled bullets."""
    items = []
    for raw_line in strip_hr_and_blank(body).split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        m = LABEL_LINE_RE.match(line)
        if m:
            label, rest = m.group(1), m.group(2)
            items.append((inline_markdown_to_latex(label), inline_markdown_to_latex(rest)))
        elif line.startswith("- "):
            items.append((None, inline_markdown_to_latex(line[2:])))
        else:
            items.append((None, inline_markdown_to_latex(line)))
    return items


def parse_readme(text):
    top_sections = split_sections(text, "## ")
    section_bodies = {name: body for name, body in top_sections}

    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "職務経歴書"

    date_match = re.search(r"^_(.+?)現在_\s*$", text, re.MULTILINE)
    date = date_match.group(1).strip() if date_match else ""

    self_pr = inline_markdown_to_latex(strip_hr_and_blank(section_bodies.get("自己PR", "")))
    summary = inline_markdown_to_latex(strip_hr_and_blank(section_bodies.get("職務要約", "")))

    skills = markdown_block_to_latex(strip_hr_and_blank(section_bodies.get("経験・技術・ツール", "")))

    jobs = []
    for company_heading, company_body in split_sections(section_bodies.get("職務経歴詳細", ""), "### "):
        company, period = split_name_and_period(company_heading)
        company = inline_markdown_to_latex(company)
        period = inline_markdown_to_latex(period)

        role = ""
        body_after_role = company_body
        for raw_line in company_body.split("\n"):
            line = raw_line.strip()
            if not line:
                continue
            m = ROLE_RE.match(line)
            if m:
                role = inline_markdown_to_latex(m.group(1))
                body_after_role = company_body[company_body.index(raw_line) + len(raw_line):]
            break

        projects = []
        for project_heading, project_body in split_sections(body_after_role, "#### "):
            proj_title, proj_period = split_project_title_and_period(project_heading)
            projects.append({
                "title": inline_markdown_to_latex(proj_title),
                "period": inline_markdown_to_latex(proj_period),
                "bullets": parse_project_body(project_body),
            })

        jobs.append({
            "company": company,
            "period": period,
            "role": role,
            "projects": projects,
        })

    education = []
    for raw_line in strip_hr_and_blank(section_bodies.get("保有資格・学歴", "")).split("\n"):
        line = raw_line.strip()
        if line.startswith("- "):
            education.append(inline_markdown_to_latex(line[2:]))

    return {
        "title": escape_latex(title),
        "date": escape_latex(date),
        "self_pr": self_pr,
        "summary": summary,
        "skills": skills,
        "jobs": jobs,
        "education": education,
    }


def render(context):
    env = jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        trim_blocks=True,
        lstrip_blocks=True,
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
    )
    template = env.get_template(TEMPLATE_NAME)
    return template.render(**context)


def main():
    readme_text = README.read_text(encoding="utf-8")
    context = parse_readme(readme_text)
    tex = render(context)
    OUTPUT.write_text(tex, encoding="utf-8")
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
