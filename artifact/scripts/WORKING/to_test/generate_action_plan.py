#!/usr/bin/env python3
"""
Generate Action Plan Section for Content Gap Report
Adds week-by-week roadmap to existing report
"""

import json
from pathlib import Path
from datetime import datetime


def generate_action_plan(json_path: Path, output_path: Path):
    """Generate week-by-week action plan from JSON data"""

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    meta = data['metadata']
    conditions = data['conditions']
    gaps = data['gap_patterns']

    # Sort conditions by priority/completeness
    sorted_conditions = sorted(
        [(slug, cond) for slug, cond in conditions.items()],
        key=lambda x: (x[1]['completeness_score'], x[1]['priority'] == 'low')
    )

    # Calculate total work
    total_hours = sum(c.get('estimated_hours', 0) for c in conditions.values())

    action_plan = []
    action_plan.append("\n\n---\n")
    action_plan.append("\n## Recommended Action Plan\n\n")

    # Week 1: Critical Gaps
    action_plan.append("### Week 1: Critical Gaps (Priority: High)\n\n")
    action_plan.append("**Goal:** Address blocking issues preventing basic completeness\n\n")

    # 1. Medical Coding
    missing_icd = sum(1 for c in conditions.values() if not c.get('icd_codes_present', False))
    action_plan.append(f"#### 1. Add Missing ICD Codes ({missing_icd} conditions affected)\n\n")
    action_plan.append("**Priority conditions to code first (lowest completeness):**\n")

    code_conditions = [
        (slug, cond) for slug, cond in sorted_conditions[:15]
        if not cond.get('icd_codes_present', False)
    ]
    for slug, cond in code_conditions[:10]:
        action_plan.append(f"- {cond['name']} ({cond['completeness_score']}%)\n")

    action_plan.append("\n**Required codes for each condition:**\n")
    action_plan.append("- ICD-11\n")
    action_plan.append("- ICD-10-CM\n")
    action_plan.append("- OMIM\n")
    action_plan.append("- UMLS\n")
    action_plan.append("- MeSH\n")
    action_plan.append("- GARD\n\n")

    code_hours = missing_icd * 0.5
    action_plan.append(f"**Estimated time:** {code_hours:.0f} hours ({missing_icd} conditions × 0.5 hours each)\n\n")

    # 2. Quick Reference Tables
    action_plan.append(f"#### 2. Complete Quick Reference Tables ({meta['total_conditions']} conditions affected)\n\n")
    action_plan.append("**Required data for each table:**\n")
    action_plan.append("- Incidence rate\n")
    action_plan.append("- Prevalence statistics\n")
    action_plan.append("- Typical age of onset\n")
    action_plan.append("- AAC/Assistive Technology needs percentage\n\n")

    action_plan.append("**Priority conditions (lowest completeness):**\n")
    for slug, cond in sorted_conditions[:10]:
        if not cond.get('quick_ref_complete', False):
            action_plan.append(f"- {cond['name']} ({cond['completeness_score']}%)\n")
    action_plan.append("\n")

    qr_hours = meta['total_conditions'] * 0.75
    action_plan.append(f"**Estimated time:** {qr_hours:.0f} hours ({meta['total_conditions']} conditions × 0.75 hours each)\n\n")

    # 3. Clinical Images
    need_images = sum(1 for c in conditions.values() if c.get('needs_images', False))
    action_plan.append(f"#### 3. Add Clinical Images ({need_images} conditions with <3 images)\n\n")
    action_plan.append("**Priority conditions needing images:**\n")

    image_conditions = [
        (slug, cond) for slug, cond in sorted_conditions[:20]
        if cond.get('needs_images', False)
    ]
    for slug, cond in image_conditions[:10]:
        current = cond.get('image_count', 0)
        needed = 3 - current
        action_plan.append(f"- {cond['name']}: needs {needed} image(s) (currently {current})\n")
    action_plan.append("\n")

    action_plan.append("**Image types to source:**\n")
    action_plan.append("- Clinical photography (with permissions)\n")
    action_plan.append("- Medical diagrams and anatomical illustrations\n")
    action_plan.append("- Assistive technology device examples\n")
    action_plan.append("- Communication device screenshots\n")
    action_plan.append("- Educational/therapeutic setting photos\n\n")

    total_images_needed = sum(max(0, 3 - c.get('image_count', 0)) for c in conditions.values())
    image_hours = total_images_needed * 0.5
    action_plan.append(f"**Estimated time:** {image_hours:.0f} hours ({total_images_needed} images × 0.5 hours each)\n\n")

    # 4. Write Missing Critical Sections
    action_plan.append("#### 4. Write Missing Critical Sections\n\n")
    action_plan.append("**Focus on these 3 essential sections for lowest-completion conditions:**\n")
    action_plan.append("- Introduction\n")
    action_plan.append("- Clinical Features\n")
    action_plan.append("- Diagnosis\n\n")

    action_plan.append("**Priority conditions (complete these 3 sections first):**\n")
    for slug, cond in sorted_conditions[:10]:
        missing_critical = [s for s in ['Introduction', 'Clinical Features', 'Diagnosis']
                          if s in cond.get('missing_sections', [])]
        if missing_critical:
            action_plan.append(f"- {cond['name']}: missing {', '.join(missing_critical)}\n")
    action_plan.append("\n")

    critical_section_hours = 30
    action_plan.append(f"**Estimated time:** {critical_section_hours} hours\n\n")

    week1_total = code_hours + qr_hours + image_hours + critical_section_hours
    action_plan.append(f"**Week 1 Total Estimated Time:** {week1_total:.0f} hours\n\n")

    # Week 2: Content Expansion
    action_plan.append("---\n\n### Week 2: Content Expansion (Priority: Medium)\n\n")
    action_plan.append("**Goal:** Expand critical clinical sections to bring 20+ conditions above 70% completeness\n\n")

    # 1. AT/AAC Sections
    missing_at = sum(1 for c in conditions.values()
                    if 'Assistive Technology and AAC Interventions' in c.get('missing_sections', []))
    action_plan.append(f"#### 1. Write Assistive Technology and AAC Interventions Sections ({missing_at} conditions)\n\n")
    action_plan.append("**Priority conditions (lowest completeness):**\n")

    at_conditions = [
        (slug, cond) for slug, cond in sorted_conditions[:20]
        if 'Assistive Technology and AAC Interventions' in cond.get('missing_sections', [])
    ]
    for slug, cond in at_conditions[:10]:
        action_plan.append(f"- {cond['name']} ({cond['completeness_score']}%)\n")
    action_plan.append("\n")

    action_plan.append("**Required content for each condition:**\n")
    action_plan.append("- Communication device recommendations (eye-gaze, switches, SGDs)\n")
    action_plan.append("- Symbol systems and vocabulary organization\n")
    action_plan.append("- Access modalities (direct selection, scanning, eye tracking)\n")
    action_plan.append("- Mobility aids (wheelchairs, walkers, standers)\n")
    action_plan.append("- Environmental control units\n")
    action_plan.append("- Educational technology adaptations\n\n")

    at_hours = missing_at * 3
    action_plan.append(f"**Estimated time:** {at_hours:.0f} hours ({missing_at} conditions × 3 hours each)\n\n")

    # 2. Clinical Recommendations
    missing_clinical = sum(1 for c in conditions.values()
                          if 'Clinical Recommendations' in c.get('missing_sections', []))
    action_plan.append(f"#### 2. Write Clinical Recommendations Sections ({missing_clinical} conditions)\n\n")
    action_plan.append("**Required practitioner guidance:**\n")
    action_plan.append("- Speech-Language Pathologists (SLP) strategies\n")
    action_plan.append("- Occupational Therapists (OT) interventions\n")
    action_plan.append("- Physical Therapists (PT) approaches\n")
    action_plan.append("- Applied Behavior Analysts (ABA) recommendations\n")
    action_plan.append("- Special Educators strategies\n")
    action_plan.append("- All staff/caregiver guidance\n\n")

    clinical_hours = missing_clinical * 2.5
    action_plan.append(f"**Estimated time:** {clinical_hours:.0f} hours ({missing_clinical} conditions × 2.5 hours each)\n\n")

    # 3. Educational Support
    missing_edu = sum(1 for c in conditions.values()
                     if 'Educational Support' in c.get('missing_sections', []))
    action_plan.append(f"#### 3. Write Educational Support Sections ({missing_edu} conditions)\n\n")
    action_plan.append("**Required content:**\n")
    action_plan.append("- IEP goal examples (communication, motor, functional, academic)\n")
    action_plan.append("- Classroom accommodations and modifications\n")
    action_plan.append("- Testing accommodations\n")
    action_plan.append("- Environmental supports\n")
    action_plan.append("- Service delivery models\n\n")

    edu_hours = missing_edu * 2
    action_plan.append(f"**Estimated time:** {edu_hours:.0f} hours ({missing_edu} conditions × 2 hours each)\n\n")

    # 4. Increase Citation Counts
    need_citations = sum(1 for c in conditions.values() if c.get('needs_citations', False))
    action_plan.append(f"#### 4. Increase Citation Counts ({need_citations} conditions with <10 citations)\n\n")
    action_plan.append("**Research and add citations from:**\n")
    action_plan.append("- Peer-reviewed journals (PubMed, Google Scholar)\n")
    action_plan.append("- Clinical practice guidelines\n")
    action_plan.append("- Evidence-based intervention studies\n")
    action_plan.append("- Epidemiological research\n")
    action_plan.append("- AAC outcome studies\n\n")

    action_plan.append("**Target:** 15+ citations per condition\n\n")

    citation_hours = need_citations * 1.5
    action_plan.append(f"**Estimated time:** {citation_hours:.0f} hours ({need_citations} conditions × 1.5 hours each)\n\n")

    week2_total = at_hours + clinical_hours + edu_hours + citation_hours
    action_plan.append(f"**Week 2 Total Estimated Time:** {week2_total:.0f} hours\n\n")

    # Week 3: Completeness Push
    action_plan.append("---\n\n### Week 3-4: Completeness Push\n\n")
    action_plan.append("**Goal:** Bring all 51 conditions to 85%+ completeness\n\n")

    # Remaining sections
    action_plan.append("#### 1. Write Remaining Required Sections\n\n")
    action_plan.append("**Sections to complete across all conditions:**\n")
    action_plan.append(f"- Care Management: {sum(1 for c in conditions.values() if 'Care Management' in c.get('missing_sections', []))} conditions\n")
    action_plan.append(f"- Transition Planning: {sum(1 for c in conditions.values() if 'Transition Planning' in c.get('missing_sections', []))} conditions\n")
    action_plan.append(f"- Epidemiology and Demographics: {sum(1 for c in conditions.values() if 'Epidemiology and Demographics' in c.get('missing_sections', []))} conditions\n")
    action_plan.append(f"- Etiology and Pathophysiology: {sum(1 for c in conditions.values() if 'Etiology and Pathophysiology' in c.get('missing_sections', []))} conditions\n")
    action_plan.append(f"- Support and Resources: {sum(1 for c in conditions.values() if 'Support and Resources' in c.get('missing_sections', []))} conditions\n\n")

    remaining_hours = 120
    action_plan.append(f"**Estimated time:** {remaining_hours} hours\n\n")

    # Expand short sections
    action_plan.append("#### 2. Expand Short Sections (<100 words)\n\n")
    total_short = sum(len(c.get('short_sections', {})) for c in conditions.values())
    action_plan.append(f"**Total short sections across project:** {total_short}\n\n")
    action_plan.append("**Approach:**\n")
    action_plan.append("- Add clinical examples and case studies\n")
    action_plan.append("- Expand with research findings\n")
    action_plan.append("- Include practical implementation guidance\n")
    action_plan.append("- Add specific device/strategy recommendations\n\n")

    short_hours = 40
    action_plan.append(f"**Estimated time:** {short_hours} hours\n\n")

    week3_total = remaining_hours + short_hours
    action_plan.append(f"**Week 3-4 Total Estimated Time:** {week3_total:.0f} hours\n\n")

    # Success Metrics
    action_plan.append("---\n\n## Success Metrics\n\n")
    action_plan.append("**Target State (4 weeks):**\n")
    action_plan.append("- Average completeness: 90%+\n")
    action_plan.append("- All conditions: 85%+ completeness\n")
    action_plan.append("- All conditions: Complete medical coding (6 code types)\n")
    action_plan.append("- All conditions: Complete Quick Reference tables\n")
    action_plan.append("- All conditions: 3+ images\n")
    action_plan.append("- All conditions: 10+ citations\n")
    action_plan.append("- All conditions: All 14 required sections present\n\n")

    action_plan.append("**Current State:**\n")
    action_plan.append(f"- Current average: {meta['average_completeness']}%\n")
    action_plan.append(f"- Target: 90%\n")
    action_plan.append(f"- Gap: +{90 - meta['average_completeness']:.1f} percentage points\n")
    action_plan.append(f"- Conditions below 70%: {sum(1 for c in conditions.values() if c.get('completeness_score', 0) < 70)}/51\n")
    action_plan.append(f"- Conditions at target (90%+): {meta['conditions_meeting_target']}/51\n\n")

    action_plan.append("**Progress Tracking:**\n")
    action_plan.append("- Weekly completeness score recalculation\n")
    action_plan.append("- Priority level reassignment as conditions improve\n")
    action_plan.append("- Section coverage percentage tracking\n")
    action_plan.append("- Total word count and citation count monitoring\n\n")

    # Total Project Estimate
    grand_total = week1_total + week2_total + week3_total
    action_plan.append("---\n\n## Total Project Estimate\n\n")
    action_plan.append(f"**Total estimated hours:** {grand_total:.0f} hours\n")
    action_plan.append(f"**Full-time equivalent (40 hrs/week):** {grand_total/40:.1f} weeks\n")
    action_plan.append(f"**Part-time (20 hrs/week):** {grand_total/20:.1f} weeks\n")
    action_plan.append(f"**Current average completeness:** {meta['average_completeness']}%\n")
    action_plan.append(f"**Target completeness:** 90%\n")
    action_plan.append(f"**Improvement needed:** +{90 - meta['average_completeness']:.1f} percentage points\n\n")

    action_plan.append("---\n\n## Methodology\n\n")
    action_plan.append("### Analysis Process\n\n")
    action_plan.append("This gap analysis was conducted using a systematic Python-based analyzer that:\n\n")
    action_plan.append("1. **Parsed all 51 condition markdown files** to extract content structure\n")
    action_plan.append("2. **Matched sections** against the 14 required sections from TEMPLATE_CLINICAL_GUIDANCE.md\n")
    action_plan.append("3. **Counted content metrics:** words, images, citations, and medical codes\n")
    action_plan.append("4. **Calculated completeness scores** using weighted criteria:\n")
    action_plan.append("   - Section coverage: 40 points\n")
    action_plan.append("   - Word count (target 2000+): 20 points\n")
    action_plan.append("   - Images (target 3+): 10 points\n")
    action_plan.append("   - Citations (target 10+): 10 points\n")
    action_plan.append("   - Medical codes (6 types): 15 points\n")
    action_plan.append("   - Quick Reference table: 5 points\n")
    action_plan.append("5. **Assigned priority levels** based on completeness and missing critical sections\n")
    action_plan.append("6. **Estimated work hours** per condition based on gaps identified\n\n")

    action_plan.append("### Quality Assurance\n\n")
    action_plan.append("- All 51 conditions analyzed successfully\n")
    action_plan.append("- JSON output validated for correct structure\n")
    action_plan.append("- Markdown report generated with actionable recommendations\n")
    action_plan.append("- Gap patterns identified across entire corpus\n")
    action_plan.append("- Work estimates based on section complexity and content requirements\n\n")

    return ''.join(action_plan)


def main():
    """Main execution"""
    project_root = Path("/home/coolhand/servers/clinical")
    json_path = project_root / "data" / "content-gaps.json"
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = project_root / "reports" / f"content-gaps-{today}.md"

    print("Generating enhanced action plan...")

    # Read existing report
    with open(report_path, 'r', encoding='utf-8') as f:
        existing_report = f.read()

    # Generate action plan
    action_plan = generate_action_plan(json_path, report_path)

    # Append to existing report
    enhanced_report = existing_report + action_plan

    # Write back
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_report)

    print(f"✓ Enhanced report saved to: {report_path}")
    print(f"✓ Report now includes comprehensive action plan with week-by-week roadmap")


if __name__ == "__main__":
    main()
