import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFReportGenerator:
    def __init__(self, filename="clinical_analysis_report.pdf"):
        self.filename = filename

    def generate_report(self, patient_name: str, measurements: dict, alerts: list, recommendations: list) -> str:
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1A365D'),
            alignment=1,
            spaceAfter=15
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4A5568'),
            alignment=1,
            spaceAfter=25
        )
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#2B6CB0'),
            spaceBefore=10,
            spaceAfter=8
        )
        
        body_style = ParagraphStyle(
            'BodyDark',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2D3748'),
            spaceAfter=6
        )

        elements.append(Paragraph("<b>Naqeeb412 HarmonizeAI™ Dentofacial Synergy</b>", title_style))
        elements.append(Paragraph("Enterprise Clinical Analysis Report | NAQclinixAI", subtitle_style))
        elements.append(Spacer(1, 10))

        patient_info = [
            [Paragraph("<b>اسم المريض / الحالة:</b>", body_style), Paragraph(patient_name, body_style)],
            [Paragraph("<b>تاريخ الإصدار:</b>", body_style), Paragraph("موسم رقمي نشط (2026)", body_style)]
        ]
        info_table = Table(patient_info, colWidths=[150, 350])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EDF2F7')),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 15))

        elements.append(Paragraph("القياسات التشريحية الحالية مقارنة بالمعايير المثالية", heading_style))
        data_table_content = [["المؤشر الإكلينيكي", "القيمة المقاسة", "المعيار النموذجي"]]
        for key, val in measurements.items():
            data_table_content.append([str(key), str(val), "المعيار المثالي (1.618 / الحدود الآمنة)"])
            
        meas_table = Table(data_table_content, colWidths=[180, 150, 170])
        meas_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F7FAFC')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ]))
        elements.append(meas_table)
        elements.append(Spacer(1, 15))

        elements.append(Paragraph("النتائج والفحوصات الآلية", heading_style))
        for alert in alerts:
            elements.append(Paragraph(f"• {alert}", body_style))
            
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("خطط العلاج المقترحة بالذكاء الاصطناعي", heading_style))
        for rec in recommendations:
            elements.append(Paragraph(f"✔️ {rec}", body_style))

        elements.append(Spacer(1, 40))
        
        signature_data = [
            [Paragraph("<b>توقيع الاستشاري / الطبيب المعالج:</b>", body_style), Paragraph("<b>ختم العيادة الرقمي:</b>", body_style)],
            [Paragraph("<br/><br/>___________________________", body_style), Paragraph("<br/><br/>___________________________", body_style)]
        ]
        sig_table = Table(signature_data, colWidths=[250, 250])
        sig_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        elements.append(sig_table)

        doc.build(elements)
        return self.filename
