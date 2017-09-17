#!/usr/bin/env python
# -*- coding:utf8 -*-
#
# created by shibaofeng@ipin.com 2017/5/31
#
import math
from urllib.parse import quote, unquote

__encrypted_short_str__ = "qrcklmDoExthWJiHAp1sVYKU3RFMQw8IGfPO92bvLNj.7zXBaSnu0TC6gy_4Ze5d"

__qrck__ = []


def jsc_qrck():
    if len(__qrck__) > 0:
        return __qrck__
    for c in __encrypted_short_str__:
        __qrck__.append(c)
    return __qrck__


def splits(arr, min_i, max_i, step):
    mid = int(math.floor((min_i + max_i) / 2.0))
    if step > 0:
        step -= 1
        if mid - min_i >= 3:
            splits(arr, min_i, mid, step)
        if max_i - mid >= 3:
            splits(arr, mid, max_i, step)
    for i in range(min_i, mid, 2):
        v = arr[i]
        w = max_i - 1 - i + min_i
        arr[i] = arr[w]
        arr[w] = v


def jsc_split_str(s):
    v = list(s)
    splits(v, 0, len(v), 2)
    return ''.join(v)


def divide_str(s, length):
    a = []
    i = 0
    l = len(s)
    while i + length < l:
        a.append(s[i:i + length])
        i += 1
    if i < l:
        a.append(s[i:])
    return a


def get_encrypt_code_array(
        password='ef ghi  jklmnoL U3F9\\_XM?Ep  q rs1PW\');A0@.7I<JDC=:RV85-O6]t uv[ QG#`^BY,/K$%&S(2!"4+TH>*ZNacbd'):
    arr = [0] * 32
    for i in password:
        arr.append(ord(i) - 33)
    return arr


def jsc_str2arr(raw):
    l = len(raw)
    arr = []
    encrypt_arr = get_encrypt_code_array()
    i = 0
    while i + 3 < l:
        a = encrypt_arr[ord(raw[i])]
        b = encrypt_arr[ord(raw[i + 1])]
        c = encrypt_arr[ord(raw[i + 2])]
        d = encrypt_arr[ord(raw[i + 3])]
        arr.append((a << 2) | (b >> 4))
        arr.append(((b & 15) << 4) | (c >> 2))
        arr.append(((c & 3) << 6) | d)
        i += 4

    if i < l:
        a = encrypt_arr[ord(raw[i])]
        b = encrypt_arr[ord(raw[i + 1])]
        arr.append((a << 2) | (b >> 4))
        if i + 2 < l:
            c = encrypt_arr[ord(raw[i + 2])]
            arr.append(((b & 15) << 4) | (c >> 2))
    return arr


def jsc_int_decode(raw):
    arr = jsc_str2arr(raw)
    a = (arr[0] << 8) + arr[1]
    l = len(arr)
    for i in range(2, l, 2):
        arr[i] ^= (a >> 8) & 0xFF
        i += 1
        if i < l:
            arr[i] ^= a & 0xFF
        a += 1
    return arr[2:]


def jsc_arr2str(arr, start=0, end=None):
    start = start if (start is not None and isinstance(start, int) and start >= 0) else 0
    end = len(arr) if end is None or end < start else end
    res = []
    while True:
        i = start + 40960
        if i >= end:
            res.append(jsc_arr_chr(arr[start:end]))
            break
        else:
            res.append(jsc_arr_chr(arr[start:i]))
            start = i
    return ''.join(res)


__CODE_ARRAY__ = []


def jsc_generate_code_array():
    if len(__CODE_ARRAY__) > 0:
        return __CODE_ARRAY__
    for v in range(0, 256):
        v7 = v
        for w in range(0, 8):
            if v7 & 0x80 != 0:
                v7 = (v7 << 1) ^ 7
            else:
                v7 <<= 1
        __CODE_ARRAY__.append(v7 & 0xff)
    return __CODE_ARRAY__


def jsc_verify_int(arr):
    if isinstance(arr, str):
        arr = jsc_str_ord(arr)
    w = 0
    b = jsc_generate_code_array()
    for v in arr:
        w = b[(w ^ v) & 0xFF]
    return w


def jsc_arr_chr(arr):
    a = []
    for i in arr:
        a.append(chr(i))
    return ''.join(a)


def jsc_str_ord(src):
    a = []
    for c in src:
        a.append(ord(c))
    return a


def jsc_verify_str(verify_int, start):
    a = []
    qrck = jsc_qrck()
    while start > 0:
        a.append(qrck[verify_int % 64])
        verify_int = int(math.floor(verify_int / 64))
        start -= 1
    a.reverse()
    return ''.join(a)


def jsc_arr_decode(arr):
    m = 63
    c = []
    i = 0
    l = len(arr)
    while i < l:
        a = arr[i]
        if a < 0x80:
            b = a
        elif a < 0xC0:
            b = m
        elif a < 0xe0:
            b = ((a & 0x0F) << 6) | (arr[i + 1] & 0x3F)
            i += 1
        elif a < 0xf0:
            b = ((a & 0x0F) << 12) | ((arr[i + 1] & 0x3F) << 6) | (arr[i + 2] & 0x3F)
            i += 2
        elif a < 0xf8:
            b = m
            i += 3
        elif a < 0xfc:
            b = m
            i += 4
        elif a < 0xfe:
            b = m
            i += 5
        else:
            b = m
        i += 1
        c.append(b)
    return jsc_arr2str(c)


def jsc_decode(raw):
    return jsc_arr_decode(jsc_int_decode(raw))


def jsc_verify_encode(src):
    if src is None:
        return ''
    vs = src.split('&')
    ve = []
    for s in vs:
        w = s.split('=')
        ve.append(quote(
            unquote(w[0]) + '=' + quote(unquote(w[1] if len(w) > 1 else 'undefined'))))
    return '&'.join(ve)

if __name__ == '__main__':
    s = '3SVh3pwbKsfWFGQ.sKqh8GS7cvJJIASnsmJWsASmc90iASltk09lsGT3lV3qwATimqEcUfWpmSxYqTVcVGzFqmQqKamArTqHKGl'
    c = jsc_str2arr(s)
    print(c)
    ia = jsc_int_decode(s)
    print(ia)
    print(jsc_arr_decode(ia))
