"""Support for Nature Remo E energy sensor."""
import logging

from homeassistant.const import (CONF_ACCESS_TOKEN, DEVICE_CLASS_HUMIDITY,
                                 DEVICE_CLASS_ILLUMINANCE, DEVICE_CLASS_POWER,
                                 DEVICE_CLASS_TEMPERATURE,
                                 DEVICE_CLASS_TIMESTAMP, ENERGY_KILO_WATT_HOUR,
                                 LIGHT_LUX, PERCENTAGE, POWER_WATT,
                                 TEMP_CELSIUS)

from . import DOMAIN, NatureRemoBase, NatureRemoDeviceBase

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Nature Remo E sensor."""
    if discovery_info is None:
        return
    _LOGGER.debug("Setting up sensor platform.")
    coordinator = hass.data[DOMAIN]["coordinator"]
    appliances = coordinator.data["appliances"]
    devices = coordinator.data["devices"]
    entities = [
        NatureRemoE(coordinator, appliance)
        for appliance in appliances.values()
        if appliance["type"] == "EL_SMART_METER"
    ]
    for device in devices.values():
        for sensor in device["newest_events"].keys():
            if sensor == "te":
                entities.append(NatureRemoTemperatureSensor(coordinator, device))
            elif sensor == "hu":
                entities.append(NatureRemoHumiditySensor(coordinator, device))
            elif sensor == "il":
                entities.append(NatureRemoIlluminanceSensor(coordinator, device))
            elif sensor == "mo":
                entities.append(NatureRemoMotionSensor(coordinator, device))
    async_add_entities(entities)


class NatureRemoE(NatureRemoBase):
    """Implementation of a Nature Remo E sensor."""

    def __init__(self, coordinator, appliance):
        super().__init__(coordinator, appliance)
        self._unit_of_measurement = POWER_WATT

    @property
    def state(self):
        """Return the state of the sensor."""
        appliance = self._coordinator.data["appliances"][self._appliance_id]
        smart_meter = appliance["smart_meter"]
        echonetlite_properties = smart_meter["echonetlite_properties"]
        measured_instantaneous = next(
            value["val"] for value in echonetlite_properties if value["epc"] == 231
        )
        _LOGGER.debug("Current state: %sW", measured_instantaneous)
        return measured_instantaneous

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_POWER

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self._coordinator.async_request_refresh()


class NatureRemoTemperatureSensor(NatureRemoDeviceBase):
    """Implementation of a Nature Remo sensor."""

    def __init__(self, coordinator, appliance):
        super().__init__(coordinator, appliance)
        self._name = self._name.strip() + " Temperature"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._device["id"] + "-te"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return TEMP_CELSIUS

    @property
    def state(self):
        """Return the state of the sensor."""
        device = self._coordinator.data["devices"][self._device["id"]]
        return device["newest_events"]["te"]["val"]

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_TEMPERATURE


class NatureRemoHumiditySensor(NatureRemoDeviceBase):
    """Implementation of a Nature Remo sensor."""

    def __init__(self, coordinator, appliance):
        super().__init__(coordinator, appliance)
        self._name = self._name.strip() + " Humidity"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._device["id"] + "-hu"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return PERCENTAGE

    @property
    def state(self):
        """Return the state of the sensor."""
        device = self._coordinator.data["devices"][self._device["id"]]
        return device["newest_events"]["hu"]["val"]

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_HUMIDITY


class NatureRemoIlluminanceSensor(NatureRemoDeviceBase):
    """Implementation of a Nature Remo sensor."""

    def __init__(self, coordinator, appliance):
        super().__init__(coordinator, appliance)
        self._name = self._name.strip() + " Illuminance"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._device["id"] + "-il"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return LIGHT_LUX

    @property
    def state(self):
        """Return the state of the sensor."""
        device = self._coordinator.data["devices"][self._device["id"]]
        return device["newest_events"]["il"]["val"]

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_ILLUMINANCE 

        
class NatureRemoMotionSensor(NatureRemoDeviceBase):
    """Implementation of a Nature Remo sensor."""

    def __init__(self, coordinator, appliance):
        super().__init__(coordinator, appliance)
        self._name = self._name.strip() + " Motion"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._device["id"] + "-mo"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return LIGHT_LUX

    @property
    def state(self):
        """Return the state of the sensor."""
        device = self._coordinator.data["devices"][self._device["id"]]
        return device["newest_events"]["mo"]["created_at"]

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_TIMESTAMP 