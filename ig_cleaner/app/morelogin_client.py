import requests
from .config import ML_API_KEY

BASE_URL = "https://api.morelogin.com/api/v2"

class MoreLoginClient:
    def __init__(self, api_key=ML_API_KEY):
        if not api_key:
            raise ValueError("MoreLogin API key is not set.")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def start_profile(self, profile_id: str):
        """
        Starts a MoreLogin profile and returns the remote debugging endpoint.
        """
        url = f"{BASE_URL}/profile/start"
        payload = {"profileId": profile_id}

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            data = response.json()
            if data.get("code") == 0 and "data" in data:
                # The exact key for the debugging port might vary, check MoreLogin docs.
                # Assuming it's in data['wsUrl'] or similar.
                return data["data"].get("wsUrl") or data["data"].get("debugPort")
            else:
                raise Exception(f"Failed to start profile: {data.get('message')}")
        except requests.exceptions.RequestException as e:
            # Handle network errors
            raise Exception(f"Error communicating with MoreLogin API: {e}")

    def stop_profile(self, profile_id: str):
        """
        Stops a MoreLogin profile.
        """
        url = f"{BASE_URL}/profile/stop"
        payload = {"profileId": profile_id}

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            data = response.json()
            if data.get("code") != 0:
                raise Exception(f"Failed to stop profile: {data.get('message')}")
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with MoreLogin API: {e}")

# Example usage (for testing)
if __name__ == "__main__":
    # This requires ML_API_KEY to be set in the environment
    client = MoreLoginClient()
    # Replace with a real profile ID for testing
    test_profile_id = "your_test_profile_id"

    try:
        print(f"Attempting to start profile {test_profile_id}...")
        endpoint = client.start_profile(test_profile_id)
        print(f"Profile started successfully. Endpoint: {endpoint}")

        input("Press Enter to stop the profile...")

        client.stop_profile(test_profile_id)
        print("Profile stopped successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
