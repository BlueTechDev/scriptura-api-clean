import os
from pathlib import Path
import json

# Sample file path (update this in your environment accordingly)
output_path = Path("app/data/embedded_data/structured_wels_content.jsonl")
output_path.parent.mkdir(parents=True, exist_ok=True)

# Dictionary of section titles, URLs, and the corresponding text file content filenames
sections = [
    ("This We Believe", "https://wels.net/about-wels/what-we-believe/this-we-believe/", "this_we_believe.txt"),
    ("God’s Revelation", "https://wels.net/about-wels/what-we-believe/this-we-believe/gods-revelation/", "gods_revelation.txt"),
    ("Creation, Man, and Sin", "https://wels.net/about-wels/what-we-believe/this-we-believe/creation/", "creation_man_sin.txt"),
    ("Christ and Redemption", "https://wels.net/about-wels/what-we-believe/this-we-believe/christ-and-redemption/", "christ_redemption.txt"),
    ("Justification", "https://wels.net/about-wels/what-we-believe/this-we-believe/justification/", "justification.txt"),
    ("Good Works and Prayer", "https://wels.net/about-wels/what-we-believe/this-we-believe/good-works/", "good_works_prayer.txt"),
    ("Means of Grace", "https://wels.net/about-wels/what-we-believe/this-we-believe/means-of-grace/", "means_of_grace.txt"),
    ("Church and Ministry", "https://wels.net/about-wels/what-we-believe/doctrinal-statements/#toggle-id-2", "church_ministry.txt"),
    ("Church and State", "https://wels.net/about-wels/what-we-believe/this-we-believe/church-and-state/", "church_state.txt"),
    ("Jesus’ Return and the Judgment", "https://wels.net/about-wels/what-we-believe/this-we-believe/jesus-return/", "jesus_return_judgment.txt"),
    ("Creeds and Confessions", "https://wels.net/about-wels/what-we-believe/creeds/", "creeds_confessions.txt"),
    ("Church Fellowship", "https://wels.net/about-wels/what-we-believe/doctrinal-statements/#toggle-id-1", "church_fellowship.txt"),
    ("antichrist", "https://wels.net/about-wels/what-we-believe/doctrinal-statements/#toggle-id-6", "antichrist.txt"),
    ("abortion", "https://wels.net/about-wels/what-we-believe/doctrinal-statements/abortion/", "abortion.txt"),
    ("man_woman_roles", "https://wels.net/about-wels/what-we-believe/doctrinal-statements/#toggle-id-3","man_woman_roles.txt"),
    ("scripture", "https://wels.net/about-wels/what-we-believe/doctrinal-statements/#toggle-id-5", "scripture.txt"),
    ("lord's_supper", "https://wels.net/about-wels/what-we-believe/doctrinal-statements/#toggle-id-7", "lords_supper.txt"),
    ("homosexuality", "https://wels.net/about-wels/what-we-believe/doctrinal-statements/#toggle-id-8", "homosexuality.txt"),
    ("means_of_grace", "https://wels.net/about-wels/what-we-believe/this-we-believe/means-of-grace/", "means_of_grace.txt"),
    ("doctrinal_statements", "https://wels.net/about-wels/what-we-believe/doctrinal-statements/", "doctrinal_statements.txt"),

]

# Create the JSONL content
jsonl_lines = []
for title, url, filename in sections:
    file_path = Path(f"app/data/raw_text_sources/{filename}")
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8").strip()
        jsonl_lines.append(json.dumps({"title": title, "url": url, "content": content}))
    else:
        jsonl_lines.append(json.dumps({"title": title, "url": url, "content": "[[MISSING CONTENT]]"}))

# Write to JSONL file
with output_path.open("w", encoding="utf-8") as f:
    for line in jsonl_lines:
        f.write(line + "\n")

output_path.name
