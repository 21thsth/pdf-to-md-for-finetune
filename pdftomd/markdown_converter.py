#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Markdown转换模块
将提取的文本转换为结构化的Markdown格式
"""

import os
import re
import logging
from tqdm import tqdm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarkdownConverter:
    """文本到Markdown转换器，将提取的文本转换为结构化的Markdown格式"""
    
    def __init__(self, input_dir, output_dir):
        """
        初始化Markdown转换器
        
        参数:
            input_dir (str): 输入文本文件目录
            output_dir (str): 输出Markdown文件目录
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"创建输出目录: {output_dir}")
    
    def identify_title(self, line):
        """
        识别并格式化标题
        
        参数:
            line (str): 文本行
            
        返回:
            tuple: (是否是标题, 格式化后的标题行)
        """
        # 数字开头的可能是标题 (如 "1. 引言", "1.1 背景")
        number_title = re.match(r'^(\d+(\.\d+)*\.?\s+)(.+)$', line.strip())
        if number_title:
            prefix = number_title.group(1)
            title_text = number_title.group(3)
            
            # 根据数字的层级确定标题级别
            level = len(re.findall(r'\d+', prefix))
            level = min(level, 6)  # Markdown最多支持6级标题
            
            return True, f"{'#' * level} {prefix}{title_text}"
        
        # 检查是否是没有编号的标题 (全大写或者较短的行)
        if line.isupper() and 3 < len(line.strip()) < 50:
            return True, f"## {line.strip()}"
        
        # 特殊关键词可能是标题
        title_keywords = ["引言", "介绍", "概述", "目录", "参考文献", "结论", "总结"]
        for keyword in title_keywords:
            if keyword in line and len(line.strip()) < 30:
                return True, f"## {line.strip()}"
        
        return False, line
    
    def identify_list_item(self, line):
        """
        识别并格式化列表项
        
        参数:
            line (str): 文本行
            
        返回:
            tuple: (是否是列表项, 格式化后的列表行)
        """
        # 匹配数字列表 (如 "1. 项目", "(1) 项目")
        number_list = re.match(r'^(\s*)((\d+\.)|\(\d+\))\s+(.+)$', line)
        if number_list:
            indent = number_list.group(1)
            prefix = number_list.group(2)
            content = number_list.group(4)
            
            # 保持原有的编号格式
            return True, f"{indent}{prefix} {content}"
        
        # 匹配符号列表 (如 "• 项目", "- 项目", "* 项目")
        symbol_list = re.match(r'^(\s*)([•\-\*])\s+(.+)$', line)
        if symbol_list:
            indent = symbol_list.group(1)
            content = symbol_list.group(3)
            
            # 统一使用Markdown的'-'符号
            return True, f"{indent}- {content}"
        
        return False, line
    
    def format_paragraphs(self, text):
        """
        格式化段落，合并多行文本为段落
        
        参数:
            text (str): 原始文本
            
        返回:
            str: 格式化后的文本
        """
        lines = text.split('\n')
        formatted_lines = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行
            if not line:
                if current_paragraph:
                    formatted_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                formatted_lines.append('')
                continue
            
            # 检查是否是标题或列表项
            is_title, title_line = self.identify_title(line)
            if is_title:
                if current_paragraph:
                    formatted_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                formatted_lines.append(title_line)
                continue
            
            is_list, list_line = self.identify_list_item(line)
            if is_list:
                if current_paragraph:
                    formatted_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                formatted_lines.append(list_line)
                continue
            
            # 如果不是特殊格式，添加到当前段落
            current_paragraph.append(line)
        
        # 处理最后一个段落
        if current_paragraph:
            formatted_lines.append(' '.join(current_paragraph))
        
        return '\n\n'.join(formatted_lines)
    
    def clean_text(self, text):
        """
        清理文本，去除页眉页脚等无关内容
        
        参数:
            text (str): 原始文本
            
        返回:
            str: 清理后的文本
        """
        # 去除页码行
        text = re.sub(r'\n\s*\d+\s*\n', '\n\n', text)
        
        # 去除常见的页眉页脚模式
        footer_patterns = [
            r'\n.{0,10}页码.{0,10}\n',
            r'\n.{0,30}版权所有.{0,30}\n',
            r'\n.{0,30}Copyright.{0,30}\n',
            r'\n.{0,30}www\..{3,50}\..{2,5}.{0,30}\n'
        ]
        
        for pattern in footer_patterns:
            text = re.sub(pattern, '\n', text, flags=re.IGNORECASE)
        
        return text
    
    def convert_text_to_markdown(self, text_path):
        """
        将单个文本文件转换为Markdown格式
        
        参数:
            text_path (str): 文本文件路径
            
        返回:
            str: 转换后的Markdown文本
        """
        try:
            # 读取文本文件，自动检测编码
            text = None
            try:
                # 先尝试UTF-8
                with open(text_path, 'r', encoding='utf-8') as file:
                    text = file.read()
            except UnicodeDecodeError:
                # 如果UTF-8失败，尝试检测编码
                with open(text_path, 'rb') as file:
                    raw_data = file.read()
                    import chardet
                    result = chardet.detect(raw_data)
                    encoding = result['encoding'] or 'utf-8'
                    text = raw_data.decode(encoding, errors='replace')
            
            if not text:
                logger.error(f"无法读取文件内容: {text_path}")
                return ""
            
            # 获取文件名作为文档标题
            file_name = os.path.basename(text_path)
            title = os.path.splitext(file_name)[0]
            
            # 添加文档标题
            markdown_text = f"# {title}\n\n"
            
            # 清理文本
            text = self.clean_text(text)
            
            # 格式化文本为Markdown
            markdown_text += self.format_paragraphs(text)
            
            return markdown_text
        
        except Exception as e:
            logger.error(f"处理文件 {text_path} 时出错: {str(e)}")
            return ""
    
    def process_all_texts(self):
        """
        处理输入目录中的所有文本文件
        
        返回:
            int: 成功处理的文件数量
        """
        if not os.path.exists(self.input_dir):
            logger.error(f"输入目录不存在: {self.input_dir}")
            return 0
        
        # 获取所有文本文件
        text_files = [f for f in os.listdir(self.input_dir) if f.lower().endswith('.txt')]
        
        if not text_files:
            logger.warning(f"在 {self.input_dir} 中没有找到文本文件")
            return 0
        
        logger.info(f"找到 {len(text_files)} 个文本文件")
        
        # 处理每个文本文件
        successful_count = 0
        for text_file in tqdm(text_files, desc="转换为Markdown"):
            text_path = os.path.join(self.input_dir, text_file)
            output_file = os.path.join(self.output_dir, f"{os.path.splitext(text_file)[0]}.md")
            
            logger.info(f"处理文件: {text_file}")
            markdown_text = self.convert_text_to_markdown(text_path)
            
            if markdown_text:
                # 保存转换后的Markdown，确保使用UTF-8编码
                with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(markdown_text)
                    
                logger.info(f"Markdown已保存到: {output_file}")
                successful_count += 1
            else:
                logger.warning(f"未能从 {text_file} 生成Markdown")
        
        logger.info(f"处理完成. 成功处理了 {successful_count}/{len(text_files)} 个文件")
        return successful_count

def main():
    """主函数，用于测试"""
    # 默认目录
    input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "text")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "markdown")
    
    # 初始化转换器
    converter = MarkdownConverter(input_dir, output_dir)
    
    # 处理所有文本文件
    converter.process_all_texts()

if __name__ == "__main__":
    main() 