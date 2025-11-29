
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE,
    UnitOfPressure,  # (not currently used, but kept if you plan pressure later)
    CONCENTRATION_PARTS_PER_MILLION,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
)
from .const import DOMAIN
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

_LOGGER = logging.getLogger(__name__)


def extend_shared(extra: dict) -> dict:
    return {**SHARED_SENSOR_TYPES, **extra}


SHARED_SENSOR_TYPES = {
    "id": {
        "name": "Mac Address",
        "unit": None,
        "device_class": None,
        "icon": "mdi:lan-connect",
    },
    "apikey": {
        "name": "API Key",
        "unit": None,
        "device_class": None,
        "icon": "mdi:key-variant",
    },
    "type": {
        "name": "Type",
        "unit": None,
        "device_class": None,
        "icon": "mdi:devices",
    },
    "model": {
        "name": "Model",
        "unit": None,
        "device_class": None,
        "icon": "mdi:chip",
    },
    "firmware_version": {
        "name": "Firmware Version",
        "unit": None,
        "device_class": None,
        "icon": "mdi:update",
    },
    "wifi_SSID": {
        "name": "WiFi SSID",
        "unit": None,
        "device_class": None,
        "icon": "mdi:wifi",
    },
    "connected": {
        "name": "Connected",
        "unit": None,
        "device_class": None,
        "icon": "mdi:connection",
    },
    "score": {
        "name": "Air Quality Score",
        "unit": "%",
        "device_class": None,
        "icon": "mdi:air-filter",
    },
    "timestamp": {
        "name": "Last Update",
        "unit": None,
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "program": {
        "name": "Program",
        "unit": None,
        "device_class": None,
        "icon": "mdi:play-circle",
    },
    "programdescription": {
        "name": "Program Description",
        "unit": None,
        "device_class": None,
        "icon": "mdi:text-box-outline",
    },
    "programicon": {
        "name": "Program Icon",
        "unit": None,
        "device_class": None,
        "icon": "mdi:image-outline",
    },
}

SHELFY_SENSOR_TYPES = extend_shared({
    "battery": {
        "name": "Battery Level",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.BATTERY,
    },
    "charging": {
        "name": "Charging",
        "unit": None,
        "device_class": None,
        "icon": "mdi:battery-charging",
    },
    "TMP01-SY": {
        "name": "Fridge Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
    },
    "DOC-SY": {
        "name": "Door Opening Times",
        "unit": None,
        "device_class": None,
        "icon": "mdi:door-open",
    },
    "DOT-SY": {
        "name": "Door Opening Seconds",
        "unit": "s",
        "device_class": None,
        "icon": "mdi:timer",
    },
    "timestamp": {
        "name": "Last Update",
        "unit": None,
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "programfan": {
        "name": "Program Fan",
        "unit": None,
        "device_class": None,
        "icon": "mdi:fan",
    },
    "programpower": {
        "name": "Program Power",
        "unit": None,
        "device_class": None,
        "icon": "mdi:lightning-bolt",
    },
    "filter": {
        "name": "Next Filter Cleaning Date",
        "unit": None,
        "device_class": SensorDeviceClass.TIMESTAMP,
        "icon": "mdi:calendar-clock",
    },
    "fridge": {
        "name": "Next Fridge Cleaning Date",
        "unit": None,
        "device_class": SensorDeviceClass.TIMESTAMP,
        "icon": "mdi:calendar-clock",
    },
    "filterdays": {
        "name": "Remaining Filter Cleaning Days",
        "unit": None,
        "device_class": None,
        "icon": "mdi:calendar-minus",
    },
    "fridgedays": {
        "name": "Remaining Fridge Cleaning Days",
        "unit": None,
        "device_class": None,
        "icon": "mdi:calendar-minus",
    },
})

NATEDE_SENSOR_TYPES = extend_shared({
    "TD01TP-N2": {
        "name": "Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
    },
    "SN01HU-N2": {
        "name": "Humidity",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.HUMIDITY,
    },
    "SN02VD-N2": {
        "name": "VOC",
        "unit": CONCENTRATION_PARTS_PER_MILLION,
        "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS,
    },
    "SN02C2-N2": {
        "name": "CO2",
        "unit": CONCENTRATION_PARTS_PER_MILLION,
        "device_class": SensorDeviceClass.CO2,
    },
    "SY01DS-N2": {
        "name": "PM2.5",
        "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        "device_class": SensorDeviceClass.PM25,
    },
})

ETERIA_SENSOR_TYPES = extend_shared({
    "SN01TP-E0": {
        "name": "Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
    },
    "SN01HU-E0": {
        "name": "Humidity",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.HUMIDITY,
    },
    "SN02VD-E0": {
        "name": "VOC",
        "unit": CONCENTRATION_PARTS_PER_MILLION,
        "device_class": SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS,
    },
    "SN02C2-E0": {
        "name": "CO2",
        "unit": CONCENTRATION_PARTS_PER_MILLION,
        "device_class": SensorDeviceClass.CO2,
    },
})


async def async_setup_entry(hass, entry, async_add_entities):
    # ⬇️ Coordinator was stored as a dict in hass.data in the updated __init__.py
    domain_entry = hass.data[DOMAIN][entry.entry_id]
    coordinator = domain_entry["coordinator"]

    entities: list[VitesySensor] = []

    # coordinator.data is expected to be a list of devices
    for device in coordinator.data or []:
        device_id = device.get("id", "").replace(":", "")
        device_type = device.get("type", "Unknown").capitalize()

        if "NATEDE" in device_type.upper():
            sensor_types = NATEDE_SENSOR_TYPES
        elif "ETERIA" in device_type.upper():
            sensor_types = ETERIA_SENSOR_TYPES
        else:
            sensor_types = SHELFY_SENSOR_TYPES

        # Add flat sensors like battery, type, etc.
        for sensor_type in sensor_types:
            if sensor_type in device and sensor_type != "program":
                entities.append(VitesySensor(coordinator, device_id, device_type, sensor_type, sensor_types))
            elif "battery" in device and sensor_type in device.get("battery", {}):
                entities.append(VitesySensor(coordinator, device_id, device_type, sensor_type, sensor_types))
            elif "program" in device and sensor_type in device and sensor_type == "program":
                entities.append(VitesySensor(coordinator, device_id, device_type, sensor_type, sensor_types))

                for extra_key in ["programdescription", "programicon", "programfan", "programpower"]:
                    if extra_key in sensor_types:
                        entities.append(VitesySensor(coordinator, device_id, device_type, extra_key, sensor_types))

        # Add from measurements (flat fields of the latest)
        if isinstance(device.get("measurements"), list) and device["measurements"]:
            latest_measurement = device["measurements"][0]
            for key in latest_measurement:
                if key in sensor_types and key != "id":
                    entities.append(VitesySensor(coordinator, device_id, device_type, key, sensor_types))

        # Add from measurements -> sensors_data[].id
        for measurement in device.get("measurements", []):
            for sensor in measurement.get("sensors_data", []):
                sensor_id = sensor.get("id")
                if sensor_id in sensor_types:
                    entities.append(VitesySensor(coordinator, device_id, device_type, sensor_id, sensor_types))

        # Add from maintenance
        for maintenance_key in device.get("maintenance", {}):
            if maintenance_key in sensor_types:
                entities.append(VitesySensor(coordinator, device_id, device_type, maintenance_key, sensor_types))
                entities.append(VitesySensor(coordinator, device_id, device_type, maintenance_key + "days", sensor_types))

    # Request initial values before adding, so sensors start “populated”
    async_add_entities(entities, update_before_add=True)


class VitesySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_id: str, device_type: str, sensor_type: str, sensor_types: Dict[str, Dict[str, Any]]):
        super().__init__(coordinator)
        self.device_id = device_id
        self.sensor_type = sensor_type
        self.device_type = device_type
        self._sensor_types = sensor_types

        self._attr_unique_id = f"vitesy_{device_type.lower()}_{device_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = self._sensor_types[sensor_type]["unit"]
        self._attr_device_class = self._sensor_types[sensor_type]["device_class"]
        self._attr_icon = self._sensor_types[sensor_type].get("icon")
        self._attr_translation_key = sensor_type.replace("_", "-").lower()
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "manufacturer": "Vitesy",
            "model": self.device_type,
            "name": f"Vitesy {self.device_type.title()}",
        }

    @property
    def native_value(self) -> Optional[Any]:
        # Safe device lookup (avoid StopIteration)
        device: Optional[Dict[str, Any]] = next(
            (d for d in (self.coordinator.data or []) if d.get("id", "").replace(":", "") == self.device_id),
            None,
        )
        if not device:
            return None

        def _get_program_data_field(d: Dict[str, Any], field: str) -> Optional[Any]:
            program_ref = d.get("program", {}).get("ref")
            if program_ref:
                fallback_ids = {
                    "boost-s0": ["boost-s0", "performance-s0"],
                    "eco-s0": ["eco-s0"],
                    "shelf-s0": ["shelf-s0"],
                }.get(program_ref, [program_ref])

                for p in d.get("programs", []):
                    if p.get("id") in fallback_ids:
                        return p.get(field)
            return None

        def _get_program_metadata_field(d: Dict[str, Any], meta_field: str) -> Optional[Any]:
            program_ref = d.get("program", {}).get("ref")
            if program_ref:
                fallback_ids = {
                    "boost-s0": ["boost-s0", "performance-s0"],
                    "eco-s0": ["eco-s0"],
                    "shelf-s0": ["shelf-s0"],
                }.get(program_ref, [program_ref])

                for p in d.get("programs", []):
                    if p.get("id") in fallback_ids:
                        return p.get("metadata", {}).get(meta_field)
            return None

        # Battery related (top-level)
        if self.sensor_type == "battery":
            return device.get("battery", {}).get("level")
        elif self.sensor_type == "charging":
            return device.get("battery", {}).get("charging")

        # Program-related
        if self.sensor_type == "program":
            if "data" in device.get("program", {}):
                return device["program"]["data"].get("name")
            return _get_program_data_field(device, "name")

        if self.sensor_type == "programdescription":
            if "data" in device.get("program", {}):
                return device["program"]["data"].get("description")
            return _get_program_data_field(device, "description")

        if self.sensor_type == "programicon":
            if "data" in device.get("program", {}):
                return device["program"]["data"].get("icon")
            return _get_program_data_field(device, "icon")

        if self.sensor_type == "programfan":
            if "data" in device.get("program", {}):
                return device["program"]["data"].get("metadata", {}).get("fan")
            return _get_program_metadata_field(device, "fan")

        if self.sensor_type == "programpower":
            if "data" in device.get("program", {}):
                return device["program"]["data"].get("metadata", {}).get("power")
            return _get_program_metadata_field(device, "power")

        # Flat attributes
        if self.sensor_type in device:
            return device[self.sensor_type]

        # From measurements (latest flat fields)
        measurements = device.get("measurements", [])
        if measurements and isinstance(measurements[0], dict) and self.sensor_type in measurements[0]:
            if self.sensor_type == "score":
                try:
                    return round(measurements[0][self.sensor_type] * 100)
                except Exception:
                    return None
            if self.sensor_type == "timestamp":
                ts = measurements[0].get(self.sensor_type)
                if ts and isinstance(ts, str):
                    try:
                        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        return None
                return None
            if self.sensor_type != "id":
                return measurements[0][self.sensor_type]

        # From measurements → sensors_data[]
        for measurement in measurements:
            for sensor in measurement.get("sensors_data", []):
                if sensor.get("id") == self.sensor_type:
                    value = sensor.get("value", {})
                    # Prefer avg if available, else try other typical fields
                    return value.get("avg", value.get("value", value.get("min")))

        # From maintenance
        maint = device.get("maintenance", {})
        if self.sensor_type in maint:
            try:
                due = maint[self.sensor_type].get("due_date")
                if isinstance(due, str):
                    return datetime.fromisoformat(due.replace("Z", "+00:00"))
            except (KeyError, ValueError, TypeError):
                return None

        if self.sensor_type.replace("days", "") in maint:
            try:
                base_key = self.sensor_type.replace("days", "")
                due = maint[base_key].get("due_date")
                if isinstance(due, str):
                    return (datetime.fromisoformat(due.replace("Z", "+00:00")) - datetime.now(timezone.utc)).days
            except (KeyError, ValueError, TypeError):
                return None

        return None
