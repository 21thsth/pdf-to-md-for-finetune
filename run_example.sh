#!/bin/bash
# PDF-to-MD-for-Finetune 示例运行脚本

# 设置Python环境
export PYTHONPATH=$PYTHONPATH:$(dirname "$0")

# 执行PDF提取和转换为Markdown步骤
pdftomd --extract --convert

# 如果需要执行所有步骤，可以使用以下命令（取消注释）
# pdftomd --all

# 如果需要单独执行某一步骤，可以使用以下命令（取消注释）
# pdftomd --extract  # 仅执行PDF提取
# pdftomd --convert  # 仅执行Markdown转换
# pdftomd --clean    # 仅执行数据清洗
# pdftomd --finetune # 仅执行模型微调

echo "处理完成！" 