import argparse
import io
import os
import pathlib
from typing import Optional
import sys

from kinnara import *

progname = 'kinnara'
progname_versioninfo = 'Kinnara'
progver = '0.5'

try:
    cmdparser = argparse.ArgumentParser(
            add_help=False, formatter_class=argparse.RawTextHelpFormatter, prog=progname,
            description='对加密的音乐文件进行解密。\n目前支持 ncm 和 qmc 两种格式。',
            epilog='“-d”，“-o”，“-S”以及它们的长选项形式互相冲突，不能放在一起使用。')

    necessary_group = cmdparser.add_argument_group('必填')

    necessary_group.add_argument('input_filepath', metavar='file', type=pathlib.Path,
                                 help='需要解密的文件')

    optional_group = cmdparser.add_argument_group('可选')
    optional_group.add_argument('-f', '--format', metavar='FORMAT', dest='input_file_format',
                                help='指定输入文件的格式：qmcflac，qmc0，qmc3，或 ncm\n'
                                     '默认情况下，根据文件扩展名判断；如果没有扩展名且没有指定格式，解密将终止。')
    optional_group.add_argument('-F', '--force', '--overwrite', action='store_true', dest='overwrite_conflict',
                                help='如果输出文件的名字与其它文件冲突，覆盖已经存在的文件\n')
    optional_group.add_argument('-q', '--quiet', action='store_false', dest='show_detail',
                                help='解密完毕后，不显示解密的文件的位置')
    optional_group.add_argument('-h', '--help', help='显示帮助信息', action='help')
    optional_group.add_argument('-v', '--version', help='显示版本信息', action='version',
                                version=f'{progname_versioninfo} - 针对加密音乐文件的解密工具，版本 v{progver}\n\n'
                                        '文件的解密部分使用了以下项目的代码，在此向他们的工作表示感谢：\n'
                                        '    yamausagi22/qmcparser\n    nondanee/ncmdump\n\n')
    # '（Kinnara 是阴阳师手游中某位式神的名字的日语发音，猜猜是哪位。）')

    conflict_group = cmdparser.add_mutually_exclusive_group()
    conflict_group.add_argument('-d', '--dir', metavar='DIR', action='store', dest='output_dir', type=pathlib.Path,
                                default=pathlib.Path(os.getcwd()),
                                help=f'保存输出文件的目录\n默认：{pathlib.Path(os.getcwd())}')
    conflict_group.add_argument('-o', '--output', metavar='FILE', action='store', dest='output_filepath',
                                type=pathlib.Path,
                                help=f'保存输出文件的名字\n输出文件将以此名字保存在 -d 参数指定的相对路径下。')
    conflict_group.add_argument('-S', '--stdout', action='store_true', dest='output_is_stdout',
                                help='将数据写入标准输出以方便重定向')

    args = vars(cmdparser.parse_args())

    input_filepath: pathlib.Path = args['input_filepath']
    input_file_format: str = args['input_file_format']
    overwrite_conflict: bool = args['overwrite_conflict']
    show_detail: bool = args['show_detail']
    output_dir: pathlib.Path = args['output_dir']
    output_filepath: Optional[pathlib.Path] = args['output_filepath']
    output_is_stdout: bool = args['output_is_stdout']

    if input_filepath.exists():
        if input_filepath.is_dir():
            print(f"{progname}：{input_filepath}：是一个目录")
            exit(1)
    else:
        print(f"{progname}：不存在的文件：{input_filepath}")
        exit(1)

    if output_dir.exists():
        if not output_dir.is_dir():
            print(f"{progname}：{output_filepath}：是一个文件")
            exit(1)
    else:
        print(f"{progname}：不存在的目录：{output_dir}")
        exit(1)

    suffix_force = ''
    if input_file_format:
        if input_file_format.lower() not in ('qmcflac', 'qmc0', 'qmc3', 'ncm'):
            print(f"{progname}：不支持或未知的格式：{input_file_format}")
            exit(1)
        else:
            suffix_force = '.' + input_file_format

    orig_suffix = ''
    prefix = ''
    while True:
        if output_filepath:
            if output_filepath.exists() and not overwrite_conflict and not output_is_stdout:
                print(f"{progname}：{output_filepath} 已经存在\n"
                      f"{progname}：如果需要覆盖已经存在的文件，请指定“-F”，“--force”或“--overwrite”选项。")
                exit(1)
            else:
                break
        else:
            suffix = ''
            prefix, orig_suffix = os.path.splitext(input_filepath.name)
            if suffix_force:
                orig_suffix = suffix_force
            if orig_suffix.lower() == '.qmcflac':
                suffix = '.flac'
            elif orig_suffix.lower() in ('.qmc0', '.qmc3'):
                suffix = '.mp3'
            elif orig_suffix.lower() == '.ncm':
                suffix = '.placeholder'
            else:
                print(f"{progname}：无法确定“{input_filepath}”的格式，因此无法进行解密。\n"
                      f"{progname}：如果您知道输入文件的格式，请使用“-f”选项指定一个。")
                exit(1)
            output_filename = prefix + suffix
            output_filepath = output_dir / pathlib.Path(output_filename)

    with open(input_filepath, 'rb') as fileobj:
        if orig_suffix.startswith('.qmc'):
            decrypted_data = qmc(fileobj)
        elif orig_suffix.startswith('.ncm'):
            encrypted_data = fileobj.read()
            fileobj1 = io.BytesIO(encrypted_data)
            fileobj2 = io.BytesIO(encrypted_data)
            decrypted_data_format, decrypted_data = ncm(fileobj1, only_get_format=True).values()
            output_filename = prefix + '.' + decrypted_data_format
            output_filepath = output_dir / pathlib.Path(output_filename)
            if output_filepath.exists() and not overwrite_conflict and not output_is_stdout:
                print(f"{progname}：{output_filepath} 已经存在\n"
                      f"{progname}：如果需要覆盖已经存在的文件，请指定“-F”，“--force”或“--overwrite”选项。")
                exit(1)
            else:
                decrypted_data_format, decrypted_data = ncm(fileobj2).values()
        else:
            print(f"{progname}：指定了一个空的格式")
            exit(1)

    if output_is_stdout:
        sys.stdout.buffer.write(decrypted_data)
        exit()
    else:
        with open(output_filepath, 'wb') as fileobj:
            fileobj.write(decrypted_data)
        if show_detail:
            print(output_filepath)
except KeyboardInterrupt:
    print(f"{progname}：解密操作被用户中断")
    exit(1)
