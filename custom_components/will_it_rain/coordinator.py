"""DataUpdateCoordinator for Will It Rain integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_URL,
    API_USER_AGENT,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_THRESHOLD,
    DOMAIN,
    SCAN_INTERVAL_MINUTES,
    TIME_PERIODS,
)

_LOGGER = logging.getLogger(__name__)


class WillItRainCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Met.no API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.latitude = entry.data[CONF_LATITUDE]
        self.longitude = entry.data[CONF_LONGITUDE]
        self.threshold = entry.data.get(CONF_THRESHOLD, 40)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            session = async_get_clientsession(self.hass)
            weather_data = await self._fetch_weather_data(session)
            
            # Analyze rain probability for each time period
            rain_data = {}
            for period_key, hours, _ in TIME_PERIODS:
                analysis = self._analyze_rain_probability(weather_data, hours)
                rain_data[period_key] = {
                    "probability": analysis["probability"],
                    "precipitation_amount": analysis["precipitation_amount"],
                    "will_rain": analysis["probability"] >= self.threshold,
                    "threshold": self.threshold,
                    "hours": hours,
                }
            
            return rain_data
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def _fetch_weather_data(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        """Fetch weather data from Open-Meteo API."""
        params = {
            "latitude": round(self.latitude, 4),
            "longitude": round(self.longitude, 4),
            "hourly": "precipitation_probability,precipitation",
            "timezone": "auto",
            "forecast_days": 2,  # Get 2 days worth of data for 24h forecasts
        }
        
        headers = {
            "User-Agent": API_USER_AGENT,
            "Accept": "application/json",
        }
        
        _LOGGER.debug("Making request to Open-Meteo API")
        _LOGGER.debug("Request URL: %s", f"{API_URL}?latitude={params['latitude']}&longitude={params['longitude']}")
        
        async with session.get(API_URL, params=params, headers=headers, timeout=30) as response:
            _LOGGER.debug("Response status: %s", response.status)
            if response.status >= 400:
                response_text = await response.text()
                _LOGGER.error("Open-Meteo API error %s: %s", response.status, response_text)
                
            response.raise_for_status()
            return await response.json()

    def _analyze_rain_probability(self, data: dict[str, Any], hours: int) -> dict[str, Any]:
        """Analyze rain probability for a specific time period using Open-Meteo data."""
        now = datetime.now()
        target_time = now + timedelta(hours=hours)
        
        max_probability = 0
        total_precipitation = 0.0
        data_points = 0
        
        # Open-Meteo returns data in hourly arrays
        hourly_data = data.get("hourly", {})
        times = hourly_data.get("time", [])
        probabilities = hourly_data.get("precipitation_probability", [])
        precipitations = hourly_data.get("precipitation", [])
        
        _LOGGER.debug("Processing %d hourly data points for %d hour forecast", len(times), hours)
        
        # Process each hourly entry within our time window
        for i, time_str in enumerate(times):
            # Parse time (Open-Meteo format: "2024-01-15T14:00")
            try:
                entry_time = datetime.fromisoformat(time_str)
                # Remove timezone info for comparison if present
                if entry_time.tzinfo is not None:
                    entry_time = entry_time.replace(tzinfo=None)
                
                # Check if this time point is within our forecast window
                if now <= entry_time <= target_time:
                    # Get precipitation probability (0-100%)
                    if i < len(probabilities) and probabilities[i] is not None:
                        prob = probabilities[i]
                        max_probability = max(max_probability, prob)
                        _LOGGER.debug("Time %s: probability %d%%", time_str, prob)
                    
                    # Get precipitation amount (mm)
                    if i < len(precipitations) and precipitations[i] is not None:
                        amount = precipitations[i]
                        total_precipitation += amount
                        data_points += 1
                        
            except (ValueError, TypeError) as err:
                _LOGGER.warning("Error parsing time %s: %s", time_str, err)
                continue
        
        _LOGGER.debug("Analysis for %dh: max_prob=%d%%, total_precip=%.2fmm, data_points=%d", 
                     hours, max_probability, total_precipitation, data_points)
        
        return {
            "probability": max_probability,
            "precipitation_amount": total_precipitation,
        }
