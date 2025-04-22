#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据清洗模块
用于进一步优化Markdown数据质量，准备用于模型微调的高质量训练数据
"""

import os
import re
import logging
from tqdm import tqdm
import pandas as pd

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗器，用于优化Markdown数据质量"""
    
    def __init__(self, input_dir, output_dir=None):
        """
        初始化数据清洗器
        
        参数:
            input_dir (str): 输入Markdown文件目录
            output_dir (str, optional): 输出清洗后Markdown文件目录，默认与输入目录相同
        """
        self.input_dir = input_dir
        self.output_dir = output_dir if output_dir else input_dir
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"创建输出目录: {self.output_dir}")
    
    def clean_markdown(self, markdown_text):
        """
        清洗Markdown文本内容
        
        参数:
            markdown_text (str): 原始Markdown文本
            
        返回:
            str: 清洗后的Markdown文本
        """
        # 1. 去除连续的空行，保留最多两个连续空行
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        # 2. 修复标题格式问题 (确保#后有空格)
        markdown_text = re.sub(r'^(#+)([^#\s])', r'\1 \2', markdown_text, flags=re.MULTILINE)
        
        # 3. 修复列表格式问题 (确保-后有空格)
        markdown_text = re.sub(r'^(\s*)-([^\s])', r'\1- \2', markdown_text, flags=re.MULTILINE)
        
        # 4. 去除特殊字符和控制字符
        markdown_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', markdown_text)
        
        # 5. 修复常见的格式问题
        # 合并孤立的段落片段
        markdown_text = re.sub(r'([^.\n!?])\n([a-z])', r'\1 \2', markdown_text)
        
        # 6. 修复引用格式，确保>后有空格
        markdown_text = re.sub(r'^(\s*>)([^>\s])', r'\1 \2', markdown_text, flags=re.MULTILINE)
        
        # 7. 修复表格格式
        table_lines = []
        in_table = False
        
        for line in markdown_text.split('\n'):
            # 检测表格行 (包含至少两个|符号)
            if '|' in line and line.count('|') >= 2:
                if not in_table:
                    in_table = True
                    # 添加表格分隔行 (如果缺少)
                    next_line_idx = markdown_text.split('\n').index(line) + 1
                    if next_line_idx < len(markdown_text.split('\n')):
                        next_line = markdown_text.split('\n')[next_line_idx]
                        if '---' not in next_line and '|' not in next_line:
                            # 根据列数创建分隔行
                            cols = line.count('|') - 1
                            table_lines.append(line)
                            table_lines.append('|' + '---|' * cols)
                            continue
                table_lines.append(line)
            else:
                if in_table:
                    in_table = False
                table_lines.append(line)
        
        markdown_text = '\n'.join(table_lines)
        
        return markdown_text
    
    def remove_duplicates(self, markdown_text):
        """
        删除重复的段落和内容
        
        参数:
            markdown_text (str): 原始Markdown文本
            
        返回:
            str: 去重后的Markdown文本
        """
        lines = markdown_text.split('\n')
        unique_lines = []
        line_set = set()
        
        # 排除非常短的行，它们可能会误判为重复
        for line in lines:
            if len(line.strip()) > 10:  # 只检查较长的行
                if line not in line_set:
                    line_set.add(line)
                    unique_lines.append(line)
            else:
                unique_lines.append(line)
        
        # 检测重复段落 (连续3行或更多相同内容)
        paragraph_chunks = []
        current_chunk = []
        
        for line in unique_lines:
            if not line.strip():
                if current_chunk:
                    paragraph_chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                paragraph_chunks.append('')
            else:
                current_chunk.append(line)
        
        if current_chunk:
            paragraph_chunks.append('\n'.join(current_chunk))
        
        # 去除重复段落
        unique_paragraphs = []
        seen_paragraphs = set()
        
        for para in paragraph_chunks:
            if len(para.strip()) > 50:  # 只检查较长的段落
                if para not in seen_paragraphs:
                    seen_paragraphs.add(para)
                    unique_paragraphs.append(para)
            else:
                unique_paragraphs.append(para)
        
        return '\n'.join(unique_paragraphs)
    
    def prepare_training_data(self, markdown_texts, output_file):
        """
        准备用于模型微调的训练数据
        
        参数:
            markdown_texts (list): Markdown文本列表
            output_file (str): 输出训练数据文件路径
            
        返回:
            bool: 是否成功准备训练数据
        """
        try:
            # 将Markdown文本转换为适合训练的格式
            training_data = []
            
            for text in markdown_texts:
                # 确保文本是Unicode字符串
                if isinstance(text, bytes):
                    try:
                        # 尝试检测编码
                        import chardet
                        detected = chardet.detect(text)
                        text = text.decode(detected['encoding'] or 'utf-8', errors='replace')
                    except Exception as e:
                        logger.warning(f"文本编码转换错误: {str(e)}")
                        text = text.decode('utf-8', errors='replace')
                
                # 分割文本为更小的训练样本
                paragraphs = re.split(r'\n\s*\n', text)
                
                for i in range(0, len(paragraphs), 3):
                    if i + 1 < len(paragraphs):
                        # 创建输入-输出对
                        input_text = paragraphs[i].strip()
                        output_text = paragraphs[i+1].strip() if i+1 < len(paragraphs) else ""
                        
                        # 确保输入和输出都是有效的Unicode字符串
                        input_text = self._ensure_valid_text(input_text)
                        output_text = self._ensure_valid_text(output_text)
                        
                        if len(input_text) > 10 and len(output_text) > 10:
                            training_data.append({
                                "input": input_text,
                                "output": output_text
                            })
            
            # 保存为CSV格式，确保使用UTF-8编码
            df = pd.DataFrame(training_data)
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"已生成训练数据: {output_file}, 共 {len(training_data)} 条记录")
            
            return True
        
        except Exception as e:
            logger.error(f"准备训练数据时出错: {str(e)}")
            return False
    
    def _ensure_valid_text(self, text):
        """
        确保文本是有效的Unicode字符串，移除无效字符
        
        参数:
            text (str): 输入文本
            
        返回:
            str: 处理后的文本
        """
        if not text:
            return ""
        
        # 移除不可打印字符和控制字符，但保留空格、换行等
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # 确保文本是有效的UTF-8
        text = text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        
        return text
    
    def process_all_files(self, prepare_training=False):
        """
        处理输入目录中的所有Markdown文件
        
        参数:
            prepare_training (bool): 是否准备训练数据
            
        返回:
            int: 成功处理的文件数量
        """
        if not os.path.exists(self.input_dir):
            logger.error(f"输入目录不存在: {self.input_dir}")
            return 0
        
        # 获取所有Markdown文件
        md_files = [f for f in os.listdir(self.input_dir) if f.lower().endswith('.md')]
        
        if not md_files:
            logger.warning(f"在 {self.input_dir} 中没有找到Markdown文件")
            return 0
        
        logger.info(f"找到 {len(md_files)} 个Markdown文件")
        
        # 处理每个Markdown文件
        successful_count = 0
        all_md_texts = []
        
        for md_file in tqdm(md_files, desc="清洗Markdown文件"):
            md_path = os.path.join(self.input_dir, md_file)
            output_file = os.path.join(self.output_dir, f"cleaned_{md_file}")
            
            try:
                # 读取Markdown文件
                with open(md_path, 'r', encoding='utf-8') as file:
                    md_text = file.read()
                
                # 清洗文本
                logger.info(f"清洗文件: {md_file}")
                cleaned_text = self.clean_markdown(md_text)
                
                # 去除重复内容
                cleaned_text = self.remove_duplicates(cleaned_text)
                
                # 保存清洗后的文件
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_text)
                
                logger.info(f"清洗后的文件已保存到: {output_file}")
                all_md_texts.append(cleaned_text)
                successful_count += 1
                
            except Exception as e:
                logger.error(f"处理文件 {md_file} 时出错: {str(e)}")
        
        # 准备训练数据
        if prepare_training and successful_count > 0:
            training_file = os.path.join(os.path.dirname(self.output_dir), "training_data.csv")
            self.prepare_training_data(all_md_texts, training_file)
        
        logger.info(f"处理完成. 成功处理了 {successful_count}/{len(md_files)} 个文件")
        return successful_count

def main():
    """主函数，用于测试"""
    # 默认目录
    input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "markdown")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cleaned_markdown")
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 初始化清洗器
    cleaner = DataCleaner(input_dir, output_dir)
    
    # 处理所有Markdown文件，并准备训练数据
    cleaner.process_all_files(prepare_training=True)

if __name__ == "__main__":
    main() 