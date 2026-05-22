# JSON Converter Tool

一个把任意 JSON 提取并转换成固定 ChatGPT auth JSON 格式的小工具。

## Windows 直接运行

双击：

```text
dist/JsonConverter.exe
```

## Windows 重新打包

```powershell
.\build_windows.ps1
```

## Ubuntu 运行源码

```bash
sudo apt install python3-tk
python3 json_converter.py --ui
```

## Ubuntu 打包

```bash
sudo apt install python3-tk python3-pip
chmod +x build_ubuntu.sh
./build_ubuntu.sh
```

生成文件：

```text
dist/JsonConverter
```
