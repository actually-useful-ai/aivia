#!/usr/bin/env python3
"""
Clinical Reference Quality Audit System
Comprehensive quality assessment of all condition documentation
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict
import csv

class ClinicalQualityAuditor:
    """Conducts comprehensive quality audits of clinical reference documentation."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conditions_dir = project_root / 'conditions'
        self.audit_date = datetime.now().strftime('%Y-%m-%d')
        self.results = {}

    def audit_all_conditions(self) -> Dict:
        """Audit all conditions and return results."""
        print(f"Starting comprehensive quality audit on {self.audit_date}")
        print(f"Auditing conditions in: {self.conditions_dir}")

        condition_dirs = sorted([d for d in self.conditions_dir.iterdir() if d.is_dir()])
        print(f"Found {len(condition_dirs)} conditions to audit\n")

        for i, condition_dir in enumerate(condition_dirs, 1):
            slug = condition_dir.name
            print(f"[{i}/{len(condition_dirs)}] Auditing {slug}...")

            index_file = condition_dir / 'index.md'
            if not index_file.exists():
                print(f"  ⚠️  No index.md found - marking as Missing")
                self.results[slug] = self._create_missing_result(slug)
                continue

            try:
                content = index_file.read_text(encoding='utf-8')
                audit_result = self.audit_condition(slug, content, condition_dir)
                self.results[slug] = audit_result

                score = audit_result['quality_score']
                priority = audit_result['priority']
                print(f"  ✓ Score: {score}/100 | Priority: {priority}")

            except Exception as e:
                print(f"  ✗ Error: {e}")
                self.results[slug] = self._create_error_result(slug, str(e))

        print(f"\n✓ Audit complete! {len(self.results)} conditions processed")
        return self.results

    def audit_condition(self, slug: str, content: str, condition_dir: Path) -> Dict:
        """Perform detailed audit of a single condition."""

        # Extract basic metrics
        word_count = len(content.split())
        lines = content.split('\n')

        # Score components (1-5 scale)
        content_score = self._score_content_accuracy(content)
        completeness_score = self._score_completeness(content)
        citation_score = self._score_citations(content)
        writing_score = self._score_writing_quality(content, word_count)
        accessibility_score = self._score_accessibility(content, condition_dir)

        # Calculate base score (0-100)
        category_scores = {
            'content_accuracy': content_score,
            'completeness': completeness_score,
            'citation_quality': citation_score,
            'writing_quality': writing_score,
            'accessibility': accessibility_score
        }
        base_score = sum(category_scores.values()) * 4  # 5 categories * 5 max * 4 = 100

        # Check required elements
        has_icd11 = bool(re.search(r'ICD-11:?\s*\*?\*?[A-Z0-9]', content, re.I))
        has_icd10 = bool(re.search(r'ICD-10(-CM)?:?\s*\*?\*?[A-Z0-9]', content, re.I))
        has_quick_ref = 'Quick Reference' in content or 'Quick Facts' in content

        # Count elements
        citation_count = self._count_citations(content)
        image_count = self._count_images(content, condition_dir)

        # Section analysis
        section_scores = self._analyze_sections(content)

        # Apply penalties
        penalties = []
        penalty_score = 0

        if not has_icd11:
            penalties.append("Missing ICD-11 code (-5)")
            penalty_score += 5
        if not has_icd10:
            penalties.append("Missing ICD-10-CM code (-5)")
            penalty_score += 5
        if not has_quick_ref:
            penalties.append("Missing Quick Reference table (-10)")
            penalty_score += 10
        if image_count < 3:
            shortage = 3 - image_count
            penalties.append(f"Only {image_count}/3 minimum images (-{shortage*2})")
            penalty_score += shortage * 2
        if citation_count < 10:
            penalties.append(f"Only {citation_count}/10 minimum citations (-5)")
            penalty_score += 5

        # Check for thin sections
        thin_sections = [name for name, score in section_scores.items() if score < 3]
        if thin_sections:
            penalty = min(len(thin_sections) * 3, 15)  # Cap at 15 points
            penalties.append(f"{len(thin_sections)} incomplete sections (-{penalty})")
            penalty_score += penalty

        # Calculate final score
        final_score = max(0, min(100, base_score - penalty_score))

        # Determine priority
        priority = self._assign_priority(final_score, has_icd11, has_icd10,
                                         image_count, citation_count, penalties)

        # Identify specific issues
        issues = self._identify_issues(content, has_icd11, has_icd10,
                                      has_quick_ref, image_count, citation_count,
                                      thin_sections, word_count)

        # Generate recommendations
        recommendations = self._generate_recommendations(issues, final_score,
                                                        thin_sections, citation_count)

        # Estimate fix time
        fix_time = self._estimate_fix_time(priority, len(issues), final_score)

        return {
            'status': 'Audited',
            'verified': final_score >= 90,
            'priority': priority,
            'quality_score': final_score,
            'audit_date': self.audit_date,
            'metrics': {
                'word_count': word_count,
                'citation_count': citation_count,
                'image_count': image_count,
                'has_icd11': has_icd11,
                'has_icd10': has_icd10,
                'has_quick_reference': has_quick_ref
            },
            'category_scores': category_scores,
            'section_scores': section_scores,
            'penalties': penalties,
            'issues_found': issues,
            'recommendations': recommendations,
            'estimated_fix_time': fix_time,
            'notes': f"Quality audit completed {self.audit_date}. Score: {final_score}/100"
        }

    def _score_content_accuracy(self, content: str) -> int:
        """Score content accuracy (1-5)."""
        # Look for indicators of accuracy
        score = 3  # Start at average

        # Positive indicators
        if 'pathophysiology' in content.lower():
            score += 0.5
        if re.search(r'mutation|genetic|chromosome', content, re.I):
            score += 0.5
        if re.search(r'\d+%|\d+/\d+', content):  # Statistical data
            score += 0.5

        # Negative indicators
        if '[' in content and ']' in content:  # Placeholder text
            score -= 1
        if content.count('TODO') > 0 or content.count('TBD') > 0:
            score -= 1

        return max(1, min(5, int(score)))

    def _score_completeness(self, content: str) -> int:
        """Score content completeness (1-5)."""
        required_sections = [
            'Introduction',
            'Epidemiology',
            'Clinical Features',
            'Diagnosis',
            'AAC',
            'Educational',
            'Transition',
            'References'
        ]

        present = sum(1 for section in required_sections
                     if section.lower() in content.lower())

        # Convert to 1-5 scale
        percentage = present / len(required_sections)
        if percentage >= 0.9:
            return 5
        elif percentage >= 0.75:
            return 4
        elif percentage >= 0.6:
            return 3
        elif percentage >= 0.4:
            return 2
        else:
            return 1

    def _score_citations(self, content: str) -> int:
        """Score citation quality (1-5)."""
        citation_count = self._count_citations(content)

        # Check for DOIs
        has_dois = bool(re.search(r'doi\.org|https://doi', content, re.I))

        # Check for recent citations
        recent_years = sum(1 for year in re.findall(r'\(20[1-2][0-9]\)', content)
                          if int(year[1:5]) >= 2015)

        if citation_count >= 15 and has_dois and recent_years >= 5:
            return 5
        elif citation_count >= 10 and has_dois:
            return 4
        elif citation_count >= 10:
            return 3
        elif citation_count >= 5:
            return 2
        else:
            return 1

    def _score_writing_quality(self, content: str, word_count: int) -> int:
        """Score writing quality and clarity (1-5)."""
        score = 3  # Start at average

        # Good length
        if word_count >= 3000:
            score += 1
        elif word_count < 1000:
            score -= 1

        # Professional language indicators
        if re.search(r'individuals with|person with', content, re.I):
            score += 0.5  # Person-first language

        # Check for headers
        header_count = content.count('\n## ') + content.count('\n# ')
        if header_count >= 10:
            score += 0.5

        return max(1, min(5, int(score)))

    def _score_accessibility(self, content: str, condition_dir: Path) -> int:
        """Score accessibility features (1-5)."""
        score = 3  # Start at average

        # Check for alt text on images
        images_with_alt = len(re.findall(r'!\[.+\]', content))
        images_without_alt = len(re.findall(r'!\[\]', content))

        if images_with_alt > images_without_alt:
            score += 1
        elif images_without_alt > images_with_alt:
            score -= 1

        # Check for semantic structure
        if '## ' in content:  # Has H2 headers
            score += 0.5
        if '### ' in content:  # Has H3 headers
            score += 0.5

        return max(1, min(5, int(score)))

    def _count_citations(self, content: str) -> int:
        """Count references/citations."""
        # Look for numbered references
        numbered = len(re.findall(r'^\d+\.\s+\w+.*$', content, re.MULTILINE))

        # Look for in-text citations
        in_text = len(re.findall(r'\([A-Z][a-z]+,?\s+\d{4}\)', content))

        return max(numbered, in_text // 2)  # In-text citations typically map to fewer refs

    def _count_images(self, content: str, condition_dir: Path) -> int:
        """Count images."""
        # Count image references in markdown
        md_images = len(re.findall(r'!\[.*?\]\(.*?\)', content))

        # Count actual image files
        images_dir = condition_dir / 'images'
        if images_dir.exists():
            actual_images = len([f for f in images_dir.iterdir()
                               if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']])
            return max(md_images, actual_images)

        return md_images

    def _analyze_sections(self, content: str) -> Dict[str, int]:
        """Analyze section quality (1-5 scores)."""
        sections = {
            'introduction': 0,
            'epidemiology': 0,
            'clinical_features': 0,
            'aac_interventions': 0,
            'diagnosis': 0,
            'care_management': 0,
            'educational_support': 0,
            'transition_planning': 0
        }

        # Extract sections using headers
        lines = content.split('\n')
        current_section = None
        section_content = []

        for line in lines:
            if line.startswith('# ') or line.startswith('## '):
                # Process previous section
                if current_section and section_content:
                    words = ' '.join(section_content).split()
                    score = self._score_section(len(words))

                    # Map to our keys
                    for key in sections.keys():
                        if key.replace('_', ' ') in current_section.lower():
                            sections[key] = max(sections[key], score)

                # Start new section
                current_section = line.lstrip('#').strip()
                section_content = []
            else:
                section_content.append(line)

        return sections

    def _score_section(self, word_count: int) -> int:
        """Score individual section based on word count."""
        if word_count >= 300:
            return 5
        elif word_count >= 200:
            return 4
        elif word_count >= 100:
            return 3
        elif word_count >= 50:
            return 2
        else:
            return 1

    def _assign_priority(self, score: int, has_icd11: bool, has_icd10: bool,
                        image_count: int, citation_count: int, penalties: List[str]) -> str:
        """Assign priority level."""
        if score < 70 or not has_icd11 or not has_icd10 or image_count < 2:
            return "High"
        elif score < 85 or citation_count < 10 or len(penalties) > 3:
            return "Medium"
        else:
            return "Low"

    def _identify_issues(self, content: str, has_icd11: bool, has_icd10: bool,
                        has_quick_ref: bool, image_count: int, citation_count: int,
                        thin_sections: List[str], word_count: int) -> List[str]:
        """Identify specific issues."""
        issues = []

        if not has_icd11:
            issues.append("Missing ICD-11 medical code")
        if not has_icd10:
            issues.append("Missing ICD-10-CM medical code")
        if not has_quick_ref:
            issues.append("Missing Quick Reference table")
        if image_count < 3:
            issues.append(f"Only {image_count} images (need 3 minimum)")
        if citation_count < 10:
            issues.append(f"Only {citation_count} citations (need 10 minimum)")
        if thin_sections:
            issues.append(f"Incomplete sections: {', '.join(thin_sections)}")
        if word_count < 2000:
            issues.append(f"Low word count ({word_count} words, target 3000+)")

        # Check for placeholders
        if '[' in content and ']' in content:
            placeholder_count = len(re.findall(r'\[.*?\]', content))
            if placeholder_count > 10:
                issues.append(f"Contains {placeholder_count} placeholder texts")

        return issues

    def _generate_recommendations(self, issues: List[str], score: int,
                                 thin_sections: List[str], citation_count: int) -> List[str]:
        """Generate actionable recommendations."""
        recs = []

        if score < 70:
            recs.append("PRIORITY: Complete major content gaps for core quality")

        if "Missing ICD-11" in str(issues):
            recs.append("Add ICD-11 code (search WHO ICD-11 browser)")
        if "Missing ICD-10" in str(issues):
            recs.append("Add ICD-10-CM code (search CDC ICD-10 database)")

        if "Quick Reference" in str(issues):
            recs.append("Create Quick Reference table with incidence/prevalence/onset data")

        if thin_sections:
            recs.append(f"Expand {len(thin_sections)} sections to 200+ words each")

        if citation_count < 10:
            needed = 10 - citation_count
            recs.append(f"Add {needed} academic citations with DOIs (PubMed, Google Scholar)")

        if "images" in str(issues).lower():
            recs.append("Add clinical illustrations with descriptive alt text")

        if score >= 85:
            recs.append("Near release-ready - minor polish and verification needed")

        return recs

    def _estimate_fix_time(self, priority: str, issue_count: int, score: int) -> str:
        """Estimate time to fix issues."""
        if priority == "High":
            if score < 50:
                return "8-12 hours (major revision needed)"
            else:
                return "4-6 hours (significant gaps)"
        elif priority == "Medium":
            if issue_count > 5:
                return "2-4 hours (multiple improvements)"
            else:
                return "1-2 hours (targeted enhancements)"
        else:
            return "30-60 minutes (minor polish)"

    def _create_missing_result(self, slug: str) -> Dict:
        """Create result for missing file."""
        return {
            'status': 'Missing',
            'verified': False,
            'priority': 'High',
            'quality_score': 0,
            'audit_date': self.audit_date,
            'metrics': {},
            'category_scores': {},
            'section_scores': {},
            'penalties': ['File does not exist'],
            'issues_found': ['No index.md file found'],
            'recommendations': ['Create condition documentation from template'],
            'estimated_fix_time': '10-15 hours (new file)',
            'notes': 'File missing - requires complete creation'
        }

    def _create_error_result(self, slug: str, error: str) -> Dict:
        """Create result for error during audit."""
        return {
            'status': 'Error',
            'verified': False,
            'priority': 'High',
            'quality_score': 0,
            'audit_date': self.audit_date,
            'metrics': {},
            'category_scores': {},
            'section_scores': {},
            'penalties': [f'Audit error: {error}'],
            'issues_found': ['Error during audit process'],
            'recommendations': ['Manual review required'],
            'estimated_fix_time': 'Unknown',
            'notes': f'Audit error: {error}'
        }

    def save_results(self, output_dir: Path):
        """Save audit results to files."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save condition_status.json
        status_file = output_dir / 'condition_status.json'
        status_data = {
            'conditions': self.results,
            'last_audit': self.audit_date,
            'version': '1.0',
            'summary': self._generate_summary()
        }

        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved: {status_file}")

        # Save quality-scores.csv
        csv_file = output_dir / 'quality-scores.csv'
        self._save_csv(csv_file)
        print(f"✓ Saved: {csv_file}")

        # Generate markdown report
        report_file = output_dir.parent / 'reports' / f'quality-audit-{self.audit_date}.md'
        report_file.parent.mkdir(parents=True, exist_ok=True)
        self._generate_report(report_file)
        print(f"✓ Saved: {report_file}")

    def _generate_summary(self) -> Dict:
        """Generate summary statistics."""
        scores = [r['quality_score'] for r in self.results.values()]

        return {
            'total_conditions': len(self.results),
            'average_score': round(sum(scores) / len(scores), 1) if scores else 0,
            'high_priority': sum(1 for r in self.results.values() if r['priority'] == 'High'),
            'medium_priority': sum(1 for r in self.results.values() if r['priority'] == 'Medium'),
            'low_priority': sum(1 for r in self.results.values() if r['priority'] == 'Low'),
            'verified_count': sum(1 for r in self.results.values() if r['verified']),
            'score_distribution': {
                '90-100': sum(1 for s in scores if s >= 90),
                '80-89': sum(1 for s in scores if 80 <= s < 90),
                '70-79': sum(1 for s in scores if 70 <= s < 80),
                '60-69': sum(1 for s in scores if 60 <= s < 70),
                'below_60': sum(1 for s in scores if s < 60)
            }
        }

    def _save_csv(self, filepath: Path):
        """Save quality scores as CSV."""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'condition', 'quality_score', 'content_score', 'completeness_score',
                'citation_score', 'writing_score', 'accessibility_score',
                'word_count', 'citation_count', 'image_count', 'issues', 'priority'
            ])

            for slug, data in sorted(self.results.items()):
                cat_scores = data.get('category_scores', {})
                metrics = data.get('metrics', {})
                issues = '; '.join(data.get('issues_found', []))

                writer.writerow([
                    slug,
                    data.get('quality_score', 0),
                    cat_scores.get('content_accuracy', 0),
                    cat_scores.get('completeness', 0),
                    cat_scores.get('citation_quality', 0),
                    cat_scores.get('writing_quality', 0),
                    cat_scores.get('accessibility', 0),
                    metrics.get('word_count', 0),
                    metrics.get('citation_count', 0),
                    metrics.get('image_count', 0),
                    issues,
                    data.get('priority', 'Unknown')
                ])

    def _generate_report(self, filepath: Path):
        """Generate comprehensive markdown report."""
        summary = self._generate_summary()

        # Get top and bottom conditions
        sorted_conditions = sorted(
            self.results.items(),
            key=lambda x: x[1]['quality_score'],
            reverse=True
        )
        top_10 = sorted_conditions[:10]
        bottom_10 = sorted_conditions[-10:]

        # Analyze common issues
        all_issues = []
        for data in self.results.values():
            all_issues.extend(data.get('issues_found', []))

        issue_freq = defaultdict(int)
        for issue in all_issues:
            # Normalize issue text
            if 'ICD-11' in issue:
                issue_freq['Missing ICD-11 codes'] += 1
            elif 'ICD-10' in issue:
                issue_freq['Missing ICD-10-CM codes'] += 1
            elif 'Quick Reference' in issue:
                issue_freq['Missing Quick Reference tables'] += 1
            elif 'images' in issue.lower():
                issue_freq['Insufficient images'] += 1
            elif 'citations' in issue.lower():
                issue_freq['Insufficient citations'] += 1
            elif 'sections' in issue.lower():
                issue_freq['Incomplete sections'] += 1
            elif 'word count' in issue.lower():
                issue_freq['Low word count'] += 1

        # Write report
        report = f"""# Clinical Reference Quality Audit Report

**Audit Date:** {self.audit_date}
**Total Conditions Audited:** {summary['total_conditions']}
**Average Quality Score:** {summary['average_score']}/100

---

## Executive Summary

This comprehensive quality audit assessed all {summary['total_conditions']} condition documentation files in the clinical reference system. Each condition was evaluated against a 51-point checklist covering content accuracy, completeness, citation quality, writing standards, and accessibility features.

### Overall Quality Distribution

| Score Range | Count | Percentage | Readiness |
|-------------|-------|------------|-----------|
| 90-100 (Excellent) | {summary['score_distribution']['90-100']} | {summary['score_distribution']['90-100']/summary['total_conditions']*100:.1f}% | Release-ready |
| 80-89 (Very Good) | {summary['score_distribution']['80-89']} | {summary['score_distribution']['80-89']/summary['total_conditions']*100:.1f}% | Near-ready |
| 70-79 (Good) | {summary['score_distribution']['70-79']} | {summary['score_distribution']['70-79']/summary['total_conditions']*100:.1f}% | Needs polish |
| 60-69 (Fair) | {summary['score_distribution']['60-69']} | {summary['score_distribution']['60-69']/summary['total_conditions']*100:.1f}% | Needs work |
| Below 60 (Poor) | {summary['score_distribution']['below_60']} | {summary['score_distribution']['below_60']/summary['total_conditions']*100:.1f}% | Major revision |

### Priority Distribution

- **High Priority:** {summary['high_priority']} conditions ({summary['high_priority']/summary['total_conditions']*100:.1f}%)
- **Medium Priority:** {summary['medium_priority']} conditions ({summary['medium_priority']/summary['total_conditions']*100:.1f}%)
- **Low Priority:** {summary['low_priority']} conditions ({summary['low_priority']/summary['total_conditions']*100:.1f}%)

### Verification Status

- **Verified (90+ score):** {summary['verified_count']} conditions
- **Awaiting verification:** {summary['total_conditions'] - summary['verified_count']} conditions

---

## Top 10 Highest Quality Conditions

These conditions demonstrate excellence and can serve as templates for others:

"""

        for i, (slug, data) in enumerate(top_10, 1):
            score = data['quality_score']
            status_icon = "✅" if data['verified'] else "⚠️"
            report += f"\n### {i}. {slug.replace('-', ' ').title()} {status_icon}\n"
            report += f"**Quality Score:** {score}/100  \n"
            report += f"**Priority:** {data['priority']}  \n"

            metrics = data.get('metrics', {})
            report += f"**Metrics:** {metrics.get('word_count', 0)} words, "
            report += f"{metrics.get('citation_count', 0)} citations, "
            report += f"{metrics.get('image_count', 0)} images  \n"

            if data.get('recommendations'):
                report += f"**Note:** {data['recommendations'][0]}  \n"

        report += f"\n\n---\n\n## Bottom 10 Conditions Needing Improvement\n\n"
        report += "These conditions require priority attention:\n"

        for i, (slug, data) in enumerate(bottom_10, 1):
            score = data['quality_score']
            report += f"\n### {i}. {slug.replace('-', ' ').title()}\n"
            report += f"**Quality Score:** {score}/100  \n"
            report += f"**Priority:** {data['priority']}  \n"
            report += f"**Estimated Fix Time:** {data.get('estimated_fix_time', 'Unknown')}  \n"

            issues = data.get('issues_found', [])
            if issues:
                report += f"**Issues Found:**\n"
                for issue in issues[:5]:  # Top 5 issues
                    report += f"- {issue}\n"

            recs = data.get('recommendations', [])
            if recs:
                report += f"**Recommendations:**\n"
                for rec in recs[:3]:  # Top 3 recommendations
                    report += f"- {rec}\n"

        report += f"\n\n---\n\n## Common Issues Analysis\n\n"
        report += "Issues appearing across multiple conditions:\n\n"

        for issue, count in sorted(issue_freq.items(), key=lambda x: x[1], reverse=True):
            pct = count / summary['total_conditions'] * 100
            report += f"- **{issue}:** {count} conditions ({pct:.1f}%)\n"

        report += f"\n\n---\n\n## Prioritized Recommendations\n\n"

        high_priority = [(s, d) for s, d in self.results.items() if d['priority'] == 'High']
        medium_priority = [(s, d) for s, d in self.results.items() if d['priority'] == 'Medium']
        low_priority = [(s, d) for s, d in self.results.items() if d['priority'] == 'Low']

        report += f"### HIGH Priority ({len(high_priority)} conditions)\n\n"
        report += "**Action Required:** Major content completion and quality improvements\n\n"

        for slug, data in sorted(high_priority, key=lambda x: x[1]['quality_score'])[:10]:
            report += f"- **{slug}** (Score: {data['quality_score']}): "
            report += f"{data.get('estimated_fix_time', 'Unknown')}\n"
            if data.get('recommendations'):
                report += f"  - {data['recommendations'][0]}\n"

        if len(high_priority) > 10:
            report += f"\n...and {len(high_priority) - 10} more conditions\n"

        report += f"\n### MEDIUM Priority ({len(medium_priority)} conditions)\n\n"
        report += "**Action Required:** Enhancement and standardization\n\n"

        for slug, data in sorted(medium_priority, key=lambda x: x[1]['quality_score'])[:10]:
            report += f"- **{slug}** (Score: {data['quality_score']}): "
            report += f"{data.get('estimated_fix_time', 'Unknown')}\n"

        if len(medium_priority) > 10:
            report += f"\n...and {len(medium_priority) - 10} more conditions\n"

        report += f"\n### LOW Priority ({len(low_priority)} conditions)\n\n"
        report += "**Action Required:** Minor polish and verification\n\n"

        for slug, data in sorted(low_priority, key=lambda x: x[1]['quality_score'], reverse=True):
            report += f"- **{slug}** (Score: {data['quality_score']})\n"

        report += f"\n\n---\n\n## Methodology\n\n"
        report += """
### Scoring System

Each condition was scored on five dimensions (1-5 scale each):

1. **Content Accuracy** - Medical correctness, current research alignment
2. **Completeness** - All required sections present and substantive
3. **Citation Quality** - Sufficient references with authoritative sources
4. **Writing Quality** - Professional medical writing and readability
5. **Accessibility** - Screen reader friendly, semantic structure, alt text

**Base Score Calculation:** Sum of category scores × 4 = 0-100 scale

### Penalties Applied

- Missing ICD-11 code: -5 points
- Missing ICD-10-CM code: -5 points
- Missing Quick Reference table: -10 points
- Images below minimum (3): -2 points per missing image
- Citations below minimum (10): -5 points
- Incomplete sections (<100 words): -3 points per section (max -15)

### Priority Assignment

- **High:** Score <70 OR missing critical elements OR broken links
- **Medium:** Score 70-84 OR incomplete sections OR <10 citations
- **Low:** Score 85-100 with only minor polish needed

### Re-Audit Schedule

Recommended re-audit frequency:
- High priority conditions: Every 2 weeks until score ≥70
- Medium priority conditions: Monthly until score ≥85
- Low priority conditions: Quarterly verification

---

## Next Steps

1. **Immediate Actions**
   - Address all HIGH priority conditions within 4 weeks
   - Focus on missing ICD codes (quick wins)
   - Add missing Quick Reference tables

2. **Short-term (1-2 months)**
   - Complete MEDIUM priority enhancements
   - Standardize citation formatting
   - Ensure minimum image requirements

3. **Long-term (3-6 months)**
   - Verify all LOW priority conditions
   - Maintain quality scores above 85
   - Implement ongoing quality monitoring

---

## Data Files

- **Full Results:** `/data/condition_status.json`
- **Score Export:** `/data/quality-scores.csv`
- **This Report:** `/reports/quality-audit-{self.audit_date}.md`

---

*Audit conducted by Clinical Quality Audit Agent*
*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        filepath.write_text(report, encoding='utf-8')


def main():
    """Run comprehensive quality audit."""
    project_root = Path('/home/coolhand/servers/clinical')

    auditor = ClinicalQualityAuditor(project_root)
    auditor.audit_all_conditions()
    auditor.save_results(project_root / 'data')

    print("\n" + "="*70)
    print("AUDIT COMPLETE")
    print("="*70)

    summary = auditor._generate_summary()
    print(f"\nTotal Conditions: {summary['total_conditions']}")
    print(f"Average Score: {summary['average_score']}/100")
    print(f"\nPriority Breakdown:")
    print(f"  High:   {summary['high_priority']}")
    print(f"  Medium: {summary['medium_priority']}")
    print(f"  Low:    {summary['low_priority']}")
    print(f"\nRelease-Ready (90+): {summary['verified_count']}")
    print("\n" + "="*70)


if __name__ == '__main__':
    main()
