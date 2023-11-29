"""The NodeRed Conversation integration."""
from __future__ import annotations

from functools import partial
import logging
import aiohttp
import json
import base64
from typing import Literal

import voluptuous as vol

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL

from homeassistant.core import (
    HomeAssistant,
)
from homeassistant.helpers import config_validation as cv, intent
from homeassistant.util import ulid

from .const import (
    CONF_NODERED_URL,
    CONF_NODERED_USER,
    CONF_NODERED_PASS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
SERVICE_GENERATE_IMAGE = "generate_image"

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NodeRed Conversation from a config entry."""

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data[CONF_NODERED_URL]

    conversation.async_set_agent(hass, entry, NodeRedAgent(hass, entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OpenAI."""
    hass.data[DOMAIN].pop(entry.entry_id)
    conversation.async_unset_agent(hass, entry)
    return True


class NodeRedAgent(conversation.AbstractConversationAgent):
    """NodeRed Conversation agent."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.history: dict[str, list[dict]] = {}

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL
    
    async def call_post_request(self, url: str, auth: str, data: dict):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            session.headers.update({"Authorization": f"Basic {auth}"})
            async with session.post(url, data=data) as response:
                return await response.text()

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""
        nodered_url = self.entry.data.get(CONF_NODERED_URL)
        nodered_user = self.entry.data.get(CONF_NODERED_USER)
        nodered_pass = self.entry.data.get(CONF_NODERED_PASS)

        # _LOGGER.debug("Nodered URL %s", nodered_url)

        if user_input.conversation_id in self.history:
            conversation_id = user_input.conversation_id
            messages = self.history[conversation_id]
        else:
            conversation_id = ulid.ulid_now()
            messages = []

        messages.append({"role": "user", "content": user_input.text})

        # _LOGGER.debug("Prompt for %s", messages)

        content = {'content': user_input.text, 'chatid': conversation_id, "messages": json.dumps(messages)}
        _LOGGER.debug("Content sent to NodeRed %s", content)
        nodered_auth = base64.b64encode(f"{nodered_user}:{nodered_pass}".encode()).decode()
        
        try:
            result = await self.call_post_request(nodered_url, nodered_auth, content)
            result = json.loads(result)
        except aiohttp.ClientError:
            _LOGGER.warning("Unable to connect to nodered endpoint")
            result = {
                "finish_reason": "error",
                "message": { "content": "Sorry, unable to connect to NodeRed endpoint. Check settings and try again." }
            }
        except json.decoder.JSONDecodeError as e:
            _LOGGER.warning(f"Something happened: {e}")
            result = {
                "finish_reason": "error",
                "message": { "content": "Sorry, I didn't get a response from NodeRed. Check your logs for possible issues." }
            }

        _LOGGER.debug("Result %s", result)

        response = result["message"]
        _LOGGER.debug("Response %s", response)

        intent_response = intent.IntentResponse(language=user_input.language)

        if result["finish_reason"]  != "error":
            messages.append(response)
            self.history[conversation_id] = messages
            intent_response.async_set_speech(response["content"])
        else:
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                response["content"],
            )


        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )

