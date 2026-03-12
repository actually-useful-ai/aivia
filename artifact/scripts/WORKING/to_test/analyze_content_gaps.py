#!/usr/bin/env python3
"""
Content Gap Analyzer for Clinical Reference Project
Analyzes all 51 conditions for completeness and generates comprehensive reports.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any

# Required sections from template
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

# Section aliases for fuzzy matching
SECTION_ALIASES = {
    "Quick Reference": ["quick reference", "quick facts"],
    "Medical Coding": ["medical coding", "medical codes", "diagnostic codes"],
    "Introduction": ["introduction"],
    "Epidemiology and Demographics": ["epidemiology", "demographics", "epidemiology and demographics"],
    "Etiology and Pathophysiology": ["etiology", "pathophysiology", "etiology and pathophysiology"],
    "Clinical Features": ["clinical features", "symptoms", "clinical presentation"],
    "Diagnosis": ["diagnosis", "diagnostic criteria"],
    "Assistive Technology and AAC Interventions": ["assistive technology", "aac", "aac interventions"],
    "Clinical Recommendations": ["clinical recommendations", "recommendations"],
    "Care Management": ["care management", "management", "treatment"],
    "Educational Support": ["educational support", "education", "iep"],
    "Transition Planning": ["transition planning", "transition"],
    "Support and Resources": ["support", "resources", "support and resources"],
    "References": ["references", "bibliography", "citations"]
}

class ContentGapAnalyzer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conditions_dir = project_root / "conditions"
        self.data_dir = project_root / "data"
        self.reports_dir = project_root / "reports"

        # Load dashboard status
        self.dashboard_data = self.load_dashboard_status()

        # Results storage
        self.condition_results = {}
        self.gap_patterns = defaultdict(int)
        self.priority_counts = {"high": 0, "medium": 0, "low": 0}

    def load_dashboard_status(self) -> Dict:
        """Load existing dashboard status data"""
        status_file = self.data_dir / "condition_status.json"
        if status_file.exists():
            with open(status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"conditions": {}}

    def get_condition_name(self, slug: str) -> str:
        """Convert slug to human-readable name"""
        # Try to get from dashboard first
        if slug in self.dashboard_data.get("conditions", {}):
            # Infer name from slug
            pass

        # Convert slug to title case
        name = slug.replace('-', ' ').title()
        # Handle special cases
        if 'aac' in name.lower():
            name = name.replace('Aac', 'AAC')
        if 'icd' in name.lower():
            name = name.replace('Icd', 'ICD')
        return name

    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())

    def count_citations(self, content: str) -> int:
        """Count references/citations in content"""
        # Find References section
        refs_match = re.search(r'##?\s+References\s*\n(.*)', content, re.IGNORECASE | re.DOTALL)
        if not refs_match:
            return 0

        refs_section = refs_match.group(1)
        # Count numbered references
        citations = re.findall(r'^\d+\.', refs_section, re.MULTILINE)
        return len(citations)

    def count_images(self, slug: str, content: str) -> int:
        """Count images in content and verify files exist"""
        # Count markdown image syntax
        image_refs = re.findall(r'!\[.*?\]\(.*?\)', content)

        # Also check images directory
        images_dir = self.conditions_dir / slug / "images"
        if images_dir.exists():
            image_files = list(images_dir.glob("*"))
            # Filter out non-image files
            valid_images = [f for f in image_files if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']]
            return max(len(image_refs), len(valid_images))

        return len(image_refs)

    def check_medical_codes(self, content: str) -> Dict[str, bool]:
        """Check for presence of medical coding"""
        codes = {
            "icd11": bool(re.search(r'\*\*ICD-11:\*\*\s*\w+', content, re.IGNORECASE)),
            "icd10": bool(re.search(r'\*\*ICD-10(-CM)?:\*\*\s*\w+', content, re.IGNORECASE)),
            "omim": bool(re.search(r'\*\*OMIM:\*\*\s*\d+', content, re.IGNORECASE)),
            "umls": bool(re.search(r'\*\*UMLS:\*\*\s*\w+', content, re.IGNORECASE)),
            "mesh": bool(re.search(r'\*\*MeSH:\*\*\s*\w+', content, re.IGNORECASE)),
            "gard": bool(re.search(r'\*\*GARD:\*\*\s*\d+', content, re.IGNORECASE))
        }
        return codes

    def check_quick_reference(self, content: str) -> Dict[str, bool]:
        """Check Quick Reference table completeness"""
        qr_data = {
            "has_table": bool(re.search(r'##?\s+Quick Reference', content, re.IGNORECASE)),
            "has_incidence": bool(re.search(r'\*\*Incidence\*\*.*?[0-9]', content, re.IGNORECASE)),
            "has_prevalence": bool(re.search(r'\*\*Prevalence\*\*.*?[0-9]', content, re.IGNORECASE)),
            "has_onset": bool(re.search(r'\*\*.*?Age.*?Onset\*\*', content, re.IGNORECASE)),
            "has_at_needs": bool(re.search(r'\*\*AT.*?Required\*\*.*?%', content, re.IGNORECASE))
        }
        return qr_data

    def extract_sections(self, content: str) -> Dict[str, Dict]:
        """Extract sections and their content from markdown"""
        sections = {}

        # Find all H1 and H2 headers
        header_pattern = r'^##?\s+(.+?)$'
        matches = list(re.finditer(header_pattern, content, re.MULTILINE))

        for i, match in enumerate(matches):
            section_title = match.group(1).strip()
            start_pos = match.end()

            # Find end position (next header or end of file)
            if i < len(matches) - 1:
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(content)

            section_content = content[start_pos:end_pos].strip()
            word_count = self.count_words(section_content)

            sections[section_title] = {
                "content": section_content[:500],  # Store snippet
                "word_count": word_count,
                "position": i
            }

        return sections

    def match_required_sections(self, found_sections: Dict[str, Dict]) -> Tuple[List[str], List[str], Dict[str, int]]:
        """Match found sections against required sections"""
        present = []
        missing = []
        short_sections = {}

        for required in REQUIRED_SECTIONS:
            matched = False
            aliases = SECTION_ALIASES.get(required, [required.lower()])

            for found_title, found_data in found_sections.items():
                found_lower = found_title.lower()
                if any(alias in found_lower for alias in aliases):
                    present.append(required)
                    matched = True

                    # Check if section is underdeveloped
                    if found_data["word_count"] < 100:
                        short_sections[required] = found_data["word_count"]
                    break

            if not matched:
                missing.append(required)

        return present, missing, short_sections

    def calculate_completeness_score(self, analysis: Dict) -> int:
        """Calculate completeness score 0-100"""
        # Use dashboard score if available
        slug = analysis.get("slug", "")
        if slug in self.dashboard_data.get("conditions", {}):
            dashboard_score = self.dashboard_data["conditions"][slug].get("quality_score", 0)
            if dashboard_score > 0:
                return dashboard_score

        # Otherwise calculate based on our analysis
        score = 100

        # Section coverage (40 points max)
        section_coverage = len(analysis["present_sections"]) / len(REQUIRED_SECTIONS)
        score = section_coverage * 40

        # Content quality (30 points max)
        if analysis["image_count"] >= 3:
            score += 10
        elif analysis["image_count"] >= 1:
            score += 5

        if analysis["citation_count"] >= 15:
            score += 10
        elif analysis["citation_count"] >= 10:
            score += 7
        elif analysis["citation_count"] >= 5:
            score += 3

        if analysis["icd_codes_present"]:
            score += 10

        # Quick Reference (10 points)
        if analysis["quick_ref_complete"]:
            score += 10

        # Penalty for short sections (up to -20 points)
        short_penalty = min(len(analysis["short_sections"]) * 3, 20)
        score -= short_penalty

        return max(0, min(100, int(score)))

    def assign_priority(self, analysis: Dict) -> str:
        """Assign priority level: high, medium, low"""
        score = analysis["completeness_score"]
        missing_count = len(analysis["missing_sections"])

        # High priority criteria
        if (score < 70 or
            missing_count >= 3 or
            not analysis["icd_codes_present"] or
            analysis["image_count"] == 0 or
            analysis["citation_count"] == 0):
            return "high"

        # Medium priority criteria
        if (score < 85 or
            missing_count >= 1 or
            analysis["image_count"] < 3 or
            analysis["citation_count"] < 10):
            return "medium"

        # Low priority
        return "low"

    def estimate_work_hours(self, analysis: Dict) -> float:
        """Estimate hours needed to fix gaps"""
        hours = 0

        # Missing sections (1-2 hours each)
        hours += len(analysis["missing_sections"]) * 1.5

        # Short sections (0.5 hours each)
        hours += len(analysis["short_sections"]) * 0.5

        # Images (0.5 hour each)
        images_needed = max(0, 3 - analysis["image_count"])
        hours += images_needed * 0.5

        # Citations (0.25 hours per 5 citations)
        citations_needed = max(0, 10 - analysis["citation_count"])
        hours += (citations_needed / 5) * 0.25

        # Medical coding (1 hour total if missing)
        if not analysis["icd_codes_present"]:
            hours += 1

        # Quick reference (0.5 hours if incomplete)
        if not analysis["quick_ref_complete"]:
            hours += 0.5

        return round(hours, 1)

    def analyze_condition(self, slug: str) -> Dict:
        """Analyze a single condition"""
        md_file = self.conditions_dir / slug / "index.md"

        if not md_file.exists():
            return {
                "slug": slug,
                "name": self.get_condition_name(slug),
                "error": "File not found",
                "priority": "high"
            }

        # Read content
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract sections
        found_sections = self.extract_sections(content)
        present, missing, short_sections = self.match_required_sections(found_sections)

        # Count images and citations
        image_count = self.count_images(slug, content)
        citation_count = self.count_citations(content)

        # Check medical codes
        codes = self.check_medical_codes(content)
        icd_codes_present = codes["icd11"] and codes["icd10"]

        # Check Quick Reference
        qr_data = self.check_quick_reference(content)
        quick_ref_complete = all([
            qr_data["has_table"],
            qr_data["has_incidence"],
            qr_data["has_prevalence"],
            qr_data["has_onset"]
        ])

        # Build analysis result
        analysis = {
            "slug": slug,
            "name": self.get_condition_name(slug),
            "present_sections": present,
            "missing_sections": missing,
            "short_sections": short_sections,
            "image_count": image_count,
            "needs_images": image_count < 3,
            "citation_count": citation_count,
            "needs_citations": citation_count < 10,
            "icd_codes_present": icd_codes_present,
            "medical_codes": codes,
            "quick_ref_complete": quick_ref_complete,
            "quick_ref_data": qr_data
        }

        # Calculate completeness score
        analysis["completeness_score"] = self.calculate_completeness_score(analysis)

        # Assign priority
        analysis["priority"] = self.assign_priority(analysis)

        # Estimate work hours
        analysis["estimated_hours"] = self.estimate_work_hours(analysis)

        return analysis

    def analyze_all_conditions(self):
        """Analyze all 51 conditions"""
        condition_dirs = sorted([d for d in self.conditions_dir.iterdir() if d.is_dir()])

        print(f"Analyzing {len(condition_dirs)} conditions...")

        for i, cond_dir in enumerate(condition_dirs, 1):
            slug = cond_dir.name
            print(f"[{i}/{len(condition_dirs)}] Analyzing {slug}...")

            analysis = self.analyze_condition(slug)
            self.condition_results[slug] = analysis

            # Update priority counts
            priority = analysis.get("priority", "high")
            self.priority_counts[priority] += 1

            # Update gap patterns
            for missing in analysis.get("missing_sections", []):
                self.gap_patterns[f"missing_{missing}"] += 1

            if analysis.get("needs_images"):
                self.gap_patterns["needs_images"] += 1

            if analysis.get("needs_citations"):
                self.gap_patterns["needs_citations"] += 1

            if not analysis.get("icd_codes_present"):
                self.gap_patterns["missing_icd"] += 1

            if not analysis.get("quick_ref_complete"):
                self.gap_patterns["incomplete_quick_ref"] += 1

        print(f"\nAnalysis complete! Processed {len(self.condition_results)} conditions.")

    def generate_json_report(self) -> Dict:
        """Generate JSON output"""
        # Calculate statistics
        total_conditions = len(self.condition_results)
        completeness_scores = [r["completeness_score"] for r in self.condition_results.values() if "completeness_score" in r]
        avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
        conditions_meeting_target = sum(1 for s in completeness_scores if s >= 90)

        # Identify most common missing sections
        missing_section_counts = []
        for section in REQUIRED_SECTIONS:
            count = self.gap_patterns.get(f"missing_{section}", 0)
            if count > 0:
                missing_section_counts.append({"section": section, "count": count})

        missing_section_counts.sort(key=lambda x: x["count"], reverse=True)

        # Build JSON structure
        json_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "analyzer_version": "1.0",
                "total_conditions": total_conditions,
                "average_completeness": round(avg_completeness, 1),
                "target_completeness": 90,
                "conditions_meeting_target": conditions_meeting_target
            },
            "conditions": {},
            "priority_summary": self.priority_counts,
            "gap_patterns": {
                "most_missing_sections": missing_section_counts[:10],
                "conditions_needing_images": self.gap_patterns.get("needs_images", 0),
                "conditions_needing_citations": self.gap_patterns.get("needs_citations", 0),
                "conditions_missing_icd": self.gap_patterns.get("missing_icd", 0),
                "conditions_incomplete_quick_ref": self.gap_patterns.get("incomplete_quick_ref", 0)
            }
        }

        # Add condition details
        for slug, analysis in self.condition_results.items():
            json_data["conditions"][slug] = {
                "name": analysis.get("name", slug),
                "completeness_score": analysis.get("completeness_score", 0),
                "present_sections": analysis.get("present_sections", []),
                "missing_sections": analysis.get("missing_sections", []),
                "short_sections": analysis.get("short_sections", {}),
                "image_count": analysis.get("image_count", 0),
                "needs_images": analysis.get("needs_images", True),
                "citation_count": analysis.get("citation_count", 0),
                "needs_citations": analysis.get("needs_citations", True),
                "icd_codes_present": analysis.get("icd_codes_present", False),
                "quick_ref_complete": analysis.get("quick_ref_complete", False),
                "priority": analysis.get("priority", "high"),
                "estimated_hours": analysis.get("estimated_hours", 0)
            }

        return json_data

    def save_json_report(self, output_path: Path):
        """Save JSON report to file"""
        json_data = self.generate_json_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"JSON report saved to: {output_path}")
        return json_data


def main():
    """Main execution"""
    project_root = Path("/home/coolhand/servers/clinical")

    analyzer = ContentGapAnalyzer(project_root)
    analyzer.analyze_all_conditions()

    # Generate and save JSON
    json_output = project_root / "data" / "content-gaps.json"
    json_data = analyzer.save_json_report(json_output)

    # Print summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total conditions analyzed: {json_data['metadata']['total_conditions']}")
    print(f"Average completeness: {json_data['metadata']['average_completeness']}%")
    print(f"Conditions meeting 90% target: {json_data['metadata']['conditions_meeting_target']}")
    print(f"\nPriority breakdown:")
    print(f"  High priority: {analyzer.priority_counts['high']}")
    print(f"  Medium priority: {analyzer.priority_counts['medium']}")
    print(f"  Low priority: {analyzer.priority_counts['low']}")
    print(f"\nTop 5 missing sections:")
    for item in json_data['gap_patterns']['most_missing_sections'][:5]:
        print(f"  - {item['section']}: {item['count']}/{json_data['metadata']['total_conditions']} conditions")
    print("="*60)


if __name__ == "__main__":
    main()
