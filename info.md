# Will It Rain Integration

A modern Home Assistant integration for precise rain forecasts based on the Met.no API.

## What does this integration do?

The "Will It Rain" integration automatically creates sensors that predict whether it will rain in the next 1, 2, 4, 8, 12, or 24 hours. You can set your own threshold for rain probability (e.g. 40%).

## Key Features

- **Simple Yes/No sensors**: One global threshold for easy automation setup
- **Flexible probability sensors**: Use exact percentages for custom threshold automations  
- **Complete data**: Precipitation amount sensors for each time period
- **Flexible location input**:
  - Use 'home' for your Home Assistant coordinates
  - Enter city names (Innsbruck, Munich, Berlin, etc.)
  - Direct coordinates (47.2692,11.4041)
- **Perfect for smart automations**:
  - Different actions for different rain certainty levels
  - Automatically retract awnings at high probability
  - Gentle warnings at low probability
  - Stop irrigation systems before rain

## Installation

1. Install via HACS
2. Restart Home Assistant
3. Go to "Settings" → "Devices & Services" → "Add Integration"
4. Search for "Will It Rain" and configure location + threshold

## Example Automation

```yaml
automation:
  - alias: "Smart rain response"
    trigger:
      - platform: state
        entity_id: sensor.rain_1h  # Uses your configured threshold
        to: "Yes"
        id: "threshold_rain"
      - platform: numeric_state
        entity_id: sensor.rain_probability_1h  # Custom threshold
        above: 80
        id: "high_certainty"
    action:
      - choose:
        - conditions:
            - condition: trigger
              id: "threshold_rain"
          sequence:
            - service: notify.mobile_app
              data:
                message: "Rain possible - check weather!"
        - conditions:
            - condition: trigger
              id: "high_certainty"
          sequence:
            - service: cover.close_cover
              entity_id: cover.awning
```

The integration uses the free and reliable Met.no API and automatically updates data every 10 minutes.
