import requests
from .config import ML_API_KEY
from .logging_config import get_logger

BASE_URL = "https://api.morelogin.com/api/v2"

class MoreLoginClient:
    def __init__(self, api_key=ML_API_KEY):
        if not api_key:
            raise ValueError("MoreLogin API key is not set.")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.log = get_logger(__name__)

    def start_profile(self, profile_id: str):
        """
        Starts a MoreLogin profile and returns the remote debugging endpoint.
        """
        url = f"{BASE_URL}/profile/start"
        payload = {"profileId": profile_id}

        self.log.info("Attempting to start MoreLogin profile.", profile_id=profile_id)
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            if data.get("code") == 0 and "data" in data:
                # The exact key for the debugging port might vary, check MoreLogin docs.
                # It's often 'wsUrl' or a 'debugPort' which needs to be assembled into a URL.
                endpoint = data["data"].get("wsUrl") or data["data"].get("debugPort")
                if not endpoint:
                    self.log.error("MoreLogin API response missing endpoint.", response_data=data, profile_id=profile_id)
                    raise Exception("MoreLogin API response missing endpoint.")

                self.log.info("Successfully started MoreLogin profile.", profile_id=profile_id, endpoint=endpoint)
                return endpoint
            else:
                self.log.error("Failed to start MoreLogin profile via API.", profile_id=profile_id, response_data=data)
                raise Exception(f"Failed to start profile: {data.get('message')}")
        except requests.exceptions.Timeout:
            self.log.exception("Request to MoreLogin API timed out while starting profile.", profile_id=profile_id)
            raise Exception("MoreLogin API request timed out.")
        except requests.exceptions.RequestException as e:
            self.log.exception("Error communicating with MoreLogin API while starting profile.", profile_id=profile_id)
            raise Exception(f"Error communicating with MoreLogin API: {e}")

    def stop_profile(self, profile_id: str):
        """
        Stops a MoreLogin profile.
        """
        url = f"{BASE_URL}/profile/stop"
        payload = {"profileId": profile_id}

        self.log.info("Attempting to stop MoreLogin profile.", profile_id=profile_id)
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data.get("code") == 0:
                self.log.info("Successfully stopped MoreLogin profile.", profile_id=profile_id)
                return True
            else:
                self.log.error("Failed to stop MoreLogin profile via API.", profile_id=profile_id, response_data=data)
                raise Exception(f"Failed to stop profile: {data.get('message')}")
        except requests.exceptions.Timeout:
            self.log.exception("Request to MoreLogin API timed out while stopping profile.", profile_id=profile_id)
            raise Exception("MoreLogin API request timed out.")
        except requests.exceptions.RequestException as e:
            self.log.exception("Error communicating with MoreLogin API while stopping profile.", profile_id=profile_id)
            raise Exception(f"Error communicating with MoreLogin API: {e}")
