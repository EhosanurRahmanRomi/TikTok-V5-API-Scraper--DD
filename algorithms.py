import hashlib
import base64
import config

class TikTokSigner:
    def __init__(self):
        self.alphabet = config.ALPHABET
        self.magic = config.MAGIC_NUMBER

    def _rc4(self, data, key):
        S = list(range(256))
        j = 0
        for i in range(256):
            j = (j + S[i] + key[i % len(key)]) % 256
            S[i], S[j] = S[j], S[i]
        i = j = 0
        out = bytearray()
        for b in data:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            out.append(b ^ S[(S[i] + S[j]) % 256])
        return bytes(out)

    def sign_xbogus(self, query: str, ua: str, ts: int) -> str:
        p_h = hashlib.md5(hashlib.md5(query.encode()).hexdigest().encode()).digest()
        ua_e = self._rc4(ua.encode(), config.XBOGUS_SALT)
        ua_h = hashlib.md5(hashlib.md5(base64.b64encode(ua_e)).hexdigest().encode()).digest()
        
        ts_b = [(ts >> i) & 0xFF for i in range(24, -1, -8)]
        mg_b = [(self.magic >> i) & 0xFF for i in range(24, -1, -8)]
        raw = [64, 0, 1, 14] + ts_b + mg_b + [p_h[-2], p_h[-1], ua_h[-2], ua_h[-1]]
        
        chk = 64
        for x in raw[1:]: chk ^= x
        raw.extend([chk, 255])
        
        while len(raw) < 22: raw.append(0)
        scrambled = bytes([raw[i] for i in config.SCRAMBLE_MAP])
        payload = b'\x02\xff' + self._rc4(scrambled, b'\xff')
        
        res = ""
        for i in range(0, len(payload), 3):
            if i + 3 > len(payload): break
            v = int.from_bytes(payload[i:i+3], 'big')
            res += self.alphabet[(v >> 18) & 63] + self.alphabet[(v >> 12) & 63] + \
                   self.alphabet[(v >> 6) & 63] + self.alphabet[v & 63]
        return res

    def sign_xgnarly(self, query: str, ts: int) -> str:
        m = hashlib.sha256(f"{query}|{ts}".encode()).hexdigest()
        return f"0404{m[:40]}{ts}"

def get_signatures(query, ua, ts):
    signer = TikTokSigner()
    return {
        "X-Bogus": signer.sign_xbogus(query, ua, ts),
        "X-Gnarly": signer.sign_xgnarly(query, ts)
    }
