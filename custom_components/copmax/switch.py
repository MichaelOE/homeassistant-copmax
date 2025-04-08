from dataclasses import dataclass
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant

from . import CopmaxCoordinator
from .const import DEVICE_MANUCFACTURER, DEVICE_MODEL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class CopmaxSwitchEntityDesc(SwitchEntityDescription):
    """Describes CustomIntegration switch entity."""

    def __init__(
        self,
        key,
        register: str,
        type: str,
        name,
        icon,
        device_class,
    ):
        super().__init__(key)
        self.key = key
        self.register = register
        self.type = type
        self.name = name
        self.icon = icon
        if device_class is not None:
            self.device_class = device_class


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities
):
    """Set up the sensor platform."""
    CustomIntegration = hass.data[DOMAIN][config.entry_id]

    # Fetch initial data so we have data when entities subscribe
    # await CustomIntegration._coordinator.async_config_entry_first_refresh()

    entities: list[CopmaxSwitch] = [
        CopmaxSwitch(CustomIntegration._coordinator, sensor, CustomIntegration)
        for sensor in SWITCH_HEATPUMP
    ]

    async_add_entities(entities)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    # Code for setting up your platform inside of the event loop
    _LOGGER.debug("async_setup_platform")


class CopmaxSwitch(SwitchEntity):
    """Representation of an input_number entity."""

    def __init__(
        self,
        coordinator: CopmaxCoordinator,
        sensor: CopmaxSwitchEntityDesc,
        client,
    ):
        """Initialize the sensor."""
        self._data = client
        self.coordinator = coordinator
        self.entity_description: CopmaxSwitchEntityDesc = sensor
        self._attr_unique_id = f"{self.coordinator.alias}_{sensor.key}"
        self._attr_name = f"{self.coordinator.alias} {sensor.name}"
        self._attr_entity_category = EntityCategory.CONFIG

        _LOGGER.info(self._attr_unique_id)
        self._is_on = False  # Initialize the native value

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.alias)},
            "manufacturer": DEVICE_MANUCFACTURER,
            "model": DEVICE_MODEL,
            "name": self.coordinator.alias,
        }

    @property
    def name(self):
        """Return the name of the entity."""
        return self._attr_name

    @property
    def friendly_name(self):
        return self.entity_description.name

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        _LOGGER.info(f"switch async_turn_on '{self.entity_description.name}'...")
        await self.send_to_device(1)
        """Turn the entity on."""

    async def async_turn_off(self, **kwargs):
        _LOGGER.info(f"switch async_turn_off '{self.entity_description.name}'...")
        await self.send_to_device(0)
        """Turn the entity off."""

    async def async_toggle(self, **kwargs):
        _LOGGER.info(f"switch async_toggle '{self.entity_description.name}'...")
        """Toggle the entity."""

    async def async_update(self):
        # _LOGGER.info(f"switch async_update '{self.entity_description.name}'...")
        # Handle User settings
        if self.entity_description.type == "SF":
            if self.coordinator.copmaxModbusPoll.special_functions_valid:
                if (
                    self.entity_description.register
                    in self.coordinator.copmaxModbusPoll.special_functions
                ):
                    self._is_on = (
                        self.coordinator.copmaxModbusPoll.special_functions[
                            self.entity_description.register
                        ]
                        != 0
                    )
                else:
                    self._is_on = False

    async def send_to_device(self, value):
        """Send the value to the device."""
        _LOGGER.info(f"Sending '{value}' to device...")
        retval = await self.coordinator.copmaxModbusPoll.modbus_write_holding_register(
            self.entity_description.register, value
        )
        _LOGGER.info(f"Got '{retval}' return...")


SWITCH_HEATPUMP: tuple[SwitchEntityDescription, ...] = (
    CopmaxSwitchEntityDesc(
        key="H_SF04",
        register=27,
        type="SF",
        name="Compensation heating",
        icon="mdi:temperature-celsius",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    CopmaxSwitchEntityDesc(
        key="H_SF05",
        register=28,
        type="SF",
        name="Heat recovery",
        icon="mdi:electric-switch",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    CopmaxSwitchEntityDesc(
        key="H_SF13",
        register=36,
        type="SF",
        name="Hot water",
        icon="mdi:electric-switch",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    CopmaxSwitchEntityDesc(
        key="H_SF14",
        register=37,
        type="SF",
        name="A/C remote control",
        icon="mdi:electric-switch",
        device_class=SwitchDeviceClass.SWITCH,
    ),
)
