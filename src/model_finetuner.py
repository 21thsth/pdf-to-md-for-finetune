#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型微调模块
用于使用处理后的数据微调大语言模型
"""

import os
import logging
import pandas as pd
from tqdm import tqdm
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelFinetuner:
    """模型微调器，用于微调大语言模型"""
    
    def __init__(self, model_name, training_data_path, output_dir):
        """
        初始化模型微调器
        
        参数:
            model_name (str): 预训练模型名称或路径
            training_data_path (str): 训练数据文件路径
            output_dir (str): 输出模型保存目录
        """
        self.model_name = model_name
        self.training_data_path = training_data_path
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"创建输出目录: {self.output_dir}")
        
        # 检查CUDA是否可用
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"使用设备: {self.device}")
        
        # 加载模型和分词器
        try:
            logger.info(f"加载模型: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            logger.info("模型和分词器加载成功")
        except Exception as e:
            logger.error(f"加载模型时出错: {str(e)}")
            raise
    
    def prepare_dataset(self):
        """
        准备训练数据集
        
        返回:
            datasets.Dataset: 准备好的数据集
        """
        try:
            # 加载训练数据
            logger.info(f"加载训练数据: {self.training_data_path}")
            df = pd.read_csv(self.training_data_path)
            
            # 将数据转换为HuggingFace数据集格式
            dataset_dict = {
                "input": df["input"].tolist(),
                "output": df["output"].tolist()
            }
            
            # 创建数据集
            dataset = Dataset.from_dict(dataset_dict)
            
            # 分词器处理
            def tokenize_function(examples):
                # 创建指令格式
                prompts = [f"输入: {input_text}\n输出:" for input_text in examples["input"]]
                targets = examples["output"]
                
                # 创建完整的输入-输出对
                texts = [prompt + " " + target for prompt, target in zip(prompts, targets)]
                
                # 分词
                tokenized_inputs = self.tokenizer(
                    texts,
                    padding="max_length",
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                )
                
                return tokenized_inputs
            
            # 应用分词
            tokenized_dataset = dataset.map(
                tokenize_function,
                batched=True,
                remove_columns=["input", "output"]
            )
            
            logger.info(f"数据集准备完成，共 {len(tokenized_dataset)} 条样本")
            return tokenized_dataset
            
        except Exception as e:
            logger.error(f"准备数据集时出错: {str(e)}")
            raise
    
    def train(self, learning_rate=5e-5, num_epochs=3, batch_size=8, warmup_steps=0):
        """
        训练模型
        
        参数:
            learning_rate (float): 学习率
            num_epochs (int): 训练轮次
            batch_size (int): 批处理大小
            warmup_steps (int): 预热步数
            
        返回:
            bool: 是否成功训练
        """
        try:
            # 准备数据集
            train_dataset = self.prepare_dataset()
            
            # 训练参数
            training_args = TrainingArguments(
                output_dir=self.output_dir,
                overwrite_output_dir=True,
                num_train_epochs=num_epochs,
                per_device_train_batch_size=batch_size,
                learning_rate=learning_rate,
                warmup_steps=warmup_steps,
                weight_decay=0.01,
                logging_dir=f"{self.output_dir}/logs",
                logging_steps=10,
                save_strategy="epoch",
                save_total_limit=2,
                fp16=torch.cuda.is_available(),  # 如果可用则使用混合精度训练
            )
            
            # 数据收集器
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False  # 不使用掩码语言模型
            )
            
            # 创建Trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                data_collator=data_collator,
                tokenizer=self.tokenizer,
            )
            
            # 开始训练
            logger.info("开始训练...")
            trainer.train()
            
            # 保存模型
            logger.info(f"保存模型到 {self.output_dir}")
            trainer.save_model(self.output_dir)
            self.tokenizer.save_pretrained(self.output_dir)
            
            logger.info("训练完成")
            return True
            
        except Exception as e:
            logger.error(f"训练模型时出错: {str(e)}")
            return False
    
    def evaluate(self, test_input):
        """
        评估模型，生成文本
        
        参数:
            test_input (str): 测试输入文本
            
        返回:
            str: 生成的文本
        """
        try:
            # 将模型移动到正确的设备
            self.model.to(self.device)
            
            # 创建完整的提示
            prompt = f"输入: {test_input}\n输出:"
            
            # 分词
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # 生成文本
            with torch.no_grad():
                output = self.model.generate(
                    inputs["input_ids"],
                    max_length=256,
                    num_return_sequences=1,
                    no_repeat_ngram_size=2,
                    do_sample=True,
                    top_k=50,
                    top_p=0.95,
                    temperature=0.7
                )
            
            # 解码输出
            generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            
            # 提取生成的部分
            generated_text = generated_text.replace(prompt, "").strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"评估模型时出错: {str(e)}")
            return ""

def main():
    """主函数，用于测试"""
    # 默认参数
    model_name = "THUDM/chatglm2-6b"  # 使用ChatGLM2-6B作为基础模型
    training_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "training_data.csv")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "finetuned_model")
    
    # 创建模型目录
    os.makedirs(os.path.dirname(output_dir), exist_ok=True)
    
    # 初始化微调器
    finetuner = ModelFinetuner(model_name, training_data_path, output_dir)
    
    # 训练模型
    finetuner.train(learning_rate=2e-5, num_epochs=1, batch_size=4)
    
    # 测试模型
    test_input = "这是一个测试输入，请生成相应的内容。"
    output = finetuner.evaluate(test_input)
    
    logger.info(f"测试输入: {test_input}")
    logger.info(f"生成输出: {output}")

if __name__ == "__main__":
    main() 