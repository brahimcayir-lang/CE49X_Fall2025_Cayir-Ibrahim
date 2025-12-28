"""
Convert Final_Report.md to HTML format optimized for PDF printing.
User can then use browser's Print to PDF function.
"""

import os
import markdown
from datetime import datetime

def convert_md_to_html():
    """Convert markdown to HTML with PDF-optimized styling."""
    
    if not os.path.exists('Final_Report.md'):
        print("ERROR: Final_Report.md not found!")
        return False
    
    # Read markdown
    with open('Final_Report.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_body = markdown.markdown(md_content, extensions=['extra', 'toc', 'tables'])
    
    # Fix image paths: markdown uses Outputs/AfterLLM/ but HTML needs ../Outputs/AfterLLM/
    import re
    html_body = re.sub(r'src="Outputs/', r'src="../Outputs/', html_body)
    
    # Ensure images are properly formatted - add figure captions styling
    # The markdown already converts ![alt](path) to <img>, we just need CSS
    # Replace italic text after images to use figure-caption class
    # Match pattern: <img> followed by <em>Figure X: ...</em>
    html_body = re.sub(
        r'(<img[^>]+>)\s*<p><em>(Figure \d+[abcde]?:[^<]+)</em></p>',
        r'\1\n<p class="figure-caption">\2</p>',
        html_body
    )
    html_body = re.sub(
        r'(<img[^>]+>)\s*<em>(Figure \d+[abcde]?:[^<]+)</em>',
        r'\1\n<p class="figure-caption">\2</p>',
        html_body
    )
    
    # Create full HTML document with PDF-optimized CSS
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CE49X Final Project Report</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 0;
            }}
            
            .page-break {{
                page-break-before: always;
            }}
            
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
            
            table {{
                page-break-inside: avoid;
            }}
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 11pt;
            line-height: 1.6;
            max-width: 210mm;
            margin: 0 auto;
            padding: 20mm;
            color: #000;
            background: #fff;
        }}
        
        h1 {{
            font-size: 20pt;
            font-weight: bold;
            margin-top: 20pt;
            margin-bottom: 12pt;
            color: #000;
            border-bottom: 2pt solid #000;
            padding-bottom: 5pt;
        }}
        
        h2 {{
            font-size: 16pt;
            font-weight: bold;
            margin-top: 16pt;
            margin-bottom: 8pt;
            color: #000;
            border-bottom: 1pt solid #666;
            padding-bottom: 3pt;
        }}
        
        h3 {{
            font-size: 14pt;
            font-weight: bold;
            margin-top: 12pt;
            margin-bottom: 6pt;
            color: #000;
        }}
        
        h4 {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 10pt;
            margin-bottom: 5pt;
        }}
        
        p {{
            margin: 6pt 0;
            text-align: justify;
        }}
        
        ul, ol {{
            margin: 8pt 0;
            padding-left: 25pt;
        }}
        
        li {{
            margin: 4pt 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12pt 0;
            font-size: 10pt;
        }}
        
        th, td {{
            border: 1pt solid #000;
            padding: 6pt;
            text-align: left;
        }}
        
        th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        code {{
            background-color: #f5f5f5;
            padding: 2pt 4pt;
            border-radius: 3pt;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }}
        
        pre {{
            background-color: #f5f5f5;
            padding: 10pt;
            border: 1pt solid #ddd;
            border-radius: 4pt;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 12pt auto;
            page-break-inside: avoid;
            border: 1pt solid #ddd;
        }}
        
        .figure-caption {{
            text-align: center;
            font-style: italic;
            font-size: 10pt;
            margin-top: 5pt;
            margin-bottom: 15pt;
            color: #333;
        }}
        
        blockquote {{
            border-left: 3pt solid #ccc;
            margin: 10pt 0;
            padding-left: 15pt;
            font-style: italic;
        }}
        
        hr {{
            border: none;
            border-top: 1pt solid #000;
            margin: 20pt 0;
        }}
        
        strong {{
            font-weight: bold;
        }}
        
        em {{
            font-style: italic;
        }}
        
        .toc {{
            background-color: #f9f9f9;
            padding: 15pt;
            margin: 20pt 0;
            border: 1pt solid #ddd;
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 5pt 0;
        }}
        
        .toc a {{
            color: #0066cc;
            text-decoration: none;
        }}
        
        .toc a:hover {{
            text-decoration: underline;
        }}
        
        @media print {{
            a {{
                color: #000 !important;
                text-decoration: none;
            }}
        }}
        
        .footer {{
            margin-top: 30pt;
            padding-top: 10pt;
            border-top: 1pt solid #ccc;
            font-size: 9pt;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    {html_body}
    
    <div class="footer">
        <p>CE49X Final Project - Civil Engineering & AI Integration: Analyzing Industry Trends through News & Media</p>
        <p>Boğaziçi University, Fall 2025 | Team: Hakan ARMAN, İbrahim ÇAYIR</p>
        <p>Generated: {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
</body>
</html>"""
    
    # Save HTML file
    output_file = 'Final_Report.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_doc)
    
    print(f"[SUCCESS] HTML file created: {output_file}")
    print("\nTo convert to PDF:")
    print("1. Open Final_Report.html in your web browser (Chrome, Edge, Firefox)")
    print("2. Press Ctrl+P (or Cmd+P on Mac)")
    print("3. Select 'Save as PDF' or 'Microsoft Print to PDF' as the printer")
    print("4. Click 'Save' to create Final_Report.pdf")
    print("\nThe HTML file is optimized for PDF printing with proper page breaks and formatting.")
    
    return True

if __name__ == "__main__":
    try:
        import markdown
    except ImportError:
        print("Installing markdown library...")
        import subprocess
        import sys
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'markdown'], check=True)
        import markdown
    
    convert_md_to_html()

