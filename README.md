# PDF-to-MD-for-Finetune

用于PDF文档转Markdown并进行数据清洗，为大语言模型微调准备高质量训练数据。

## 核心需求 (MVP)

### 1. 基本功能

- 批量提取PDF文件中的文本内容
- 将提取的文本转换为结构化的Markdown格式
- 识别并保留文档的标题、段落、列表等结构
- 清洗数据，去除无意义内容和格式问题
- 将处理后的数据转换为适合模型微调的格式

### 2. 模型微调

- 从Hugging Face下载预训练模型
- 使用处理后的Markdown数据进行微调
- 支持调整微调参数（学习率、训练轮次等）
- 保存微调后的模型

### 3. 数据处理要求

- 支持中文PDF文档处理
- 保留文档的语义结构
- 识别并正确格式化标题层级
- 保留列表、表格等特殊格式（尽可能）
- 去除页眉、页脚、页码等无关内容

### 4. 技术要求

- 使用Python实现
- 利用PyPDF2进行PDF文本提取
- 使用正则表达式进行文本清洗和格式化
- 基于Transformers库进行模型微调
- 支持多进程处理以提高效率

### 5. 用户界面

- 命令行接口，支持批处理
- 提供详细的处理进度和结果报告
- 可配置的参数设置

### 6. 版本控制

- 使用Git进行版本管理
- 遵循语义化版本规范
- 维护清晰的提交记录和分支策略

### 7. 输出要求

- 处理后的Markdown文件应保持良好的可读性
- 生成的训练数据应符合模型微调的输入格式要求
- 微调后的模型应能正确加载和使用

## 项目结构

本项目采用模块化设计，主要包括以下组件：

```
PDF-to-MD-for-Finetune/
├── src/                        # 源代码目录
│   ├── pdf_extractor.py        # PDF提取模块
│   ├── markdown_converter.py   # Markdown转换模块
│   ├── data_cleaner.py         # 数据清洗模块
│   ├── model_finetuner.py      # 模型微调模块
│   └── main.py                 # 主程序入口
├── data/                       # 数据目录
│   ├── pdf/                    # 原始PDF文件
│   ├── text/                   # 提取的文本文件
│   ├── markdown/               # 转换后的Markdown文件
│   └── cleaned_markdown/       # 清洗后的Markdown文件
├── models/                     # 模型目录
│   └── finetuned_model/        # 微调后的模型
├── requirements.txt            # 项目依赖
├── run_example.bat             # Windows示例运行脚本
├── run_example.sh              # Linux/Mac示例运行脚本
└── README.md                   # 项目说明文档
```

## 安装说明

### 1. 环境要求

- Python 3.8或更高版本
- 足够的磁盘空间（用于存储模型和数据）
- 对于模型微调，建议使用支持CUDA的GPU

### 2. 安装步骤

#### 方法一：从源码安装

1. 克隆项目代码
```bash
git clone https://github.com/21thsth/pdf-to-md-for-finetune.git
cd PDF-to-MD-for-Finetune
```

2. 安装为Python包
```bash
pip install -e .
```

#### 方法二：直接使用pip安装
```bash
pip install pdftomd
```

3. 准备PDF文件
   - 将需要处理的PDF文件放入`data/pdf`目录

## 使用说明

### 1. 基本用法

项目提供了多种运行方式，可以根据需要选择：

#### 作为命令行工具使用

安装后可以直接使用`pdftomd`命令：

```bash
# 执行所有步骤
pdftomd --all

# 仅执行PDF提取
pdftomd --extract

# 仅执行Markdown转换
pdftomd --convert

# 仅执行数据清洗
pdftomd --clean

# 仅执行模型微调
pdftomd --finetune

# 自定义参数
pdftomd --extract --convert --model_name "THUDM/chatglm2-6b" --num_epochs 3 --batch_size 8
```

#### 作为Python模块使用

```python
from pdftomd import PDFExtractor, MarkdownConverter, DataCleaner, ModelFinetuner

# 从PDF提取文本
extractor = PDFExtractor("data/pdf", "data/text")
extractor.process_all_pdfs()

# 转换为Markdown
converter = MarkdownConverter("data/text", "data/markdown")
converter.process_all_texts()

# 清洗数据
cleaner = DataCleaner("data/markdown", "data/cleaned_markdown")
cleaner.process_all_files(prepare_training=True)

# 微调模型
finetuner = ModelFinetuner(
    model_name="THUDM/chatglm2-6b",
    output_dir="models/finetuned_model"
)
finetuner.finetune("data/training_data.csv")
```

### 2. 使用脚本运行

项目还提供了传统的脚本运行方式：

**Windows用户**:
```
run_example.bat
```

**Linux/Mac用户**:
```bash
chmod +x run_example.sh
./run_example.sh
```

### 2. 命令行参数

可以通过命令行参数控制执行流程：

```bash
# 执行所有步骤
python src/main.py --all

# 仅执行PDF提取
python src/main.py --extract

# 仅执行Markdown转换
python src/main.py --convert

# 仅执行数据清洗
python src/main.py --clean

# 仅执行模型微调
python src/main.py --finetune

# 自定义参数
python src/main.py --extract --convert --model_name "THUDM/chatglm2-6b" --num_epochs 3 --batch_size 8
```

### 3. 高级配置

以下是可用的高级配置参数：

```
--pdf_dir        输入PDF文件目录
--text_dir       输出文本文件目录
--markdown_dir   输出Markdown文件目录
--cleaned_dir    清洗后的Markdown文件目录
--model_name     预训练模型名称或路径
--output_dir     微调后模型保存目录
--learning_rate  学习率
--num_epochs     训练轮次
--batch_size     批处理大小
```

## 处理流程

1. **PDF提取阶段**：从PDF文件提取原始文本，保存为文本文件
2. **Markdown转换阶段**：将文本转换为结构化的Markdown格式
3. **数据清洗阶段**：优化数据质量，去除噪声和重复内容
4. **模型微调阶段**：使用处理后的数据微调大语言模型

## 注意事项

- 微调过程可能需要较长时间，取决于数据量和硬件配置
- 对于大型PDF文件，建议确保有足够的内存和磁盘空间
- 微调模型需要占用大量GPU内存，请确保有足够的GPU资源

## 贡献指南

欢迎提交问题和改进建议！请遵循以下步骤：

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m '添加某功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详情请参阅[LICENSE](LICENSE)文件。

## 联系方式

项目维护者：21thsth

项目链接: [https://github.com/21thsth/pdf-to-md-for-finetune](https://github.com/21thsth/pdf-to-md-for-finetune)
