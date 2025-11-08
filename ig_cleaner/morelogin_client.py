# ig_cleaner/morelogin_client.py
import requests


class MoreLoginClient:
    def __init__(self, api_key, api_url, timeout=10):
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ------------------
    # INTERNAL HELPERS
    # ------------------

    def _extract_ws_endpoint(self, data):
        """
        Robust extractor for WebSocket / CDP endpoints.
        Tries multiple formats:
        - data.data.wsEndpoint
        - data.ws
        - webSocketDebuggerUrl
        - any nested key starting with ws:// or wss://
        Return: str or None
        """
        if not data:
            return None

        def scan(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, str) and v.startswith(("ws://", "wss://")):
                        return v
                    nested = scan(v)
                    if nested:
                        return nested
            elif isinstance(obj, list):
                for item in obj:
                    nested = scan(item)
                    if nested:
                        return nested
            return None

        return scan(data)

    # ------------------
    # PUBLIC API
    # ------------------

    def start_profile(self, profile_id):
        """
        Start MoreLogin profile.
        Return: CDP WebSocket endpoint (string)
        """
        url = f"{self.api_url}/api/v2/profile/start"
        params = {"profileId": profile_id}

        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            raise RuntimeError(f"MoreLogin start_profile network error: {e}")

        ws = self._extract_ws_endpoint(data)
        if not ws:
            raise RuntimeError(f"Cannot extract WS endpoint from MoreLogin response:\n{data}")

        return ws

    def stop_profile(self, profile_id):
        """
        Stop profile best-effort.
        """
        url = f"{self.api_url}/api/v2/profile/stop"
        params = {"profileId": profile_id}

        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            r.raise_for_status()
            return True
        except Exception as e:
            print(f"Warning: failed to stop profile {profile_id}: {e}")
            return False
