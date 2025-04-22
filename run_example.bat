@echo off
REM PDF-to-MD-for-Finetune 示例运行脚本

REM 设置Python环境
set PYTHONPATH=%PYTHONPATH%;%~dp0

REM 执行PDF提取和转换为Markdown步骤
pdftomd --extract --convert

REM 如果需要执行所有步骤，可以使用以下命令（取消注释）
REM pdftomd --all

REM 如果需要单独执行某一步骤，可以使用以下命令（取消注释）
REM pdftomd --extract  REM 仅执行PDF提取
REM pdftomd --convert  REM 仅执行Markdown转换
REM pdftomd --clean    REM 仅执行数据清洗
REM pdftomd --finetune REM 仅执行模型微调

echo 处理完成！
pause 