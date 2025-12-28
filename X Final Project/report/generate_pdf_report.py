"""
Generate PDF from Final_Report.md using Python libraries.
Tries multiple methods: markdown + weasyprint, markdown + pdfkit, or markdown + reportlab
"""

import os
import sys
import subprocess

def try_weasyprint():
    """Try converting using weasyprint."""
    try:
        from weasyprint import HTML, CSS
        import markdown
        
        print("Using WeasyPrint to convert markdown to PDF...")
        
        # Read markdown
        with open('Final_Report.md', 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['extra', 'toc', 'codehilite'])
        
        # Add CSS styling
        html_with_style = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    size: A4;
                    margin: 1in;
                }}
                body {{
                    font-family: 'Times New Roman', serif;
                    font-size: 11pt;
                    line-height: 1.6;
                }}
                h1 {{
                    font-size: 20pt;
                    margin-top: 1em;
                    margin-bottom: 0.5em;
                    page-break-after: avoid;
                }}
                h2 {{
                    font-size: 16pt;
                    margin-top: 0.8em;
                    margin-bottom: 0.4em;
                    page-break-after: avoid;
                }}
                h3 {{
                    font-size: 14pt;
                    margin-top: 0.6em;
                    margin-bottom: 0.3em;
                    page-break-after: avoid;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1em 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    font-family: 'Courier New', monospace;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    overflow-x: auto;
                }}
            </style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        HTML(string=html_with_style).write_pdf('Final_Report.pdf')
        print("[SUCCESS] PDF created successfully: Final_Report.pdf")
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"❌ Error with WeasyPrint: {e}")
        return False

def try_markdown_pdf():
    """Try using markdown-pdf package via command line."""
    try:
        # Check if markdown-pdf is installed
        result = subprocess.run(['npm', 'list', '-g', 'markdown-pdf'], 
                              capture_output=True, text=True)
        if 'markdown-pdf' in result.stdout or result.returncode == 0:
            print("Using markdown-pdf to convert...")
            subprocess.run(['markdown-pdf', 'Final_Report.md', '-o', 'Final_Report.pdf'])
            if os.path.exists('Final_Report.pdf'):
                print("[SUCCESS] PDF created successfully: Final_Report.pdf")
                return True
        return False
    except:
        return False

def try_reportlab():
    """Try using reportlab with markdown parsing."""
    try:
        import markdown
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        print("Using ReportLab to convert markdown to PDF...")
        
        # Read markdown
        with open('Final_Report.md', 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Create PDF
        pdf_file = 'Final_Report.pdf'
        doc = SimpleDocTemplate(pdf_file, pagesize=A4,
                               rightMargin=1*inch, leftMargin=1*inch,
                               topMargin=1*inch, bottomMargin=1*inch)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#000000'),
            spaceAfter=12,
        )
        heading1_style = ParagraphStyle(
            'CustomH1',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#000000'),
            spaceAfter=10,
        )
        heading2_style = ParagraphStyle(
            'CustomH2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#000000'),
            spaceAfter=8,
        )
        
        # Build content
        story = []
        lines = md_content.split('\n')
        
        in_table = False
        table_data = []
        
        for line in lines:
            line = line.strip()
            
            # Handle headers
            if line.startswith('# '):
                story.append(Paragraph(line[2:], title_style))
                story.append(Spacer(1, 0.2*inch))
            elif line.startswith('## '):
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(line[3:], heading1_style))
                story.append(Spacer(1, 0.05*inch))
            elif line.startswith('### '):
                story.append(Paragraph(line[4:], heading2_style))
                story.append(Spacer(1, 0.03*inch))
            # Handle tables (simple)
            elif line.startswith('|') and '|' in line:
                if not in_table:
                    in_table = True
                    table_data = []
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                table_data.append(cells)
            elif in_table and not line.startswith('|'):
                # End of table
                if table_data:
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 0.1*inch))
                in_table = False
                table_data = []
            # Handle regular text
            elif line and not line.startswith('**') and not line.startswith('-'):
                # Simple paragraph
                if line:
                    story.append(Paragraph(line, styles['Normal']))
                    story.append(Spacer(1, 0.05*inch))
        
        # Build PDF
        doc.build(story)
        print("[SUCCESS] PDF created successfully: Final_Report.pdf")
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"❌ Error with ReportLab: {e}")
        import traceback
        traceback.print_exc()
        return False

def install_and_convert():
    """Try to install required packages and convert."""
    print("\nAttempting to install required packages...")
    print("Trying to install markdown and weasyprint...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'markdown', 'weasyprint'], 
                      check=True, capture_output=True)
        return try_weasyprint()
    except:
        print("❌ Could not install packages automatically.")
        return False

def main():
    # Set UTF-8 encoding for console output
    import sys
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    print("="*60)
    print("Converting Final_Report.md to PDF")
    print("="*60)
    
    if not os.path.exists('Final_Report.md'):
        print("[ERROR] Final_Report.md not found!")
        return
    
    # Try different methods
    if try_weasyprint():
        return
    
    if try_reportlab():
        return
    
    if try_markdown_pdf():
        return
    
    # If all fail, try installing and retrying
    if install_and_convert():
        return
    
    # Final fallback: instructions
    print("\n" + "="*60)
    print("[ERROR] Could not convert automatically.")
    print("="*60)
    print("\nPlease use one of these methods:\n")
    print("1. Install pandoc: https://pandoc.org/installing.html")
    print("   Then run: pandoc Final_Report.md -o Final_Report.pdf --toc")
    print("\n2. Install VS Code extension 'Markdown PDF'")
    print("   Then open Final_Report.md and export to PDF")
    print("\n3. Use online converter:")
    print("   https://www.markdowntopdf.com/")
    print("   Upload Final_Report.md and download PDF")
    print("\n4. Install Python packages manually:")
    print("   pip install markdown weasyprint")
    print("   Then run this script again")
    print("="*60)

if __name__ == "__main__":
    main()

