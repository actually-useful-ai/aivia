#!/usr/bin/env python3
"""
Bulk Markdown to HTML Converter for Clinical Reference
Handles varying structures, extracts images, and generates styled HTML pages
"""

import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import html
from datetime import datetime

class ConditionConverter:
    """Converts condition markdown files to HTML using the template"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conditions_dir = project_root / 'conditions'
        self.template_path = project_root / '_meta' / 'template.html'
        self.template = self._load_template()
        
    def _load_template(self) -> str:
        """Load the HTML template"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_metadata(self, content: str) -> Tuple[Dict[str, str], str]:
        """Extract metadata from top of markdown file"""
        metadata = {}
        lines = content.split('\n')
        content_start = 0
        
        # Extract owner, tags, verification status from top lines
        for i, line in enumerate(lines[:20]):
            if line.startswith('Owner:'):
                metadata['owner'] = line.replace('Owner:', '').strip()
                content_start = max(content_start, i + 1)
            elif line.startswith('Tags:'):
                metadata['tags'] = line.replace('Tags:', '').strip()
                content_start = max(content_start, i + 1)
            elif 'verification' in line.lower() and ':' in line:
                metadata['verification'] = 'VERIFIED'
                content_start = max(content_start, i + 1)
        
        # Return remaining content
        remaining_content = '\n'.join(lines[content_start:])
        return metadata, remaining_content
    
    def _find_images(self, condition_slug: str, content: str) -> List[Dict[str, str]]:
        """Find all images for this condition"""
        images = []
        condition_dir = self.conditions_dir / condition_slug
        images_dir = condition_dir / 'images'
        
        if images_dir.exists():
            # Get all image files
            for img_file in sorted(images_dir.iterdir()):
                if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                    images.append({
                        'filename': img_file.name,
                        'path': f'images/{img_file.name}',
                        'alt': f'Clinical illustration for {condition_slug.replace("-", " ").title()}'
                    })
        
        return images
    
    def _extract_title(self, content: str) -> str:
        """Extract the main title from markdown"""
        # Look for first H1
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            title = match.group(1).strip()
            # Remove emojis and clean up
            title = re.sub(r'[^\w\s\-\(\)\']+', '', title).strip()
            return title
        return "Clinical Condition"
    
    def _extract_quick_reference(self, content: str) -> Dict[str, str]:
        """Extract quick reference data from content"""
        quick_ref = {
            'prevalence': 'Data not available',
            'onset': 'Varies',
            'inheritance': 'See content',
            'icd10': 'See content'
        }
        
        # Try to extract incidence/prevalence from prose text first
        # Look for patterns like "incidence of approximately 1 in 10,000"
        incidence_match = re.search(r'incidence of (?:approximately |about )?([^,.]+(?:in \d+[,\d]*|per \d+[,\d]*))[^.]*', 
                                   content, re.IGNORECASE)
        if incidence_match:
            quick_ref['prevalence'] = incidence_match.group(1).strip()
        else:
            # Look for prevalence patterns
            prev_match = re.search(r'prevalence (?:of|is) (?:estimated to be )?(?:between )?([^,.]+(?:in \d+[,\d]*|per \d+[,\d]*))[^.]*',
                                  content, re.IGNORECASE)
            if prev_match:
                quick_ref['prevalence'] = prev_match.group(1).strip()
        
        # Look for onset age patterns
        onset_match = re.search(r'(?:onset|typically (?:occurs|begins|manifests)).*?(?:at |between |around )?(\d+[^.]*?(?:months?|years?|age))',
                               content, re.IGNORECASE)
        if onset_match:
            quick_ref['onset'] = onset_match.group(1).strip()
        
        # Look for demographic/coding sections as fallback
        demo_match = re.search(r'##\s*(?:Demographic|Demographics|Incidence).*?\n(.*?)(?=\n##|\Z)', 
                              content, re.DOTALL | re.IGNORECASE)
        if demo_match and quick_ref['prevalence'] == 'Data not available':
            demo_text = demo_match.group(1)
            # Extract incidence/prevalence
            if 'incidence' in demo_text.lower() or 'prevalence' in demo_text.lower():
                lines = demo_text.split('\n')
                for line in lines:
                    if 'incidence' in line.lower() or 'prevalence' in line.lower():
                        quick_ref['prevalence'] = line.split(':', 1)[-1].strip().strip('-*').strip()
                        break
            
            # Extract onset age
            if 'onset' in demo_text.lower():
                for line in demo_text.split('\n'):
                    if 'onset' in line.lower():
                        quick_ref['onset'] = line.split(':', 1)[-1].strip().strip('-*').strip()
                        break
        
        # Look for coding section
        coding_match = re.search(r'##\s*Coding.*?\n(.*?)(?=\n##|\Z)', 
                                content, re.DOTALL | re.IGNORECASE)
        if coding_match:
            coding_text = coding_match.group(1)
            # Extract ICD-10
            icd_match = re.search(r'ICD-10.*?[:：]\s*([A-Z]\d+\.?\d*)', coding_text, re.IGNORECASE)
            if icd_match:
                quick_ref['icd10'] = icd_match.group(1)
        
        return quick_ref
    
    def _markdown_to_html(self, md_content: str) -> str:
        """Convert markdown to HTML (basic implementation)"""
        html_content = md_content
        
        # Remove emoji patterns that might break rendering
        html_content = re.sub(r'[📓🧪🎯💊🧬⚕️🔬🏥👨‍⚕️👩‍⚕️🧑‍⚕️]+', '', html_content)
        
        # Headers (H1-H6)
        html_content = re.sub(r'^######\s+(.+)$', r'<h6>\1</h6>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^#####\s+(.+)$', r'<h5>\1</h5>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        
        # Bold and italic
        html_content = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html_content)
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
        
        # Code blocks
        html_content = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html_content, flags=re.DOTALL)
        html_content = re.sub(r'`(.+?)`', r'<code>\1</code>', html_content)
        
        # Images BEFORE links (images start with !)
        html_content = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', r'<img src="\2" alt="\1" loading="lazy" />', html_content)
        
        # Links (after images so we don't catch image syntax)
        html_content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html_content)
        
        # Unordered lists
        def replace_ul(match):
            items = match.group(0).strip().split('\n')
            html_items = ['<ul>']
            for item in items:
                item = item.strip()
                if item.startswith('- ') or item.startswith('* '):
                    content = item[2:].strip()
                    html_items.append(f'<li>{content}</li>')
            html_items.append('</ul>')
            return '\n'.join(html_items)
        
        # Match unordered list blocks
        html_content = re.sub(r'^(?:[-*]\s+.+\n?)+', replace_ul, html_content, flags=re.MULTILINE)
        
        # Paragraphs (wrap text blocks)
        lines = html_content.split('\n')
        processed_lines = []
        in_paragraph = False
        paragraph_buffer = []
        
        for line in lines:
            stripped = line.strip()
            
            # Skip if it's already HTML or empty
            if (not stripped or 
                stripped.startswith('<') or 
                stripped.startswith('---')):
                
                # Close any open paragraph
                if in_paragraph and paragraph_buffer:
                    processed_lines.append('<p>' + ' '.join(paragraph_buffer) + '</p>')
                    paragraph_buffer = []
                    in_paragraph = False
                
                if stripped == '---':
                    processed_lines.append('<hr />')
                elif stripped:
                    processed_lines.append(line)
            else:
                # Regular text - add to paragraph
                paragraph_buffer.append(stripped)
                in_paragraph = True
        
        # Close final paragraph if needed
        if in_paragraph and paragraph_buffer:
            processed_lines.append('<p>' + ' '.join(paragraph_buffer) + '</p>')
        
        return '\n'.join(processed_lines)
    
    def _build_toc(self, content: str) -> str:
        """Build table of contents from headers (H1, H2, and H3)"""
        # Find all H1, H2, and H3 headers with their level
        header_pattern = r'^(#{1,3})\s+(.+)$'
        matches = re.finditer(header_pattern, content, re.MULTILINE)

        headers = []
        for match in matches:
            level = len(match.group(1))  # 1 for H1, 2 for H2, 3 for H3
            text = match.group(2).strip()
            headers.append((level, text))

        if not headers:
            return ''

        toc_html = ['<nav class="table-of-contents">', '<h2>Table of Contents</h2>', '<ul>']

        current_level = 1
        for level, header in headers:
            # Clean header for display and anchor
            clean_header = re.sub(r'[^\w\s-]', '', header).strip()
            # Remove ** bold markers if present
            clean_header = clean_header.replace('**', '')
            anchor = clean_header.lower().replace(' ', '-').replace('--', '-')

            # Handle nesting
            if level == 1:
                # Close any open H2 or H3 lists
                if current_level == 3:
                    toc_html.append('</ul></li>')  # Close H3 list
                    toc_html.append('</li>')  # Close H2 item
                elif current_level == 2:
                    toc_html.append('</li>')  # Close H2 item
                current_level = 1
                toc_html.append(f'<li><a href="#{anchor}">{html.escape(clean_header)}</a>')
            elif level == 2:
                # Close any open H3 list
                if current_level == 3:
                    toc_html.append('</ul></li>')
                elif current_level == 1:
                    # Open H2 list under H1
                    toc_html.append('<ul>')
                current_level = 2
                toc_html.append(f'<li><a href="#{anchor}">{html.escape(clean_header)}</a>')
            elif level == 3:
                # Open H3 list if needed
                if current_level == 2:
                    toc_html.append('<ul>')
                    current_level = 3
                toc_html.append(f'<li><a href="#{anchor}">{html.escape(clean_header)}</a></li>')

        # Close any open lists
        if current_level == 3:
            toc_html.append('</ul></li>')  # Close H3 list
            toc_html.append('</li>')  # Close H2 item
            toc_html.append('</ul></li>')  # Close H2 list
        elif current_level == 2:
            toc_html.append('</li>')  # Close H2 item
            toc_html.append('</ul></li>')  # Close H2 list

        toc_html.extend(['</ul>', '</nav>'])

        return '\n'.join(toc_html)
    
    def convert_condition(self, condition_slug: str) -> bool:
        """Convert a single condition from markdown to HTML"""
        try:
            condition_dir = self.conditions_dir / condition_slug
            md_path = condition_dir / 'index.md'
            html_path = condition_dir / 'index.html'
            
            if not md_path.exists():
                print(f"  ❌ No markdown file found for {condition_slug}")
                return False
            
            # Read markdown content
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Extract metadata
            metadata, content = self._extract_metadata(md_content)
            
            # Extract title
            title = self._extract_title(content)
            
            # Find images
            images = self._find_images(condition_slug, content)
            
            # Extract quick reference data
            quick_ref = self._extract_quick_reference(content)
            
            # Convert markdown to HTML
            html_content = self._markdown_to_html(content)
            
            # Build table of contents
            toc = self._build_toc(content)
            
            # Prepare template variables - fill ALL variables from template
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            variables = {
                # Basic metadata
                '{{TITLE}}': html.escape(title),
                '{{CONDITION_NAME}}': html.escape(title),
                '{{DESCRIPTION}}': f'Comprehensive clinical guide for {title} covering AAC, assistive technology, and evidence-based interventions.',
                '{{KEYWORDS}}': f'{title}, clinical guidance, AAC, assistive technology, speech therapy',
                '{{AUTHOR}}': html.escape(metadata.get('owner', 'Lucas Steuber, MS CCC-SLP, MA Applied Linguistics')),
                '{{OWNER}}': html.escape(metadata.get('owner', 'Lucas Steuber, MS CCC-SLP, MA Applied Linguistics')),
                '{{OG_TITLE}}': html.escape(f'{title} - Clinical Reference Guide'),
                '{{OG_DESCRIPTION}}': f'Comprehensive clinical guide for {title} covering AAC, assistive technology, clinical recommendations, and evidence-based interventions for SLPs, educators, and healthcare professionals.',
                '{{VERIFICATION_STATUS}}': metadata.get('verification', 'IN PROGRESS'),
                '{{VERIFICATION_STATUS_CLASS}}': 'verified' if metadata.get('verification') else 'in-progress',
                '{{LAST_UPDATED}}': current_date,
                '{{LAST_REVIEWED}}': current_date,
                '{{NEXT_REVIEW}}': '',
                '{{CREATED_DATE}}': current_date,
                '{{VERSION}}': '1.0',
                
                # Quick reference data
                '{{PREVALENCE}}': html.escape(quick_ref['prevalence']),
                '{{INCIDENCE}}': html.escape(quick_ref['prevalence']),  # Use same as prevalence
                '{{ONSET}}': html.escape(quick_ref['onset']),
                '{{AGE_OF_ONSET}}': html.escape(quick_ref['onset']),
                '{{INHERITANCE}}': html.escape(quick_ref['inheritance']),
                '{{AT_PERCENTAGE}}': '80-90',  # Default estimate
                
                # Medical coding
                '{{ICD10}}': html.escape(quick_ref['icd10']),
                '{{ICD11}}': '',
                '{{OMIM}}': '',
                '{{UMLS}}': '',
                '{{MESH}}': '',
                '{{GARD}}': '',
                
                # Navigation
                '{{TOC}}': toc,
                '{{TABLE_OF_CONTENTS}}': toc,
                
                # Main content
                '{{CONTENT}}': html_content,
                '{{INTRODUCTION_CONTENT}}': html_content,
                '{{EPIDEMIOLOGY_CONTENT}}': '',
                '{{ETIOLOGY_CONTENT}}': '',
                '{{PATHOPHYSIOLOGY_CONTENT}}': '',
                '{{CLINICAL_FEATURES_CONTENT}}': '',
                '{{DIAGNOSTIC_CRITERIA_CONTENT}}': '',
                '{{DIFFERENTIAL_DIAGNOSIS_CONTENT}}': '',
                '{{GENETIC_TESTING_CONTENT}}': '',
                '{{MEDICAL_MANAGEMENT_CONTENT}}': '',
                
                # AT and AAC
                '{{AT_INTRO}}': '',
                '{{COMMUNICATION_DEVICES_CONTENT}}': '',
                '{{ACCESS_MODALITIES_CONTENT}}': '',
                '{{MOBILITY_AIDS_CONTENT}}': '',
                '{{POSITIONING_CONTENT}}': '',
                '{{FEEDING_CONTENT}}': '',
                
                # Recommendations
                '{{RECOMMENDATIONS_INTRO}}': '',
                '{{SLP_RECOMMENDATIONS_CONTENT}}': '',
                '{{OT_RECOMMENDATIONS_CONTENT}}': '',
                '{{PT_RECOMMENDATIONS_CONTENT}}': '',
                '{{ABA_RECOMMENDATIONS_CONTENT}}': '',
                '{{EDUCATOR_RECOMMENDATIONS_CONTENT}}': '',
                '{{STAFF_RECOMMENDATIONS_CONTENT}}': '',
                
                # Educational support
                '{{ACCOMMODATIONS_CONTENT}}': '',
                '{{IEP_GOALS_CONTENT}}': '',
                '{{TRANSITION_PLANNING_CONTENT}}': '',
                
                # Resources
                '{{PSYCHOSOCIAL_CONTENT}}': '',
                '{{COMMUNITIES_CONTENT}}': '',
                '{{FOUNDATIONS_CONTENT}}': '',
                '{{FINANCIAL_RESOURCES_CONTENT}}': '',
                '{{EDUCATIONAL_RESOURCES_CONTENT}}': '',
                '{{ECU_CONTENT}}': '',
                '{{REFERENCES_CONTENT}}': '',
            }
            
            # Add hero image if available
            if images:
                hero_image = images[0]
                variables['{{HERO_IMAGE}}'] = f'<img src="{hero_image["path"]}" alt="{hero_image["alt"]}" class="hero-image" />'
            else:
                variables['{{HERO_IMAGE}}'] = ''
            
            # Replace all variables in template
            html_output = self.template
            for key, value in variables.items():
                html_output = html_output.replace(key, value)
            
            # Write HTML file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_output)
            
            print(f"  ✅ {condition_slug} → {title}")
            if images:
                print(f"     📸 {len(images)} image(s) included")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error converting {condition_slug}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert_all(self) -> Dict[str, int]:
        """Convert all conditions"""
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        print("🔄 Starting bulk conversion...\n")
        
        # Get all condition directories
        conditions = sorted([d for d in self.conditions_dir.iterdir() if d.is_dir()])
        stats['total'] = len(conditions)
        
        for condition_dir in conditions:
            condition_slug = condition_dir.name
            
            # Skip if already converted (unless forced)
            html_path = condition_dir / 'index.html'
            
            print(f"📄 Converting: {condition_slug}")
            
            if self.convert_condition(condition_slug):
                stats['success'] += 1
            else:
                stats['failed'] += 1
            
            print()  # Blank line between conditions
        
        return stats


def main():
    """Main conversion script"""
    project_root = Path('/home/coolhand/servers/clinical')
    
    print("=" * 60)
    print("Clinical Reference - Bulk Markdown to HTML Converter")
    print("=" * 60)
    print()
    
    converter = ConditionConverter(project_root)
    stats = converter.convert_all()
    
    print("=" * 60)
    print("Conversion Complete!")
    print("=" * 60)
    print(f"Total conditions: {stats['total']}")
    print(f"✅ Successfully converted: {stats['success']}")
    print(f"❌ Failed: {stats['failed']}")
    print(f"⏭️  Skipped: {stats['skipped']}")
    print()
    print(f"Success rate: {(stats['success']/stats['total']*100):.1f}%")
    print()
    print("🌐 View at: https://dr.eamer.dev/clinical/conditions")


if __name__ == '__main__':
    main()
