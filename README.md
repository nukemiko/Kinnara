# Kinnara - 针对加密音乐文件的解密工具

![shieid](https://img.shields.io/badge/python-3.6%2B-blue)

## 主要功能

这个工具可以用来干什么，大概不用我多说了吧？

## 安装说明

### 版本要求

python 3.6 及以上版本

### 依赖关系

- `pycryptodome`
- `mutagen`

需要在安装 Kinnara 之前安装它们。

### 安装步骤

1. `git clone https://github.com/nukemiko/Kinnara.git`
2. 找到克隆下来的仓库，把仓库的路径加入 `PYTHONPATH` 环境变量，或者加入 `.pth` 文件

## 如何使用？

作为应用程序使用：

```
$ python -m kinnara

usage: kinnara [-f FORMAT] [-F] [-q] [-h] [-v] [-d DIR | -o FILE | -S] file

对加密的音乐文件进行解密。
目前支持 ncm 和 qmc 两种格式。

optional arguments:
  -d DIR, --dir DIR     保存输出文件的目录
                        默认：/home/menacing/Music/DRMed
  -o FILE, --output FILE
                        保存输出文件的名字
                        输出文件将以此名字保存在 -d 参数指定的相对路径下。
  -S, --stdout          将数据写入标准输出以方便重定向

必填:
  file                  需要解密的文件

可选:
  -f FORMAT, --format FORMAT
                        指定输入文件的格式：qmcflac，qmc0，qmc3，或 ncm
                        默认情况下，根据文件扩展名判断；如果没有扩展名且没有指定格式，解密将终止。
  -F, --force, --overwrite
                        如果输出文件的名字与其它文件冲突，覆盖已经存在的文件
  -q, --quiet           解密完毕后，不显示解密的文件的位置
  -h, --help            显示帮助信息
  -v, --version         显示版本信息

“-d”，“-o”，“-S”以及它们的长选项形式互相冲突，不能放在一起使用。
```

作为 python 模块导入后使用：

```python
>>> import kinnara
>>> decrypted_from_qmc = kinnara.qmc(open('1.qmc0', 'rb'))
>>> with open('1.mp3', 'wb') as fileobj:
...     fileobj.write(decrypted_from_qmc)
...
>>> decrypted_from_ncm = kinnara.ncm(open('2.ncm', 'rb'))
>>> decrypted_from_ncm['format']
'flac'
>>> with open('2.flac', 'wb') as fileobj:
...     fileobj.write(decrypted_from_ncm)
...
>>>
```

## 问题解决

如果遇到问题，建议采取以下方式进行排查：

- `DecryptionError`

    如果你传入了.ncm文件，确认它是从网易云音乐客户端的下载目录里面找到的。

- `SyntaxError`

    运行命令：`python -V`，如果显示的版本低于3.6，快点去更新 python 吧。

- `ModuleNotFoundError: No module named 'Crypto'` 或者 `ModuleNotFoundError: No module named 'mutagen'`

    请查看[依赖关系](#依赖关系)中列出的依赖是否已经全部安装。

