# Kinnara - 针对受版权保护的音乐文件的解密工具

![shieid](https://img.shields.io/badge/python-3.6%2B-green)

## 安装说明

### 版本要求

Python 3.6 及以上版本

### 依赖关系

- `pycryptodomex`
- `mutagen`

如果使用[方法2](#方法2)安装 Kinnara，那么需要在安装 Kinnara 之前安装它们。

### 安装步骤

#### 方法1（推荐）

`pip install git+https://github.com/nukemiko/Kinnara.git`

#### 方法2

1. `git clone https://github.com/nukemiko/Kinnara.git`
2. 找到克隆下来的仓库，把仓库的路径加入 `PYTHONPATH` 环境变量，或者加入 `.pth` 文件

## 如何使用？

### 作为应用程序使用

```
$ python -m kinnara -h
usage: kinnara [-f FORMAT] [-F] [-q] [-h] [-v] [-d DIR | -o FILE | -S] file

解密受到版权保护的音乐文件。
目前支持 ncm 和 qmc 两种格式。

optional arguments:
  -d DIR, --dir DIR     保存输出文件的目录
                        默认：<当前工作目录>
  -o FILE, --output FILE
                        保存输出文件的名字
                        如果填入相对路径，那么输出文件的保存路径是：当前工作目录 + 相对路径
  -S, --stdout          将数据写入标准输出，用于重定向

必填:
  file                  需要解密的文件

可选:
  -f FORMAT, --format FORMAT
                        指定输入文件的格式：qmcflac，qmc0，qmc3，或 ncm
                        如果未指定此选项，则根据文件扩展名判断；如果没有扩展名且没有指定格式，解密将终止。
  -F, --force, --overwrite
                        如果输出文件的名字与其它文件冲突，覆盖已经存在的文件
  -q, --quiet           不显示所有常规输出
                        “-S”、“--stdout”选项不受此选项的影响。
  -h, --help            显示帮助信息
  -v, --version         显示版本信息

“-d”，“-o”，“-S”以及它们的长选项形式互相冲突，不能放在一起使用。
```

### 作为 python 模块导入后使用

```python
>>> import kinnara
# QMC文件解密
>>> with open('1.qmc0', 'rb') as qmcfile:
...     qmc_data = qmcfile.read()
...
>>> decrypted_data = kinnara.qmc(qmc_data)
>>> with open('1.mp3', 'wb') as fileobj:
...     fileobj.write(decrypted_data)
...
# NCM文件解密
>>> with open('2.ncm', 'rb') as ncmfile:
...     ncm_data = ncmfile.read()
...
# 获取采用NCM方式加密的音频文件的格式
>>> music_format = kinnara.ncm_format(ncm_data)
'flac'
>>> decrypted_data = kinnara.ncm(ncm_data)
>>> with open('.'.join(['2', music_format]), 'wb') as fileobj:
...     fileobj.write(decrypted_data)
...
>>>
```

## 问题解决

- `SyntaxError: invalid syntax`
    - 升级 Python 至 3.6 或者更高版本后再次尝试
- `ModuleNotFoundError: No module named 'Crypto'`, `ModuleNotFoundError: No module named 'mutagen'`
    - 如果采用[方法2](#方法2)安装，可能会出现。
    - 解决方案：安装[依赖关系](#依赖关系)中的 Python 包：
        - `pip install -U pycryptodome`
        - `pip install -U mutagen`
- `kinnara: 错误：input data not with NCM encryption`
    - 如果指定了输入文件的加密方式是 NCM，或者 kinnara 判断输入文件的加密方式是 NCM，但是实际上输入文件的加密方式不是 NCM（或者根本没有加密），就会出现这个错误。
