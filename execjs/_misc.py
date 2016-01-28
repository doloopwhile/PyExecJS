import re


def encode_unicode_codepoints(str):
    r"""
    >>> encode_unicode_codepoints("a") == 'a'
    True
    >>> ascii = ''.join(chr(i) for i in range(0x80))
    >>> encode_unicode_codepoints(ascii) == ascii
    True
    >>> encode_unicode_codepoints('\u4e16\u754c') == '\\u4e16\\u754c'
    True
    """
    codepoint_format = '\\u{0:04x}'.format

    def codepoint(m):
        return codepoint_format(ord(m.group(0)))

    return re.sub('[^\x00-\x7f]', codepoint, str)
