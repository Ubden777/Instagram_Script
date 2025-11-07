import requests
import os

class MoreLoginClient:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def start_profile(self, profile_id):
        """Starts a MoreLogin profile and returns the WebSocket endpoint."""
        url = f'{self.api_url}/api/v2/profile/start'
        params = {'profileId': profile_id}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data['code'] == 0:
                return data['data']['wsUrl']
            else:
                print(f"Ошибка при запуске профиля: {data['msg']}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети при запуске профиля: {e}")
            return None

    def stop_profile(self, profile_id):
        """Stops a MoreLogin profile."""
        url = f'{self.api_url}/api/v2/profile/stop'
        params = {'profileId': profile_id}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data['code'] == 0:
                print(f"Профиль {profile_id} успешно остановлен.")
                return True
            else:
                print(f"Ошибка при остановке профиля: {data['msg']}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети при остановке профиля: {e}")
            return False
