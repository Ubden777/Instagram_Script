# morelogin_client.py
import requests
import json

class MoreLoginClient:
    def __init__(self, api_key, api_url, timeout=10):
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _extract_ws_endpoint(self, data):
        """
        Попытаться безопасно извлечь ws/cdp endpoint из разных возможных форматов ответа.
        Возвращает строку или None.
        """
        if not data:
            return None
        # несколько распространённых путей
        # 1) data['data']['wsEndpoint']
        # 2) data['data']['ws'] / data['ws']
        # 3) data.get('webSocketDebuggerUrl')
        # 4) возможно, data is list or string
        # Попробуем пройтись по вариантам:
        if isinstance(data, dict):
            # common nested
            maybe = data.get('data') or data.get('result') or data
            if isinstance(maybe, dict):
                for key in ('wsEndpoint', 'ws', 'webSocketEndpoint', 'endpoint', 'websocket'):
                    v = maybe.get(key)
                    if isinstance(v, str) and v:
                        return v
            # top-level keys
            for key in ('webSocketDebuggerUrl', 'ws', 'endpoint', 'wsEndpoint'):
                v = data.get(key)
                if isinstance(v, str) and v:
                    return v
        # If it's a string, maybe API returned the URL directly
        if isinstance(data, str) and data.startswith("ws"):
            return data
        return None

    def start_profile(self, profile_id):
        """Starts a MoreLogin profile and returns a CDP/WS endpoint string or raises."""
        url = f'{self.api_url}/api/v2/profile/start'
        params = {'profileId': profile_id}
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"Start profile network error: {e}")

        # Try to extract endpoint
        endpoint = self._extract_ws_endpoint(data)
        if not endpoint:
            # Sometimes API returns structure with 'code' and 'data' that contains 'message' or inner structure.
            # Try to be tolerant and inspect nested dicts
            def scan(obj):
                if isinstance(obj, dict):
                    for k,v in obj.items():
                        if isinstance(v, str) and v.startswith("ws"):
                            return v
                        r = scan(v)
                        if r:
                            return r
                elif isinstance(obj, list):
                    for it in obj:
                        r = scan(it)
                        if r:
                            return r
                return None
            endpoint = scan(data)

        if not endpoint:
            raise RuntimeError(f"Не удалось извлечь WebSocket/CDP endpoint из ответа MoreLogin: {data}")

        # Some APIs return full "ws://host:port/devtools/browser/..." or "http://.../devtools/browser/...".
        # Playwright expects connect_over_cdp(ws_url) — if endpoint looks like http and contains '/json/version' etc,
        # user may need to transform; keep it as-is and let caller handle if not compatible.
        return endpoint

    def stop_profile(self, profile_id):
        url = f'{self.api_url}/api/v2/profile/stop'
        params = {'profileId': profile_id}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            # best-effort reporting
            if isinstance(data, dict) and data.get('code') == 0:
                return True
            # fallback: accept any successful HTTP 2xx as True
            return True
        except requests.exceptions.RequestException as e:
            # network error - return False but don't raise
            print(f"Ошибка сети при остановке профиля: {e}")
            return False
        except Exception as e:
            print(f"Ошибка при остановке профиля: {e}")
            return False
