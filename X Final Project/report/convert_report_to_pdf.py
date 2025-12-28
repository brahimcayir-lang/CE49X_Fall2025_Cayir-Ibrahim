"""
Script to convert Final_Report.md to PDF format.

Requirements:
- pip install markdown pypandoc
- OR use pandoc directly: pandoc Final_Report.md -o Final_Report.pdf

Alternative: Use online converter or VS Code extension "Markdown PDF"
"""

import subprocess
import os
import sys

def convert_with_pandoc():
    """Convert markdown to PDF using pandoc."""
    md_file = "Final_Report.md"
    pdf_file = "Final_Report.pdf"
    
    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found!")
        return False
    
    try:
        # Try pandoc command
        cmd = [
            "pandoc",
            md_file,
            "-o", pdf_file,
            "--pdf-engine=xelatex",  # Better Unicode support
            "-V", "geometry:margin=1in",
            "--toc",  # Table of contents
            "--highlight-style=tango"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully created {pdf_file}")
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ pandoc not found. Please install pandoc:")
        print("   Windows: Download from https://pandoc.org/installing.html")
        print("   Or use: choco install pandoc")
        print("\nAlternative: Use VS Code extension 'Markdown PDF'")
        return False

def convert_with_markdown_pdf_vscode():
    """Instructions for using VS Code Markdown PDF extension."""
    print("\n" + "="*60)
    print("ALTERNATIVE: Convert using VS Code")
    print("="*60)
    print("1. Install VS Code extension: 'Markdown PDF' by yzane")
    print("2. Open Final_Report.md in VS Code")
    print("3. Press Ctrl+Shift+P (Cmd+Shift+P on Mac)")
    print("4. Type 'Markdown PDF: Export (pdf)' and select it")
    print("5. PDF will be generated in the same directory")
    print("="*60)

if __name__ == "__main__":
    print("Converting Final_Report.md to PDF...\n")
    
    if not convert_with_pandoc():
        convert_with_markdown_pdf_vscode()

