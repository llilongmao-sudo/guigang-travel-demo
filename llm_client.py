"""
LLM API 调用客户端
支持 OpenAI 兼容接口（可用于 Qclaw、文心一言、通义千问等）
"""

import json
import urllib.request
import urllib.error


class LLMClient:
    """LLM API 客户端，支持任何 OpenAI 兼容接口"""

    def __init__(self, api_base: str, api_key: str, model: str = None):
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.model = model

    def chat(self, messages, temperature=0.7, max_tokens=2000):
        """调用 LLM 聊天接口"""
        url = f"{self.api_base}/chat/completions"

        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if self.model:
            payload["model"] = self.model

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                # Handle different response formats
                if "choices" in result:
                    return result["choices"][0]["message"]["content"]
                elif "response" in result:
                    return result["response"]
                else:
                    return str(result)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            return f"[API 错误 {e.code}]: {body}"
        except Exception as e:
            return f"[请求失败]: {str(e)}"

    def test_connection(self):
        """测试 API 连接是否正常"""
        try:
            resp = self.chat(
                [{"role": "user", "content": "你好"}],
                temperature=0.3,
                max_tokens=10,
            )
            if resp.startswith("[API 错误") or resp.startswith("[请求失败"):
                return False, resp
            return True, resp
        except Exception as e:
            return False, str(e)
