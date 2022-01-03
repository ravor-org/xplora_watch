""" Xplora Watch """
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components import binary_sensor, device_tracker, sensor, switch
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_SCAN_INTERVAL

from datetime import datetime

from .const import (
    CONF_COUNTRY_CODE,
    CONF_PHONENUMBER,
    CONF_PASSWORD,
    CONF_TYPES,
    CONF_USERLANG,
    CONF_TIMEZONE,
    DATA_XPLORA,
    SENSOR_TYPE_BATTERY_SENSOR,
    SENSOR_TYPE_XCOIN_SENSOR,
    XPLORA_CONTROLLER,
    DOMAIN,
)

from pyxplora_api import pyxplora_api as PXA

DEFAULT_SCAN_INTERVAL = 3 *60

#PLATFORMS = [switch.DOMAIN, sensor.DOMAIN, binary_sensor.DOMAIN]
PLATFORMS = [sensor.DOMAIN]

SENSORS = [SENSOR_TYPE_BATTERY_SENSOR, SENSOR_TYPE_XCOIN_SENSOR]

_LOGGER = logging.getLogger(__name__)

CONTROLLER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_COUNTRY_CODE): cv.string,
        vol.Required(CONF_PHONENUMBER): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_USERLANG): cv.string,
        vol.Required(CONF_TIMEZONE): cv.time_zone,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
        vol.Optional(CONF_TYPES, default=SENSORS): cv.ensure_list,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema(vol.All(cv.ensure_list, [CONTROLLER_SCHEMA]))},
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
    _LOGGER.debug(f"init")
    hass.data[DATA_XPLORA] = []
    hass.data[CONF_COUNTRY_CODE] = []
    hass.data[CONF_PHONENUMBER] = []
    hass.data[CONF_PASSWORD] = []
    hass.data[CONF_USERLANG] = []
    hass.data[CONF_TIMEZONE] = []
    hass.data[CONF_TYPES] = []
    hass.data[CONF_SCAN_INTERVAL] = []
    hass.data["start_time"] = []

    success = False
    for controller_config in config[DOMAIN]:
        success = success or _setup_controller(hass, controller_config, config)

    return True

def _setup_controller(hass, controller_config, config):
    cc = controller_config[CONF_COUNTRY_CODE]
    phoneNumber = controller_config[CONF_PHONENUMBER]
    password = controller_config[CONF_PASSWORD]
    userlang = controller_config[CONF_USERLANG]
    _types = controller_config[CONF_TYPES]
    tz = controller_config[CONF_TIMEZONE]
    si = controller_config[CONF_SCAN_INTERVAL]
    timeNow = datetime.timestamp(datetime.now())
    controller = PXA.PyXploraApi(cc, phoneNumber, password, userlang, tz)
    position = len(hass.data[DATA_XPLORA])

    hass.data[DATA_XPLORA].append(controller)
    hass.data[CONF_COUNTRY_CODE].append(cc)
    hass.data[CONF_PHONENUMBER].append(phoneNumber)
    hass.data[CONF_PASSWORD].append(password)
    hass.data[CONF_USERLANG].append(userlang)
    hass.data[CONF_TYPES].append(_types)
    hass.data[CONF_TIMEZONE].append(tz)
    hass.data[CONF_SCAN_INTERVAL].append(si)
    hass.data["start_time"].append(timeNow)
    for platform in PLATFORMS:
        discovery.load_platform(
            hass,
            platform,
            DOMAIN,
            {XPLORA_CONTROLLER: position, **controller_config},
            config,
        )
    return True