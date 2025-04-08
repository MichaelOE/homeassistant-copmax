from dataclasses import dataclass
import logging

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant

from . import CopmaxCoordinator
from .const import DEVICE_MANUCFACTURER, DEVICE_MODEL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class CustomIntegrationNumberEntityDescription(NumberEntityDescription):
    """Describes CustomIntegration sensor entity."""

    def __init__(
        self,
        key,
        register: str,
        type: str,
        name,
        min,
        max,
        step,
        icon,
        device_class,
        native_unit_of_measurement,
        format=None,
    ):
        super().__init__(key)
        self.key = key
        self.register = register
        self.type = type
        self.name = name
        self.min = min
        self.max = max
        self.step = step
        self.icon = icon
        if device_class is not None:
            self.device_class = device_class
        self.native_unit_of_measurement = native_unit_of_measurement
        self.format = format


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities
):
    """Set up the sensor platform."""
    CustomIntegration = hass.data[DOMAIN][config.entry_id]

    # Fetch initial data so we have data when entities subscribe
    # await CustomIntegration._coordinator.async_config_entry_first_refresh()

    entities: list[CustomIntegrationNumber] = [
        CustomIntegrationNumber(
            CustomIntegration._coordinator, sensor, CustomIntegration
        )
        for sensor in NUMBER_HEATPUMP
    ]

    async_add_entities(entities)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    # Code for setting up your platform inside of the event loop
    _LOGGER.debug("async_setup_platform")


class CustomIntegrationNumber(NumberEntity):
    """Representation of an input_number entity."""

    def __init__(
        self,
        coordinator: CopmaxCoordinator,
        sensor: CustomIntegrationNumberEntityDescription,
        client,
    ):
        """Initialize the sensor."""
        self._data = client
        self.coordinator = coordinator
        self.entity_description: CustomIntegrationNumberEntityDescription = sensor
        self._attr_unique_id = f"{self.coordinator.alias}_{sensor.key}"
        self._attr_name = f"{self.coordinator.alias} {sensor.name}"
        self._attr_entity_category = EntityCategory.CONFIG

        self.mode = "box"
        self._min = self.entity_description.min
        self._max = self.entity_description.max
        self._step = self.entity_description.step

        _LOGGER.info(self._attr_unique_id)
        self._attr_native_value = 0.0  # Initialize the native value

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
    def name(self):
        """Return the name of the entity."""
        return self._attr_name

    @property
    def friendly_name(self):
        return self.entity_description.name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._attr_native_value is None:
            return self._attr_native_value

        if "ST06" in self.entity_description.key:
            return self._attr_native_value

        return self._attr_native_value / 100

    @property
    def min_value(self):
        """Return the minimum value for the input_number."""
        return self._min

    @property
    def max_value(self):
        """Return the maximum value for the input_number."""
        return self._max

    @property
    def step(self):
        """Return the step size for the input_number."""
        return self._step

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""

        # Handle User settings
        if self.entity_description.type == "ST":
            if self.coordinator.copmaxModbusPoll.user_settings_valid:
                if (
                    self.entity_description.register
                    in self.coordinator.copmaxModbusPoll.user_settings
                ):
                    self._attr_native_value = (
                        self.coordinator.copmaxModbusPoll.user_settings[
                            (self.entity_description.register)
                        ]
                    )
                else:
                    self._attr_native_value = None

        # Handle Special functions
        if self.entity_description.type == "SF":
            if self.coordinator.copmaxModbusPoll.special_functions_valid:
                self._attr_native_value = (
                    self.coordinator.copmaxModbusPoll.special_functions[
                        (self.entity_description.register)
                    ]
                )

        return self._attr_native_value

    def update(self) -> None:
        self.native_value

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value of the input_number."""
        self.send_to_device(value)
        self.async_write_ha_state()

    def send_to_device(self, value):
        """Send the value to the device."""
        _LOGGER.info(f"Sending '{value}' to device...")
        retval = self.coordinator.copmaxModbusPoll.modbus_write_holding_register(
            self.entity_description.register, value
        )
        _LOGGER.info(f"Got '{retval}' return...")


NUMBER_HEATPUMP: tuple[SensorEntityDescription, ...] = (
    CustomIntegrationNumberEntityDescription(
        key="H_ST01",
        register=38,
        type="ST",
        name="Cooling target",
        min=0.0,
        max=60.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST02",
        register=39,
        type="ST",
        name="Heating target",
        min=0.0,
        max=80.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST03",
        register=40,
        type="ST",
        min=0.0,
        max=10.0,
        step=0.1,
        name="Cooling hysteresis",
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST04",
        register=41,
        type="ST",
        name="Heating hysteresis",
        min=0.0,
        max=10.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST05",
        register=42,
        type="ST",
        name="Heat compensation target",
        min=0.0,
        max=30.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST06",
        register=43,
        type="ST",
        name="Heat compensation factor",
        min=0.0,
        max=30.0,
        step=0.1,
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST07",
        register=44,
        type="ST",
        name="Heating rod start",
        min=-10.0,
        max=20.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST08",
        register=45,
        type="ST",
        name="Heating rod diff stop (@ST07)",
        min=1.0,
        max=20.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST09",
        register=46,
        type="ST",
        name="Hot water target",
        min=0.00,
        max=80.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST10",
        register=47,
        type="ST",
        name="Hot water diff",
        min=1.0,
        max=10.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST11",
        register=48,
        type="ST",
        name="Cooling temp min",
        min=0.0,
        max=60.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST12",
        register=49,
        type="ST",
        name="Cooling temp max",
        min=0.0,
        max=60.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST13",
        register=50,
        type="ST",
        name="Heating temp min",
        min=0.0,
        max=80.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST14",
        register=51,
        type="ST",
        name="Heating temp max",
        min=0.0,
        max=80.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST15",
        register=52,
        type="ST",
        name="Hot water temp min",
        min=1.0,
        max=20.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST16",
        register=53,
        type="ST",
        name="Hot water temp max",
        min=1.0,
        max=20.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST17",
        register=54,
        type="ST",
        name="Check/adjust time delay",
        min=1,
        max=1000,
        step=1,
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST18",
        register=55,
        type="ST",
        name="Run mode transfer temp",
        min=1.0,
        max=20.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_ST19",
        register=56,
        type="ST",
        name="Run mode transfer temp diff",
        min=1.0,
        max=20.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # Special functions
    CustomIntegrationNumberEntityDescription(
        key="H_SF01",
        register=24,
        type="SF",
        name="System mode",
        min=0,
        max=2,
        step=1,
        icon="mdi:information",
        device_class=None,
        native_unit_of_measurement=None,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_SF02",
        register=25,
        type="SF",
        name="Ambient temp stop HP",
        min=-20.0,
        max=20.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_SF03",
        register=26,
        type="SF",
        name="Ambient temp restart HP (@SF02)",
        min=0.0,
        max=10.0,
        step=0.1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # CustomIntegrationNumberEntityDescription(
    #     key="H_SF04",
    #     register=27,
    #     type="SF",
    #     name="Compensation function heat",
    #     min=0,
    #     max=1,
    #     step=1,
    #     icon="mdi:electric-switch",
    #     device_class=None,
    #     native_unit_of_measurement=None,
    #     value=lambda data, key: data[key],
    # ),
    # CustomIntegrationNumberEntityDescription(
    #     key="H_SF05",
    #     register=28,
    #     type="SF",
    #     name="Heat recovery",
    #     min=0,
    #     max=1,
    #     step=1,
    #     icon="mdi:electric-switch",
    #     device_class=None,
    #     native_unit_of_measurement=None,
    #     value=lambda data, key: data[key],
    # ),
    CustomIntegrationNumberEntityDescription(
        key="H_SF06",
        register=29,
        type="SF",
        name="Outdoor temp anti-freeze",
        min=0.0,
        max=10.0,
        step=1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_SF07",
        register=30,
        type="SF",
        name="Outdoor temp anti-freeze restart (@ST06)",
        min=-1.0,
        max=10.0,
        step=1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_SF08",
        register=31,
        type="SF",
        name="Water temp anti-freeze",
        min=1.0,
        max=10.0,
        step=1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CustomIntegrationNumberEntityDescription(
        key="H_SF09",
        register=32,
        type="SF",
        name="Water temp anti-freeze restart (@SF08)",
        min=1.0,
        max=10.0,
        step=1,
        icon="mdi:temperature-celsius",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # CustomIntegrationNumberEntityDescription(
    #     key="H_SF10",
    #     register=33,
    #     type="SF",
    #     name="SF10",
    #     min=0,
    #     max=1,
    #     step=1,
    #     icon="mdi:electric-switch",
    #     device_class=None,
    #     native_unit_of_measurement=None,
    #     value=lambda data, key: data[key],
    # ),
    # CustomIntegrationNumberEntityDescription(
    #     key="H_SF11",
    #     register=34,
    #     type="SF",
    #     name="SF11",
    #     min=15.0,
    #     max=50.0,
    #     step=0.1,
    #     icon="mdi:temperature-celsius",
    #     device_class=NumberDeviceClass.TEMPERATURE,
    #     native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    #     value=lambda data, key: data[key],
    # ),
    # CustomIntegrationNumberEntityDescription(
    #     key="H_SF12",
    #     register=35,
    #     type="SF",
    #     name="SF12",
    #     min=1.0,
    #     max=15.0,
    #     step=0.1,
    #     icon="mdi:temperature-celsius",
    #     device_class=NumberDeviceClass.TEMPERATURE,
    #     native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    #     value=lambda data, key: data[key],
    # ),
    # CustomIntegrationNumberEntityDescription(
    #     key="H_SF13",
    #     register=36,
    #     type="SF",
    #     name="Hot water control method",
    #     min=0,
    #     max=1,
    #     step=1,
    #     icon="mdi:electric-switch",
    #     device_class=None,
    #     native_unit_of_measurement=None,
    #     value=lambda data, key: data[key],
    # ),
    # CustomIntegrationNumberEntityDescription(
    #     key="H_SF14",
    #     register=37,
    #     type="SF",
    #     name="A/C remote controlled",
    #     min=0,
    #     max=1,
    #     step=1,
    #     icon="mdi:electric-switch",
    #     device_class=None,
    #     native_unit_of_measurement=None,
    #     value=lambda data, key: data[key],
    # ),
)
