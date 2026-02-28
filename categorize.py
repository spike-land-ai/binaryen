import glob
import os
import re
from collections import defaultdict

files = glob.glob("docs/issues/*.md")
files.sort(key=lambda x: int(os.path.basename(x).replace('.md', '')) if os.path.basename(x).replace('.md', '').isdigit() else 0)

kept = []
deleted = []

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

stats = {'duplicate': 0, 'irrelevant': 0, 'useless': 0}

for f in files:
    if f.endswith("SUMMARY.md"): continue
    
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # parse
    num_match = re.search(r'# #(\d+): (.*)', content)
    if not num_match:
        # try fallback
        base = os.path.basename(f).replace('.md', '')
        num = base
        title = "Unknown"
    else:
        num = num_match.group(1)
        title = num_match.group(2).strip()
    
    desc_match = re.search(r'## Description\n+(.*?)\n+## Comments', content, re.DOTALL)
    if desc_match:
        desc = desc_match.group(1).strip()
    else:
        desc = ""
        
    lower_content = content.lower()
    
    # check delete
    if not desc or "pure noise" in lower_content or len(desc) < 5:
        deleted.append((f, 'useless'))
        stats['useless'] += 1
        continue
        
    if "duplicate of" in lower_content or "closing as duplicate" in lower_content or "is a duplicate" in lower_content:
        deleted.append((f, 'duplicate'))
        stats['duplicate'] += 1
        continue
        
    if "spam" in lower_content or "not about binaryen" in lower_content or "wrong repo" in lower_content:
        deleted.append((f, 'irrelevant'))
        stats['irrelevant'] += 1
        continue
        
    # Categorize
    cat = 'feature' # default
    if re.search(r'\b(crash|incorrect|regression|error|fix|bug|segfault|assert|fails?)\b', lower_content):
        cat = 'bug'
    if re.search(r'\b(missed optimization|peephole|pass improvement|optimize|inline|inlining)\b', lower_content):
        cat = 'optimization'
    if re.search(r'\b(speed|size|slow|fast|performance|benchmark|O3|Os)\b', lower_content):
        cat = 'performance'
    if re.search(r'\b(spec|compliance|validation|webassembly spec|compliant|valid)\b', lower_content):
        cat = 'spec-compliance'
    if re.search(r'\b(api|c api|js api|bindings)\b', lower_content):
        cat = 'api'
    if re.search(r'\b(tracking|epic|plan|roadmap|meta)\b', lower_content):
        cat = 'meta'
    if re.search(r'\b(test|ci|failing|failure|suite|builder|bot|flake|asan|ubsan)\b', lower_content):
        cat = 'test-ci'
    if re.search(r'\b(doc|readme|typo|documentation)\b', lower_content):
        cat = 'docs'
    if re.search(r'\b(won\'t fix|limitation|known limitation)\b', lower_content):
        cat = 'known-limitation'
        
    categories[cat].append({'num': num, 'title': title})

print(f"Total: {len(files)}, Kept: {sum(len(v) for v in categories.values())}, Deleted: {len(deleted)}")
for cat, items in categories.items():
    print(f"{cat}: {len(items)}")

