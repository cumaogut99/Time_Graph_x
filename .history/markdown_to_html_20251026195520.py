#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown to HTML Converter
Pandoc'a ihtiyaç duymadan Markdown'ı HTML'e çevirir
"""

import re
import sys
from pathlib import Path
from datetime import datetime

class MarkdownToHTML:
    """Gelişmiş Markdown → HTML dönüştürücü"""
    
    def __init__(self):
        self.toc = []  # Table of contents
        self.in_code_block = False
        self.code_language = ""
        
    def convert_file(self, input_file: str, output_file: str, css_file: str = None):
        """Markdown dosyasını HTML'e çevir"""
        try:
            # Markdown dosyasını oku
            with open(input_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # HTML'e çevir
            html_body = self.convert_markdown(markdown_content)
            
            # TOC oluştur
            toc_html = self.generate_toc()
            
            # CSS içeriğini al
            css_content = ""
            if css_file and Path(css_file).exists():
                with open(css_file, 'r', encoding='utf-8') as f:
                    css_content = f.read()
            
            # Tam HTML sayfası oluştur
            full_html = self.create_html_page(html_body, toc_html, css_content)
            
            # HTML dosyasına yaz
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            print(f"✅ HTML oluşturuldu: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            return False
    
    def convert_markdown(self, markdown: str) -> str:
        """Markdown içeriğini HTML'e çevir"""
        lines = markdown.split('\n')
        html_lines = []
        
        for line in lines:
            html_line = self.convert_line(line)
            if html_line:
                html_lines.append(html_line)
        
        return '\n'.join(html_lines)
    
    def convert_line(self, line: str) -> str:
        """Tek satırı HTML'e çevir"""
        # Boş satır
        if not line.strip():
            return '<p></p>' if not self.in_code_block else line
        
        # Code block başlangıç/bitiş
        if line.strip().startswith('```'):
            if self.in_code_block:
                self.in_code_block = False
                return '</code></pre>'
            else:
                self.in_code_block = True
                self.code_language = line.strip()[3:].strip()
                lang_class = f' class="language-{self.code_language}"' if self.code_language else ''
                return f'<pre><code{lang_class}>'
        
        # Code block içi
        if self.in_code_block:
            return self.escape_html(line)
        
        # Başlıklar (H1-H6)
        if line.startswith('#'):
            return self.convert_heading(line)
        
        # Horizontal rule
        if line.strip() in ['---', '***', '___']:
            return '<hr>'
        
        # Blockquote
        if line.startswith('>'):
            content = line[1:].strip()
            content = self.convert_inline(content)
            return f'<blockquote><p>{content}</p></blockquote>'
        
        # Liste (unordered)
        if re.match(r'^[\-\*\+]\s', line):
            content = re.sub(r'^[\-\*\+]\s', '', line)
            content = self.convert_inline(content)
            return f'<ul><li>{content}</li></ul>'
        
        # Liste (ordered)
        if re.match(r'^\d+\.\s', line):
            content = re.sub(r'^\d+\.\s', '', line)
            content = self.convert_inline(content)
            return f'<ol><li>{content}</li></ol>'
        
        # Tablo satırı
        if '|' in line:
            return self.convert_table_row(line)
        
        # Normal paragraf
        content = self.convert_inline(line)
        return f'<p>{content}</p>'
    
    def convert_heading(self, line: str) -> str:
        """Başlık dönüştür ve TOC'a ekle"""
        level = len(re.match(r'^#+', line).group())
        content = line.lstrip('#').strip()
        
        # ID oluştur (URL-friendly)
        heading_id = re.sub(r'[^\w\s-]', '', content.lower())
        heading_id = re.sub(r'[-\s]+', '-', heading_id)
        
        # TOC'a ekle
        self.toc.append({
            'level': level,
            'text': content,
            'id': heading_id
        })
        
        # HTML oluştur
        content = self.convert_inline(content)
        return f'<h{level} id="{heading_id}">{content}</h{level}>'
    
    def convert_inline(self, text: str) -> str:
        """Inline markdown elementleri çevir"""
        # Emoji'leri koru (📸, ✅, vb.)
        # Hiçbir şey yapmaya gerek yok, UTF-8 zaten destekliyor
        
        # Bold (**text** veya __text__)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        
        # Italic (*text* veya _text_)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        
        # Inline code (`code`)
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        
        # Links ([text](url))
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
        
        # Images (![alt](url))
        text = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1" />', text)
        
        # Keyboard shortcuts (Ctrl+O)
        text = re.sub(r'\b(Ctrl|Alt|Shift)\+([A-Z0-9])\b', r'<kbd>\1+\2</kbd>', text)
        
        return text
    
    def convert_table_row(self, line: str) -> str:
        """Tablo satırı çevir"""
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        
        # Header/separator kontrolü
        if all(re.match(r'^[\-:]+$', cell) for cell in cells):
            return ''  # Separator satırını atla
        
        # Header row mu?
        is_header = line.strip().startswith('|')
        tag = 'th' if is_header else 'td'
        
        cells_html = ''.join(f'<{tag}>{self.convert_inline(cell)}</{tag}>' for cell in cells)
        return f'<tr>{cells_html}</tr>'
    
    def generate_toc(self) -> str:
        """İçindekiler (Table of Contents) oluştur"""
        if not self.toc:
            return ""
        
        toc_html = ['<nav id="TOC">', '<h2>📋 İçindekiler</h2>', '<ul>']
        
        current_level = 1
        for item in self.toc:
            level = item['level']
            
            # Seviye değişikliklerini yönet
            if level > current_level:
                for _ in range(level - current_level):
                    toc_html.append('<ul>')
            elif level < current_level:
                for _ in range(current_level - level):
                    toc_html.append('</ul>')
            
            current_level = level
            
            # TOC item
            toc_html.append(f'<li><a href="#{item["id"]}">{item["text"]}</a></li>')
        
        # Kalan ul'ları kapat
        for _ in range(current_level - 1):
            toc_html.append('</ul>')
        
        toc_html.extend(['</ul>', '</nav>'])
        return '\n'.join(toc_html)
    
    def create_html_page(self, body: str, toc: str, css: str) -> str:
        """Tam HTML sayfası oluştur"""
        return f'''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Time Graph X - Kullanım Kılavuzu">
    <meta name="author" content="Time Graph X Development Team">
    <title>Time Graph X - Kullanım Kılavuzu</title>
    <style>
{css if css else self.get_default_css()}
    </style>
</head>
<body>
    <div class="document-header">
        <h1>📊 Time Graph X</h1>
        <div class="subtitle">Kullanım Kılavuzu</div>
        <div class="version">Versiyon: 1.0.0 | {datetime.now().strftime("%d %B %Y")}</div>
    </div>
    
    {toc}
    
    <main>
        {body}
    </main>
    
    <footer class="document-footer">
        <p><strong>Copyright © 2025 Time Graph X</strong></p>
        <p>Tüm hakları saklıdır.</p>
        <p>Oluşturulma Tarihi: {datetime.now().strftime("%d %B %Y, %H:%M")}</p>
    </footer>
</body>
</html>'''
    
    def get_default_css(self) -> str:
        """Varsayılan CSS"""
        return '''
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 { color: #2563eb; font-size: 2.5em; margin: 1em 0 0.5em 0; border-bottom: 3px solid #2563eb; }
        h2 { color: #1e40af; font-size: 2em; margin: 1.5em 0 0.5em 0; border-bottom: 2px solid #e5e7eb; }
        h3 { font-size: 1.5em; margin: 1.2em 0 0.5em 0; }
        p { margin: 0.8em 0; }
        code { background: #f3f4f6; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }
        pre { background: #f3f4f6; border: 1px solid #e5e7eb; border-radius: 6px; padding: 15px; overflow-x: auto; margin: 1em 0; }
        pre code { background: none; padding: 0; }
        blockquote { background: #fff3cd; border-left: 5px solid #f59e0b; padding: 15px 20px; margin: 1.5em 0; }
        table { width: 100%; border-collapse: collapse; margin: 1.5em 0; }
        th { background: #2563eb; color: white; padding: 12px; text-align: left; }
        td { padding: 12px; border-bottom: 1px solid #e5e7eb; }
        img { max-width: 100%; height: auto; margin: 1.5em auto; display: block; border-radius: 8px; }
        #TOC { background: #f9fafb; border: 2px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 30px 0; }
        #TOC ul { list-style: none; }
        #TOC a { color: #2563eb; text-decoration: none; }
        .document-header { text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #2563eb, #1e40af); color: white; border-radius: 12px; margin-bottom: 30px; }
        .document-footer { margin-top: 50px; padding: 30px; background: #f9fafb; border-radius: 12px; text-align: center; }
        '''
    
    def escape_html(self, text: str) -> str:
        """HTML karakterlerini escape et"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    """Ana fonksiyon"""
    if len(sys.argv) < 2:
        print("Kullanım: python markdown_to_html.py <markdown_file> [output_file] [css_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.md', '.html')
    css_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    converter = MarkdownToHTML()
    success = converter.convert_file(input_file, output_file, css_file)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

