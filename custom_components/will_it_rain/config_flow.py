"""Config flow for Will It Rain integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from geopy.geocoders import Nominatim
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CITIES,
    CONF_LATITUDE,
    CONF_LOCATION,
    CONF_LOCATION_NAME,
    CONF_LONGITUDE,
    CONF_THRESHOLD,
    DEFAULT_THRESHOLD,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def validate_location(hass: HomeAssistant, location: str) -> dict[str, Any]:
    """Validate location and return coordinates."""
    location = location.strip()
    
    # Use Home Assistant's configured location
    if location.lower() == "home":
        if hasattr(hass.config, "latitude") and hasattr(hass.config, "longitude"):
            return {
                "latitude": hass.config.latitude,
                "longitude": hass.config.longitude,
                "location_name": f"Home ({hass.config.location_name or 'Your Location'})",
            }
        else:
            raise vol.Invalid("Home Assistant location not configured. Please set up your location in Settings → System → General.")

    # Check if it's coordinates in format "lat,lon"
    if "," in location:
        try:
            parts = location.split(",")
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                # Validate coordinate ranges
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    raise vol.Invalid("Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180.")
                return {
                    "latitude": lat,
                    "longitude": lon,
                    "location_name": f"Custom Location ({lat:.4f}, {lon:.4f})",
                }
        except ValueError:
            raise vol.Invalid("Invalid coordinate format. Use: latitude,longitude (e.g., 47.2692,11.4041)")

    # Check if it's a predefined city
    location_lower = location.lower()
    if location_lower in CITIES:
        lat, lon, display_name = CITIES[location_lower]
        return {
            "latitude": lat,
            "longitude": lon,
            "location_name": display_name,
        }

    # Use geocoding service
    try:
        geolocator = Nominatim(user_agent="will-it-rain-hacs")
        location_data = geolocator.geocode(location)
        
        if location_data:
            return {
                "latitude": location_data.latitude,
                "longitude": location_data.longitude,
                "location_name": location_data.address,
            }
    except Exception as err:
        _LOGGER.error("Error geocoding location %s: %s", location, err)

    raise vol.Invalid(f"Could not find location: {location}. Try using exact coordinates (lat,lon) or 'home' for your Home Assistant location.")


class WillItRainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Will It Rain."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate location
                location_info = await validate_location(self.hass, user_input[CONF_LOCATION])
                
                # Create unique ID based on coordinates
                unique_id = f"{location_info['latitude']:.4f}_{location_info['longitude']:.4f}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                # Prepare config entry data
                data = {
                    CONF_LOCATION: user_input[CONF_LOCATION],
                    CONF_LATITUDE: location_info["latitude"],
                    CONF_LONGITUDE: location_info["longitude"], 
                    CONF_LOCATION_NAME: location_info["location_name"],
                    CONF_THRESHOLD: user_input[CONF_THRESHOLD],
                }

                return self.async_create_entry(
                    title=location_info["location_name"],
                    data=data,
                )

            except vol.Invalid:
                errors["base"] = "invalid_location"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Default to Home Assistant's home location
        default_location = "home"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_LOCATION, default=default_location): str,
                vol.Required(CONF_THRESHOLD, default=DEFAULT_THRESHOLD): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=100)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "examples": "Innsbruck, Wien, Berlin, Munich, 47.2692,11.4041"
            },
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguration."""
        config_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        
        if user_input is not None:
            try:
                # Validate location
                location_info = await validate_location(self.hass, user_input[CONF_LOCATION])
                
                # Update config entry
                data = {
                    CONF_LOCATION: user_input[CONF_LOCATION],
                    CONF_LATITUDE: location_info["latitude"],
                    CONF_LONGITUDE: location_info["longitude"],
                    CONF_LOCATION_NAME: location_info["location_name"],
                    CONF_THRESHOLD: user_input[CONF_THRESHOLD],
                }

                return self.async_update_reload_and_abort(
                    config_entry, data_updates=data, title=location_info["location_name"]
                )

            except vol.Invalid:
                return self.async_abort(reason="invalid_location")
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during reconfiguration")
                return self.async_abort(reason="unknown")

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_LOCATION, default=config_entry.data[CONF_LOCATION]
                ): str,
                vol.Required(
                    CONF_THRESHOLD, default=config_entry.data.get(CONF_THRESHOLD, DEFAULT_THRESHOLD)
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
            }
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=data_schema,
            description_placeholders={
                "examples": "Innsbruck, Wien, Berlin, Munich, 47.2692,11.4041"
            },
        )
