"""Constants for the Will It Rain integration."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = "will_it_rain"
NAME: Final = "Will It Rain"
VERSION: Final = "1.1.0"

# Configuration keys
CONF_LOCATION: Final = "location"
CONF_THRESHOLD: Final = "threshold"
CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"
CONF_LOCATION_NAME: Final = "location_name"

# Default values
DEFAULT_THRESHOLD: Final = 40
DEFAULT_LOCATION: Final = "home"

# Scan interval
SCAN_INTERVAL_MINUTES: Final = 10

# API Configuration - Open-Meteo (free, with precipitation probability)
API_URL: Final = "https://api.open-meteo.com/v1/forecast"
# Open-Meteo doesn't require User-Agent but we'll keep it for good practice
API_USER_AGENT: Final = "Home Assistant n0c1@github.com"

# Sensor types and time periods
TIME_PERIODS: Final = [
    ("1h", 1, "within the next 1 hour"),
    ("2h", 2, "within the next 2 hours"), 
    ("4h", 4, "within the next 4 hours"),
    ("8h", 8, "within the next 8 hours"),
    ("12h", 12, "within the next 12 hours"),
    ("24h", 24, "within the next 24 hours"),
]

# Common cities with coordinates (for geocoding fallback)
CITIES: Final = {
    "innsbruck": (47.2692, 11.4041, "Innsbruck, Austria"),
    "vienna": (48.2082, 16.3738, "Vienna, Austria"),
    "wien": (48.2082, 16.3738, "Vienna, Austria"),
    "zurich": (47.3769, 8.5417, "Zurich, Switzerland"),
    "munich": (48.1351, 11.5820, "Munich, Germany"),
    "münchen": (48.1351, 11.5820, "Munich, Germany"),
    "berlin": (52.5200, 13.4050, "Berlin, Germany"),
    "amsterdam": (52.3676, 4.9041, "Amsterdam, Netherlands"),
    "paris": (48.8566, 2.3522, "Paris, France"),
    "london": (51.5074, -0.1278, "London, United Kingdom"),
}

# Sensor attributes
ATTR_PROBABILITY: Final = "probability"
ATTR_PRECIPITATION_AMOUNT: Final = "precipitation_amount"
ATTR_THRESHOLD: Final = "threshold"
ATTR_LOCATION: Final = "location"
ATTR_NEXT_UPDATE: Final = "next_update"
ATTR_PERIOD: Final = "period"
