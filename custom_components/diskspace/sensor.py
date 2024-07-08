"""Sensor platform for Local Diskspace."""

import datetime
import logging
import shutil

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.const import CONF_ICON, CONF_NAME, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle

__version__ = "v0.5"
_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = []

CONF_PATH = "path"
CONF_UOM = "unit_of_measure"

DEFAULT_UOM = "GB"
DEFAULT_ICON = "mdi:harddisk"
DEFAULT_PATH = "/"

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_PATH, default=DEFAULT_PATH): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.string,
        vol.Required(CONF_UOM, default=DEFAULT_UOM): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Setup Platform."""
    add_entities(
        [
            DiskSpaceSensor(
                name=config[CONF_NAME],
                path=config[CONF_PATH],
                icon=config[CONF_ICON],
                uom=config[CONF_UOM],
            )
        ]
    )


class DiskSpaceSensor(SensorEntity):
    def __init__(self, name: str, path: str, icon: str, uom: str) -> None:
        self._state = None
        self._icon = icon
        self._attributes = {}
        self._path = path
        self._uom = uom
        self._name = name
        self._attr_native_unit_of_measurement = UnitOfInformation.BYTES
        self._attr_device_class = SensorDeviceClass.DATA_SIZE

    @property
    def name(self) -> str:
        return "Disk Space " + self._name

    @property
    def native_value(self) -> int | None:
        return self._state

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def state_attributes(self) -> dict:
        return self._attributes

    @property
    def suggested_unit_of_measurement(self) -> str:
        return self._uom

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self) -> None:
        self._attributes = {}
        self._state = 0

        try:
            total, used, free = shutil.disk_usage(self._path)
            _LOGGER.debug("Path %s", self._path)
            _LOGGER.debug("Total %s", total)
            _LOGGER.debug("Used %s", used)
            _LOGGER.debug("Free %s", free)
        except Exception as err:
            _LOGGER.warning("Other Error: %s", err)

        self._attributes["total"] = total
        self._attributes["used"] = used
        self._attributes["free"] = free

        self._attributes["percentage_free"] = round((free / total) * 100, 1)
        self._state = self._attributes["free"]
