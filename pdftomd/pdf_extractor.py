#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF提取模块
用于从PDF文件中提取文本内容
"""

import os
import PyPDF2
from tqdm import tqdm
import logging
import chardet

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFExtractor:
    """PDF文本提取器，用于从PDF文件中提取文本内容"""
    
    def __init__(self, input_dir, output_dir):
        """
        初始化PDF提取器
        
        参数:
            input_dir (str): 输入PDF文件目录
            output_dir (str): 输出文本文件目录
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"创建输出目录: {output_dir}")
    
    def extract_text_from_pdf(self, pdf_path):
        """
        从单个PDF文件中提取文本
        
        参数:
            pdf_path (str): PDF文件路径
            
        返回:
            str: 提取的文本内容
        """
        try:
            with open(pdf_path, 'rb') as file:
                # 创建PDF读取对象
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 获取页数
                num_pages = len(pdf_reader.pages)
                logger.info(f"PDF文件 {os.path.basename(pdf_path)} 共有 {num_pages} 页")
                
                # 提取所有页面的文本
                text = ""
                for page_num in tqdm(range(num_pages), desc=f"提取 {os.path.basename(pdf_path)}"):
                    page = pdf_reader.pages[page_num]
                    try:
                        page_text = page.extract_text()
                        # 确保文本是UTF-8格式
                        if isinstance(page_text, bytes):
                            detected = chardet.detect(page_text)
                            page_text = page_text.decode(detected['encoding'] or 'utf-8', errors='replace')
                        text += page_text + "\n\n"  # 添加额外换行以分隔页面
                    except Exception as e:
                        logger.warning(f"提取第 {page_num+1} 页时出错: {str(e)}")
                
                return text
        except Exception as e:
            logger.error(f"处理文件 {pdf_path} 时出错: {str(e)}")
            return ""
    
    def process_all_pdfs(self):
        """
        处理输入目录中的所有PDF文件
        
        返回:
            int: 成功处理的文件数量
        """
        if not os.path.exists(self.input_dir):
            logger.error(f"输入目录不存在: {self.input_dir}")
            return 0
        
        # 获取所有PDF文件
        pdf_files = [f for f in os.listdir(self.input_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"在 {self.input_dir} 中没有找到PDF文件")
            return 0
        
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        # 处理每个PDF文件
        successful_count = 0
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.input_dir, pdf_file)
            output_file = os.path.join(self.output_dir, f"{os.path.splitext(pdf_file)[0]}.txt")
            
            logger.info(f"处理文件: {pdf_file}")
            text = self.extract_text_from_pdf(pdf_path)
            
            if text:
                # 保存提取的文本，确保使用UTF-8编码
                with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(text)
                logger.info(f"文本已保存到: {output_file}")
                successful_count += 1
            else:
                logger.warning(f"未能从 {pdf_file} 提取文本")
        
        logger.info(f"处理完成. 成功处理了 {successful_count}/{len(pdf_files)} 个文件")
        return successful_count

def main():
    """主函数，用于测试"""
    # 默认目录
    input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pdf")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "text")
    
    # 初始化提取器
    extractor = PDFExtractor(input_dir, output_dir)
    
    # 处理所有PDF文件
    extractor.process_all_pdfs()

if __name__ == "__main__":
    main() 