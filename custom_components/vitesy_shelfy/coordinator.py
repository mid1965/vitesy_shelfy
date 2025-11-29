
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict, List

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import OPTION_POLL_MINUTES, DEFAULT_POLL_MINUTES

_LOGGER = logging.getLogger(__name__)


class VitesyDataUpdateCoordinator(DataUpdateCoordinator[List[Dict[str, Any]]]):
    """Coordinator that fetches Vitesy cloud data on a schedule."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api):
        self.hass = hass
        self.entry = entry
        self.api = api

        # Read polling interval from UI options, fallback to default from const.py
        poll_minutes = entry.options.get(OPTION_POLL_MINUTES, DEFAULT_POLL_MINUTES)

        super().__init__(
            hass,
            _LOGGER,
            name="vitesy_shelfy",
            update_interval=timedelta(minutes=poll_minutes),
        )

        # Optional: keep an attribute for convenience
        self.devices: List[Dict[str, Any]] = []

    async def _async_update_data(self) -> List[Dict[str, Any]]:
        """Fetch the latest data from the Vitesy API."""
        try:
            self.devices = await self._get_devices()

            for device in self.devices:
                device_id = device["id"]
                device_type = device["type"]
                firmware_version = device["firmware_version"]

                # device["apikey"] = await self._get_or_create_api_key()
                device["measurements"] = await self._get_measurements(device_id)
                device["maintenancehistory"] = await self._get_maintenance(device_id)
                device["programs"] = await self._get_programs(device_type, firmware_version)

            return self.devices

        except Exception as err:
            # Wrap any error so HA can surface it properly in logs/UI
            raise UpdateFailed(f"Error fetching Vitesy data: {err}") from err

    async def _get_devices(self) -> List[Dict[str, Any]]:
        return await self.hass.async_add_executor_job(self.api.get_devices)

    async def _get_measurements(self, device_id: str) -> Any:
        return await self.hass.async_add_executor_job(self.api.get_measurements, device_id)

    async def _get_maintenance(self, device_id: str) -> Any:
        return await self.hass.async_add_executor_job(self.api.get_maintenance, device_id)

    async def _get_programs(self, device_type: str, firmware_version: str) -> Any:
        return await self.hass.async_add_executor_job(self.api.get_programs, device_type, firmware_version)

    # async def _get_or_create_api_key(self) -> str:
    #     return await self.hass.async_add_executor_job(self.api.get_or_create_api_key)
