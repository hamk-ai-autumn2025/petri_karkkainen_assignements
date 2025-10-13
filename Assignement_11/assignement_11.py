#!/usr/bin/env python3
"""
generate_article.py

Generates a scientific-article draft in Markdown from a user-provided topic.
Creates APA-style in-text citation placeholders and a reference list.
Tries to convert Markdown -> PDF using pandoc if available.

Usage: python generate_article.py
"""

import os
import sys
import argparse
import datetime
import random
import shutil
import subprocess
from textwrap import indent

# -----------------------
# Helpers
# -----------------------
def slugify(s):
    return "".join(c if c.isalnum() else "_" for c in s.strip())[:80]

def now_date():
    return datetime.date.today().isoformat()

def pick_refs(n, pool):
    return random.sample(pool, min(n, len(pool)))

def apa_citation(ref):
    # returns in-text APA placeholder like (Smith, 2020)
    return f"({ref['author_last']}, {ref['year']})"

def apa_reference_entry(ref):
    # basic APA-style placeholder entry
    return f"{ref['author_last']}, {ref['author_initials']}. ({ref['year']}). {ref['title']}. {ref['source']}."

# -----------------------
# Reference pool (placeholders)
# -----------------------
DEFAULT_REF_POOL = [
    {"author_last":"Smith","author_initials":"J.","year":"2020","title":"An overview of {topic}","source":"Journal of Example Studies, 12(3), 12-34"},
    {"author_last":"Johnson","author_initials":"L.","year":"2018","title":"Methods in {topic} research","source":"Methods Quarterly, 8(1), 45-67"},
    {"author_last":"Wang","author_initials":"H.","year":"2021","title":"Recent advances in {topic}","source":"International Review of {topic}, 3(2), 101-120"},
    {"author_last":"Garcia","author_initials":"M.","year":"2019","title":"Case study: {topic} applications","source":"Applied Science Letters, 5(4), 200-215"},
    {"author_last":"Khan","author_initials":"S.","year":"2017","title":"Statistical approaches for {topic}","source":"Statistics and Data, 10(2), 88-105"},
    {"author_last":"Brown","author_initials":"P.","year":"2016","title":"Challenges in {topic}","source":"Critical Reviews, 22(5), 300-320"},
    {"author_last":"Nguyen","author_initials":"T.","year":"2022","title":"Emerging trends in {topic}","source":"Future Tech, 1(1), 1-20"},
    {"author_last":"Lopez","author_initials":"R.","year":"2015","title":"Foundational theory for {topic}","source":"Theory Journal, 40(7), 400-430"},
]

# -----------------------
# Article template generation
# -----------------------
def generate_markdown(topic, author, keywords, word_target=1500, include_table=True):
    # personalize references with topic token
    pool = []
    for r in DEFAULT_REF_POOL:
        r2 = dict(r)
        r2["title"] = r2["title"].format(topic=topic)
        r2["source"] = r2["source"].replace("{topic}", topic)
        pool.append(r2)

    # choose 5 references to use inside text
    intext_refs = pick_refs(5, pool)

    # section content generator (naive templated paragraphs)
    def para(sentences=4):
        s = []
        for i in range(sentences):
            ref = random.choice(intext_refs)
            sentence = (
                f"{topic} is discussed in the literature and exhibits several important aspects. "
                f"Prior work has examined this (see {apa_citation(ref)})."
            )
            s.append(sentence)
        return " ".join(s)

    md = []
    md.append(f"# {topic}\n")
    md.append(f"**Author:** {author}  ")
    md.append(f"**Date:** {now_date()}  ")
    if keywords:
        md.append(f"**Keywords:** {', '.join(keywords)}  ")
    md.append("\n---\n")

    # Abstract
    md.append("## Abstract\n")
    md.append(f"{para(5)}\n")

    # Keywords repeated
    if keywords:
        md.append(f"**Keywords:** {', '.join(keywords)}\n")

    # Introduction
    md.append("## 1. Introduction\n")
    md.append(f"{para(6)}\n")

    # Background / Literature Review
    md.append("## 2. Background and Literature Review\n")
    md.append("### 2.1 Historical context\n")
    md.append(f"{para(4)}\n")
    md.append("### 2.2 Current state of research\n")
    md.append(f"{para(5)}\n")

    # Methods
    md.append("## 3. Methods\n")
    md.append("### 3.1 Data sources\n")
    md.append(f"{para(4)}\n")
    md.append("### 3.2 Analysis approach\n")
    md.append(f"{para(5)}\n")

    # Results
    md.append("## 4. Results\n")
    md.append("### 4.1 Main findings\n")
    md.append(f"{para(5)}\n")

    # Optionally include table
    if include_table:
        md.append("### 4.2 Example summary table\n")
        md.append("Table: Example summary of variables and outcomes.\n")
        md.append("| Variable | Description | Observed effect |\n")
        md.append("| --- | --- | --- |\n")
        md.append("| VarA | Description of VarA | Increase |\n")
        md.append("| VarB | Description of VarB | Decrease |\n")
        md.append("| VarC | Description of VarC | No change |\n")
        md.append("\n")
        md.append("The table above summarizes illustrative results and should be replaced with actual data.\n")

    # Discussion
    md.append("## 5. Discussion\n")
    md.append("### 5.1 Interpretation of results\n")
    md.append(f"{para(6)}\n")
    md.append("### 5.2 Limitations\n")
    md.append(f"{para(4)}\n")

    # Conclusions
    md.append("## 6. Conclusions\n")
    md.append(f"{para(4)}\n")

    # Acknowledgements (optional)
    md.append("## Acknowledgements\n")
    md.append("The author thanks contributors and funding sources where applicable.\n")

    # References
    md.append("## References\n")
    # build reference list entries
    # ensure deterministic ordering for stability
    used_refs = sorted(intext_refs, key=lambda x: (x['author_last'], x['year']))
    for r in used_refs:
        md.append(f"- {apa_reference_entry(r)}")

    md.append("\n---\n")
    md.append("_Note: In-text citations are APA-style placeholders. Replace placeholder references with real sources before submission._\n")

    # join and return
    return "\n".join(md)

# -----------------------
# PDF conversion attempts
# -----------------------
def try_convert_to_pdf(md_path, pdf_path):
    # Try pandoc
    if shutil.which("pandoc"):
        try:
            subprocess.run(["pandoc", md_path, "-o", pdf_path], check=True)
            return True, "Converted with pandoc."
        except subprocess.CalledProcessError as e:
            return False, f"pandoc failed: {e}"
    # Try wkhtmltopdf via markdown->html->pdf chain if wkhtmltopdf present
    if shutil.which("wkhtmltopdf"):
        try:
            html_path = md_path + ".html"
            # use python-markdown if available
            try:
                import markdown
                with open(md_path, "r", encoding="utf-8") as f:
                    mdtext = f.read()
                html = markdown.markdown(mdtext, extensions=["tables", "fenced_code"])
                with open(html_path, "w", encoding="utf-8") as fh:
                    fh.write(html)
                subprocess.run(["wkhtmltopdf", html_path, pdf_path], check=True)
                os.remove(html_path)
                return True, "Converted via wkhtmltopdf."
            except Exception as e:
                return False, f"wkhtmltopdf available but conversion failed: {e}"
        except Exception as e:
            return False, f"wkhtmltopdf attempt error: {e}"
    # No converter found
    return False, "No supported converter (pandoc or wkhtmltopdf) found. PDF not created."

# -----------------------
# CLI / main
# -----------------------
def main():
    parser = argparse.ArgumentParser(description="Generate scientific-article draft in Markdown.")
    parser.add_argument("--topic", "-t", help="Article topic", default=None)
    parser.add_argument("--author", "-a", help="Author name", default="Author Name")
    parser.add_argument("--keywords", "-k", help="Comma-separated keywords", default="")
    parser.add_argument("--output", "-o", help="Output filename base (without extension)", default=None)
    parser.add_argument("--no-table", dest="table", action="store_false", help="Do not include example table")
    args = parser.parse_args()

    # interactive prompts if topic not given
    if not args.topic:
        args.topic = input("Enter article topic: ").strip()
        if not args.topic:
            print("Topic is required. Exiting.")
            sys.exit(1)
    if not args.output:
        args.output = slugify(args.topic)

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else []
    md_text = generate_markdown(args.topic, args.author, keywords, include_table=args.table)

    md_filename = args.output + ".md"
    pdf_filename = args.output + ".pdf"

    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(md_text)

    print(f"Markdown article written to '{md_filename}'.")

    converted, message = try_convert_to_pdf(md_filename, pdf_filename)
    if converted:
        print(f"PDF created: '{pdf_filename}'. ({message})")
    else:
        print(f"PDF not created. {message}")
        print("If you want PDF output, install pandoc (recommended) or wkhtmltopdf, then re-run.")
        print(f"You can also convert manually: pandoc {md_filename} -o {pdf_filename}")

    print("Done.")

if __name__ == "__main__":
    main()
