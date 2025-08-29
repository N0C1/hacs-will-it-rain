"""Sensor platform for Will It Rain integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfVolumetricFlux
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_LOCATION,
    ATTR_NEXT_UPDATE,
    ATTR_PERIOD,
    ATTR_PRECIPITATION_AMOUNT,
    ATTR_PROBABILITY,
    ATTR_THRESHOLD,
    CONF_LOCATION_NAME,
    DOMAIN,
    TIME_PERIODS,
)
from .coordinator import WillItRainCoordinator

_LOGGER = logging.getLogger(__name__)


SENSOR_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    f"rain_{period_key}": SensorEntityDescription(
        key=f"rain_{period_key}",
        name=f"Rain {period_name}",
        icon="mdi:weather-rainy",
        device_class=SensorDeviceClass.ENUM,  # Use ENUM for Yes/No values
        entity_category=None,
        native_unit_of_measurement=None,
        state_class=None,
        options=["No", "Yes"],  # Define the enum options
    )
    for period_key, _, period_name in TIME_PERIODS
}

# Add probability sensors
PROBABILITY_SENSOR_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    f"rain_probability_{period_key}": SensorEntityDescription(
        key=f"rain_probability_{period_key}",
        name=f"Rain Probability {period_name}",
        icon="mdi:water-percent",
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    )
    for period_key, _, period_name in TIME_PERIODS
}

# Add precipitation amount sensors
PRECIPITATION_SENSOR_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    f"precipitation_{period_key}": SensorEntityDescription(
        key=f"precipitation_{period_key}",
        name=f"Precipitation {period_name}",
        icon="mdi:weather-pouring",
        device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    )
    for period_key, _, period_name in TIME_PERIODS
}

# Combine all sensor descriptions
ALL_SENSOR_DESCRIPTIONS = {
    **SENSOR_DESCRIPTIONS,
    **PROBABILITY_SENSOR_DESCRIPTIONS,
    **PRECIPITATION_SENSOR_DESCRIPTIONS,
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Will It Rain sensors."""
    coordinator: WillItRainCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    
    # Create sensors for each time period
    for period_key, _, _ in TIME_PERIODS:
        # Create main rain sensor (Yes/No based on threshold)
        entities.append(
            WillItRainSensor(
                coordinator,
                SENSOR_DESCRIPTIONS[f"rain_{period_key}"],
                period_key,
                "rain"
            )
        )
        
        # Create probability sensor (exact percentage)
        entities.append(
            WillItRainSensor(
                coordinator,
                PROBABILITY_SENSOR_DESCRIPTIONS[f"rain_probability_{period_key}"],
                period_key,
                "probability"
            )
        )
        
        # Create precipitation amount sensor
        entities.append(
            WillItRainSensor(
                coordinator,
                PRECIPITATION_SENSOR_DESCRIPTIONS[f"precipitation_{period_key}"],
                period_key,
                "precipitation"
            )
        )

    async_add_entities(entities, True)


class WillItRainSensor(CoordinatorEntity[WillItRainCoordinator], SensorEntity):
    """Representation of a Will It Rain sensor."""

    def __init__(
        self,
        coordinator: WillItRainCoordinator,
        description: SensorEntityDescription,
        period_key: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._period_key = period_key
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": f"Will It Rain - {coordinator.entry.data[CONF_LOCATION_NAME]}",
            "manufacturer": "Will It Rain",
            "model": "Rain Forecast",
            "sw_version": "1.0.0",
            "entry_type": "service",
        }

    @property
    def native_value(self) -> str | int | float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or self._period_key not in self.coordinator.data:
            return None
            
        period_data = self.coordinator.data[self._period_key]
        
        if self._sensor_type == "rain":
            # Return string values for better UI display
            return "Yes" if period_data["will_rain"] else "No"
        elif self._sensor_type == "probability":
            return period_data["probability"]
        elif self._sensor_type == "precipitation":
            return period_data["precipitation_amount"]
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data or self._period_key not in self.coordinator.data:
            return {}
            
        period_data = self.coordinator.data[self._period_key]
        
        base_attrs = {
            ATTR_PERIOD: f"{period_data['hours']} hours",
            ATTR_LOCATION: self.coordinator.entry.data[CONF_LOCATION_NAME],
        }
        
        if self._sensor_type == "rain":
            base_attrs.update({
                ATTR_THRESHOLD: f"{period_data['threshold']}%",
                ATTR_PROBABILITY: f"{period_data['probability']}%",
                ATTR_PRECIPITATION_AMOUNT: f"{period_data['precipitation_amount']:.1f} mm",
            })
        
        return base_attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        if self._sensor_type == "rain" and self.coordinator.data:
            period_data = self.coordinator.data.get(self._period_key, {})
            if period_data.get("will_rain", False):
                return "mdi:weather-rainy"
            return "mdi:weather-sunny"
        elif self._sensor_type == "probability":
            return "mdi:water-percent"
        elif self._sensor_type == "precipitation":
            return "mdi:weather-pouring"
        return self.entity_description.icon or "mdi:weather-partly-cloudy"
