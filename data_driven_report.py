#!/usr/bin/env python3
"""
Data-Driven CEO Report Generator
Heavy planning -> Real data -> Real analysis -> Real report
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import tempfile
import numpy as np
from agents.chain_of_thought_agent import ChainOfThoughtReportAgent

class BoardRoomCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        num_pages = len(self._saved_page_states)
        for (page_num, state) in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            self._draw_page_decoration(page_num + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def _draw_page_decoration(self, page_num, total_pages):
        # Header line
        self.setStrokeColor(colors.HexColor('#1a1a1a'))
        self.setLineWidth(2)
        self.line(2*cm, A4[1] - 2*cm, A4[0] - 2*cm, A4[1] - 2*cm)
        
        self.setFont('Helvetica-Bold', 9)
        self.setFillColor(colors.HexColor('#1a1a1a'))
        self.drawRightString(A4[0] - 2*cm, A4[1] - 1.6*cm, "EXECUTIVE INTELLIGENCE")
        
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#cc0000'))
        self.drawString(2*cm, A4[1] - 1.6*cm, "CONFIDENTIAL")
        
        # Footer
        self.setStrokeColor(colors.HexColor('#cccccc'))
        self.setLineWidth(1)
        self.line(2*cm, 1.8*cm, A4[0] - 2*cm, 1.8*cm)
        
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#666666'))
        self.drawString(2*cm, 1.2*cm, datetime.now().strftime('%B %d, %Y'))
        self.drawCentredString(A4[0]/2, 1.2*cm, f"Page {page_num} of {total_pages}")
        self.drawRightString(A4[0] - 2*cm, 1.2*cm, "Data-Driven Analysis")

class DataDrivenReportGenerator:
    """
    Generates reports from REAL data analysis
    """
    
    def __init__(self, supabase_agent):
        self.supabase_agent = supabase_agent
        self.agent = ChainOfThoughtReportAgent(supabase_agent)
        self.temp_dir = tempfile.mkdtemp()
        self._setup_styles()
        
    def _setup_styles(self):
        self.styles = getSampleStyleSheet()
        
        # Professional Report Title
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=colors.HexColor('#1a365d'),
            alignment=TA_LEFT,
            spaceBefore=15,
            spaceAfter=20,
            leading=34,
            letterSpacing=0.5
        ))
        
        # Section Titles with accent line
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor('#2c5282'),
            spaceBefore=25,
            spaceAfter=15,
            leading=22,
            borderWidth=0,
            borderPadding=0,
            leftIndent=0
        ))
        
        # Body text - clean and readable
        self.styles.add(ParagraphStyle(
            name='ExecutiveBody',
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_JUSTIFY,
            spaceBefore=6,
            spaceAfter=12,
            leading=18,
            firstLineIndent=0
        ))
        
        # Bullet points style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_LEFT,
            spaceBefore=4,
            spaceAfter=4,
            leading=16,
            leftIndent=25,
            bulletIndent=10
        ))
        
        # Key Finding Title
        self.styles.add(ParagraphStyle(
            name='FindingTitle',
            fontName='Helvetica-Bold',
            fontSize=13,
            textColor=colors.HexColor('#2c5282'),
            spaceBefore=12,
            spaceAfter=6,
            leading=16
        ))
        
        # Highlight box for important info
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=10,
            leading=16,
            leftIndent=20,
            rightIndent=20,
            borderWidth=1,
            borderColor=colors.HexColor('#4299e1'),
            borderPadding=15,
            backColor=colors.HexColor('#ebf8ff')
        ))
        
        # Recommendation style
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=12,
            leading=17,
            leftIndent=20,
            bulletIndent=10
        ))
    
    def create_pdf_report(self, user_request: str) -> str:
        """
        Main entry: Generate complete data-driven report
        """
        
        # Step 1: Agent performs chain-of-thought analysis
        report_data = self.agent.generate_report(user_request)
        
        # Step 2: Create PDF from real data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Executive_Report_{timestamp}.pdf"
        filepath = os.path.join(self.temp_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2.5*cm,
            canvasmaker=BoardRoomCanvas
        )
        
        story = []
        
        # MANDATORY STRUCTURE - McKinsey/BCG Consulting Style
        # 1. Cover page with User Request
        story.extend(self._create_cover(report_data, user_request))
        
        # 2. Executive Summary (single focused paragraph)
        story.extend(self._create_executive_summary(report_data))
        
        # 3. Data Overview (metadata only)
        story.extend(self._create_data_overview(report_data))
        
        # 4. Key Metrics Dashboard
        story.extend(self._create_metrics_dashboard(report_data))
        
        # 5. Problem Identification (links to recommendations)
        if 'problems' in report_data['narrative_content']:
            story.extend(self._create_problems_section(report_data))
        
        # 6. Performance Analysis
        # 7. Critical Insights  
        # 8. Strategic Recommendations
        story.extend(self._create_content_sections(report_data))
        
        # 9. Next Steps for Leadership (Concluding section)
        if 'next_steps' in report_data['narrative_content']:
            story.extend(self._create_next_steps_section(report_data))
        
        # Build PDF with validation
        self._validate_no_duplication(report_data)
        doc.build(story)
        
        print(f"\n📄 PDF Generated: {filepath}")
        
        return filepath
    
    def _create_cover(self, report_data, user_request):
        content = []
        
        # Confidential header
        conf_style = ParagraphStyle(
            'Conf', fontName='Helvetica-Bold', fontSize=10,
            textColor=colors.HexColor('#e53e3e'), alignment=TA_LEFT,
            spaceBefore=0, spaceAfter=10
        )
        content.append(Paragraph("CONFIDENTIAL - EXECUTIVE USE ONLY", conf_style))
        
        # Add accent line
        from reportlab.platypus import HRFlowable
        content.append(HRFlowable(width="100%", thickness=3, color=colors.HexColor('#2c5282'), 
                                 spaceBefore=5, spaceAfter=15))
        
        content.append(Spacer(1, 0.6*inch))
        
        # Title with better styling
        title = report_data['title']
        content.append(Paragraph(title, self.styles['ReportTitle']))
        
        # Subtitle with icon-like element
        subtitle = f"""<font color='#4a5568'>
        <b>Sales Performance Analysis by City: Trends and Strategic Recommendations</b><br/>
        📊 Generated: {datetime.now().strftime('%B %d, %Y')}<br/>
        🔍 Powered by Advanced Analytics AI
        </font>"""
        sub_style = ParagraphStyle(
            'Sub', fontName='Helvetica', fontSize=12,
            textColor=colors.HexColor('#4a5568'), leading=20, spaceAfter=10
        )
        content.append(Paragraph(subtitle, sub_style))
        content.append(Spacer(1, 0.4*inch))
        
        # User request box with better styling
        request_text = f"""<para alignment='justify'>
        <font color='#2c5282'><b>ANALYSIS REQUEST</b></font><br/>
        <font color='#2d3748'>{user_request}</font>
        </para>"""
        req_style = ParagraphStyle(
            'Req', fontName='Helvetica', fontSize=11,
            alignment=TA_JUSTIFY, leftIndent=25, rightIndent=25,
            borderWidth=2, borderColor=colors.HexColor('#1a1a1a'),
            borderPadding=15, backColor=colors.HexColor('#f8f8f8'),
            spaceBefore=10, spaceAfter=20
        )
        content.append(Paragraph(request_text, req_style))
        
        content.append(PageBreak())
        
        return content
    
    def _create_executive_summary(self, report_data):
        content = []
        
        content.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionTitle']))
        from reportlab.platypus import HRFlowable
        content.append(HRFlowable(width="25%", thickness=2, color=colors.HexColor('#4299e1'),
                                 spaceBefore=3, spaceAfter=15, hAlign='LEFT'))
        
        exec_summary = report_data['narrative_content'].get('executive_summary', '')
        
        if exec_summary:
            exec_summary = self._clean_narrative_text(exec_summary)
            paragraphs = exec_summary.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para and not para.startswith('#'):
                    content.append(Paragraph(para, self.styles['ExecutiveBody']))
        
        content.append(Spacer(1, 0.2*inch))
        
        return content
    
    def _create_data_overview(self, report_data):
        """Data overview section"""
        content = []
        
        content.append(Paragraph("DATA OVERVIEW", self.styles['SectionTitle']))
        from reportlab.platypus import HRFlowable
        content.append(HRFlowable(width="25%", thickness=2, color=colors.HexColor('#4299e1'),
                                 spaceBefore=3, spaceAfter=15, hAlign='LEFT'))
        
        data_overview = report_data['narrative_content'].get('data_overview', '')
        
        if data_overview:
            data_overview = self._clean_narrative_text(data_overview)
            paragraphs = data_overview.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para and not para.startswith('#'):
                    content.append(Paragraph(para, self.styles['ExecutiveBody']))
        else:
            # Generate basic overview from datasets
            datasets = report_data.get('datasets', {})
            total_records = sum(len(df) for df in datasets.values())
            
            overview_text = f"""
This analysis is based on {total_records:,} records from {len(datasets)} dataset(s). 
The data has been extracted, validated, and analyzed to provide comprehensive insights 
supporting strategic decision-making.
"""
            content.append(Paragraph(overview_text.strip(), self.styles['ExecutiveBody']))
        
        content.append(Spacer(1, 0.2*inch))
        
        return content
    
    def _create_recommendations_section(self, report_data):
        """Recommendations section"""
        content = []
        
        content.append(Paragraph("STRATEGIC RECOMMENDATIONS", self.styles['SectionTitle']))
        from reportlab.platypus import HRFlowable
        content.append(HRFlowable(width="25%", thickness=2, color=colors.HexColor('#4299e1'),
                                 spaceBefore=3, spaceAfter=15, hAlign='LEFT'))
        
        # Check if there's a recommendations narrative
        narratives = report_data.get('narrative_content', {})
        sections = report_data['execution_plan'].get('report_sections', [])
        
        # Look for recommendations in section narratives
        has_recommendations = False
        for section in sections:
            if 'recommend' in section['title'].lower():
                if section['section_id'] in narratives:
                    narrative = narratives[section['section_id']]
                    if narrative:
                        narrative = self._clean_narrative_text(narrative)
                        paragraphs = narrative.split('\n\n')
                        for para in paragraphs:
                            para = para.strip()
                            if para and not para.startswith('#'):
                                # Check if numbered item for better formatting
                                if len(para) > 0 and para[0].isdigit() and '. ' in para[:5]:
                                    # Just use the para as-is since _clean_narrative_text already handled the bold
                                    content.append(Paragraph(para, self.styles['Recommendation']))
                                    content.append(Spacer(1, 0.12*inch))
                                else:
                                    content.append(Paragraph(para, self.styles['ExecutiveBody']))
                has_recommendations = True
                break
        
        if not has_recommendations:
            # Generic recommendations based on analysis
            rec_text = """
Based on the comprehensive data analysis, the following strategic actions are recommended:

<b>1. Focus on High-Performing Segments:</b> Allocate additional resources to top-performing 
categories identified in the analysis to maximize ROI and accelerate growth.

<b>2. Address Underperforming Areas:</b> Develop targeted improvement strategies for segments 
showing below-average performance, with specific KPIs for measuring progress.

<b>3. Implement Data-Driven Decision Making:</b> Establish regular review cycles using these 
metrics to track performance and adjust strategies accordingly.
"""
            content.append(Paragraph(rec_text.strip(), self.styles['ExecutiveBody']))
        
        content.append(Spacer(1, 0.2*inch))
        
        return content
    
    def _create_metrics_dashboard(self, report_data):
        content = []
        
        content.append(Paragraph("KEY PERFORMANCE METRICS", self.styles['SectionTitle']))
        from reportlab.platypus import HRFlowable
        content.append(HRFlowable(width="25%", thickness=2, color=colors.HexColor('#4299e1'),
                                 spaceBefore=3, spaceAfter=15, hAlign='LEFT'))
        
        analysis_results = report_data.get('analysis_results', {})
        datasets = report_data.get('datasets', {})
        
        metrics_data = []
        
        # Get metrics from analysis results - show ALL metrics
        if analysis_results:
            for analysis_id, result in analysis_results.items():
                metric_name = result.get('metric', analysis_id).replace('_', ' ').title()
                metric_value = result.get('formatted', str(result.get('value', 'N/A')))
                
                # Clean up metric value - remove raw data structures
                metric_value_str = str(metric_value)
                
                # If it looks like a dict/list (contains { or [), skip it or clean it
                if '{' in metric_value_str or '[' in metric_value_str:
                    # Try to extract just the numeric part if possible
                    import re
                    numbers = re.findall(r'[\d,]+\.?\d*', metric_value_str)
                    if numbers:
                        # Use first meaningful number
                        metric_value_str = numbers[0]
                    else:
                        # Skip this metric if we can't clean it
                        continue
                
                # Truncate very long strings
                if len(metric_value_str) > 50:
                    metric_value_str = metric_value_str[:47] + "..."
                
                metrics_data.append([metric_name, metric_value_str])
        
        # If still no metrics, calculate from datasets directly
        if not metrics_data and datasets:
            for dataset_id, df in datasets.items():
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                
                for col in list(numeric_cols)[:6]:  # Top 6 numeric columns
                    if col.lower() not in ['id', 'ordernumber', 'qtr_id', 'month_id', 'year_id']:
                        col_sum = float(df[col].sum())
                        col_avg = float(df[col].mean())
                        
                        metric_name = f"Total {col.replace('_', ' ').title()}"
                        if 'sales' in col.lower() or 'price' in col.lower() or 'revenue' in col.lower():
                            formatted_value = f"${col_sum:,.2f}"
                        else:
                            formatted_value = f"{col_sum:,.0f}"
                        
                        metrics_data.append([metric_name, formatted_value])
                        
                        # Add average too
                        avg_name = f"Average {col.replace('_', ' ').title()}"
                        if 'sales' in col.lower() or 'price' in col.lower() or 'revenue' in col.lower():
                            avg_formatted = f"${col_avg:,.2f}"
                        else:
                            avg_formatted = f"{col_avg:,.2f}"
                        
                        metrics_data.append([avg_name, avg_formatted])
        
        if metrics_data:
                # Limit to top 12 metrics for readability
                metrics_data = metrics_data[:12]
                
                metrics_table = Table(metrics_data, colWidths=[3.5*inch, 2*inch])
                
                # Alternating row colors for better readability
                table_style = [
                    ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                    ('FONTNAME', (1,0), (1,-1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 11),
                    ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#2d3748')),
                    ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor('#2c5282')),
                    ('ALIGN', (0,0), (0,-1), 'LEFT'),
                    ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 12),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 12),
                    ('LEFTPADDING', (0,0), (-1,-1), 15),
                    ('RIGHTPADDING', (0,0), (-1,-1), 15),
                ]
                
                # Add alternating row backgrounds
                for i in range(len(metrics_data)):
                    if i % 2 == 0:
                        table_style.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor('#f7fafc')))
                    # Add bottom border for each row
                    table_style.append(('LINEBELOW', (0,i), (-1,i), 0.5, colors.HexColor('#e2e8f0')))
                
                # Bold top border
                table_style.append(('LINEABOVE', (0,0), (-1,0), 2, colors.HexColor('#2c5282')))
                table_style.append(('LINEBELOW', (0,-1), (-1,-1), 2, colors.HexColor('#2c5282')))
                
                metrics_table.setStyle(TableStyle(table_style))
                content.append(metrics_table)
        
        content.append(Spacer(1, 0.2*inch))
        
        return content
    
    def _clean_narrative_text(self, text):
        """Clean narrative text by removing markdown and fixing special characters"""
        import re
        
        # Remove markdown headers (##, ###, etc.) at start of lines
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Fix **bold** markers - convert to <b>bold</b>
        # Use a more careful approach to avoid nesting issues
        text = re.sub(r'\*\*([^\*]+)\*\*', r'<b>\1</b>', text)
        
        # Fix escaped dollar signs \\$ -> $
        text = text.replace('\\$', '$')
        
        # Fix escaped characters
        text = text.replace('\\n', ' ')
        
        # Remove any remaining markdown-style emphasis
        text = text.replace('*', '')
        text = text.replace('_', '')
        
        return text.strip()
    
    def _create_content_sections(self, report_data):
        content = []
        
        sections = report_data['execution_plan'].get('report_sections', [])
        narratives = report_data.get('narrative_content', {})
        visualizations = report_data.get('visualizations', {})
        
        for section in sections:
            section_id = section['section_id']
            section_title = section['title']
            
            # Section header with accent line
            content.append(Paragraph(section_title.upper(), self.styles['SectionTitle']))
            from reportlab.platypus import HRFlowable
            content.append(HRFlowable(width="25%", thickness=2, color=colors.HexColor('#4299e1'),
                                     spaceBefore=3, spaceAfter=15, hAlign='LEFT'))
            
            # Process content items in order
            for content_item in section.get('content', []):
                if content_item.startswith('visualization:'):
                    viz_id = content_item.split(':')[1]
                    if viz_id in visualizations:
                        viz_path = visualizations[viz_id]
                        if os.path.exists(viz_path):
                            try:
                                img = RLImage(viz_path, width=6.5*inch, height=4*inch)
                                content.append(img)
                                content.append(Spacer(1, 0.15*inch))
                            except Exception as e:
                                print(f"⚠ Could not embed {viz_id}: {e}")
                
                elif content_item.startswith('narrative:'):
                    # Add section narrative with enhanced formatting
                    if section_id in narratives:
                        narrative = narratives[section_id]
                        if narrative:
                            # FIRST: Clean all markdown formatting
                            narrative = self._clean_narrative_text(narrative)
                            
                            # Split into paragraphs
                            paragraphs = narrative.split('\n\n')
                            for para in paragraphs:
                                para = para.strip()
                                if not para:
                                    continue
                                
                                # Check if it starts with markdown heading (###, ##, #)
                                if para.startswith('#'):
                                    # Remove the # markers and treat as heading
                                    para = para.lstrip('#').strip()
                                    if para:
                                        content.append(Paragraph(para, self.styles['FindingTitle']))
                                    continue
                                
                                # Check if it's a numbered list item
                                if len(para) > 0 and para[0].isdigit() and '. ' in para[:5]:
                                    # Don't add extra formatting - text is already cleaned with <b> tags
                                    content.append(Paragraph(para, self.styles['Recommendation']))
                                    content.append(Spacer(1, 0.12*inch))
                                
                                # Check if it's a bullet point (- or •)
                                elif para.startswith('•') or para.startswith('- '):
                                    bullet_text = para.lstrip('•-').strip()
                                    # Format bullet with bold if it has a colon
                                    if ':' in bullet_text:
                                        parts = bullet_text.split(':', 1)
                                        formatted = f"• <b>{parts[0]}:</b> {parts[1]}"
                                        content.append(Paragraph(formatted, self.styles['BulletPoint']))
                                    else:
                                        content.append(Paragraph(f"• {bullet_text}", self.styles['BulletPoint']))
                                
                                # Check if it's a heading (all caps or ends with colon)
                                elif para.isupper() or (para.endswith(':') and len(para) < 80):
                                    content.append(Paragraph(para, self.styles['FindingTitle']))
                                
                                # Regular paragraph
                                else:
                                    content.append(Paragraph(para, self.styles['ExecutiveBody']))
                            
                            content.append(Spacer(1, 0.1*inch))
                
                elif content_item.startswith('analysis:'):
                    # Analysis results already in metrics dashboard
                    pass
            
            content.append(Spacer(1, 0.15*inch))
        
        return content
    
    def _create_problems_section(self, report_data):
        """Problem Identification section"""
        content = []
        
        content.append(Paragraph("PROBLEM IDENTIFICATION", self.styles['SectionTitle']))
        from reportlab.platypus import HRFlowable
        content.append(HRFlowable(width="25%", thickness=2, color=colors.HexColor('#4299e1'),
                                 spaceBefore=3, spaceAfter=15, hAlign='LEFT'))
        
        problems = report_data['narrative_content'].get('problems', '')
        
        if problems:
            problems = self._clean_narrative_text(problems)
            paragraphs = problems.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para and not para.startswith('#'):
                    # Check for problem numbering
                    if 'Problem' in para and ':' in para:
                        content.append(Paragraph(para, self.styles['FindingTitle']))
                    elif para.startswith('-') or para.startswith('•'):
                        bullet_text = para[1:].strip()
                        content.append(Paragraph(f"• {bullet_text}", self.styles['BulletPoint']))
                    else:
                        content.append(Paragraph(para, self.styles['ExecutiveBody']))
            
            content.append(Spacer(1, 0.2*inch))
        
        return content
    
    def _create_next_steps_section(self, report_data):
        """Next Steps for Leadership concluding section"""
        content = []
        
        content.append(PageBreak())
        content.append(Paragraph("NEXT STEPS FOR LEADERSHIP", self.styles['SectionTitle']))
        from reportlab.platypus import HRFlowable
        content.append(HRFlowable(width="25%", thickness=2, color=colors.HexColor('#e53e3e'),
                                 spaceBefore=3, spaceAfter=15, hAlign='LEFT'))
        
        next_steps = report_data['narrative_content'].get('next_steps', '')
        
        if next_steps:
            next_steps = self._clean_narrative_text(next_steps)
            paragraphs = next_steps.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para and not para.startswith('#'):
                    # Check for section headers (all caps or ends with colon)
                    if para.isupper() or (para.endswith(':') and len(para) < 80):
                        content.append(Paragraph(para, self.styles['FindingTitle']))
                    elif para.startswith('-') or para.startswith('•'):
                        bullet_text = para[1:].strip()
                        # Format bullet with bold if it has a colon
                        if ':' in bullet_text:
                            parts = bullet_text.split(':', 1)
                            formatted = f"• <b>{parts[0]}:</b> {parts[1]}"
                            content.append(Paragraph(formatted, self.styles['BulletPoint']))
                        else:
                            content.append(Paragraph(f"• {bullet_text}", self.styles['BulletPoint']))
                    else:
                        content.append(Paragraph(para, self.styles['ExecutiveBody']))
            
            content.append(Spacer(1, 0.2*inch))
        
        return content
    
    def _validate_no_duplication(self, report_data):
        """Validate report has no duplicate sections or repeated content"""
        narratives = report_data.get('narrative_content', {})
        
        # Check for duplicate sections
        section_titles = []
        for section in report_data.get('execution_plan', {}).get('report_sections', []):
            title = section['title']
            if title in section_titles:
                print(f"⚠ WARNING: Duplicate section detected: {title}")
            section_titles.append(title)
        
        # Check for repeated long phrases (possible copy-paste)
        all_text = ' '.join([str(v) for v in narratives.values()])
        
        # Simple check: if same sentence appears multiple times
        sentences = all_text.split('. ')
        seen_sentences = {}
        for sentence in sentences:
            if len(sentence) > 50:  # Only check substantial sentences
                clean = sentence.strip().lower()
                if clean in seen_sentences:
                    seen_sentences[clean] += 1
                else:
                    seen_sentences[clean] = 1
        
        duplicates = {k: v for k, v in seen_sentences.items() if v > 1}
        if duplicates:
            print(f"⚠ WARNING: {len(duplicates)} repeated sentences detected in report")
        
        print("✓ Report validation complete")

# Compatibility
CEOGradeReportGenerator = DataDrivenReportGenerator
ProfessionalPDFReportGenerator = DataDrivenReportGenerator
