#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF文档信息提取脚本
提取PDF文件的元数据和文本内容
"""
import os
import sys
import json
from pathlib import Path

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

def extract_pdf_info_pypdf2(pdf_path):
    """使用PyPDF2提取PDF信息"""
    info = {
        'filename': os.path.basename(pdf_path),
        'pages': 0,
        'text_length': 0,
        'metadata': {},
        'extractable': False,
        'error': None
    }
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            info['pages'] = len(pdf_reader.pages)
            
            # 提取元数据
            if pdf_reader.metadata:
                info['metadata'] = {
                    str(k): str(v) if v else '' 
                    for k, v in pdf_reader.metadata.items()
                }
            
            # 尝试提取文本
            text_content = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                        info['text_length'] += len(text)
                except Exception as e:
                    pass
            
            info['extractable'] = info['text_length'] > 0
            info['preview'] = ' '.join(text_content[:500]) if text_content else ''
            
    except Exception as e:
        info['error'] = str(e)
    
    return info

def extract_pdf_info_pdfplumber(pdf_path):
    """使用pdfplumber提取PDF信息"""
    info = {
        'filename': os.path.basename(pdf_path),
        'pages': 0,
        'text_length': 0,
        'metadata': {},
        'extractable': False,
        'error': None
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            info['pages'] = len(pdf.pages)
            
            # 提取元数据
            if pdf.metadata:
                info['metadata'] = {
                    str(k): str(v) if v else '' 
                    for k, v in pdf.metadata.items()
                }
            
            # 提取文本
            text_content = []
            for page in pdf.pages:
                try:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                        info['text_length'] += len(text)
                except Exception as e:
                    pass
            
            info['extractable'] = info['text_length'] > 0
            info['preview'] = ' '.join(text_content[:500]) if text_content else ''
            
    except Exception as e:
        info['error'] = str(e)
    
    return info

def main():
    # 获取当前目录
    current_dir = Path('.')
    pdf_files = list(current_dir.glob('*.pdf'))
    
    if not pdf_files:
        print("未找到PDF文件")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    results = []
    
    for pdf_file in sorted(pdf_files):
        print(f"正在处理: {pdf_file.name}")
        
        info = None
        if HAS_PDFPLUMBER:
            info = extract_pdf_info_pdfplumber(str(pdf_file))
        elif HAS_PYPDF2:
            info = extract_pdf_info_pypdf2(str(pdf_file))
        else:
            # 如果没有库，至少获取基本信息
            info = {
                'filename': pdf_file.name,
                'size': pdf_file.stat().st_size,
                'extractable': False,
                'error': '未安装PDF解析库'
            }
        
        if info:
            info['size'] = pdf_file.stat().st_size
            results.append(info)
    
    # 保存结果
    output_file = 'pdf_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析完成！结果已保存到 {output_file}")
    print(f"可提取文本的PDF: {sum(1 for r in results if r.get('extractable', False))}/{len(results)}")
    
    return results

if __name__ == '__main__':
    main()
