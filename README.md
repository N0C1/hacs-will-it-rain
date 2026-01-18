# Will It Rain? - HACS Integration

[![GitHub Release](https://img.shields.io/github/release/n0c1/hacs-will-it-rain.svg?style=flat-square)](https://github.com/n0c1/hacs-will-it-rain/releases)
[![License](https://img.shields.io/github/license/n0c1/hacs-will-it-rain.svg?style=flat-square)](LICENSE)
[![hacs](https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square)](https://github.com/hacs/integration)

> **Disclaimer:** Parts of this project were created with the assistance of AI tools.  
> All generated code has been reviewed, tested, and verified by the author.  
 This software is provided "as is", without any warranty or guarantee of correctness.

A modern Home Assistant integration that provides rain forecasts based on the Open-Meteo API. Simple "Yes/No" sensors with a global threshold, plus detailed probability sensors for flexible automations.

## Why This Integration?

**The Problem:** Home Assistant's built-in weather integrations are great for general weather data, but they're frustrating when you need specific rain predictions for automations:

-  **Generic weather states** like "rainy" don't tell you *when* rain will start
-  **No probability thresholds** - you can't say "close awning when rain is 80% likely"  
-  **No time-specific forecasts** - will it rain in the next hour or next day?
-  **Complex setup** for simple questions like "should I water the garden?"

**The Solution:** This integration gives you exactly what you need for smart home automations:

- **Simple Yes/No answers** - "Will it rain in the next 2 hours?" 
- **Your own threshold** - Define what "likely" means to you (30%? 60%? 80%?)
- **Multiple time horizons** - 1h for awnings, 24h for garden planning
- **Flexible automation options** - Use simple triggers or custom probability values

## Features

- **Rain forecast** for 6 different time periods (1h, 2h, 4h, 8h, 12h, 24h)
- **3 sensor types** per time period:
  - Main sensor: "Yes/No" based on configurable threshold
  - Probability sensor: Exact percentage value
  - Precipitation sensor: Expected precipitation amount in mm
- **Automatic location detection** using Home Assistant coordinates
- **Flexible location input**: City names, coordinates, or predefined cities
- **Easy configuration** through Home Assistant UI
- **Multi-language support**: German and English
- **Asynchronous architecture** with modern DataUpdateCoordinator implementation
- **Automatic updates** every 10 minutes

## Installation

[![Add to Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=n0c1&repository=hacs-will-it-rain&category=integration)


### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right and select "Custom repositories"
4. Add `https://github.com/n0c1/hacs-will-it-rain`
5. Select "Integration" as category
6. Click "Add"
7. Search for "Will It Rain" and install it
8. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/will_it_rain` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to "Settings" → "Devices & Services" → "Add Integration"
4. Search for "Will It Rain"

## Configuration

1. Go to "Settings" → "Devices & Services" → "Add Integration"
2. Search for "Will It Rain" and click on it
3. Configure the integration:
   - **Location**: City, coordinates (lat,lon) or 'home' for Home Assistant location
   - **Rain probability threshold (%)**: This sets the threshold for your Yes/No sensors (default: 40%)
     - If probability ≥ threshold → `sensor.rain_1h` shows "Yes"
     - If probability < threshold → `sensor.rain_1h` shows "No"
     - You can always use `sensor.rain_probability_1h` for custom thresholds in automations

### Location Input Guide

- **`home`** - Uses your Home Assistant location (recommended)
- **City name** - e.g., `Vienna`, `Munich`, `London`
- **Coordinates** - e.g., `47.2692,11.4041` (latitude,longitude)


## Credits

- **Open-Meteo API** - Free weather data with precipitation probability
- **HACS Documentation** - Integration development guidelines and best practices  
- **Home Assistant Community** - Modern integration architecture and patterns
