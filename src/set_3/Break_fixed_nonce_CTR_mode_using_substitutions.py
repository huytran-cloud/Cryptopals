import base64
from Crypto.Random import get_random_bytes

from src.set_1.Break_repeating_key_XOR import decode_single_byte_xor_cypher
from src.Utilities.AES import AesCtr
from src.Utilities.Byte_Calculations import xor_bytes

# globals
AES_BLOCK_SIZE = 16


strings = list(map(base64.b64decode,
                   ['SSBoYXZlIG1ldCB0aGVtIGF0IGNsb3NlIG9mIGRheQ==',
                    'Q29taW5nIHdpdGggdml2aWQgZmFjZXM=',
                    'RnJvbSBjb3VudGVyIG9yIGRlc2sgYW1vbmcgZ3JleQ==',
                    'RWlnaHRlZW50aC1jZW50dXJ5IGhvdXNlcy4=',
                    'SSBoYXZlIHBhc3NlZCB3aXRoIGEgbm9kIG9mIHRoZSBoZWFk',
                    'T3IgcG9saXRlIG1lYW5pbmdsZXNzIHdvcmRzLA==',
                    'T3IgaGF2ZSBsaW5nZXJlZCBhd2hpbGUgYW5kIHNhaWQ=',
                    'UG9saXRlIG1lYW5pbmdsZXNzIHdvcmRzLA==',
                    'QW5kIHRob3VnaHQgYmVmb3JlIEkgaGFkIGRvbmU=',
                    'T2YgYSBtb2NraW5nIHRhbGUgb3IgYSBnaWJl',
                    'VG8gcGxlYXNlIGEgY29tcGFuaW9u',
                    'QXJvdW5kIHRoZSBmaXJlIGF0IHRoZSBjbHViLA==',
                    'QmVpbmcgY2VydGFpbiB0aGF0IHRoZXkgYW5kIEk=',
                    'QnV0IGxpdmVkIHdoZXJlIG1vdGxleSBpcyB3b3JuOg==',
                    'QWxsIGNoYW5nZWQsIGNoYW5nZWQgdXR0ZXJseTo=',
                    'QSB0ZXJyaWJsZSBiZWF1dHkgaXMgYm9ybi4=',
                    'VGhhdCB3b21hbidzIGRheXMgd2VyZSBzcGVudA==',
                    'SW4gaWdub3JhbnQgZ29vZCB3aWxsLA==',
                    'SGVyIG5pZ2h0cyBpbiBhcmd1bWVudA==',
                    'VW50aWwgaGVyIHZvaWNlIGdyZXcgc2hyaWxsLg==',
                    'V2hhdCB2b2ljZSBtb3JlIHN3ZWV0IHRoYW4gaGVycw==',
                    'V2hlbiB5b3VuZyBhbmQgYmVhdXRpZnVsLA==',
                    'U2hlIHJvZGUgdG8gaGFycmllcnM/',
                    'VGhpcyBtYW4gaGFkIGtlcHQgYSBzY2hvb2w=',
                    'QW5kIHJvZGUgb3VyIHdpbmdlZCBob3JzZS4=',
                    'VGhpcyBvdGhlciBoaXMgaGVscGVyIGFuZCBmcmllbmQ=',
                    'V2FzIGNvbWluZyBpbnRvIGhpcyBmb3JjZTs=',
                    'SGUgbWlnaHQgaGF2ZSB3b24gZmFtZSBpbiB0aGUgZW5kLA==',
                    'U28gc2Vuc2l0aXZlIGhpcyBuYXR1cmUgc2VlbWVkLA==',
                    'U28gZGFyaW5nIGFuZCBzd2VldCBoaXMgdGhvdWdodC4=',
                    'VGhpcyBvdGhlciBtYW4gSSBoYWQgZHJlYW1lZA==',
                    'QSBkcnVua2VuLCB2YWluLWdsb3Jpb3VzIGxvdXQu',
                    'SGUgaGFkIGRvbmUgbW9zdCBiaXR0ZXIgd3Jvbmc=',
                    'VG8gc29tZSB3aG8gYXJlIG5lYXIgbXkgaGVhcnQs',
                    'WWV0IEkgbnVtYmVyIGhpbSBpbiB0aGUgc29uZzs=',
                    'SGUsIHRvbywgaGFzIHJlc2lnbmVkIGhpcyBwYXJ0',
                    'SW4gdGhlIGNhc3VhbCBjb21lZHk7',
                    'SGUsIHRvbywgaGFzIGJlZW4gY2hhbmdlZCBpbiBoaXMgdHVybiw=',
                    'VHJhbnNmb3JtZWQgdXR0ZXJseTo=',
                    'QSB0ZXJyaWJsZSBiZWF1dHkgaXMgYm9ybi4=']))


def transpose_streams(streams: list[bytes]) -> list[bytes]:
    """
    Transpose the streams:
    make a stream that is the first byte of every stream,
    and a stream that is the second byte of every stream, and so on...
    """
    # Tìm độ dài lớn nhất của các luồng (list)
    max_len = max(map(len, streams))

    # Tạo 1 danh sách các luồng rỗng với độ dài max len
    out_streams = [bytes() for _ in range(max_len)]

    # Vòng lặp để lấy các byte đầu tiên, byte t2, byte t3, ...
    for stream in streams:
        for idx, i in enumerate(stream):
            out_streams[idx] += bytes([i])

    return out_streams


def detect_key_stream(streams: list[bytes]) -> bytes:
    inv_stream = transpose_streams(streams)
    # each stream is a single-character XOR cipher
    # we detect it, to build the key stream
    # Hàm sau đó áp dụng hàm decode_single_byte_xor_cypher cho mỗi luồng trong inv_stream để giải mã mỗi luồng
    key_stream = bytes(map(decode_single_byte_xor_cypher, inv_stream))

    # Kết quả là một chuỗi byte, mỗi byte trong chuỗi đại diện cho một khóa
    # được sử dụng để mã hóa một byte tương ứng trong các luồng đầu vào
    return key_stream


def main():
    # encrypt all the lines with the same nonce
    key = get_random_bytes(AES_BLOCK_SIZE)
    aes_ctr = AesCtr(key=key, nonce=bytes(8), byteorder='little')
    strings_enc = list(map(aes_ctr.encrypt, strings))

    # detect key stream
    key_stream = detect_key_stream(strings_enc)

    # decrypt the strings
    for stream in strings_enc:
        key_stream_trimmed = key_stream[:len(stream)]
        decrypted_string = xor_bytes((stream, key_stream_trimmed))
        print(decrypted_string)


if __name__ == '__main__':
    main()
