"""Platform for CustomIntegration sensor integration."""

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CustomIntegrationCoordinator
from .const import DEFAULT_INVERTER_POLLRATE, DEVICE_MANUCFACTURER, DEVICE_MODEL, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=DEFAULT_INVERTER_POLLRATE)


@dataclass
class CustomIntegrationEntityDescription(SensorEntityDescription):
    """Describes CustomIntegration sensor entity."""

    def __init__(
        self,
        key,
        register: str,
        type: str,
        name,
        icon,
        device_class,
        native_unit_of_measurement,
        value,
        format=None,
    ):
        super().__init__(key)
        self.key = key
        self.register = register
        self.type = type
        self.name = name
        self.icon = icon
        if device_class is not None:
            self.device_class = device_class
        self.native_unit_of_measurement = native_unit_of_measurement
        self.value = value
        self.format = format


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities
):
    """Set up the sensor platform."""
    CustomIntegration = hass.data[DOMAIN][config.entry_id]

    entities: list[CustomIntegrationSensor] = [
        CustomIntegrationSensor(
            CustomIntegration._coordinator, sensor, CustomIntegration
        )
        for sensor in BINARY_SENSORS_HEATPUMP
    ]

    async_add_entities(entities)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    # Code for setting up your platform inside of the event loop
    _LOGGER.debug("async_setup_platform")


class CustomIntegrationSensor(CoordinatorEntity, SensorEntity):
    """Representation of a meter reading sensor."""

    def __init__(
        self,
        coordinator: CustomIntegrationCoordinator,
        sensor: CustomIntegrationEntityDescription,
        client,
    ):
        """Initialize the sensor."""
        self._data = client
        self.coordinator = coordinator
        self.entity_description: CustomIntegrationEntityDescription = sensor
        self._attr_unique_id = f"{self.coordinator.alias}_{sensor.key}"
        self._attr_name = f"{self.coordinator.alias} {sensor.name}"

        _LOGGER.info(self._attr_unique_id)
        self._attr_native_value = None  # Initialize the native value
        self.suggested_display_precision = 1

    @property
    def device_info(self):
        """Return device information about this entity."""
        _LOGGER.debug("CustomIntegration: device_info")

        return {
            "identifiers": {(DOMAIN, self.coordinator.alias)},
            "manufacturer": DEVICE_MANUCFACTURER,
            "model": DEVICE_MODEL,
            "name": self.coordinator.alias,
        }

    @property
    def should_poll(self):
        return True

    @property
    def friendly_name(self):
        return self.entity_description.name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._attr_native_value is None:
            return self._attr_native_value

        if self.entity_description.type == "STATUS":
            return self._attr_native_value

        return self._attr_native_value / 100

    async def async_added_to_hass(self):
        """Handle entity addition to hass."""
        # Add the coordinator listener for data updates
        self.coordinator.async_add_listener(self._handle_coordinator_update)
        # Ensure that data is fetched initially
        await self.coordinator.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data_available = False

        try:
            # Handle User settings
            if self.entity_description.type == "STATUS":
                if self.coordinator.copmaxModbusPoll.status_valid:
                    self._attr_native_value = self.coordinator.copmaxModbusPoll.status[
                        self.entity_description.register
                    ]
                    data_available = True

            self._attr_available = data_available

            # Only call async_write_ha_state if the state has changed
            # if data_available:
            self.async_write_ha_state()

        except KeyError as ex:
            _LOGGER.debug(
                f"KeyError: {str(ex)} while handling {self.entity_description.key}"
            )
        except ValueError as ex:
            _LOGGER.debug(
                f"ValueError: {str(ex)} while handling {self.entity_description.key}"
            )
        except Exception as ex:
            _LOGGER.debug(
                f"Unexpected error: {str(ex)} while handling {self.entity_description.key}"
            )


BINARY_SENSORS_HEATPUMP: tuple[SensorEntityDescription, ...] = (
    # Status registers
    CustomIntegrationEntityDescription(
        key="I_R6",
        register=6,
        type="STATUS",
        name="I_R6",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R7",
        register=7,
        type="STATUS",
        name="I_R7",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R8",
        register=8,
        type="STATUS",
        name="I_R8",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R9",
        register=9,
        type="STATUS",
        name="Remote run signal",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R10",
        register=10,
        type="STATUS",
        name="I_R10",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R11",
        register=11,
        type="STATUS",
        name="Comp run",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R12",
        register=12,
        type="STATUS",
        name="I_R12",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R13",
        register=13,
        type="STATUS",
        name="Circ. pump",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R14",
        register=14,
        type="STATUS",
        name="I_R14",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R15",
        register=15,
        type="STATUS",
        name="I_R15",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R16",
        register=16,
        type="STATUS",
        name="I_R16",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R17",
        register=17,
        type="STATUS",
        name="I_R17",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R18",
        register=18,
        type="STATUS",
        name="I_R18",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R19",
        register=19,
        type="STATUS",
        name="I_R19",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
    CustomIntegrationEntityDescription(
        key="I_R20",
        register=20,
        type="STATUS",
        name="I_R20",
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
        value=lambda data, key: data[key],
    ),
)
