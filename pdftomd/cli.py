#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
命令行接口
用于提供命令行工具执行PDF转Markdown和模型微调的功能
"""

import os
import argparse
import logging
from datetime import datetime

from .pdf_extractor import PDFExtractor
from .markdown_converter import MarkdownConverter
from .data_cleaner import DataCleaner
from .model_finetuner import ModelFinetuner

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_to_md.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="PDF文档转Markdown并进行数据清洗，为大语言模型微调准备数据")
    
    # 输入输出目录
    parser.add_argument("--pdf_dir", type=str, default="data/pdf", help="输入PDF文件目录")
    parser.add_argument("--text_dir", type=str, default="data/text", help="输出文本文件目录")
    parser.add_argument("--markdown_dir", type=str, default="data/markdown", help="输出Markdown文件目录")
    parser.add_argument("--cleaned_dir", type=str, default="data/cleaned_markdown", help="清洗后的Markdown文件目录")
    
    # 步骤控制
    parser.add_argument("--all", action="store_true", help="执行所有步骤")
    parser.add_argument("--extract", action="store_true", help="执行PDF提取步骤")
    parser.add_argument("--convert", action="store_true", help="执行Markdown转换步骤")
    parser.add_argument("--clean", action="store_true", help="执行数据清洗步骤")
    parser.add_argument("--finetune", action="store_true", help="执行模型微调步骤")
    
    # 模型参数
    parser.add_argument("--model_name", type=str, default="THUDM/chatglm2-6b", help="模型名称或路径")
    parser.add_argument("--output_dir", type=str, default="models/finetuned_model", help="微调后模型保存目录")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="学习率")
    parser.add_argument("--num_epochs", type=int, default=3, help="训练轮次")
    parser.add_argument("--batch_size", type=int, default=8, help="批处理大小")
    
    return parser.parse_args()

def main():
    """主函数，执行PDF转Markdown和模型微调流程"""
    args = get_args()
    
    # 如果选择了--all，则执行所有步骤
    if args.all:
        args.extract = args.convert = args.clean = args.finetune = True
    
    # 如果没有选择任何步骤，显示帮助信息
    if not (args.extract or args.convert or args.clean or args.finetune):
        logger.warning("未指定任何步骤，请使用--all或--extract/--convert/--clean/--finetune指定要执行的步骤")
        return
    
    # 确保所有目录存在
    for dir_path in [args.pdf_dir, args.text_dir, args.markdown_dir, args.cleaned_dir, os.path.dirname(args.output_dir)]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"创建目录: {dir_path}")
    
    # 步骤1: 从PDF提取文本
    if args.extract:
        logger.info("===== 步骤1: 开始从PDF提取文本 =====")
        extractor = PDFExtractor(args.pdf_dir, args.text_dir)
        processed_count = extractor.process_all_pdfs()
        logger.info(f"提取完成，成功处理了 {processed_count} 个PDF文件")
    
    # 步骤2: 将文本转换为Markdown
    if args.convert:
        logger.info("===== 步骤2: 开始转换为Markdown =====")
        converter = MarkdownConverter(args.text_dir, args.markdown_dir)
        processed_count = converter.process_all_texts()
        logger.info(f"转换完成，成功处理了 {processed_count} 个文本文件")
    
    # 步骤3: 清洗Markdown数据
    if args.clean:
        logger.info("===== 步骤3: 开始清洗数据 =====")
        cleaner = DataCleaner(args.markdown_dir, args.cleaned_dir)
        processed_count = cleaner.process_all_files(prepare_training=True)
        logger.info(f"清洗完成，成功处理了 {processed_count} 个Markdown文件")
    
    # 步骤4: 微调模型
    if args.finetune:
        logger.info("===== 步骤4: 开始微调模型 =====")
        finetuner = ModelFinetuner(
            model_name=args.model_name,
            output_dir=args.output_dir,
            learning_rate=args.learning_rate,
            num_epochs=args.num_epochs,
            batch_size=args.batch_size
        )
        training_file = os.path.join(os.path.dirname(args.cleaned_dir), "training_data.csv")
        success = finetuner.finetune(training_file)
        if success:
            logger.info(f"微调完成，模型已保存到 {args.output_dir}")
        else:
            logger.error("微调失败")

if __name__ == "__main__":
    main() 