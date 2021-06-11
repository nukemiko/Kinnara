# -*- coding: UTF-8 -*-
import base64
import binascii
import io
import json
import os
from struct import unpack
from typing import Union, Optional, IO
from tempfile import NamedTemporaryFile

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util.strxor import strxor
from mutagen import mp3, flac, id3


class DecryptionError(Exception):
    pass


class QMCDecrypter:
    """不建议直接使用此类，以及此类中的任何方法。`qmc()` 函数对此类进行了封装，请使用 `qmc()`。"""
    _x, _y, _dx, _index = -1, 8, 1, -1
    _seed_map = [
        [0x4a, 0xd6, 0xca, 0x90, 0x67, 0xf7, 0x52],
        [0x5e, 0x95, 0x23, 0x9f, 0x13, 0x11, 0x7e],
        [0x47, 0x74, 0x3d, 0x90, 0xaa, 0x3f, 0x51],
        [0xc6, 0x09, 0xd5, 0x9f, 0xfa, 0x66, 0xf9],
        [0xf3, 0xd6, 0xa1, 0x90, 0xa0, 0xf7, 0xf0],
        [0x1d, 0x95, 0xde, 0x9f, 0x84, 0x11, 0xf4],
        [0x0e, 0x74, 0xbb, 0x90, 0xbc, 0x3f, 0x92],
        [0x00, 0x09, 0x5b, 0x9f, 0x62, 0x66, 0xa1]
    ]

    @classmethod
    def _reset(cls):
        cls._x, cls._y, cls._dx, cls._index = -1, 8, 1, -1
        _seed_map = [
            [0x4a, 0xd6, 0xca, 0x90, 0x67, 0xf7, 0x52],
            [0x5e, 0x95, 0x23, 0x9f, 0x13, 0x11, 0x7e],
            [0x47, 0x74, 0x3d, 0x90, 0xaa, 0x3f, 0x51],
            [0xc6, 0x09, 0xd5, 0x9f, 0xfa, 0x66, 0xf9],
            [0xf3, 0xd6, 0xa1, 0x90, 0xa0, 0xf7, 0xf0],
            [0x1d, 0x95, 0xde, 0x9f, 0x84, 0x11, 0xf4],
            [0x0e, 0x74, 0xbb, 0x90, 0xbc, 0x3f, 0x92],
            [0x00, 0x09, 0x5b, 0x9f, 0x62, 0x66, 0xa1]
        ]

    @classmethod
    def _next_mask(cls):
        cls._index += 1
        # ret = None
        if cls._x < 0:
            cls._dx = 1
            cls._y = ((8 - cls._y) % 8)
            ret = 0xc3
        elif cls._x > 6:
            cls._dx = -1
            cls._y = 7 - cls._y
            ret = 0xd8
        else:
            ret = cls._seed_map[cls._y][cls._x]
        cls._x += cls._dx
        if cls._index == 0x8000 or (cls._index > 0x8000 and (cls._index + 1) % 0x8000 == 0):
            return cls._next_mask()
        return ret

    @classmethod
    def decrypt(cls, input_bytes: bytes):
        cls._reset()
        input_bytes_len = len(input_bytes)
        bytes_temp = bytearray(input_bytes_len)
        for index in range(input_bytes_len):
            bytes_temp[index] = cls._next_mask() ^ input_bytes[index]
        return bytes(bytes_temp)


def qmc(obj: Union[bytes, bytearray, IO[bytes]]):
    """用于解密采用QMC方式加密的数据。

    :param obj: 需要解密的内容，可以是 bytes、bytearray，或任何类文件对象
    :return: 解密后的数据，bytes
    :rtype: bytes"""
    while True:
        if isinstance(obj, (bytes, bytearray)):
            input_bytes = bytes(obj)
            break
        elif getattr(obj, 'read', None):
            obj = obj.read()
        else:
            raise TypeError(f"only access bytes or file-like object, but input {obj.__class__.__name__}")

    return QMCDecrypter.decrypt(input_bytes=input_bytes)


def ncm_format(obj: Union[bytes, bytearray, IO[bytes]]):
    """用于获取采用NCM方式加密的数据所用的音频格式（flac 或 mp3）。

    :param obj: 需要操作的内容，可以是 bytes、bytearray，或任何类文件对象
    :return: 获取到的格式（flac 或 mp3），str
    :raises DecryptionError: 在输入的内容不是来自NCM格式的文件时触发"""
    while True:
        if isinstance(obj, (bytes, bytearray)):
            八重樱 = io.BytesIO(obj)
            break
        elif getattr(obj, 'read', None):
            obj = obj.read()
        else:
            raise TypeError(f"only access bytes, bytearray or file-like object, but input {obj.__class__.__name__}")

    meta_key = binascii.a2b_hex('2331346C6A6B5F215C5D2630553C2728')

    # If the first 8 bytes are not specific content, raise DecryptionError
    data_header = 八重樱.read(8)
    if binascii.b2a_hex(data_header) != b'4354454e4644414d':
        raise DecryptionError("input data not with NCM encryption")

    八重樱.seek(2, 1)

    # Skip all key data
    key_len = 八重樱.read(4)
    key_len = unpack('<I', bytes(key_len))[0]

    八重樱.seek(key_len, 1)

    # Get meta data
    meta_len = 八重樱.read(4)
    meta_len = unpack('<I', bytes(meta_len))[0]

    if meta_len:
        metadata = bytearray(八重樱.read(meta_len))
        metadata = bytes(bytearray([byte ^ 0x63 for byte in metadata]))
        metadata = base64.b64decode(metadata[22:])

        cryptor = AES.new(meta_key, AES.MODE_ECB)
        metadata = unpad(cryptor.decrypt(metadata), 16).decode('UTF-8')
        metadata = json.loads(metadata[6:])
    else:
        metadata = {'format': 'flac' if os.fstat(八重樱.fileno()).st_size > 1024 ** 2 * 16 else 'mp3'}
    八重樱.close()
    del 八重樱

    return metadata['format']


def ncm(obj: Union[bytes, bytearray, IO[bytes]], add_tags=True):
    """用于解密采用NCM方式加密的数据。

    在写入元数据时，将会先把解密后的音频数据写入临时文件，然后再写入元数据（这是由 `mutagen` 的特性决定的）。

    如果需要处理的数据或文件较多，可能会引起系统的卡顿。

    :param obj: 需要解密的内容，可以是 bytes、bytearray，或任何类文件对象
    :param add_tags: 是否在解密后添加元信息，默认为 True
    :return: 解密后的数据，bytes
    :raises DecryptionError: 在输入的内容不是来自NCM格式的文件时触发"""
    while True:
        if isinstance(obj, (bytes, bytearray)):
            八重樱 = io.BytesIO(obj)
            break
        elif getattr(obj, 'read', None):
            obj = obj.read()
        else:
            raise TypeError(f"only access bytes, bytearray or file-like object, but input {obj.__class__.__name__}")

    core_key = binascii.a2b_hex('687A4852416D736F356B496E62617857')
    meta_key = binascii.a2b_hex('2331346C6A6B5F215C5D2630553C2728')

    # If the first 8 bytes are not specific content, raise DecryptionError
    data_header = 八重樱.read(8)
    if binascii.b2a_hex(data_header) != b'4354454e4644414d':
        raise DecryptionError("input data not with NCM encryption")

    八重樱.seek(2, 1)

    # Get key data
    key_len = 八重樱.read(4)
    key_len = unpack('<I', bytes(key_len))[0]

    key_data = bytearray(八重樱.read(key_len))
    key_data = bytes(bytearray(byte ^ 0x64 for byte in key_data))

    cryptor = AES.new(core_key, AES.MODE_ECB)
    key_data = unpad(cryptor.decrypt(key_data), 16)[17:]
    key_len = len(key_data)

    # S-box
    key = bytearray(key_data)
    S = bytearray(range(256))
    j = 0

    for i in range(256):
        j = (j + S[i] + key[i % key_len]) & 0xff
        S[i], S[j] = S[j], S[i]

    # Get meta data
    meta_len = 八重樱.read(4)
    meta_len = unpack('<I', bytes(meta_len))[0]

    if meta_len:
        metadata = bytearray(八重樱.read(meta_len))
        metadata = bytes(bytearray([byte ^ 0x63 for byte in metadata]))
        identifier = metadata.decode('UTF-8')
        metadata = base64.b64decode(metadata[22:])

        cryptor = AES.new(meta_key, AES.MODE_ECB)
        metadata = unpad(cryptor.decrypt(metadata), 16).decode('UTF-8')
        metadata = json.loads(metadata[6:])
    else:
        metadata = {'format': 'flac' if os.fstat(八重樱.fileno()).st_size > 1024 ** 2 * 16 else 'mp3'}
        identifier = ''

    八重樱.seek(5, 1)

    # Get album cover
    image_space = 八重樱.read(4)
    image_space = unpack('<I', bytes(image_space))[0]
    image_size = 八重樱.read(4)
    image_size = unpack('<I', bytes(image_size))[0]
    if image_size:
        image_data = 八重樱.read(image_size)
    else:
        image_data = None

    八重樱.seek(image_space - image_size, 1)

    # Get decrypted media data
    encrypted_data = 八重樱.read()
    八重樱.close()
    del 八重樱

    # Stream cipher
    stream = [S[(S[i] + S[(i + S[i]) & 0xFF]) & 0xFF] for i in range(256)]
    stream = bytes(bytearray(stream * (len(encrypted_data) // 256 + 1))[1:1 + len(encrypted_data)])
    decrypted_data = strxor(encrypted_data, stream)
    del encrypted_data

    # Add media tags to decrypted data
    # First, write encrypted data to a temporary file
    if add_tags:
        八重凛 = NamedTemporaryFile(mode='wb', delete=False)
        tmpfile_name = 八重凛.name
        八重凛.write(decrypted_data)
        八重凛.close()
        del decrypted_data, 八重凛

        # Second, add media tags
        def embed(item: Union[flac.Picture, id3.APIC], content: Optional[bytes], content_type: int):
            try:
                if content[:4] == binascii.a2b_hex('89504E47'):
                    item.mime = 'image/png'
                else:
                    item.mime = 'image/jpeg'
            except TypeError:
                return
            else:
                item.encoding = 0
                item.type = content_type
                item.data = content

        if image_data:
            if metadata['format'] == 'flac':
                audio = flac.FLAC(tmpfile_name)
                image = flac.Picture()
                embed(image, image_data, 3)
                audio.clear_pictures()
                audio.add_picture(image)
            else:
                audio = mp3.MP3(tmpfile_name)
                image = id3.APIC()
                embed(image, image_data, 6)
                audio.tags.add(image)
            audio.save()

        if meta_len:
            if metadata['format'] == 'flac':
                audio = flac.FLAC(tmpfile_name)
                audio['descripition'] = identifier
            else:
                audio = mp3.EasyMP3(tmpfile_name)
                audio['title'] = 'placeholder'
                audio.tags.RegisterTextKey('comment', 'COMM')
                audio['comment'] = identifier
            audio['title'] = metadata['musicName']
            audio['album'] = metadata['album']
            audio['artist'] = '/'.join([artist[0] for artist in metadata['artist']])
            audio.save()

        # Third, read from temporary file
        with open(tmpfile_name, 'rb') as tmpfileobj:
            ret = tmpfileobj.read()
        os.remove(tmpfile_name)
    else:
        ret = decrypted_data

    return ret
