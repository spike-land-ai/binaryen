import glob
import os
import re

def summarize(desc):
    if not desc: return "No description provided."
    desc_clean = re.sub(r'```.*?```', '', desc, flags=re.DOTALL)
    desc_clean = re.sub(r'<!--.*?-->', '', desc_clean, flags=re.DOTALL)
    desc_clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', desc_clean)
    desc_clean = re.sub(r'[*`#_]', '', desc_clean)
    sentences = re.split(r'(?<=[.!?])\s+|' + chr(10) + r'+', desc_clean.strip())
    for s in sentences:
        s = s.strip()
        if len(s) > 15:
            s = re.sub(r'\s+', ' ', s)
            if len(s) > 80:
                s = s[:77] + "..."
            return s
    return "See issue for details."

def main():
    files = glob.glob("docs/issues/*.md")
    files.sort(key=lambda x: int(os.path.basename(x).replace('.md', '')) if os.path.basename(x).replace('.md', '').isdigit() else 0)

    kept = []
    deleted_reasons = {'duplicate': 0, 'irrelevant': 0, 'useless': 0}

    categories = {
        'bug': [],
        'optimization': [],
        'feature': [],
        'performance': [],
        'spec-compliance': [],
        'api': [],
        'meta': [],
        'test-ci': [],
        'docs': [],
        'known-limitation': []
    }

    files_to_delete = []

    for f in files:
        if f.endswith("SUMMARY.md"): continue
        
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        num_match = re.search(r'# #(\d+): (.*)', content)
        if not num_match:
            continue
            
        num = num_match.group(1)
        title = num_match.group(2).strip()
        
        desc_match = re.search(r'## Description\n+(.*?)(?=\n+## Comments|\Z)', content, re.DOTALL)
        desc = desc_match.group(1).strip() if desc_match else ""
        
        lower_content = content.lower()
        lower_desc = desc.lower()

        is_deleted = False
        if "duplicate of #" in lower_content or "closing as duplicate" in lower_content or "marked as duplicate" in lower_content:
            deleted_reasons['duplicate'] += 1
            files_to_delete.append(f)
            is_deleted = True
        elif not desc or "pure noise" in lower_content or len(re.sub(r'\s+', '', desc)) < 10:
            deleted_reasons['useless'] += 1
            files_to_delete.append(f)
            is_deleted = True
        elif "spam" in lower_content or "not about binaryen" in lower_content or "wrong repo" in lower_content:
            deleted_reasons['irrelevant'] += 1
            files_to_delete.append(f)
            is_deleted = True
            
        if is_deleted:
            continue

        scores = {k: 0 for k in categories}
        
        keywords = {
            'bug': ['crash', 'incorrect', 'error', 'bug ', 'regression', 'segfault', 'assert', 'fails to', 'panic', 'undefined behavior', 'abort'],
            'optimization': ['missed optimization', 'peephole', 'pass improvement', 'optimize ', 'inline', 'inlining', 'dead code', 'simplify', 'shrink'],
            'feature': ['feature request', 'proposal', 'implement', 'support for', 'add support', 'new instruction', 'add ', 'allow '],
            'performance': ['speed', 'size regression', 'slow', 'fast', 'performance', 'benchmark', 'O3', 'Os', 'Oz', 'compile time', 'memory leak'],
            'spec-compliance': ['spec ', 'compliance', 'validation', 'webassembly spec', 'compliant', 'valid ', 'invalid ', 'type error'],
            'api': ['c api', 'js api', 'bindings', 'export', 'header', 'binaryen.js'],
            'meta': ['tracking issue', 'epic', 'plan', 'roadmap', 'meta issue'],
            'test-ci': ['test failure', 'ci ', 'failing test', 'test suite', 'builder', 'bot ', 'flake', 'asan', 'ubsan', 'lit test', 'fuzzer'],
            'docs': ['doc ', 'readme', 'typo', 'documentation', 'comment '],
            'known-limitation': ['won\'t fix', 'limitation', 'known issue', 'design choice', 'by design']
        }
        
        search_text = (title + " " + desc).lower()
        title_text = title.lower()
        
        for cat, kw_list in keywords.items():
            for kw in kw_list:
                if kw in search_text:
                    scores[cat] += search_text.count(kw)
                # Boost if keyword is in the title!
                if kw in title_text:
                    scores[cat] += 5
        
        # Adjust overlaps
        if 'crash' in search_text or 'segfault' in search_text or 'assert' in search_text:
            scores['bug'] += 10
            
        if 'duplicate-function-elimination' in search_text:
             scores['optimization'] += 5
             
        # "spec " often means it's a feature, not necessarily compliance, but if it says "validation" then compliance
        if 'validation' in search_text or 'validator' in search_text:
             scores['spec-compliance'] += 5

        best_cat = max(scores, key=scores.get)
        if scores[best_cat] == 0:
            best_cat = 'feature'
            
        summary_line = summarize(desc)
        categories[best_cat].append((num, title, summary_line))

    total_kept = sum(len(v) for v in categories.values())
    total_deleted = sum(deleted_reasons.values())
    
    summary_content = [
        "# Binaryen Open Issues Summary\n",
        f"**Total issues reviewed:** {len(files)}",
        f"**Kept:** {total_kept}",
        f"**Deleted:** {total_deleted} ({deleted_reasons['duplicate']} duplicates, {deleted_reasons['irrelevant']} irrelevant, {deleted_reasons['useless']} useless)\n"
    ]
    
    cat_titles = {
        'bug': 'Bugs',
        'optimization': 'Optimization Opportunities',
        'feature': 'Feature Requests',
        'performance': 'Performance',
        'spec-compliance': 'Spec Compliance',
        'api': 'API Issues',
        'meta': 'Meta / Tracking',
        'test-ci': 'Test / CI',
        'docs': 'Documentation',
        'known-limitation': 'Known Limitations'
    }
    
    order = ['bug', 'optimization', 'feature', 'performance', 'spec-compliance', 'api', 'meta', 'test-ci', 'docs', 'known-limitation']
    
    for cat in order:
        items = categories[cat]
        if items:
            summary_content.append(f"## {cat_titles[cat]} ({len(items)})")
            for num, title, summary in items:
                summary = summary.replace(chr(10), ' ')
                summary_content.append(f"- #{num}: {title} — {summary}")
            summary_content.append("")
            
    with open("docs/issues/SUMMARY.md", "w", encoding="utf-8") as f:
        f.write("\n".join(summary_content))
        
    for f in files_to_delete:
        os.remove(f)
        
    print(f"Kept: {total_kept}, Deleted: {total_deleted}")

if __name__ == "__main__":
    main()
