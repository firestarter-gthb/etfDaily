from pathlib import Path
import os
import shutil
import zipfile

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FIGURES_DIR = BASE_DIR / "reports" / "figures"
TARGET_DIR = Path(r"C:\Users\ROB5293\antigravity\datasente")
PACKAGE_DIR = BASE_DIR / "reports" / "annual_cycle_package"

TARGET_DIR.mkdir(parents=True, exist_ok=True)
PACKAGE_DIR.mkdir(parents=True, exist_ok=True)

# 1. Copy HTML guide to website
html_source = PACKAGE_DIR / "annual_cycle_handleiding.html"
html_target = TARGET_DIR / "annual_cycle_handleiding.html"
if html_source.exists():
    shutil.copy2(html_source, html_target)
    print(f"Copied HTML guide to: {html_target}")

# 2. Copy figures
figures = [
    "annual_cycle_opex_calendar.png"
]

for fig in figures:
    src = FIGURES_DIR / fig
    if src.exists():
        shutil.copy2(src, PACKAGE_DIR / fig)
        shutil.copy2(src, TARGET_DIR / fig)
        shutil.copy2(src, TARGET_DIR / "img" / fig)
        print(f"Copied {fig} to package and website directories.")

# 3. Create the ZIP archive in TARGET_DIR
zip_output_path = TARGET_DIR / "annual_cycle_articles_and_figures.zip"

with zipfile.ZipFile(zip_output_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for file in PACKAGE_DIR.iterdir():
        if file.is_file():
            zf.write(file, arcname=file.name)
            print(f"Added {file.name} to zip archive.")

print(f"\nSuccessfully created ZIP file at: {zip_output_path}")
print(f"ZIP Size: {zip_output_path.stat().st_size / 1024:.1f} KB")

# 4. Update insights_nl.html if needed
insights_file = TARGET_DIR / "insights_nl.html"
if insights_file.exists():
    content = insights_file.read_text(encoding="utf-8")
    if "annual_cycle_handleiding.html" not in content:
        # Add post above the presidential cycle post
        new_post_html = """        <!-- Featured Annual Cycle Post -->
        <article class="blog-post" style="border: 1px solid rgba(0, 210, 255, 0.6);">
          <div class="blog-image" style="background-image: linear-gradient(135deg, #091a2e 0%, #11283d 100%);">
            <span class="blog-category-badge" style="background: #00d2ff; color: #000;">Quant Seizoensonderzoek</span>
          </div>
          <div class="blog-content">
            <div class="blog-date">6 september 2026 &bull; DataSente Quant Research</div>
            <h3>De Jaarlijkse Cyclus: 24 Expiratie-Perioden & OpEx Seizoenspatronen</h3>
            <p>
              Waarom traditionele kalendermaanden de plank misslaan. Een empirische analyse van 33 jaar S&P 500 data (SPY 1993–2026) over 12 OpEx-cycli opgedeeld in 24 twee-wekelijkse perioden.
            </p>
            <a href="annual_cycle_handleiding.html" class="blog-readmore" style="color: #00d2ff; font-weight: 700;">
              Lees het volledige onderzoek &rarr;
            </a>
          </div>
        </article>
"""
        marker = '<!-- Featured Presidential Cycle Post -->'
        if marker in content:
            content = content.replace(marker, new_post_html + "\n        " + marker)
            insights_file.write_text(content, encoding="utf-8")
            print("Successfully updated insights_nl.html with the new article card!")
        else:
            print("Marker not found in insights_nl.html")
    else:
        print("insights_nl.html already contains reference to annual_cycle_handleiding.html")
