#!/usr/bin/env python3
"""
Citation Validation Agent for Clinical Reference Project
Performs comprehensive citation audit across all 51 clinical conditions
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Set

class CitationAuditor:
    """Audits citations across clinical condition documentation"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conditions_dir = project_root / 'conditions'
        self.bibliography_path = project_root / 'inbox' / 'bibliography.md'
        self.results = {}
        self.bibliography_entries = []

    def extract_citations(self, content: str, condition_slug: str) -> Dict:
        """Extract all citations from markdown content"""

        # Find References section (try both H2 and H3)
        refs_match = re.search(r'###+\s+References.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        refs_section = refs_match.group(1) if refs_match else ""

        # Count different citation types
        citations = {
            'total': 0,
            'with_doi': 0,
            'with_pmid': 0,
            'with_url': 0,
            'full_references': [],
            'inline_citations': [],
            'quality_indicators': []
        }

        # Extract numbered/bulleted references
        ref_lines = []
        for line in refs_section.split('\n'):
            line = line.strip()
            # Match lines starting with: -, *, digit.
            # Also match lines that look like citations (have author names, years, DOIs, etc.)
            if line and (line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line)):
                ref_lines.append(line)
            elif line and (re.search(r'\b\d{4}\b', line) and  # Has a year
                          (re.search(r'doi\.org|DOI:', line, re.I) or  # Has DOI
                           re.search(r'http[s]?://', line) or  # Has URL
                           re.search(r'[A-Z][a-z]+,?\s+[A-Z]\.', line))):  # Has author format
                # Line looks like a citation even without leading marker
                ref_lines.append(line)

        citations['full_references'] = ref_lines
        citations['total'] = len(ref_lines)

        # Count DOIs
        doi_pattern = r'(?:https?://)?(?:dx\.)?doi\.org/[^\s)\]>]+'
        dois = re.findall(doi_pattern, content, re.IGNORECASE)
        citations['with_doi'] = len(set(dois))

        # Count PMIDs
        pmid_pattern = r'PMID:\s*\d+|pubmed/\d+'
        pmids = re.findall(pmid_pattern, content, re.IGNORECASE)
        citations['with_pmid'] = len(set(pmids))

        # Count URLs (academic sources)
        url_pattern = r'https?://[^\s)\]>]+'
        urls = re.findall(url_pattern, content)
        academic_urls = [u for u in urls if any(domain in u.lower() for domain in
                         ['pubmed', 'ncbi', 'doi.org', 'nature.com', 'science', 'elsevier',
                          'wiley', 'springer', 'oxford', 'nejm', 'jama', 'bmj', 'lancet'])]
        citations['with_url'] = len(set(academic_urls))

        # Extract inline citations (Author et al., YYYY)
        inline_pattern = r'\([A-Z][a-z]+(?:\s+et al\.)?,?\s+\d{4}[a-z]?\)'
        inline_cites = re.findall(inline_pattern, content)
        citations['inline_citations'] = list(set(inline_cites))

        # Look for quality indicators
        if re.search(r'\bmeta-analysis\b', content, re.IGNORECASE):
            citations['quality_indicators'].append('meta_analysis')
        if re.search(r'\bsystematic review\b', content, re.IGNORECASE):
            citations['quality_indicators'].append('systematic_review')
        if re.search(r'\brandomized controlled trial\b|RCT', content, re.IGNORECASE):
            citations['quality_indicators'].append('rct')
        if re.search(r'\bclinical guideline\b|\bguideline\b', content, re.IGNORECASE):
            citations['quality_indicators'].append('clinical_guidelines')

        return citations

    def assess_citation_quality(self, citations: Dict, content: str) -> Tuple[float, List[str]]:
        """
        Assess citation quality on 0-5 scale
        Returns: (score, missing_common_types)
        """
        score = 0.0
        missing_types = []

        # Base score from citation count
        total = citations['total']
        if total == 0:
            score = 0.0
        elif total <= 2:
            score = 1.0
        elif total <= 5:
            score = 2.0
        elif total <= 10:
            score = 3.0
        elif total <= 15:
            score = 4.0
        else:
            score = 4.5

        # Bonus points for DOIs/PMIDs (up to +0.5)
        if citations['with_doi'] > 0 or citations['with_pmid'] > 0:
            score += 0.2
            if citations['with_doi'] >= total * 0.5:  # 50%+ have DOIs
                score += 0.3

        # Bonus for quality indicators (up to +0.3)
        if citations['quality_indicators']:
            score += len(citations['quality_indicators']) * 0.1

        # Cap at 5.0
        score = min(5.0, score)

        # Identify missing citation types
        sections_to_check = {
            'epidemiology': r'##\s+Epidemiology|##\s+Demographics',
            'treatment': r'##\s+Treatment|##\s+Intervention|##\s+Management',
            'diagnosis': r'##\s+Diagnosis',
            'genetics': r'##\s+Etiology|##\s+Pathophysiology|##\s+Genetic',
            'aac': r'##\s+AAC|##\s+Assistive Technology',
            'outcomes': r'##\s+Prognosis|##\s+Outcomes'
        }

        for section_type, pattern in sections_to_check.items():
            if re.search(pattern, content, re.IGNORECASE):
                # Section exists - check if it has citations
                section_match = re.search(f'{pattern}.*?(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
                if section_match:
                    section_text = section_match.group(0)
                    # Check for citations in section
                    has_citation = bool(re.search(r'\([A-Z][a-z]+.*?\d{4}\)|doi\.org|PMID:', section_text))
                    if not has_citation:
                        if section_type == 'epidemiology':
                            missing_types.append('prevalence_data')
                        elif section_type == 'treatment':
                            missing_types.append('treatment_guidelines')
                        elif section_type == 'diagnosis':
                            missing_types.append('diagnostic_criteria')
                        elif section_type == 'genetics':
                            missing_types.append('genetic_research')
                        elif section_type == 'aac':
                            missing_types.append('AAC_interventions')
                        elif section_type == 'outcomes':
                            missing_types.append('clinical_outcomes')

        return round(score, 1), missing_types

    def parse_bibliography(self) -> List[Dict]:
        """Parse master bibliography file"""
        if not self.bibliography_path.exists():
            print(f"Warning: Bibliography not found at {self.bibliography_path}")
            return []

        content = self.bibliography_path.read_text(encoding='utf-8')
        entries = []

        # Extract filenames from markdown links [filename](path)
        # Pattern: [Some text](Filename.txt)
        link_pattern = r'\[(.*?)\]\((.*?)\)'

        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Try to extract markdown link
            match = re.search(link_pattern, line)
            if match:
                display_text = match.group(1)
                filename = match.group(2)

                # Parse filename for metadata
                # Format: Author_Author_Year_Title_Journal.txt
                filename_clean = filename.replace('.txt', '').replace('_', ' ')

                entries.append({
                    'text': display_text,
                    'filename': filename,
                    'searchable': filename_clean.lower(),
                    'display': display_text
                })
            elif line and not line.startswith('['):
                # Plain text line
                entries.append({
                    'text': line,
                    'filename': line,
                    'searchable': line.lower(),
                    'display': line
                })

        return entries

    def match_bibliography_to_condition(self, condition_slug: str, condition_content: str) -> List[str]:
        """Find relevant bibliography entries for a condition"""

        # Extract key terms from condition name
        condition_terms = condition_slug.replace('-', ' ').split()
        condition_terms = [t for t in condition_terms if len(t) > 3]  # Filter short words

        # Also extract key terms from content (condition name variations)
        title_match = re.search(r'^#\s+(.+?)$', condition_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
            # Extract meaningful words (capitalized, longer than 3 chars)
            title_terms = re.findall(r'\b[A-Z][a-z]+\b', title)
            condition_terms.extend(title_terms)

        # Deduplicate and clean terms
        condition_terms = list(set([t.lower() for t in condition_terms if len(t) > 3]))

        # Special handling for common abbreviations
        abbrev_map = {
            'rett': ['rett', 'mecp2'],
            'cdkl5': ['cdkl5', 'rett'],
            'cerebral': ['cerebral', 'palsy', 'cp'],
            'down': ['down', 'trisomy 21', 'chromosome 21'],
            'fragile': ['fragile x', 'fmr1', 'fragile'],
            'angelman': ['angelman', 'ube3a'],
            'prader': ['prader willi', 'prader', 'willi'],
            'turner': ['turner', 'monosomy x'],
            'williams': ['williams', 'williams syndrome'],
            'huntington': ['huntington', 'huntingtons'],
            'parkinson': ['parkinson', 'parkinsons'],
            'friedreich': ['friedreich', 'frda', 'ataxia'],
            'muscular': ['muscular dystrophy', 'dmd', 'becker'],
            'myasthenia': ['myasthenia', 'gravis', 'mg'],
            'multiple': ['multiple sclerosis', 'ms'] if 'sclerosis' in condition_slug else ['multiple system atrophy', 'msa'],
            'guillain': ['guillain barre', 'gbs'],
            'leigh': ['leigh', 'leigh syndrome'],
            'joubert': ['joubert', 'joubert syndrome'],
            'aicardi': ['aicardi', 'aicardi syndrome'],
            'foxg1': ['foxg1', 'rett'],
            'pura': ['pura', 'pura syndrome'],
        }

        # Expand terms based on abbreviations
        expanded_terms = condition_terms.copy()
        for term in condition_terms:
            if term in abbrev_map:
                expanded_terms.extend(abbrev_map[term])

        condition_terms = list(set(expanded_terms))

        # Search bibliography for matches
        suggestions = []
        scored_matches = []

        for entry in self.bibliography_entries:
            searchable = entry['searchable']
            score = 0

            # Count how many condition terms appear
            for term in condition_terms:
                if term in searchable:
                    score += 1

            if score > 0:
                scored_matches.append((score, entry['display']))

        # Sort by relevance score (descending)
        scored_matches.sort(reverse=True, key=lambda x: x[0])

        # Return top 10 suggestions with truncation for display
        suggestions = [display[:120] for score, display in scored_matches[:10]]

        return suggestions

    def analyze_condition(self, condition_slug: str) -> Dict:
        """Perform comprehensive citation analysis for one condition"""

        md_path = self.conditions_dir / condition_slug / 'index.md'
        if not md_path.exists():
            return None

        content = md_path.read_text(encoding='utf-8')

        # Extract citations
        citations = self.extract_citations(content, condition_slug)

        # Assess quality
        quality_score, missing_types = self.assess_citation_quality(citations, content)

        # Find bibliography suggestions
        bib_suggestions = self.match_bibliography_to_condition(condition_slug, content)

        result = {
            'count': citations['total'],
            'quality_score': quality_score,
            'has_doi': citations['with_doi'],
            'has_pmid': citations['with_pmid'],
            'inline_count': len(citations['inline_citations']),
            'missing_common': missing_types,
            'suggested_from_bibliography': bib_suggestions,
            'quality_indicators': citations['quality_indicators'],
            'full_references': citations['full_references'][:10]  # First 10
        }

        return result

    def run_audit(self) -> Dict:
        """Run complete audit across all conditions"""

        print("Starting citation audit...")
        print(f"Project root: {self.project_root}")
        print(f"Conditions directory: {self.conditions_dir}")

        # Load bibliography
        print("\nLoading bibliography...")
        self.bibliography_entries = self.parse_bibliography()
        print(f"Loaded {len(self.bibliography_entries)} bibliography entries")

        # Get all conditions
        conditions = sorted([d.name for d in self.conditions_dir.iterdir() if d.is_dir()])
        print(f"\nFound {len(conditions)} conditions to audit")

        # Analyze each condition
        results = {}
        for i, condition_slug in enumerate(conditions, 1):
            print(f"[{i}/{len(conditions)}] Analyzing {condition_slug}...")
            result = self.analyze_condition(condition_slug)
            if result:
                results[condition_slug] = result

        self.results = results
        return results

    def generate_markdown_report(self, output_path: Path):
        """Generate comprehensive markdown report"""

        # Calculate statistics
        total_conditions = len(self.results)
        conditions_with_0 = sum(1 for r in self.results.values() if r['count'] == 0)
        conditions_with_1_5 = sum(1 for r in self.results.values() if 1 <= r['count'] <= 5)
        conditions_with_6_10 = sum(1 for r in self.results.values() if 6 <= r['count'] <= 10)
        conditions_with_10plus = sum(1 for r in self.results.values() if r['count'] >= 10)
        avg_citations = sum(r['count'] for r in self.results.values()) / total_conditions if total_conditions > 0 else 0
        avg_quality = sum(r['quality_score'] for r in self.results.values()) / total_conditions if total_conditions > 0 else 0

        # Sort conditions by different criteria
        by_citation_count = sorted(self.results.items(), key=lambda x: x[1]['count'], reverse=True)
        by_quality_score = sorted(self.results.items(), key=lambda x: x[1]['quality_score'], reverse=True)
        priority_conditions = sorted(
            [(k, v) for k, v in self.results.items() if v['count'] < 5],
            key=lambda x: x[1]['count']
        )

        # Generate report
        report = f"""# Citation Validation Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Project**: Clinical Reference Documentation
**Auditor**: Citation Validation Agent

## Executive Summary

This report provides a comprehensive citation audit across all 51 clinical condition documentation pages. The audit evaluated citation quantity, quality, and coverage to identify gaps and prioritize citation enhancement efforts.

### Summary Statistics

```
Total conditions: {total_conditions}
Conditions with 0 citations: {conditions_with_0}
Conditions with 1-5 citations: {conditions_with_1_5}
Conditions with 6-10 citations: {conditions_with_6_10}
Conditions with 10+ citations: {conditions_with_10plus}
Average citations per condition: {avg_citations:.1f}
Average quality score: {avg_quality:.1f}/5.0
```

### Key Findings

- **{conditions_with_10plus}** conditions ({conditions_with_10plus/total_conditions*100:.1f}%) meet the 10+ citation target
- **{conditions_with_0 + conditions_with_1_5}** conditions ({(conditions_with_0 + conditions_with_1_5)/total_conditions*100:.1f}%) urgently need citation enhancement
- **Target Achievement**: Currently at {conditions_with_10plus/total_conditions*100:.1f}% of 80% goal

---

## Priority Conditions (Need Citations Urgently)

The following {len(priority_conditions)} conditions have fewer than 5 citations and require immediate attention:

"""

        for condition_slug, data in priority_conditions:
            condition_name = condition_slug.replace('-', ' ').title()
            report += f"### {condition_name}\n"
            report += f"- **Current Citations**: {data['count']}\n"
            report += f"- **Quality Score**: {data['quality_score']}/5.0\n"
            report += f"- **DOI Links**: {data['has_doi']}\n"
            report += f"- **Missing Coverage**: {', '.join(data['missing_common']) if data['missing_common'] else 'None identified'}\n"
            if data['suggested_from_bibliography']:
                report += f"- **Recommended Additions**:\n"
                for suggestion in data['suggested_from_bibliography'][:3]:
                    report += f"  - {suggestion}\n"
            report += "\n"

        report += "---\n\n## Complete Citation Quality Analysis\n\n"
        report += "Detailed analysis of all 51 conditions, sorted by quality score:\n\n"

        for condition_slug, data in by_quality_score:
            condition_name = condition_slug.replace('-', ' ').title()
            report += f"### {condition_name}\n\n"
            report += f"- **Condition Slug**: `{condition_slug}`\n"
            report += f"- **Current Citations**: {data['count']}\n"
            report += f"- **Quality Score**: {data['quality_score']}/5.0\n"
            report += f"- **Citations with DOI**: {data['has_doi']}\n"
            report += f"- **Citations with PMID**: {data['has_pmid']}\n"
            report += f"- **Inline Citations**: {data['inline_count']}\n"

            if data['quality_indicators']:
                report += f"- **Quality Indicators**: {', '.join(data['quality_indicators'])}\n"

            if data['full_references']:
                report += f"- **Citations Found**:\n"
                for ref in data['full_references'][:5]:  # Show first 5
                    report += f"  - {ref}\n"

            if data['missing_common']:
                report += f"- **Missing Coverage**: {', '.join(data['missing_common'])}\n"

            if data['suggested_from_bibliography']:
                report += f"- **Recommended Additions from Bibliography**:\n"
                for suggestion in data['suggested_from_bibliography']:
                    report += f"  - {suggestion}\n"

            report += "\n"

        report += "---\n\n## Top 20 Recommendations\n\n"
        report += "Conditions ranked by priority for citation enhancement:\n\n"

        # Create priority ranking
        priority_ranking = []
        for slug, data in self.results.items():
            # Priority score: lower is more urgent
            # Factors: low citation count (weight 3), low quality score (weight 2), missing types (weight 1)
            priority_score = (
                (10 - data['count']) * 3 +  # Fewer citations = higher priority
                (5 - data['quality_score']) * 2 +  # Lower quality = higher priority
                len(data['missing_common']) * 1  # More gaps = higher priority
            )
            priority_ranking.append((slug, data, priority_score))

        priority_ranking.sort(key=lambda x: x[2], reverse=True)

        for i, (slug, data, priority_score) in enumerate(priority_ranking[:20], 1):
            condition_name = slug.replace('-', ' ').title()
            needed = max(0, 10 - data['count'])
            report += f"**{i}. {condition_name}** needs {needed} new citations (Priority Score: {priority_score:.1f})\n\n"
            report += f"   - Current: {data['count']} citations, Quality: {data['quality_score']}/5.0\n"
            report += f"   - Missing: {', '.join(data['missing_common']) if data['missing_common'] else 'General research support'}\n"

            if data['suggested_from_bibliography']:
                report += f"   - **Suggested additions**:\n"
                for suggestion in data['suggested_from_bibliography'][:3]:
                    report += f"     - {suggestion}\n"
            report += "\n"

        report += "---\n\n## Conditions with Excellent Coverage (10+ Citations)\n\n"

        excellent = [(k, v) for k, v in by_citation_count if v['count'] >= 10]
        if excellent:
            for condition_slug, data in excellent:
                condition_name = condition_slug.replace('-', ' ').title()
                report += f"- **{condition_name}**: {data['count']} citations (Quality: {data['quality_score']}/5.0)\n"
        else:
            report += "*No conditions currently meet the 10+ citation threshold.*\n"

        report += "\n---\n\n## Methodology\n\n"
        report += """### Citation Extraction

Citations were identified using multiple patterns:
- In-text citations: `(Author et al., YYYY)` or `(Author, YYYY)`
- DOI links: `https://doi.org/` or `DOI:`
- PMID identifiers: `PMID: ` or PubMed URLs
- Reference sections: Full citations under `## References` headers
- Inline academic URLs: Links to journals, PubMed, etc.

### Quality Scoring (0-5 Scale)

- **0.0**: No citations present
- **1.0**: 1-2 weak citations, no DOIs, incomplete references
- **2.0**: Some citations present, mostly incomplete, significant gaps
- **3.0**: Decent coverage (6-10 citations), some DOIs, minor gaps
- **4.0**: Strong coverage (11-15 citations), DOIs present, most claims sourced
- **5.0**: Excellent (15+ citations with DOIs, clinical guidelines, comprehensive)

**Bonuses**:
- +0.2 for having any DOIs or PMIDs
- +0.3 additional if 50%+ of citations have DOIs
- +0.1 per quality indicator (meta-analysis, systematic review, RCT, clinical guidelines)

### Missing Citation Types

The following citation gaps are tracked:
- `prevalence_data`: Epidemiology sections lacking research support
- `treatment_guidelines`: Treatment sections without cited guidelines
- `diagnostic_criteria`: Diagnosis sections missing formal criteria citations
- `genetic_research`: Etiology sections without genetic research
- `AAC_interventions`: AAC sections lacking intervention research
- `clinical_outcomes`: Outcomes/prognosis sections without studies

---

## Action Plan

### Immediate Priorities (Next 2 Weeks)

1. **Address Zero-Citation Conditions**: {conditions_with_0} conditions have no references
2. **Strengthen Priority Conditions**: Focus on top 20 identified above
3. **Add DOI Links**: {sum(1 for r in self.results.values() if r['has_doi'] == 0)} conditions lack DOI-linked citations

### Medium-Term Goals (Next Month)

1. **Achieve 50% Coverage**: Get 25+ conditions to 10+ citations
2. **Quality Enhancement**: Raise average quality score from {avg_quality:.1f} to 3.5+
3. **Bibliography Integration**: Match and add relevant papers from master bibliography

### Long-Term Target (3 Months)

1. **80% Achievement**: 41+ conditions with 10+ citations
2. **Clinical Guidelines**: Ensure all conditions cite relevant clinical guidelines
3. **Recent Research**: Add 2020+ publications for currency

---

## Report Generated By

**Citation Validation Agent v1.0**
Automated clinical research auditor for medical documentation
Project: Clinical Reference Documentation System
Date: {datetime.now().strftime('%Y-%m-%d')}

---
"""

        # Write report
        output_path.write_text(report, encoding='utf-8')
        print(f"\nMarkdown report written to: {output_path}")

        return report

    def generate_json_output(self, output_path: Path):
        """Generate JSON file with citation counts"""

        json_data = {}
        for slug, data in self.results.items():
            json_data[slug] = {
                'count': data['count'],
                'quality_score': data['quality_score'],
                'has_doi': data['has_doi'],
                'has_pmid': data['has_pmid'],
                'missing_common': data['missing_common'],
                'suggested_from_bibliography': data['suggested_from_bibliography'][:3]  # Top 3
            }

        output_path.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
        print(f"JSON data written to: {output_path}")


def main():
    """Main execution"""

    # Use the actual project path from CLAUDE.md
    project_root = Path('/home/coolhand/servers/clinical')

    print("=" * 80)
    print("CITATION VALIDATION AGENT - Clinical Reference Project")
    print("=" * 80)

    auditor = CitationAuditor(project_root)

    # Run audit
    results = auditor.run_audit()

    # Generate outputs
    today = datetime.now().strftime('%Y-%m-%d')
    report_path = project_root / 'reports' / f'citation-validation-{today}.md'
    json_path = project_root / 'data' / 'citation-counts.json'

    print("\n" + "=" * 80)
    print("Generating outputs...")
    print("=" * 80)

    auditor.generate_markdown_report(report_path)
    auditor.generate_json_output(json_path)

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print(f"\nReports generated:")
    print(f"  - Markdown: {report_path}")
    print(f"  - JSON: {json_path}")

    # Print summary statistics
    total = len(results)
    with_10plus = sum(1 for r in results.values() if r['count'] >= 10)
    avg_citations = sum(r['count'] for r in results.values()) / total if total > 0 else 0
    avg_quality = sum(r['quality_score'] for r in results.values()) / total if total > 0 else 0

    print(f"\nSummary Statistics:")
    print(f"  Total conditions analyzed: {total}")
    print(f"  Conditions with 10+ citations: {with_10plus} ({with_10plus/total*100:.1f}%)")
    print(f"  Average citations per condition: {avg_citations:.1f}")
    print(f"  Average quality score: {avg_quality:.1f}/5.0")
    print(f"  Target achievement: {with_10plus/total*100:.1f}% of 80% goal")
    print()


if __name__ == '__main__':
    main()
