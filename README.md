
# 一键部署教程 🚀（推荐方式）

> **推荐用户优先使用此方式完成部署，操作简单、无需命令行基础。**

1. 解压 **aipc-ds.zip** 压缩包，运行其中的 `setup` 安装软件主体；  
2. 可自行选择安装位置；  
3. 在运行前**务必将模型权重所有文件夹**放入安装目录下的 `AIPC-DS\ds-amd\_internal\models` 文件夹中；  
4. 双击运行桌面图标或 `AIPC.exe` 启动程序。

📦 安装包下载链接（通过百度网盘分享）：  
**[ 点击下载 aipc-ds.zip ](https://pan.baidu.com/s/1CjGXViEEK2A0SjgXUruLLA?pwd=ecxk)** 提取码: `ecxk`

# Introduction
在AMD Ryzen系列芯片上部署deepseek模型，支持的模型列表如下：

- [DeepSeek-R1-Distill-Qwen-1.5B](https://huggingface.co/amd/DeepSeek-R1-Distill-Qwen-1.5B-awq-asym-uint4-g128-lmhead-onnx-hybrid)
- [DeepSeek-R1-Distill-Llama-8B](https://huggingface.co/amd/DeepSeek-R1-Distill-Llama-8B-awq-asym-uint4-g128-lmhead-onnx-hybrid)
- [DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/amd/DeepSeek-R1-Distill-Qwen-7B-awq-asym-uint4-g128-lmhead-onnx-hybrid)

# Supported computer configuration
仅支持运行Windows 11的Strix （STX）和Krackan Point （KRK）处理器。



# Requirements
- NPU驱动，可参考[NPU](https://ryzenai.docs.amd.com/en/latest/inst.html)

- iGPU驱动，可参考[iGPU](https://www.amd.com/en/support/download/drivers.html)

- 下载必要的.wheel文件与.dll文件，下载链接：[wheel](),下载并解压完成后将其中的wheel和dll文件拷贝到`wheel`目录下

# Execution using Python

## 环境准备
1. 创建conda环境
```bash
conda create --name <env name> python=3.10
```
2. 激活conda环境
```bash
conda activate <env name>
```
3. 安装wheel文件
```bash
cd wheel
pip install onnxruntime_genai-0.4.0.dev0-cp310-cp310-win_amd64.whl
pip install onnxruntime_directml-1.20.1-cp310-cp310-win_amd64.whl
```
4. 安装requirements
```bash
pip install -i requirements.txt
```
## 模型准备
1. 从[huggingface]( https://huggingface.co/collections/amd/amd-ryzenai-deepseek-r1-distill-hybrid-67a53471e9d5f14bece775d2)下载所需的模型，并将模型拷贝到`models`目录下

2. 打开`genai_config.json`文件。位于已下载模型文件夹中的文件。使用位于`wheel`文件夹中的`onnx_custom_ops.dll`的完整路径更新`custom_ops_library`的值.
```bash
"session_options": {
          ...
          "custom_ops_library":"wheel\\onnx_custom_ops.dll",
          ...
}
```

## 运行模型

### 方式1(非接口访问)
```bash
python run_model.py --model_dir path_to\your\model
```

### 方式2(接口访问)

#### 简单开始
修改server.py中的models_paths值为你的模型路径。
```bash
models_paths = {"DeepSeek-R1-Distill-Qwen-1.5B":"path\\to\\DeepSeek-R1-Distill-Qwen-1.5B-awq-asym-uint4-g128-lmhead-onnx-hybrid ",
                "DeepSeek-R1-Distill-Llama-8B":"path\\to\\DeepSeek-R1-Distill-Llama-8B-awq-asym-uint4-g128-lmhead-onnx-hybrid",
                "DeepSeek-R1-Distill-Qwen-7B":"path\\to\\DeepSeek-R1-Distill-Qwen-7B-awq-asym-uint4-g128-lmhead-onnx-hybrid"
              }
```
开启接口服务
```bash
python server.py --port 9090
```

#### API Endpoints

##### Get `/health` : Returns heath check result

- Body : `{"status": "ok" }`
- the model is successfully loaded and the server is ready.

##### Post `/v1/chat/completions`: Given a `prompt`,it returns the result of reasoning

example :
```bash
{"input":"Please solve following problem and explain it to me. Then give me final answer at the end with a single number preceded by string '#### '. Question: Rory orders 2 subs for $7.50 each, 2 bags of chips for $1.50 each and 2 cookies for $1.00 each for delivery.\nAnswer:"}
```

##### Post `/change_model`: change the servering model

example:
```bash
{
    "model_name":"DeepSeek-R1-Distill-Qwen-7B"
}
```











