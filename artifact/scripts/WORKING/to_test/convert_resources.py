#!/usr/bin/env python3
"""
Convert resource markdown files to HTML
"""

from pathlib import Path
import re


def markdown_to_html(md_text):
    """Convert markdown to HTML with basic formatting"""
    html = md_text

    # Convert headers
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Convert bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)

    # Convert italic
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

    # Convert links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Convert unordered lists
    lines = html.split('\n')
    processed_lines = []
    in_list = False

    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                processed_lines.append('<ul>')
                in_list = True
            item = line.strip()[2:]
            processed_lines.append(f'<li>{item}</li>')
        else:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            processed_lines.append(line)

    if in_list:
        processed_lines.append('</ul>')

    html = '\n'.join(processed_lines)

    # Convert paragraphs (double newline = paragraph break)
    paragraphs = html.split('\n\n')
    formatted_paragraphs = []

    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<') and para:
            formatted_paragraphs.append(f'<p>{para}</p>')
        elif para:
            formatted_paragraphs.append(para)

    return '\n\n'.join(formatted_paragraphs)


def extract_toc(html_content):
    """Extract table of contents from headers"""
    toc_items = []
    h2_pattern = re.compile(r'<h2>(.*?)</h2>')

    for match in h2_pattern.finditer(html_content):
        title = match.group(1)
        # Create slug from title
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        toc_items.append(f'<li><a href="#{slug}">{title}</a></li>')

    if toc_items:
        return '<ul class="toc-list">\n' + '\n'.join(toc_items) + '\n</ul>'
    return ''


def add_header_ids(html_content):
    """Add IDs to headers for anchor linking"""
    def replace_h2(match):
        title = match.group(1)
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return f'<h2 id="{slug}">{title}</h2>'

    return re.sub(r'<h2>(.*?)</h2>', replace_h2, html_content)


def create_resource_html(title, description, content, base_url='/clinical'):
    """Create complete HTML page for a resource"""

    # Convert markdown to HTML
    html_content = markdown_to_html(content)

    # Add IDs to headers
    html_content = add_header_ids(html_content)

    # Extract table of contents
    toc = extract_toc(html_content)

    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <meta name="author" content="Lucas Steuber, MS CCC-SLP, MA Applied Linguistics">
    <title>{title} - Clinical Reference</title>

    <link rel="stylesheet" href="{base_url}/assets/css/clinical-reference.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Merriweather:wght@400;700&display=swap">
</head>
<body>
    <!-- Skip to main content (accessibility) -->
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <!-- Header / Navigation -->
    <header class="site-header" role="banner">
        <div class="container">
            <nav class="main-nav" role="navigation" aria-label="Main navigation">
                <div class="logo">
                    <a href="{base_url}/">
                        <strong>Clinical Reference</strong>
                        <span class="tagline">Evidence-Based Guidance</span>
                    </a>
                </div>
                <ul class="nav-menu">
                    <li><a href="{base_url}/conditions">All Conditions</a></li>
                    <li><a href="{base_url}/resources">Resources</a></li>
                    <li><a href="{base_url}/about">About</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <!-- Main Content -->
    <main id="main-content" class="main-content">

        <!-- Hero Section -->
        <section class="hero-section">
            <div class="container">
                <div class="breadcrumbs" aria-label="Breadcrumb">
                    <a href="{base_url}/">Home</a>
                    <span aria-hidden="true">›</span>
                    <a href="{base_url}/resources">Resources</a>
                    <span aria-hidden="true">›</span>
                    <span aria-current="page">{title}</span>
                </div>

                <h1 class="page-title">{title}</h1>
                <p class="lead">{description}</p>

                <div class="metadata">
                    <span class="badge badge-verified">Verified</span>
                    <span class="meta-item"><strong>Owner:</strong> Lucas Steuber</span>
                </div>
            </div>
        </section>

        <!-- Content Layout with TOC -->
        <div class="container content-layout">
            <aside class="table-of-contents" role="navigation" aria-label="Table of contents">
                <div class="toc-sticky">
                    <h2>Contents</h2>
                    <nav class="toc-nav">
                        {toc}
                    </nav>
                </div>
            </aside>

            <!-- Article Content -->
            <article class="article-content">
                {html_content}
            </article>
        </div>

    </main>

    <!-- Footer -->
    <footer class="site-footer" role="contentinfo">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Clinical Reference</h3>
                    <p>Evidence-based guidance for complex communication needs.</p>
                    <p><strong>Created by:</strong> Lucas Steuber, MS CCC-SLP, MA Applied Linguistics</p>
                </div>

                <div class="footer-section">
                    <h3>Quick Links</h3>
                    <ul>
                        <li><a href="{base_url}/conditions">Browse Conditions</a></li>
                        <li><a href="{base_url}/resources">Resources</a></li>
                        <li><a href="{base_url}/about">About</a></li>
                    </ul>
                </div>

                <div class="footer-section">
                    <h3>Contact</h3>
                    <p>Email: <a href="mailto:luke@lukesteuber.com">luke@lukesteuber.com</a></p>
                    <p>Website: <a href="https://lukesteuber.com">lukesteuber.com</a></p>
                </div>
            </div>

            <div class="footer-bottom">
                <p>&copy; 2025 Lucas Steuber. This document may be shared and used for educational purposes with proper attribution.</p>
            </div>
        </div>
    </footer>

    <script src="{base_url}/assets/js/clinical-reference.js"></script>
</body>
</html>
"""

    return template


def main():
    """Convert all resource markdown files to HTML"""

    project_root = Path('/home/coolhand/servers/clinical')
    resources_dir = project_root / 'resources'

    # Define resources to convert
    resources = [
        {
            'slug': 'glossary',
            'title': 'Clinical Glossary with Etymology',
            'description': 'Comprehensive glossary of medical, genetic, and neurological terms with etymological information',
            'md_file': resources_dir / 'glossary.md'
        },
        {
            'slug': 'aac-device-acquisition',
            'title': 'AAC Device Acquisition Process',
            'description': 'Clinical guide for the AAC process from assessment to device use',
            'md_file': resources_dir / 'aac-device-acquisition.md'
        },
        {
            'slug': 'clinical-guidance-index',
            'title': 'Clinical Guidance Index',
            'description': 'Comprehensive index of all clinical conditions and resources',
            'md_file': resources_dir / 'clinical-guidance-index.md'
        }
    ]

    for resource in resources:
        print(f"Converting {resource['slug']}...")

        # Read markdown file
        if not resource['md_file'].exists():
            print(f"  Warning: {resource['md_file']} not found")
            continue

        md_content = resource['md_file'].read_text(encoding='utf-8')

        # Create output directory
        output_dir = resources_dir / resource['slug']
        output_dir.mkdir(exist_ok=True)

        # Generate HTML
        html_content = create_resource_html(
            title=resource['title'],
            description=resource['description'],
            content=md_content
        )

        # Write HTML file
        output_file = output_dir / 'index.html'
        output_file.write_text(html_content, encoding='utf-8')

        print(f"  ✓ Created {output_file}")

    print("\nConversion complete!")


if __name__ == '__main__':
    main()
