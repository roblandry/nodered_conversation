"""Config flow for NodeRed Conversation integration."""
from __future__ import annotations

import logging
import types
from types import MappingProxyType
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_NODERED_URL,
    CONF_NODERED_USER,
    CONF_NODERED_PASS,
    DEFAULT_NODERED_URL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NODERED_URL): str,
        vol.Optional(CONF_NODERED_USER): str,
        vol.Optional(CONF_NODERED_PASS): str,
    }
)

DEFAULT_OPTIONS = types.MappingProxyType(
    {
        CONF_NODERED_URL: "https://noderedip:1880/endpoint/gpt",
        CONF_NODERED_USER: "username",
        CONF_NODERED_PASS: "password",
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    return


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NodeRed Conversation."""
    # TODO remove config flow and use options

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
    #     """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            await validate_input(self.hass, user_input)
    #         # except error.APIConnectionError:
    #         #     errors["base"] = "cannot_connect"
    #         # except error.AuthenticationError:
    #         #     errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            pass
    #         #     _LOGGER.exception("Unexpected exception")
    #         #     errors["base"] = "unknown"
        else:
            return self.async_create_entry(title="NodeRed Conversation", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlow(config_entry)


# TODO: options currently not used
class OptionsFlow(config_entries.OptionsFlow):
    """NodeRed config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="NodeRed Conversation", data=user_input)
        schema = nodered_config_option_schema(self.config_entry.options)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
        )


def nodered_config_option_schema(options: MappingProxyType[str, Any]) -> dict:
    """Return a schema for NodeRed completion options."""
    if not options:
        options = DEFAULT_OPTIONS
    return {
        vol.Required(
            CONF_NODERED_URL,
            description={"suggested_value": options.get(CONF_NODERED_URL, DEFAULT_NODERED_URL)},
            default=DEFAULT_NODERED_URL,
        ): str,
        vol.Optional(
            CONF_NODERED_USER,
            description={"suggested_value": ""},
            default="",
        ): str,
        vol.Optional(
            CONF_NODERED_PASS,
            description={"suggested_value": ""},
            default="",
        ): str,
    }
