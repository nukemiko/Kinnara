# -*- coding: UTF-8 -*-
import argparse
import os
import pathlib
from typing import Optional
import sys

import kinnara

progname = 'kinnara'
progname_versioninfo = progname.title()
progver = '0.5'

try:
    cmdparser = argparse.ArgumentParser(
            add_help=False, formatter_class=argparse.RawTextHelpFormatter, prog=progname,
            description='解密受到版权保护的音乐文件。\n目前支持 ncm 和 qmc 两种格式。',
            epilog='“-d”，“-o”，“-S”以及它们的长选项形式互相冲突，不能放在一起使用。')

    necessary_group = cmdparser.add_argument_group('必填')

    necessary_group.add_argument('input_filepath', metavar='file', type=pathlib.Path,
                                 help='需要解密的文件')

    optional_group = cmdparser.add_argument_group('可选')
    optional_group.add_argument('-f', '--format', metavar='FORMAT', dest='input_file_format',
                                help='指定输入文件的格式：qmcflac，qmc0，qmc3，或 ncm\n'
                                     '如果未指定此选项，则根据文件扩展名判断；如果没有扩展名且没有指定格式，解密将终止。')
    optional_group.add_argument('-F', '--force', '--overwrite', action='store_true', dest='overwrite_conflict',
                                help='如果输出文件的名字与其它文件冲突，覆盖已经存在的文件\n')
    optional_group.add_argument('-q', '--quiet', action='store_false', dest='show_detail',
                                help='不显示所有常规输出\n'
                                     '“-S”、“--stdout”选项不受此选项的影响。')
    optional_group.add_argument('-h', '--help', help='显示帮助信息', action='help')
    optional_group.add_argument('-v', '--version', help='显示版本信息', action='version',
                                version=f'{progname_versioninfo} - 针对受到版权保护的音乐文件的解密工具，版本 v{progver}\n\n'
                                        '文件的解密部分使用了以下项目的代码，在此向他们的工作表示感谢：\n'
                                        '    yamausagi22/qmcparser\n    nondanee/ncmdump\n\n')

    conflict_group = cmdparser.add_mutually_exclusive_group()
    conflict_group.add_argument('-d', '--dir', metavar='DIR', action='store', dest='output_dir', type=pathlib.Path,
                                # default=pathlib.Path(os.getcwd()),
                                help=f'保存输出文件的目录\n默认：{pathlib.Path(os.getcwd())}')
    conflict_group.add_argument('-o', '--output', metavar='FILE', action='store', dest='output_filepath',
                                type=pathlib.Path,
                                help=f'保存输出文件的名字\n'
                                     f'如果填入相对路径，那么输出文件的保存路径是：当前工作目录 + 相对路径')
    conflict_group.add_argument('-S', '--stdout', action='store_true', dest='output_is_stdout',
                                help='将数据写入标准输出，用于重定向')

    args = vars(cmdparser.parse_args())

    input_filepath: pathlib.Path = args['input_filepath']
    input_file_format: str = args['input_file_format']
    overwrite_conflict: bool = args['overwrite_conflict']
    show_detail: bool = args['show_detail']
    output_dir: pathlib.Path = args['output_dir']
    output_filepath: Optional[pathlib.Path] = args['output_filepath']
    output_is_stdout: bool = args['output_is_stdout']

    if input_filepath.exists():
        # input_filepath存在
        if input_filepath.is_dir():
            # 如果input_filepath是目录，退出
            sys.stderr.write(f"{progname}: 错误：“{input_filepath}”是一个目录\n{progname}: 操作中断\n")
            exit(1)
    else:
        # input_filepath不存在
        sys.stderr.write(f"{progname}: 错误：“{input_filepath}”不存在\n{progname}: 操作中断\n")
        exit(1)

    input_filepath_parent, input_filename = input_filepath.parent, input_filepath.name
    input_filename_base, input_filename_suffix = os.path.splitext(input_filename)

    # 输入文件格式判定
    format_suffix_map = {
        '.ncm': '.placeholder',
        '.qmc3': '.mp3',
        '.qmc0': '.mp3',
        '.qmcflac': '.flac'
    }
    if input_file_format:
        # 指定了文件格式
        if input_file_format.lower() not in [item.removeprefix('.') for item in format_suffix_map.keys()]:
            sys.stderr.write(f"{progname}: 错误：不支持“{input_file_format}”格式\n{progname}: 操作中断\n")
            exit(1)
        else:
            input_file_format = '.' + input_file_format
            output_filename_suffix = format_suffix_map.get(input_file_format)
    elif input_filename_suffix:
        # 未指定格式，根据扩展名猜测文件格式
        # 如果扩展名是 .ncm，在解密过程中进行猜测
        input_file_format = input_filename_suffix.lower()
        output_filename_suffix = format_suffix_map.get(input_file_format)
        if not output_filename_suffix:
            sys.stderr.write(f"{progname}: 错误：无法判定输入文件“{input_filepath}”的格式\n{progname}: 操作中断\n")
            exit(1)
    else:
        sys.stderr.write(f"{progname}: 错误：无法判定输入文件“{input_filepath}”的格式\n{progname}: 操作中断\n")
        exit(1)

    # output_dir, output_filepath, output_is_stdout 三选一
    if output_dir:
        if output_dir.exists():
            if output_dir.is_file():
                sys.stderr.write(f"{progname}: 错误：“{output_dir}”是一个文件而不是目录\n{progname}: 操作中断\n")
                exit(1)
        else:
            sys.stderr.write(f"{progname}: 错误：“{output_dir}”不存在\n{progname}: 操作中断\n")
            exit(1)
    elif output_filepath:
        if output_filepath.exists():
            sys.stderr.write(f"{progname}: 错误：“{output_filepath}”已经存在\n{progname}: 操作中断\n")
            exit(1)
    elif output_is_stdout:
        pass
    else:
        output_dir = pathlib.Path(os.getcwd())

    # 开始解密过程
    with open(input_filepath, 'rb') as inputfile:
        input_data = inputfile.read()
    if input_file_format in ('.placeholder', '.ncm'):
        output_filename_suffix = '.' + kinnara.ncm_format(input_data)
        output_data = kinnara.ncm(input_data)
    elif input_file_format.startswith('.qmc'):
        sys.stderr.write("解密QMC方式加密的文件需要一些时间，请稍安勿躁。\n")
        output_data = kinnara.qmc(input_data)
    else:
        sys.stderr.write(f"{progname}: 漏网之鱼：{input_file_format}\n")
        exit(1)
    if output_is_stdout:
        sys.stdout.buffer.write(output_data)
        exit()
    # 如果 output_filepath 未指定，生成一个
    if not output_filepath:
        output_filepath = output_dir / pathlib.Path(input_filename_base + output_filename_suffix)
    if show_detail:
        sys.stdout.write(str(output_filepath) + '\n')
    with open(output_filepath, 'wb') as outputfile:
        outputfile.write(output_data)
except KeyboardInterrupt:
    sys.stderr.write(f"{progname}: 操作被 Ctrl-C 组合键中断\n")
    exit(1)
except kinnara.DecryptionError as e:
    sys.stderr.write(f"{progname}: 错误：{e}\n{progname}: 操作中断\n")
