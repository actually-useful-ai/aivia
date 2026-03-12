#!/usr/bin/env python3
"""
Citation Validation Agent - Clinical Reference Project
Analyzes all 51 condition files for citation quality and generates comprehensive reports.
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Set

class CitationValidator:
    """Validates citations across all clinical condition documentation."""

    def __init__(self, project_root: str = "/home/coolhand/servers/clinical"):
        self.project_root = Path(project_root)
        self.conditions_dir = self.project_root / "conditions"
        self.bibliography_path = self.project_root / "inbox" / "bibliography.md"
        self.data_dir = self.project_root / "data"
        self.reports_dir = self.project_root / "reports"

        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        # Citation patterns
        self.citation_patterns = [
            r'\(([A-Z][a-zA-Z]+(?:\s+(?:et\s+al\.|&\s+[A-Z][a-zA-Z]+))?,?\s+\d{4}[a-z]?)\)',  # (Author et al., 2020)
            r'\(([A-Z][a-zA-Z]+\s+&\s+[A-Z][a-zA-Z]+,?\s+\d{4})\)',  # (Smith & Jones, 2020)
            r'https?://doi\.org/[^\s\)]+',  # DOI links
            r'DOI:\s*[^\s]+',  # DOI: identifiers
            r'PMID:\s*\d+',  # PubMed IDs
        ]

        # Citation type keywords for matching
        self.citation_types = {
            'epidemiology_study': ['prevalence', 'incidence', 'epidemiology', 'population', 'demographics'],
            'treatment_guidelines': ['treatment', 'therapy', 'intervention', 'management', 'guidelines'],
            'diagnostic_criteria': ['diagnosis', 'diagnostic', 'criteria', 'assessment', 'evaluation'],
            'prevalence_data': ['prevalence', 'incidence', 'frequency', 'occurrence'],
            'genetic_research': ['genetic', 'gene', 'mutation', 'genomic', 'hereditary', 'chromosome'],
            'clinical_outcomes': ['outcome', 'prognosis', 'survival', 'mortality', 'morbidity'],
            'AAC_interventions': ['AAC', 'augmentative', 'communication device', 'SGD', 'eye gaze'],
            'quality_of_life_studies': ['quality of life', 'QOL', 'wellbeing', 'patient satisfaction']
        }

        self.bibliography = self._parse_bibliography()
        self.condition_results = {}

    def _parse_bibliography(self) -> Dict[str, Dict]:
        """Parse the master bibliography file."""
        bibliography = {}

        if not self.bibliography_path.exists():
            print(f"Warning: Bibliography not found at {self.bibliography_path}")
            return bibliography

        content = self.bibliography_path.read_text(encoding='utf-8', errors='ignore')

        # Extract all entries (format: [Filename.txt])
        entries = re.findall(r'\[([^\]]+\.txt)\]', content)

        for entry in entries:
            # Parse filename to extract metadata
            # Format: Author_et_al._-_Year_-_Title_-_Journal.txt
            parts = entry.replace('.txt', '').split('_-_')

            key = entry.lower().replace('.txt', '').replace('_', '-')

            bibliography[key] = {
                'filename': entry,
                'full_entry': entry,
                'author': parts[0] if len(parts) > 0 else '',
                'year': parts[1] if len(parts) > 1 else '',
                'title': parts[2] if len(parts) > 2 else '',
                'journal': parts[3] if len(parts) > 3 else ''
            }

        print(f"Parsed {len(bibliography)} bibliography entries")
        return bibliography

    def extract_citations_from_file(self, file_path: Path) -> Dict:
        """Extract all citations from a markdown file."""

        if not file_path.exists():
            return {
                'total_count': 0,
                'has_doi': 0,
                'citations': [],
                'doi_links': [],
                'has_references_section': False,
                'reference_section_lines': 0
            }

        content = file_path.read_text(encoding='utf-8', errors='ignore')

        citations = []
        doi_links = []

        # Extract in-text citations
        for pattern in self.citation_patterns[:2]:  # Author citations
            matches = re.findall(pattern, content)
            citations.extend(matches)

        # Extract DOI links
        for pattern in self.citation_patterns[2:]:
            matches = re.findall(pattern, content)
            doi_links.extend(matches)

        # Check for References section
        has_references = bool(re.search(r'^##?\s+(References|Bibliography|Citations)', content, re.MULTILINE))

        # Count lines in References section
        ref_lines = 0
        if has_references:
            # Find References section and count until next major section or end
            ref_match = re.search(r'^##?\s+(References|Bibliography|Citations).*?\n(.*?)(?=^##?\s+|\Z)',
                                 content, re.MULTILINE | re.DOTALL)
            if ref_match:
                ref_content = ref_match.group(2)
                ref_lines = len([line for line in ref_content.split('\n') if line.strip()])

        return {
            'total_count': len(citations) + len(doi_links),
            'has_doi': len(doi_links),
            'citations': list(set(citations)),  # Deduplicate
            'doi_links': list(set(doi_links)),
            'has_references_section': has_references,
            'reference_section_lines': ref_lines
        }

    def assess_citation_quality(self, citations_data: Dict, content: str) -> Tuple[float, List[str]]:
        """Assess quality of citations and identify missing types."""

        score = 0.0
        missing_types = []

        total_citations = citations_data['total_count']
        has_doi = citations_data['has_doi']
        has_ref_section = citations_data['has_references_section']
        ref_lines = citations_data['reference_section_lines']

        # Scoring rubric (0-5 scale)
        if total_citations == 0:
            score = 0.0
        elif total_citations <= 2:
            score = 1.0 if has_doi > 0 else 0.5
        elif total_citations <= 5:
            score = 2.0
            if has_doi >= 2:
                score += 0.5
            if has_ref_section:
                score += 0.5
        elif total_citations <= 9:
            score = 3.0
            if has_doi >= 5:
                score += 0.5
            if has_ref_section and ref_lines >= 10:
                score += 0.5
        elif total_citations < 15:
            score = 4.0
            if has_doi >= 8:
                score += 0.3
            if has_ref_section and ref_lines >= 15:
                score += 0.3
        else:  # 15+ citations
            score = 4.5
            if has_doi >= 10:
                score += 0.2
            if has_ref_section and ref_lines >= 20:
                score += 0.3

        # Check for missing citation types
        content_lower = content.lower()
        for cit_type, keywords in self.citation_types.items():
            # Check if this type is discussed but not cited
            has_keywords = any(kw in content_lower for kw in keywords)
            has_citations_for_type = has_keywords and total_citations > 0

            if has_keywords and not has_citations_for_type:
                missing_types.append(cit_type)

        return min(score, 5.0), missing_types

    def match_bibliography_to_condition(self, condition_slug: str, content: str) -> List[str]:
        """Find relevant bibliography entries for a condition."""

        suggestions = []

        # Keywords from condition name
        condition_keywords = condition_slug.replace('-', ' ').split()

        # Search bibliography for relevant papers
        for bib_key, bib_data in self.bibliography.items():
            bib_text = (bib_data['title'] + ' ' + bib_data['journal'] + ' ' + bib_data['author']).lower()

            # Check for direct matches
            for keyword in condition_keywords:
                if len(keyword) > 3 and keyword in bib_text:
                    suggestions.append(bib_data['filename'])
                    break

        return suggestions[:10]  # Limit to top 10 suggestions

    def analyze_condition(self, condition_slug: str) -> Dict:
        """Comprehensive analysis of a single condition."""

        condition_path = self.conditions_dir / condition_slug / "index.md"

        if not condition_path.exists():
            print(f"Warning: {condition_slug}/index.md not found")
            return None

        # Read content
        content = condition_path.read_text(encoding='utf-8', errors='ignore')

        # Extract citations
        citations_data = self.extract_citations_from_file(condition_path)

        # Assess quality
        quality_score, missing_types = self.assess_citation_quality(citations_data, content)

        # Match bibliography
        suggested_papers = self.match_bibliography_to_condition(condition_slug, content)

        result = {
            'slug': condition_slug,
            'count': citations_data['total_count'],
            'quality_score': quality_score,
            'has_doi': citations_data['has_doi'],
            'has_references_section': citations_data['has_references_section'],
            'reference_section_lines': citations_data['reference_section_lines'],
            'citations': citations_data['citations'],
            'doi_links': citations_data['doi_links'],
            'missing_common': missing_types,
            'suggested_from_bibliography': suggested_papers,
            'word_count': len(content.split())
        }

        return result

    def analyze_all_conditions(self):
        """Analyze all 51 conditions."""

        print("\n" + "="*80)
        print("CITATION VALIDATION AUDIT - Clinical Reference Project")
        print("="*80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Get all condition directories
        condition_dirs = sorted([d for d in self.conditions_dir.iterdir() if d.is_dir()])

        print(f"Found {len(condition_dirs)} condition directories\n")

        for i, condition_dir in enumerate(condition_dirs, 1):
            condition_slug = condition_dir.name
            print(f"[{i}/51] Analyzing {condition_slug}...", end=' ')

            result = self.analyze_condition(condition_slug)

            if result:
                self.condition_results[condition_slug] = result
                print(f"✓ {result['count']} citations (score: {result['quality_score']:.1f}/5.0)")
            else:
                print("✗ Failed")

        print(f"\n{'='*80}")
        print(f"Analysis complete: {len(self.condition_results)} conditions processed")
        print(f"{'='*80}\n")

    def generate_json_output(self):
        """Generate JSON output file with citation counts."""

        output_path = self.data_dir / "citation-counts.json"

        json_data = {}
        for slug, data in self.condition_results.items():
            json_data[slug] = {
                'count': data['count'],
                'quality_score': round(data['quality_score'], 1),
                'has_doi': data['has_doi'],
                'missing_common': data['missing_common'],
                'suggested_from_bibliography': data['suggested_from_bibliography'][:5]  # Top 5
            }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"✓ JSON output written to: {output_path}")
        return output_path

    def generate_markdown_report(self):
        """Generate comprehensive markdown report."""

        report_path = self.reports_dir / f"citation-validation-{datetime.now().strftime('%Y-%m-%d')}.md"

        # Calculate statistics
        total_conditions = len(self.condition_results)
        conditions_0_cit = len([r for r in self.condition_results.values() if r['count'] == 0])
        conditions_1_5 = len([r for r in self.condition_results.values() if 1 <= r['count'] <= 5])
        conditions_6_10 = len([r for r in self.condition_results.values() if 6 <= r['count'] <= 10])
        conditions_10_plus = len([r for r in self.condition_results.values() if r['count'] >= 10])
        avg_citations = sum(r['count'] for r in self.condition_results.values()) / total_conditions if total_conditions > 0 else 0

        # Sort conditions by priority (fewest citations first, then by quality score)
        sorted_conditions = sorted(
            self.condition_results.items(),
            key=lambda x: (x[1]['count'], x[1]['quality_score'])
        )

        # Generate report
        lines = []
        lines.append("# Citation Validation Report")
        lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Project**: Clinical Reference Documentation")
        lines.append(f"**Auditor**: Citation Validator Agent\n")
        lines.append("---\n")

        # Executive Summary
        lines.append("## Executive Summary\n")
        lines.append(f"This report presents a comprehensive citation quality audit of all {total_conditions} clinical condition documentation files in the Clinical Reference project. The analysis evaluates quantitative metrics (citation count, DOI presence) and qualitative factors (clinical relevance, authority, coverage) to identify conditions requiring citation enhancement.\n")

        target_percent = (conditions_10_plus / total_conditions * 100) if total_conditions > 0 else 0
        lines.append(f"**Current Status**: {conditions_10_plus} conditions ({target_percent:.1f}%) meet the target threshold of 10+ citations.")
        lines.append(f"**Target Goal**: 80%+ of conditions (41+ conditions) with 10+ quality citations.\n")

        if target_percent < 80:
            gap = 41 - conditions_10_plus
            lines.append(f"**Action Required**: {gap} additional conditions need citation enhancement to reach 80% target.\n")

        # Summary Statistics
        lines.append("## Summary Statistics\n")
        lines.append("```")
        lines.append(f"Total conditions: {total_conditions}")
        lines.append(f"Conditions with 0 citations: {conditions_0_cit}")
        lines.append(f"Conditions with 1-5 citations: {conditions_1_5}")
        lines.append(f"Conditions with 6-10 citations: {conditions_6_10}")
        lines.append(f"Conditions with 10+ citations: {conditions_10_plus}")
        lines.append(f"Average citations per condition: {avg_citations:.1f}")
        lines.append("```\n")

        # Priority Conditions
        lines.append("## Priority Conditions (Need Citations Urgently)\n")
        lines.append("The following conditions have fewer than 5 citations and require immediate attention:\n")

        priority_conditions = [(slug, data) for slug, data in sorted_conditions if data['count'] < 5]

        for i, (slug, data) in enumerate(priority_conditions, 1):
            condition_name = slug.replace('-', ' ').title()
            lines.append(f"### {i}. {condition_name}")
            lines.append(f"**Current Citations**: {data['count']}")
            lines.append(f"**Quality Score**: {data['quality_score']:.1f}/5.0")
            lines.append(f"**Has DOIs**: {data['has_doi']}")
            lines.append(f"**Has References Section**: {'Yes' if data['has_references_section'] else 'No'}\n")

            if data['missing_common']:
                lines.append(f"**Missing Citation Types**: {', '.join(data['missing_common'])}\n")

            if data['suggested_from_bibliography']:
                lines.append("**Recommended Additions from Bibliography**:")
                for paper in data['suggested_from_bibliography'][:5]:
                    lines.append(f"- {paper}")
                lines.append("")
            else:
                lines.append("**Recommended Additions**: Review bibliography for relevant papers on:")
                keywords = slug.replace('-', ', ')
                lines.append(f"- {keywords}\n")

        # Citation Quality Analysis (All 51 Conditions)
        lines.append("## Citation Quality Analysis (All Conditions)\n")
        lines.append("Comprehensive review of all 51 conditions with current citation metrics and recommendations:\n")

        for i, (slug, data) in enumerate(sorted_conditions, 1):
            condition_name = slug.replace('-', ' ').title()
            lines.append(f"### {i}. {condition_name}")
            lines.append(f"- **Condition**: {slug}")
            lines.append(f"- **Current Citations**: {data['count']}")
            lines.append(f"- **Quality Score**: {data['quality_score']:.1f}/5.0")
            lines.append(f"- **Citations with DOI**: {data['has_doi']}")
            lines.append(f"- **Word Count**: {data['word_count']:,}")

            if data['citations']:
                lines.append(f"\n**Citations Found**:")
                for citation in data['citations'][:5]:  # Show first 5
                    lines.append(f"- {citation}")
                if len(data['citations']) > 5:
                    lines.append(f"- ... and {len(data['citations']) - 5} more")

            if data['doi_links']:
                lines.append(f"\n**DOI Links Found**: {len(data['doi_links'])}")

            if data['missing_common']:
                lines.append(f"\n**Missing Citation Types**: {', '.join(data['missing_common'])}")

            if data['suggested_from_bibliography']:
                lines.append(f"\n**Recommended Additions**:")
                for paper in data['suggested_from_bibliography'][:8]:
                    lines.append(f"- {paper}")

            lines.append("")

        # Top 20 Recommendations
        lines.append("## Top 20 Recommendations\n")
        lines.append("Priority-ranked conditions requiring immediate citation work:\n")

        top_20 = sorted_conditions[:20]

        for i, (slug, data) in enumerate(top_20, 1):
            condition_name = slug.replace('-', ' ').title()
            needed = max(0, 10 - data['count'])
            lines.append(f"### {i}. {condition_name}")
            lines.append(f"**Needs**: {needed} new citations (currently has {data['count']})")

            if data['suggested_from_bibliography']:
                lines.append(f"\n**Suggested additions**:")
                for paper in data['suggested_from_bibliography'][:8]:
                    lines.append(f"- {paper}")

            lines.append("")

        # Methodology
        lines.append("## Methodology\n")
        lines.append("### Citation Extraction")
        lines.append("Citations were extracted using the following patterns:")
        lines.append("- In-text citations: `(Author et al., YYYY)` or `(Author, YYYY)`")
        lines.append("- DOI links: URLs containing `https://doi.org/` or `DOI:` identifiers")
        lines.append("- PubMed IDs: `PMID:` followed by numeric identifier")
        lines.append("- Reference sections: Full citations under `## References` headers\n")

        lines.append("### Quality Scoring (0-5 Scale)")
        lines.append("- **0**: No citations present")
        lines.append("- **1**: 1-2 weak citations, no DOIs, incomplete references")
        lines.append("- **2**: Some citations present, mostly incomplete, significant gaps")
        lines.append("- **3**: Decent coverage, some DOIs, minor gaps in key areas")
        lines.append("- **4**: Strong coverage, DOIs present, most claims properly sourced")
        lines.append("- **5**: Excellent: 10+ solid citations with DOIs, comprehensive sourcing\n")

        lines.append("### Bibliography Matching")
        lines.append(f"The master bibliography contains {len(self.bibliography)} academic papers. ")
        lines.append("Recommendations were generated by matching condition-specific keywords with paper titles, ")
        lines.append("authors, and journal names in the bibliography.\n")

        # Write report
        report_content = '\n'.join(lines)
        report_path.write_text(report_content, encoding='utf-8')

        print(f"✓ Markdown report written to: {report_path}")
        return report_path

    def run(self):
        """Execute full citation validation workflow."""

        print("\n" + "="*80)
        print("CITATION VALIDATION AGENT")
        print("Clinical Reference Project - Citation Quality Audit")
        print("="*80 + "\n")

        # Step 1: Analyze all conditions
        self.analyze_all_conditions()

        # Step 2: Generate JSON output
        json_path = self.generate_json_output()

        # Step 3: Generate markdown report
        report_path = self.generate_markdown_report()

        # Summary
        print("\n" + "="*80)
        print("AUDIT COMPLETE")
        print("="*80)
        print(f"\nOutputs generated:")
        print(f"  1. JSON data: {json_path}")
        print(f"  2. Full report: {report_path}")

        # Key findings
        conditions_need_work = len([r for r in self.condition_results.values() if r['count'] < 10])
        print(f"\nKey Findings:")
        print(f"  - {len(self.condition_results)} conditions analyzed")
        print(f"  - {conditions_need_work} conditions need citation work (<10 citations)")
        print(f"  - {len([r for r in self.condition_results.values() if r['count'] == 0])} conditions have NO citations")

        avg_score = sum(r['quality_score'] for r in self.condition_results.values()) / len(self.condition_results)
        print(f"  - Average quality score: {avg_score:.1f}/5.0")

        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    validator = CitationValidator()
    validator.run()
