
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, OPTION_POLL_MINUTES, DEFAULT_POLL_MINUTES
from .coordinator import VitesyDataUpdateCoordinator
from .api import VitesyOAuth

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]  # extend if you add more


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Vitesy Shelfy from a config entry."""
    session = async_get_clientsession(hass)
    email = entry.data["email"]
    password = entry.data["password"]

    # Authenticate and get tokens
    api = VitesyOAuth(email, password, session)
    # If VitesyOAuth.login() is synchronous, offload to executor:
    await hass.async_add_executor_job(api.login)

    # Create coordinator; it should read entry.options internally, but we also set explicitly
    coordinator = VitesyDataUpdateCoordinator(hass, entry, api)

    # Ensure the interval reflects options (in case coordinator sets a default)
    poll_minutes = entry.options.get(OPTION_POLL_MINUTES, DEFAULT_POLL_MINUTES)
    coordinator.update_interval = timedelta(minutes=poll_minutes)

    # Prime data
    await coordinator.async_config_entry_first_refresh()

    # Store references in hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    # Forward platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for options changes (Options Flow submissions)
    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a Vitesy Shelfy config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Clean up stored data
        domain_data = hass.data.get(DOMAIN, {})
        domain_data.pop(entry.entry_id, None)
    return unload_ok


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """
    React to changes in entry.options (from the Options Flow).
    Update the coordinator's interval dynamically and trigger a refresh.
    """
    domain_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not domain_data:
        return

    coordinator: VitesyDataUpdateCoordinator = domain_data["coordinator"]

    # Read the latest polling interval from options (fallback to default)
    poll_minutes = entry.options.get(OPTION_POLL_MINUTES, DEFAULT_POLL_MINUTES)

    _LOGGER.info("Vitesy Shelfy: updating polling interval to %s minute(s)", poll_minutes)
    coordinator.update_interval = timedelta(minutes=poll_minutes)

    # Optional: request an immediate refresh after changing interval
    await coordinator.async_request_refresh()
