import json
from urllib.parse import quote_plus
from django.conf import settings
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import base64
import os

class Alpay:
    def __init__(self):
        self.app_id = getattr(settings, 'ALIPAY_APPID', '')
        self.notify_url = getattr(settings, 'ALIPAY_NOTIFY_URL', '')
        self.return_url = getattr(settings, 'ALIPAY_RETURN_URL', '')
        self.app_private_key_path = getattr(settings, 'APP_PRIVATE_KEY_PATH', '')
        self.alipay_public_key_path = getattr(settings, 'ALI_PUB_KEY_PATH', '')
        self.debug = getattr(settings, 'ALIPAY_DEBUG', True)
        self.app_private_key = None
        self.alipay_public_key = None

        self._load_keys()

        if self.debug:
            self.gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, **kwargs):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
        }
        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        query = self.sign_data(data)
        return f"{self.gateway}?{query}"

    def build_body(self, method, biz_content, return_url=None):
        from datetime import datetime
        data = {
            "app_id": self.app_id,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }
        if return_url is not None:
            data["return_url"] = return_url
        if self.notify_url is not None:
            data["notify_url"] = self.notify_url
        return data

    def sign_data(self, data):
        data.pop("sign", None)
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.sign(unsigned_string.encode("utf-8"))
        quoted_string = "&".join("{0}={1}".format(k, self._smart_quote(v)) for k, v in unsigned_items)
        quoted_string += "&sign=" + quote_plus(sign)
        return quoted_string

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))
        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_bytes: bytes):
        signer = PKCS1_v1_5.new(self.app_private_key)
        signature = signer.sign(SHA256.new(unsigned_bytes))
        return base64.b64encode(signature).decode("utf-8")

    def verify(self, data: dict) -> bool:
        """验证支付宝回调签名。
        data: 包含支付宝回传所有参数（包含 sign 和 sign_type）。
        返回 True/False。
        """
        sign = data.pop('sign', None)
        data.pop('sign_type', None)
        if not sign:
            return False
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join(f"{k}={v}" for k, v in unsigned_items)
        try:
            verifier = PKCS1_v1_5.new(self.alipay_public_key)
            digest = SHA256.new(unsigned_string.encode('utf-8'))
            return verifier.verify(digest, base64.b64decode(sign))
        except Exception:
            return False

    def _smart_quote(self, v):
        if isinstance(v, str):
            return quote_plus(v)
        return v

    def _read_file_if_exists(self, path: str):
        if not path:
            return None
        if not os.path.exists(path):
            return None
        with open(path, 'rb') as fp:
            return fp.read()

    def _import_rsa_key(self, raw: bytes | str, key_type: str):
        if raw is None:
            raise ValueError(f'{key_type} 为空，无法加载')
        if isinstance(raw, str):
            raw_bytes = raw.encode('utf-8')
        else:
            raw_bytes = raw
        text = raw_bytes.decode('utf-8', 'ignore').strip()
        # 若已包含 PEM 头直接尝试
        candidates = []
        if 'BEGIN' in text and 'END' in text:
            candidates.append(text)
        else:
            # 可能是单行 base64，无头尾
            # 去除空白并按 64 列切分
            b64_body = ''.join(text.split())
            def wrap(header):
                lines = [b64_body[i:i+64] for i in range(0, len(b64_body), 64)]
                return f'-----BEGIN {header}-----\n' + '\n'.join(lines) + f'\n-----END {header}-----\n'
            # 先尝试 PKCS8 PRIVATE KEY，再尝试 PKCS1 RSA PRIVATE KEY
            candidates.append(wrap('PRIVATE KEY'))
            candidates.append(wrap('RSA PRIVATE KEY'))
        last_err = None
        for pem in candidates:
            try:
                return RSA.import_key(pem)
            except Exception as e:
                last_err = e
        sample = text[:60]
        raise ValueError(
            f'{key_type} 格式不支持，尝试自动补全失败，请确认为合法 PEM。首段片段: {sample}\n原始错误: {last_err}'
        )

    def _load_keys(self):
        # 允许通过 settings 直接提供密钥字符串（便于容器环境）
        app_key_str = getattr(settings, 'ALIPAY_APP_PRIVATE_KEY', None)
        ali_key_str = getattr(settings, 'ALIPAY_PUBLIC_KEY', None)
        app_key_raw = app_key_str.encode('utf-8') if app_key_str else self._read_file_if_exists(self.app_private_key_path)
        ali_key_raw = ali_key_str.encode('utf-8') if ali_key_str else self._read_file_if_exists(self.alipay_public_key_path)
        self.app_private_key = self._import_rsa_key(app_key_raw, '应用私钥')
        self.alipay_public_key = self._import_rsa_key(ali_key_raw, '支付宝公钥')
