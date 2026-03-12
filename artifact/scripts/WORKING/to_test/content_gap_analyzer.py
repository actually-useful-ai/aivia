#!/usr/bin/env python3
"""
Content Gap Analyzer for Clinical Reference Project
Analyzes all 51 condition markdown files for completeness and quality metrics
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

# Template required sections
REQUIRED_SECTIONS = [
    "Quick Reference",
    "Medical Coding",
    "Introduction",
    "Epidemiology and Demographics",
    "Etiology and Pathophysiology",
    "Clinical Features",
    "Diagnosis",
    "Assistive Technology and AAC Interventions",
    "Clinical Recommendations",
    "Care Management",
    "Educational Support",
    "Transition Planning",
    "Support and Resources",
    "References"
]

# Medical coding types expected
MEDICAL_CODES = ["ICD-11", "ICD-10-CM", "OMIM", "UMLS", "MeSH", "GARD"]

# Quick Reference table fields
QUICK_REF_FIELDS = ["Incidence", "Prevalence", "Onset", "AT Required"]


class ConditionAnalyzer:
    """Analyzes a single condition markdown file"""

    def __init__(self, md_path: Path):
        self.md_path = md_path
        self.slug = md_path.parent.name
        self.content = md_path.read_text(encoding='utf-8', errors='ignore')
        self.lines = self.content.split('\n')

    def get_condition_name(self) -> str:
        """Extract condition name from first H1 header"""
        for line in self.lines[:20]:
            if line.startswith('# ') and not line.startswith('## '):
                return line.replace('# ', '').strip()
        return self.slug.replace('-', ' ').title()

    def detect_sections(self) -> Tuple[List[str], List[str]]:
        """Detect which required sections are present vs missing"""
        present = []
        content_lower = self.content.lower()

        for section in REQUIRED_SECTIONS:
            # Flexible matching for section headers
            section_patterns = [
                f"# {section}",
                f"## {section}",
                f"### {section}",
                section.lower(),
            ]

            found = False
            for pattern in section_patterns:
                if pattern.lower() in content_lower:
                    found = True
                    break

            if found:
                present.append(section)

        missing = [s for s in REQUIRED_SECTIONS if s not in present]
        return present, missing

    def count_words(self) -> int:
        """Count total words in markdown file"""
        # Remove markdown syntax for accurate count
        text = re.sub(r'[#*_`\[\]\(\)]', '', self.content)
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # Remove images
        words = text.split()
        return len(words)

    def count_images(self) -> int:
        """Count embedded images in markdown"""
        image_pattern = r'!\[.*?\]\(.*?\)'
        return len(re.findall(image_pattern, self.content))

    def count_citations(self) -> int:
        """Count references in References section"""
        # Look for References section
        in_references = False
        citation_count = 0

        for line in self.lines:
            if re.match(r'^#+ References?', line, re.IGNORECASE):
                in_references = True
                continue

            if in_references:
                # Stop if we hit another major section
                if line.startswith('# ') and not line.lower().startswith('# ref'):
                    break

                # Count numbered references or DOI/URL patterns
                if re.match(r'^\d+\.', line.strip()) or 'doi.org' in line.lower() or 'http' in line.lower():
                    citation_count += 1

        return citation_count

    def check_medical_codes(self) -> Dict[str, bool]:
        """Check which medical codes are present"""
        codes_present = {}
        content_lower = self.content.lower()

        for code_type in MEDICAL_CODES:
            # Look for code type in content
            pattern = code_type.lower().replace('-', '[- ]?')
            codes_present[code_type] = bool(re.search(pattern, content_lower))

        return codes_present

    def check_quick_reference(self) -> bool:
        """Check if Quick Reference table is complete"""
        # Look for Quick Reference section
        quick_ref_section = ""
        in_quick_ref = False

        for i, line in enumerate(self.lines):
            if 'quick reference' in line.lower():
                in_quick_ref = True
                # Grab next 30 lines
                quick_ref_section = '\n'.join(self.lines[i:i+30])
                break

        if not quick_ref_section:
            return False

        # Check for key fields
        qr_lower = quick_ref_section.lower()
        has_incidence = 'incidence' in qr_lower
        has_prevalence = 'prevalence' in qr_lower
        has_onset = 'onset' in qr_lower or 'age' in qr_lower
        has_at = 'at required' in qr_lower or 'assistive technology' in qr_lower

        return has_incidence and has_prevalence and (has_onset or has_at)

    def analyze_section_depth(self) -> Dict[str, int]:
        """Analyze word count per section"""
        section_words = {}
        current_section = None
        current_content = []

        for line in self.lines:
            # Check if this is a section header
            header_match = re.match(r'^(#{1,3})\s+(.+)', line)
            if header_match:
                # Save previous section
                if current_section:
                    text = ' '.join(current_content)
                    text = re.sub(r'[#*_`\[\]\(\)]', '', text)
                    section_words[current_section] = len(text.split())

                # Start new section
                current_section = header_match.group(2).strip()
                current_content = []
            else:
                if current_section:
                    current_content.append(line)

        # Save last section
        if current_section:
            text = ' '.join(current_content)
            text = re.sub(r'[#*_`\[\]\(\)]', '', text)
            section_words[current_section] = len(text.split())

        return section_words

    def calculate_completeness_score(self, present_sections: List[str],
                                     word_count: int, image_count: int,
                                     citation_count: int, codes_present: Dict[str, bool],
                                     quick_ref_complete: bool) -> int:
        """Calculate 0-100 completeness score"""
        score = 0

        # Section coverage: 40 points
        section_pct = len(present_sections) / len(REQUIRED_SECTIONS)
        score += section_pct * 40

        # Word count: 20 points (target: 2000+ words)
        word_pct = min(word_count / 2000, 1.0)
        score += word_pct * 20

        # Images: 10 points (target: 3+ images)
        image_pct = min(image_count / 3, 1.0)
        score += image_pct * 10

        # Citations: 10 points (target: 10+ citations)
        citation_pct = min(citation_count / 10, 1.0)
        score += citation_pct * 10

        # Medical codes: 15 points
        codes_pct = sum(codes_present.values()) / len(MEDICAL_CODES)
        score += codes_pct * 15

        # Quick reference: 5 points
        if quick_ref_complete:
            score += 5

        return int(score)

    def estimate_work_hours(self, missing_sections: List[str], word_count: int,
                           image_count: int, citation_count: int) -> int:
        """Estimate hours of work needed"""
        hours = 0

        # Missing sections: 2 hours each for major sections
        major_sections = ["Assistive Technology and AAC Interventions",
                         "Clinical Recommendations", "Care Management"]
        for section in missing_sections:
            if section in major_sections:
                hours += 3
            else:
                hours += 1.5

        # Low word count
        if word_count < 1000:
            hours += 4
        elif word_count < 1500:
            hours += 2

        # Missing images
        if image_count < 3:
            hours += (3 - image_count) * 0.5

        # Missing citations
        if citation_count < 10:
            hours += (10 - citation_count) * 0.2

        return max(1, int(hours))


class ProjectAnalyzer:
    """Analyzes all conditions in the project"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conditions_dir = project_root / "conditions"
        self.results = {}
        self.gap_patterns = defaultdict(int)

    def analyze_all(self) -> Dict:
        """Analyze all 51 conditions"""
        condition_paths = sorted(self.conditions_dir.glob("*/index.md"))

        print(f"Found {len(condition_paths)} condition files")

        for md_path in condition_paths:
            try:
                analyzer = ConditionAnalyzer(md_path)
                slug = analyzer.slug

                # Run analysis
                condition_name = analyzer.get_condition_name()
                present, missing = analyzer.detect_sections()
                word_count = analyzer.count_words()
                image_count = analyzer.count_images()
                citation_count = analyzer.count_citations()
                codes_present = analyzer.check_medical_codes()
                quick_ref = analyzer.check_quick_reference()
                section_words = analyzer.analyze_section_depth()

                # Calculate completeness
                completeness = analyzer.calculate_completeness_score(
                    present, word_count, image_count, citation_count,
                    codes_present, quick_ref
                )

                # Estimate work
                work_hours = analyzer.estimate_work_hours(
                    missing, word_count, image_count, citation_count
                )

                # Determine priority
                if completeness < 70 or len(missing) >= 3:
                    priority = "high"
                elif completeness < 85 or len(missing) >= 1:
                    priority = "medium"
                else:
                    priority = "low"

                # Find short sections (<100 words)
                short_sections = {k: v for k, v in section_words.items()
                                 if v < 100 and v > 0}

                # Store results
                self.results[slug] = {
                    "name": condition_name,
                    "completeness_score": completeness,
                    "present_sections": present,
                    "missing_sections": missing,
                    "short_sections": short_sections,
                    "word_count": word_count,
                    "image_count": image_count,
                    "needs_images": image_count < 3,
                    "citation_count": citation_count,
                    "needs_citations": citation_count < 10,
                    "icd_codes_present": codes_present.get("ICD-11", False) and codes_present.get("ICD-10-CM", False),
                    "medical_codes": codes_present,
                    "quick_ref_complete": quick_ref,
                    "priority": priority,
                    "estimated_hours": work_hours
                }

                # Track patterns
                for section in missing:
                    self.gap_patterns[f"missing_{section}"] += 1

                print(f"✓ {slug}: {completeness}% complete, {priority} priority")

            except Exception as e:
                print(f"✗ Error analyzing {md_path}: {e}")
                self.results[slug] = {
                    "name": slug,
                    "error": str(e),
                    "priority": "high"
                }

        return self.results

    def generate_json_output(self, output_path: Path):
        """Generate JSON data file"""
        priority_counts = {"high": 0, "medium": 0, "low": 0}
        total_completeness = 0
        valid_count = 0

        for data in self.results.values():
            if "error" not in data:
                priority_counts[data["priority"]] += 1
                total_completeness += data["completeness_score"]
                valid_count += 1

        avg_completeness = total_completeness / valid_count if valid_count > 0 else 0

        # Find most missing sections
        missing_sections_count = defaultdict(int)
        for data in self.results.values():
            if "missing_sections" in data:
                for section in data["missing_sections"]:
                    missing_sections_count[section] += 1

        most_missing = sorted(missing_sections_count.items(),
                             key=lambda x: x[1], reverse=True)[:5]

        output_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "analyzer_version": "1.0",
                "total_conditions": len(self.results),
                "average_completeness": round(avg_completeness, 1),
                "target_completeness": 90,
                "conditions_meeting_target": sum(1 for d in self.results.values()
                                                if d.get("completeness_score", 0) >= 90)
            },
            "conditions": self.results,
            "priority_summary": priority_counts,
            "gap_patterns": {
                "most_missing_sections": [{"section": s, "count": c} for s, c in most_missing],
                "conditions_needing_images": sum(1 for d in self.results.values()
                                                if d.get("needs_images", False)),
                "conditions_needing_citations": sum(1 for d in self.results.values()
                                                   if d.get("needs_citations", False)),
                "conditions_missing_icd": sum(1 for d in self.results.values()
                                             if not d.get("icd_codes_present", True))
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ JSON output saved to: {output_path}")
        return output_data

    def generate_markdown_report(self, output_path: Path, json_data: Dict):
        """Generate comprehensive markdown report"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report_lines = []
        meta = json_data["metadata"]
        priority = json_data["priority_summary"]
        gaps = json_data["gap_patterns"]

        # Header
        report_lines.append("# Content Gap Analysis Report")
        report_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        report_lines.append("*Analyzer: Content Gap Analyzer Agent*")
        report_lines.append("")

        # Executive Summary
        report_lines.append("## Executive Summary")
        report_lines.append("")
        report_lines.append(f"- **Total conditions analyzed:** {meta['total_conditions']}/51")
        report_lines.append(f"- **Average completeness score:** {meta['average_completeness']}%")
        report_lines.append(f"- **Target completeness:** {meta['target_completeness']}%")
        report_lines.append(f"- **Conditions meeting target:** {meta['conditions_meeting_target']}/51")
        report_lines.append(f"- **Gap from target:** {meta['target_completeness'] - meta['average_completeness']:.1f} percentage points")
        report_lines.append("")

        # Most common gaps
        report_lines.append("### Most Common Missing Sections")
        for i, item in enumerate(gaps["most_missing_sections"], 1):
            pct = (item['count'] / meta['total_conditions']) * 100
            report_lines.append(f"{i}. **{item['section']}** - missing in {item['count']}/{meta['total_conditions']} conditions ({pct:.0f}%)")
        report_lines.append("")

        # Top 10 urgent
        report_lines.append("### Top 10 Conditions Needing Urgent Attention")
        report_lines.append("")

        # Sort by completeness (lowest first) and priority
        sorted_conditions = sorted(
            [(slug, data) for slug, data in self.results.items() if "error" not in data],
            key=lambda x: (x[1]["completeness_score"], x[1]["priority"] == "low")
        )[:10]

        for i, (slug, data) in enumerate(sorted_conditions, 1):
            report_lines.append(f"{i}. **{data['name']}** (slug: {slug})")
            report_lines.append(f"   - Completeness: {data['completeness_score']}%")
            report_lines.append(f"   - Priority: {data['priority'].title()}")
            report_lines.append(f"   - Missing {len(data['missing_sections'])} sections, {data['word_count']} words, {data['image_count']} images, {data['citation_count']} citations")
            report_lines.append("")

        report_lines.append("---")
        report_lines.append("")

        # Detailed analysis by priority
        report_lines.append("## Detailed Analysis by Priority")
        report_lines.append("")

        for priority_level in ["high", "medium", "low"]:
            priority_conditions = [(s, d) for s, d in self.results.items()
                                  if d.get("priority") == priority_level and "error" not in d]
            priority_conditions.sort(key=lambda x: x[1]["completeness_score"])

            if priority_level == "high":
                title = "High Priority Conditions (Completeness <70%)"
            elif priority_level == "medium":
                title = "Medium Priority Conditions (70-85% Completeness)"
            else:
                title = "Low Priority Conditions (85-100% Completeness)"

            report_lines.append(f"### {title}")
            report_lines.append("")
            report_lines.append(f"*{len(priority_conditions)} conditions in this category*")
            report_lines.append("")

            for slug, data in priority_conditions:
                report_lines.append(f"#### {data['name']}")
                report_lines.append(f"- **Slug:** `{slug}`")
                report_lines.append(f"- **Current completeness:** {data['completeness_score']}%")
                report_lines.append(f"- **Word count:** {data['word_count']}")
                report_lines.append(f"- **Images:** {data['image_count']} (needs_images: {data['needs_images']})")
                report_lines.append(f"- **Citations:** {data['citation_count']} (needs_citations: {data['needs_citations']})")
                report_lines.append(f"- **ICD codes present:** {'Yes' if data['icd_codes_present'] else 'No'}")
                report_lines.append(f"- **Quick Reference complete:** {'Yes' if data['quick_ref_complete'] else 'No'}")
                report_lines.append("")

                if data['missing_sections']:
                    report_lines.append("**Missing sections:**")
                    for section in data['missing_sections']:
                        report_lines.append(f"- {section}")
                    report_lines.append("")

                if data['short_sections']:
                    report_lines.append("**Short/underdeveloped sections:**")
                    for section, words in sorted(data['short_sections'].items(), key=lambda x: x[1]):
                        report_lines.append(f"- {section}: {words} words (needs 100+ words)")
                    report_lines.append("")

                report_lines.append(f"**Estimated work required:** {data['estimated_hours']} hours")
                report_lines.append("")
                report_lines.append("**Recommended actions:**")

                if not data['icd_codes_present']:
                    report_lines.append("1. Add complete medical coding (ICD-11, ICD-10-CM, OMIM, UMLS, MeSH, GARD)")
                if not data['quick_ref_complete']:
                    report_lines.append("2. Complete Quick Reference table with all key fields")
                if data['missing_sections']:
                    report_lines.append(f"3. Write {len(data['missing_sections'])} missing section(s)")
                if data['image_count'] < 3:
                    report_lines.append(f"4. Add {3 - data['image_count']} clinical image(s)")
                if data['citation_count'] < 10:
                    report_lines.append(f"5. Add {10 - data['citation_count']} citation(s)")

                report_lines.append("")
                report_lines.append("---")
                report_lines.append("")

        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"✓ Markdown report saved to: {output_path}")


def main():
    """Main execution"""
    project_root = Path("/home/coolhand/servers/clinical")

    print("=" * 60)
    print("Clinical Reference Content Gap Analyzer")
    print("=" * 60)
    print()

    analyzer = ProjectAnalyzer(project_root)

    # Analyze all conditions
    print("Analyzing all conditions...")
    print()
    results = analyzer.analyze_all()

    print()
    print("=" * 60)
    print("Generating outputs...")
    print()

    # Generate JSON
    json_path = project_root / "data" / "content-gaps.json"
    json_data = analyzer.generate_json_output(json_path)

    # Generate Markdown report
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = project_root / "reports" / f"content-gaps-{today}.md"
    analyzer.generate_markdown_report(report_path, json_data)

    print()
    print("=" * 60)
    print("Analysis complete!")
    print("=" * 60)
    print()
    print(f"Total conditions: {json_data['metadata']['total_conditions']}")
    print(f"Average completeness: {json_data['metadata']['average_completeness']}%")
    print(f"High priority: {json_data['priority_summary']['high']}")
    print(f"Medium priority: {json_data['priority_summary']['medium']}")
    print(f"Low priority: {json_data['priority_summary']['low']}")
    print()


if __name__ == "__main__":
    main()
