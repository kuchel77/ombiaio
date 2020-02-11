"""Support for Ombi."""
from datetime import timedelta
import logging

from homeassistant.components.ombi.pyaioombi import Ombi
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.setup import async_setup_component
import json

from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)
CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_API_KEY = "api_key"
CONF_PASSWORD = "password"
CONF_PORT = "port"
CONF_URLBASE = "urlbase"
CONF_SSL = "ssl"
DEFAULT_PORT = "3579"
DEFAULT_URLBASE = "/"
DEFAULT_SSL = False

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=15)
import logging
import voluptuous as vol
from homeassistant.components.ombi.pyaioombi import Ombi
from homeassistant.const import (
CONF_API_KEY,
CONF_HOST,
CONF_PASSWORD,
CONF_PORT,
CONF_SSL,
CONF_USERNAME,
)
import homeassistant.helpers.config_validation as cv
from .const import (
ATTR_NAME,
ATTR_SEASON,
CONF_URLBASE,
DEFAULT_PORT,
DEFAULT_SEASON,
DEFAULT_SSL,
DEFAULT_URLBASE,
DOMAIN,
SERVICE_MOVIE_REQUEST,
SERVICE_MUSIC_REQUEST,
SERVICE_TV_REQUEST,
)



async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Ombi sensor platform."""
    if discovery_info is None:
        return

    session = async_get_clientsession(hass)

    ombi = Ombi(
        hass.loop,
        session,
        ssl=False,
        username="mark@kuchel.net",
        host="192.168.0.200",
        port="3579",
        urlbase="",
        api_key="2df11d4658934d3a9b8454e993f370f8",
        password="",
    )

    available_instance = OmbiSensor(ombi=ombi, sensor_type="available", icon="mdi:movies", label="available")
    pending_instance = OmbiSensor(ombi=ombi, sensor_type="pending", icon="mdi:movies", label="pending")
    approved_instance = OmbiSensor(ombi=ombi, sensor_type="approved", icon="mdi:movies", label="approved")
    tv_instance = OmbiSensor(ombi=ombi, sensor_type="tv", icon="mdi:movies", label="tv")
    music_instance = OmbiSensor(ombi=ombi, sensor_type="music", icon="mdi:music", label="music")
    movies_instance = OmbiSensor(ombi=ombi, sensor_type="movies", icon="mdi:movies", label="movies")
    movie_requests_list = OmbiSensor(ombi=ombi, sensor_type="movie_requests_list", icon="mdi:movies", label="movie_requests_list")

    async_add_entities([music_instance, movies_instance, tv_instance, available_instance, pending_instance, approved_instance, movie_requests_list], True)
    #async_add_entities([total_instance], True)

class OmbiSensor(Entity):
    """Representation of an Ombi sensor."""

    def __init__(self, ombi, sensor_type, icon, label):
        """Initialize the sensor."""
        self._state = None
        self._ombi = ombi
        self._sensor_type = sensor_type
        self._icon = icon
        self._label = label
        self._attributes = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Ombi " + self._label

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        attributes = {}
        card_items = []
        if self._attributes is not None:
            for attr in self._attributes:
                card_items.append(attr)

        attributes["data"] = json.dumps(card_items)
        return attributes

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self, **kwargs):
        await self._ombi.update_requests()

        try:
            if self._label == "movies":
                self._state = self._ombi.movie_requests
            elif self._label == "tv":
                self._state = self._ombi.tv_requests
            elif self._label == "music":
                self._state = self._ombi.music_requests
            elif self._label == "pending":
                self._state = self._ombi.total_requests["pending"]
            elif self._label == "approved":
                self._state = self._ombi.total_requests["approved"]
            elif self._label == "available":
                self._state = self._ombi.total_requests["available"]
            elif self._label == "movie_requests_list":
                self._state = "Online"
                self._attributes = self._ombi.movie_requests_list
        except OmbiError as err:
            _LOGGER.warning("Unable to update Ombi sensor: %s", err)
            self._state = None
