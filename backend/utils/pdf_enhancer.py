"""
Enhanced PDF Report Generator with Charts and Metrics
Generates professional PDF reports with matplotlib charts
"""

import io
from pathlib import Path
from typing import List, Dict
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak,
        Table, TableStyle, Image as RLImage
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-GUI backend
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class EnhancedPDFGenerator:
    """Generate enhanced PDF reports with charts and metrics"""

    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required. Install with: pip install reportlab")
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required. Install with: pip install matplotlib")

        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=HexColor('#667eea'),
            spaceAfter=30,
            alignment=1,  # Center
            fontName='Helvetica-Bold'
        )

        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=HexColor('#4a5568'),
            spaceBefore=20,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )

        # Subheading style
        self.subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=HexColor('#2d3748'),
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )

    def _create_severity_chart(self, results: List[Dict]) -> io.BytesIO:
        """Create severity distribution bar chart"""
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

        for item in results:
            severity = item.get('vulnerability', {}).get('severity', 'MEDIUM')
            if severity in severity_counts:
                severity_counts[severity] += 1

        # Filter out zero counts
        severities = [k for k, v in severity_counts.items() if v > 0]
        counts = [severity_counts[k] for k in severities]

        if not severities:
            return None

        # Create chart
        fig, ax = plt.subplots(figsize=(8, 5))
        colors_map = {'CRITICAL': '#ef4444', 'HIGH': '#f97316', 'MEDIUM': '#eab308', 'LOW': '#3b82f6'}
        bar_colors = [colors_map.get(s, '#6b7280') for s in severities]

        ax.bar(severities, counts, color=bar_colors, alpha=0.8, edgecolor='black')
        ax.set_xlabel('Severity Level', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Vulnerabilities', fontsize=12, fontweight='bold')
        ax.set_title('Vulnerability Severity Distribution', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for i, (sev, count) in enumerate(zip(severities, counts)):
            ax.text(i, count + 0.1, str(count), ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()

        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()

        return img_buffer

    def _create_type_pie_chart(self, results: List[Dict]) -> io.BytesIO:
        """Create vulnerability type distribution pie chart"""
        type_counts = {'SAST': 0, 'SCA': 0, 'DAST': 0}

        for item in results:
            vuln_type = item.get('type', 'UNKNOWN')
            if vuln_type in type_counts:
                type_counts[vuln_type] += 1

        # Filter out zero counts
        types = [k for k, v in type_counts.items() if v > 0]
        counts = [type_counts[k] for k in types]

        if not types:
            return None

        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        colors_map = ['#3b82f6', '#10b981', '#a855f7']  # Blue, Green, Purple
        explode = [0.05] * len(types)  # Slight separation

        wedges, texts, autotexts = ax.pie(
            counts,
            labels=types,
            colors=colors_map[:len(types)],
            autopct='%1.1f%%',
            explode=explode,
            shadow=True,
            startangle=90
        )

        # Enhance text
        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')

        ax.set_title('Scan Type Distribution', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()

        return img_buffer

    def _create_compliance_coverage_chart(self, compliance_analysis: Dict) -> io.BytesIO:
        """Create compliance coverage bar chart"""
        if not compliance_analysis:
            return None

        categories = []
        percentages = []

        # NIST CSF coverage
        if 'nist_csf' in compliance_analysis:
            nist = compliance_analysis['nist_csf']
            categories.append('NIST CSF')
            percentages.append(nist.get('coverage_percentage', 0))

        # ISO 27001 coverage
        if 'iso_27001' in compliance_analysis:
            iso = compliance_analysis['iso_27001']
            categories.append('ISO 27001')
            percentages.append(iso.get('coverage_percentage', 0))

        if not categories:
            return None

        # Create chart
        fig, ax = plt.subplots(figsize=(8, 5))
        bar_colors = ['#667eea', '#10b981']

        bars = ax.barh(categories, percentages, color=bar_colors[:len(categories)], alpha=0.8, edgecolor='black')
        ax.set_xlabel('Coverage Percentage (%)', fontsize=12, fontweight='bold')
        ax.set_title('Compliance Framework Coverage', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, 100)
        ax.grid(axis='x', alpha=0.3)

        # Add percentage labels
        for i, (cat, pct) in enumerate(zip(categories, percentages)):
            ax.text(pct + 2, i, f'{pct:.1f}%', va='center', fontweight='bold')

        plt.tight_layout()

        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()

        return img_buffer

    def generate_enhanced_pdf(
        self,
        pdf_path: Path,
        results: List[Dict],
        sast_vulns: List,
        sca_vulns: List,
        dast_vulns: List,
        compliance_analysis: Dict = None,
        evaluation_metrics: Dict = None
    ):
        """Generate enhanced PDF report with charts and metrics"""

        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        story = []

        # TITLE PAGE
        story.append(Paragraph("SecurAI Security Policy Report", self.title_style))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.5 * inch))

        # EXECUTIVE SUMMARY TABLE
        summary_data = [
            ['Metric', 'Value'],
            ['Total Vulnerabilities', str(len(sast_vulns) + len(sca_vulns) + len(dast_vulns))],
            ['SAST Findings', str(len(sast_vulns))],
            ['SCA Findings', str(len(sca_vulns))],
            ['DAST Findings', str(len(dast_vulns))],
            ['Policies Generated', str(len(results))],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f7fafc')]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.4 * inch))

        # SEVERITY DISTRIBUTION CHART
        story.append(Paragraph("Vulnerability Analysis", self.heading_style))
        severity_chart = self._create_severity_chart(results)
        if severity_chart:
            img = RLImage(severity_chart, width=6 * inch, height=3.5 * inch)
            story.append(img)
            story.append(Spacer(1, 0.3 * inch))

        # TYPE DISTRIBUTION CHART
        type_chart = self._create_type_pie_chart(results)
        if type_chart:
            img = RLImage(type_chart, width=6 * inch, height=4 * inch)
            story.append(img)
        story.append(PageBreak())

        # COMPLIANCE COVERAGE
        if compliance_analysis:
            story.append(Paragraph("Compliance Framework Coverage", self.heading_style))

            # Compliance table
            nist = compliance_analysis.get('nist_csf', {})
            iso = compliance_analysis.get('iso_27001', {})

            compliance_data = [
                ['Framework', 'Controls Covered', 'Total Controls', 'Coverage %'],
                [
                    'NIST CSF',
                    str(nist.get('covered_controls', 0)),
                    str(nist.get('total_controls', 0)),
                    f"{nist.get('coverage_percentage', 0):.1f}%"
                ],
                [
                    'ISO 27001',
                    str(iso.get('covered_controls', 0)),
                    str(iso.get('total_controls', 0)),
                    f"{iso.get('coverage_percentage', 0):.1f}%"
                ],
            ]

            compliance_table = Table(compliance_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
            compliance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f0fdf4')]),
            ]))
            story.append(compliance_table)
            story.append(Spacer(1, 0.3 * inch))

            # Compliance chart
            compliance_chart = self._create_compliance_coverage_chart(compliance_analysis)
            if compliance_chart:
                img = RLImage(compliance_chart, width=6 * inch, height=3.5 * inch)
                story.append(img)

            story.append(PageBreak())

        # QUALITY METRICS
        if evaluation_metrics:
            story.append(Paragraph("Policy Quality Metrics", self.heading_style))

            metrics_data = [
                ['Metric', 'Score', 'Description'],
                [
                    'BLEU-4',
                    f"{evaluation_metrics.get('avg_bleu', 0) * 100:.1f}%",
                    'Text similarity using n-gram precision'
                ],
                [
                    'ROUGE-L',
                    f"{evaluation_metrics.get('avg_rouge', 0) * 100:.1f}%",
                    'Longest common subsequence overlap'
                ],
                [
                    'Overall Quality',
                    f"{((evaluation_metrics.get('avg_bleu', 0) + evaluation_metrics.get('avg_rouge', 0)) * 50):.1f}%",
                    'Combined quality score'
                ],
            ]

            metrics_table = Table(metrics_data, colWidths=[2 * inch, 1.5 * inch, 3 * inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#8b5cf6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#faf5ff')]),
            ]))
            story.append(metrics_table)
            story.append(PageBreak())

        # LLM MODELS INFO
        story.append(Paragraph("AI Models Used", self.heading_style))
        story.append(Paragraph("• <b>LLaMA 3.3 70B (Groq)</b> - Used for SAST and SCA policy generation", self.styles['Normal']))
        story.append(Paragraph("• <b>LLaMA 3.1 8B Instant (Groq)</b> - Used for DAST policy generation", self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # INDIVIDUAL POLICIES
        story.append(Paragraph("Generated Security Policies", self.heading_style))
        story.append(Spacer(1, 0.2 * inch))

        for i, item in enumerate(results):
            vuln_type = item['type']
            llm_used = item.get('llm_used', 'Unknown')

            # Get title based on type
            if vuln_type == 'SAST':
                title = item['vulnerability'].get('title', 'Unknown')
            elif vuln_type == 'SCA':
                pkg = item['vulnerability'].get('package_name', 'Unknown')
                cve = item['vulnerability'].get('cve_id', 'Unknown')
                title = f"{pkg} - {cve}"
            elif vuln_type == 'DAST':
                title = item['vulnerability'].get('issue_type', 'Unknown')
            else:
                title = 'Unknown'

            # Policy header
            story.append(Paragraph(f"<b>Policy #{i + 1}: {vuln_type}</b>", self.subheading_style))
            story.append(Paragraph(f"<b>Title:</b> {title}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Severity:</b> {item['vulnerability'].get('severity', 'MEDIUM')}", self.styles['Normal']))
            story.append(Paragraph(f"<b>LLM Model:</b> {llm_used}", self.styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))

            # Policy content
            policy_text = item['policy'].replace('\n', '<br/>')
            story.append(Paragraph(policy_text, self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))

            if i < len(results) - 1:
                story.append(PageBreak())

        # Build PDF
        doc.build(story)
