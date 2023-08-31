"""Config flow for the Nature Remo platform."""
import asyncio
import logging

import voluptuous as vol
from aiohttp import ClientError, web_exceptions
from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.data_entry_flow import FlowResult
# from homeassistant.components import zeroconf
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import NatureRemoAPI
from .const import (CONF_COOL_TEMP, CONF_HEAT_TEMP, DEFAULT_COOL_TEMP,
                    DEFAULT_HEAT_TEMP, DOMAIN, KEY_MAC, TIMEOUT)

_LOGGER = logging.getLogger(__name__)

class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow."""
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1

    def __init__(self):
        """Initialize the Daikin config flow."""
        self.host = None

    @property
    def schema(self):
        """Return current schema."""
        return vol.Schema(
            {
        # DOMAIN: vol.Schema(
            # {
                # vol.Required(CONF_HOST, default=self.host): str,
                vol.Required(CONF_ACCESS_TOKEN): cv.string,
                vol.Optional(CONF_COOL_TEMP, default=DEFAULT_COOL_TEMP): vol.Coerce(
                    int
                ),
                vol.Optional(CONF_HEAT_TEMP, default=DEFAULT_HEAT_TEMP): vol.Coerce(
                    int
                )
            # }
        # )
    },
    extra=vol.ALLOW_EXTRA,
        )

    async def _create_entry(self, mac, key):
        """Register new entry."""
        if not self.unique_id:
            await self.async_set_unique_id(mac)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=DOMAIN,
            data={         
                # CONF_HOST: host,
                KEY_MAC: mac,
                CONF_ACCESS_TOKEN: key,
            }
        )

    async def _create_device(self, host, key=None):
        """Create device."""
        # BRP07Cxx devices needs uuid together with key
        # if key:
        #     uuid = str(uuid4())
        # else:
        #     uuid = None
        #     key = None

        # if not password:
        #     password = None

        try:
            # try to fetch API to test token
            async with asyncio.timeout(TIMEOUT):
                api = await NatureRemoAPI(key, async_get_clientsession(self.hass))
                response = api.get()

        #     async with asyncio.timeout(TIMEOUT):
        #         device = await Appliance.factory(
        #             host,
        #             async_get_clientsession(self.hass),
        #             key=key,
        #             uuid=uuid,
        #             password=password,
        #         )
        except (asyncio.TimeoutError, ClientError):
            self.host = None
            return self.async_show_form(
                step_id="user",
                data_schema=self.schema,
                errors={"base": "cannot_connect"},
            )
        except web_exceptions.HTTPForbidden:
            return self.async_show_form(
                step_id="user",
                data_schema=self.schema,
                errors={"base": "invalid_auth"},
            )
        # except DaikinException as daikin_exp:
        #     _LOGGER.error(daikin_exp)
        #     return self.async_show_form(
        #         step_id="user",
        #         data_schema=self.schema,
        #         errors={"base": "unknown"},
        #     )
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected error creating device")
            return self.async_show_form(
                step_id="user",
                data_schema=self.schema,
                errors={"base": "unknown"},
            )
            

        mac = response.devices[0].mac_address
        return await self._create_entry(mac, key)


    # async def async_step_user(self, info):
    #     if info is not None:
    #         pass  # TODO: process info

    #     return self.async_show_form(
    #         step_id="user", data_schema=vol.Schema({vol.Required(CONF_ACCESS_TOKEN): cv.string})
    #     )

    async def async_step_user(self, user_input=None):
        """User initiated config flow."""

        _LOGGER.debug("User initiated config flow.")

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=self.schema)
        if user_input.get(CONF_ACCESS_TOKEN):
            # self.host = user_input.get(CONF_HOST)
            return self.async_show_form(
                step_id="user",
                data_schema=self.schema,
                errors={"base": "api_password"},
            )
        return await self._create_device(
            # user_input[CONF_HOST],
            user_input.get(CONF_ACCESS_TOKEN),
        )


    # async def async_step_zeroconf(
    #     self, discovery_info: zeroconf.ZeroconfServiceInfo
    # ) -> FlowResult:
    #     """Prepare configuration for a discovered Nature remo device."""
    #     _LOGGER.debug("Zeroconf user_input: %s", discovery_info)
    #     devices = Discovery().poll(ip=discovery_info.host)
    #     if not devices:
    #         _LOGGER.debug(
    #             (
    #                 "Could not find MAC-address for %s, make sure the required UDP"
    #                 " ports are open (see integration documentation)"
    #             ),
    #             discovery_info.host,
    #         )
    #         return self.async_abort(reason="cannot_connect")
    #     await self.async_set_unique_id(next(iter(devices))[KEY_MAC])
    #     self._abort_if_unique_id_configured()
    #     self.host = discovery_info.host
    #     return await self.async_step_user()
