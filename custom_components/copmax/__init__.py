"""The CustomIntegration integration."""

import asyncio
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .modbus_poll import CopmaxModbusPoll

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["number", "sensor"]
# PLATFORMS = ["number"]
# PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the CustomIntegration component."""

    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up CustomIntegration from a config entry."""
    device_hostname = entry.data["inverter_host"]
    device_port = entry.data["inverter_port"]
    device_scaninterval = entry.data["scan_interval"]
    device_alias = entry.data["alias"]

    copmaxPoll = CopmaxModbusPoll(device_hostname, device_port)

    # Fetch initial data so we have data when entities subscribe
    coordinator = CustomIntegrationCoordinator(
        hass, copmaxPoll, device_alias, device_scaninterval
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = HassCustomIntegration(
        coordinator, device_hostname, device_port
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class HassCustomIntegration:
    def __init__(
        self, coordinator: DataUpdateCoordinator, inverter_host: str, inverter_port: int
    ):
        self._inverter_host = inverter_host
        self._inverter_port = inverter_port
        _LOGGER.debug("CustomIntegration __init__" + self._inverter_host)

        # create an instance of StecaConnector
        self._coordinator = coordinator

    def get_name(self):
        return f"steca_grid_{self._inverter_host}_{str(self._inverter_port)}"

    def get_unique_id(self):
        return f"steca_grid_power_{self._inverter_host}_{str(self._inverter_port)}"


class CustomIntegrationCoordinator(DataUpdateCoordinator):
    """CustomIntegration coordinator."""

    def __init__(
        self, hass, copmaxPoll: CopmaxModbusPoll, alias: str, pollinterval: int
    ):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=f"CustomIntegration coordinator for '{alias}'",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=pollinterval),
        )
        self.copmaxModbusPoll = copmaxPoll
        self.alias = alias

    async def _async_update_data(self):
        # Fetch data from API endpoint. This is the place to pre-process the data to lookup tables so entities can quickly look up their data.

        try:
            retval = await self.copmaxModbusPoll.poll_heat_pump_data()
            # return retval

        except Exception as e:
            _LOGGER.error(
                f"CustomIntegrationCoordinator _async_update_data failed: {e}"
            )
