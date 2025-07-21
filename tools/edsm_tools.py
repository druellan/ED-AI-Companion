import requests
from config import EDSM_API
from components.utils import log


class EDSMAPI:
    """
    A class to interact with the EDSM API for Elite Dangerous star system data.
    """

    def __init__(self, api_url=None):
        self.api_url = api_url or EDSM_API

    def get_system(self, system_name):
        """
        Get information for the given system name.
        """
        if not system_name:
            log("error", "System name is required for get_system.")
            return None

        params = {
            "systemName": system_name,
            "showPermit": 1,
            "showInformation": 1,
        }
        try:
            response = requests.get(self.api_url + "/api-v1/system", params=params)
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            log("error", f"Error fetching data for {system_name}: {e}")
        return None

    def get_system_bodies(self, system_name):
        """
        Get the bodies present in a given system.
        """
        if not system_name:
            log("error", "System name is required for get_system_bodies.")
            return None

        params = {"systemName": system_name}
        try:
            response = requests.get(
                self.api_url + "/api-system-v1/bodies", params=params
            )
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            log("error", f"Error fetching bodies data for {system_name}: {e}")
        return None

    def get_system_scan(self, system_name):
        """
        Get estimated value and valuable bodies in a given system.
        """
        if not system_name:
            log("error", "System name is required for get_system_scan.")
            return None

        params = {"systemName": system_name}
        try:
            response = requests.get(
                self.api_url + "/api-system-v1/estimated-value", params=params
            )
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            log("error", f"Error fetching scan data for {system_name}: {e}")
        return None

    def get_system_stations(self, system_name):
        """
        Get information about the stations in a given system.
        """
        if not system_name:
            log("error", "System name is required for get_system_stations.")
            return None

        params = {"systemName": system_name}
        try:
            response = requests.get(
                self.api_url + "/api-system-v1/stations", params=params
            )
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            log("error", f"Error fetching station data for {system_name}: {e}")
        return None

    def get_station_market(self, system_name):
        """
        Get information about the markets in a given system.
        """
        if not system_name:
            log("error", "System name is required for get_station_market.")
            return None

        params = {"systemName": system_name}
        try:
            response = requests.get(
                self.api_url + "/api-system-v1/stations/market", params=params
            )
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            log("error", f"Error fetching market data for {system_name}: {e}")
        return None

    def get_system_factions(self, system_name):
        """
        Get information about the factions in a given system.
        """
        if not system_name:
            log("error", "System name is required for get_system_factions.")
            return None

        params = {"systemName": system_name}
        try:
            response = requests.get(
                self.api_url + "/api-system-v1/factions", params=params
            )
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            log("error", f"Error fetching factions data for {system_name}: {e}")
        return None
