# PDF-to-MD-for-Finetune 安装指南

## 基本安装

### 方法一：使用pip安装（推荐）

```bash
pip install pdftomd
```

### 方法二：从源码安装

1. 克隆仓库
```bash
git clone https://github.com/21thsth/pdf-to-md-for-finetune.git
cd PDF-to-MD-for-Finetune
```

2. 安装包
```bash
pip install -e .
```

## 验证安装

安装完成后，可以通过执行以下命令验证安装是否成功：

```bash
pdftomd --help
```

如果正确显示帮助信息，说明安装成功。

## 离线安装

如果需要在没有网络连接的环境下安装，可以按照以下步骤操作：

1. 在有网络的环境中打包项目：
```bash
pip wheel -w ./dist .
```

2. 将生成的wheel文件和requirements.txt复制到目标环境

3. 在目标环境中安装：
```bash
pip install pdftomd-0.1.0-py3-none-any.whl
```

## GPU支持（用于模型微调）

如果需要使用GPU进行模型微调，请确保安装了适合您GPU的PyTorch版本：

```bash
# 对于CUDA 11.7
pip install torch==2.0.0+cu117 -f https://download.pytorch.org/whl/torch_stable.html

# 对于CUDA 11.8
pip install torch==2.0.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html
```

## 常见问题

### 1. 找不到命令 `pdftomd`

确保Python的Scripts目录在系统PATH中。对于Windows用户，可能需要手动添加。

### 2. 安装依赖失败

如果某些依赖安装失败，可以尝试逐个安装：

```bash
pip install PyPDF2 regex transformers datasets torch tqdm numpy pandas scikit-learn matplotlib chardet
```

### 3. 模型微调时内存不足

- 减小batch_size参数：`pdftomd --finetune --batch_size 4`
- 使用较小的模型：`pdftomd --finetune --model_name "THUDM/chatglm-6b"` 