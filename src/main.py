#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF-to-MD-for-Finetune 主程序
整合所有模块，提供完整的PDF处理、转换、清洗和模型微调流程
"""

import os
import argparse
import logging
from pathlib import Path
import time

# 导入各模块
from pdf_extractor import PDFExtractor
from markdown_converter import MarkdownConverter
from data_cleaner import DataCleaner
from model_finetuner import ModelFinetuner

# 配置日志
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
    parser = argparse.ArgumentParser(description="PDF-to-MD-for-Finetune: PDF文档转Markdown并微调大语言模型")
    
    # 数据处理相关参数
    parser.add_argument("--pdf_dir", type=str, default="data/pdf",
                        help="输入PDF文件目录")
    parser.add_argument("--text_dir", type=str, default="data/text",
                        help="输出文本文件目录")
    parser.add_argument("--markdown_dir", type=str, default="data/markdown",
                        help="输出Markdown文件目录")
    parser.add_argument("--cleaned_dir", type=str, default="data/cleaned_markdown",
                        help="清洗后的Markdown文件目录")
    
    # 流程控制参数
    parser.add_argument("--extract", action="store_true", help="执行PDF提取步骤")
    parser.add_argument("--convert", action="store_true", help="执行Markdown转换步骤")
    parser.add_argument("--clean", action="store_true", help="执行数据清洗步骤")
    parser.add_argument("--finetune", action="store_true", help="执行模型微调步骤")
    parser.add_argument("--all", action="store_true", help="执行所有步骤")
    
    # 模型微调相关参数
    parser.add_argument("--model_name", type=str, default="THUDM/chatglm2-6b",
                        help="预训练模型名称或路径")
    parser.add_argument("--output_dir", type=str, default="models/finetuned_model",
                        help="微调后模型保存目录")
    parser.add_argument("--learning_rate", type=float, default=2e-5,
                        help="学习率")
    parser.add_argument("--num_epochs", type=int, default=1,
                        help="训练轮次")
    parser.add_argument("--batch_size", type=int, default=4,
                        help="批处理大小")
    
    return parser.parse_args()

def main():
    """主程序入口"""
    # 获取命令行参数
    args = get_args()
    
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    
    # 设置各目录的绝对路径
    pdf_dir = os.path.join(base_dir, args.pdf_dir)
    text_dir = os.path.join(base_dir, args.text_dir)
    markdown_dir = os.path.join(base_dir, args.markdown_dir)
    cleaned_dir = os.path.join(base_dir, args.cleaned_dir)
    output_dir = os.path.join(base_dir, args.output_dir)
    
    # 确保各目录存在
    for directory in [pdf_dir, text_dir, markdown_dir, cleaned_dir, os.path.dirname(output_dir)]:
        os.makedirs(directory, exist_ok=True)
    
    # 记录开始时间
    start_time = time.time()
    
    # 步骤1: 提取PDF文本
    if args.extract or args.all:
        logger.info("===== 步骤1: 开始提取PDF文本 =====")
        extractor = PDFExtractor(pdf_dir, text_dir)
        num_processed = extractor.process_all_pdfs()
        logger.info(f"提取完成，成功处理了 {num_processed} 个PDF文件")
    
    # 步骤2: 转换为Markdown
    if args.convert or args.all:
        logger.info("===== 步骤2: 开始转换为Markdown =====")
        converter = MarkdownConverter(text_dir, markdown_dir)
        num_processed = converter.process_all_texts()
        logger.info(f"转换完成，成功处理了 {num_processed} 个文本文件")
    
    # 步骤3: 清洗数据
    if args.clean or args.all:
        logger.info("===== 步骤3: 开始清洗数据 =====")
        cleaner = DataCleaner(markdown_dir, cleaned_dir)
        num_processed = cleaner.process_all_files(prepare_training=True)
        logger.info(f"清洗完成，成功处理了 {num_processed} 个Markdown文件")
    
    # 步骤4: 微调模型
    if args.finetune or args.all:
        logger.info("===== 步骤4: 开始微调模型 =====")
        training_data_path = os.path.join(base_dir, "data", "training_data.csv")
        
        if os.path.exists(training_data_path):
            finetuner = ModelFinetuner(
                args.model_name,
                training_data_path,
                output_dir
            )
            
            success = finetuner.train(
                learning_rate=args.learning_rate,
                num_epochs=args.num_epochs,
                batch_size=args.batch_size
            )
            
            if success:
                logger.info("模型微调成功")
                
                # 简单测试
                test_input = "这是一个测试输入，请生成相应的内容。"
                output = finetuner.evaluate(test_input)
                logger.info(f"模型测试结果:")
                logger.info(f"输入: {test_input}")
                logger.info(f"输出: {output}")
            else:
                logger.error("模型微调失败")
        else:
            logger.error(f"找不到训练数据: {training_data_path}")
    
    # 计算总耗时
    elapsed_time = time.time() - start_time
    logger.info(f"处理完成，总耗时: {elapsed_time:.2f}秒")

if __name__ == "__main__":
    main() 