# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from homeassistant.exceptions import HomeAssistantError

from ..const import _LOGGER
from ..modem import Modem


class SmsSender:
    async def send(self, modem: Modem, phone_number: str, message: str) -> None:
        # Set text mode
        lines = await modem.execute_at("AT+CMGF=1", timeout=5, end_markers=["OK", "ERROR", "+CME ERROR"])
        reply = " ".join(lines)
        _LOGGER.debug(f"Modem replied with {reply}")
        if "ERROR" in reply:
            raise HomeAssistantError(f"Failed to set text mode: {reply}")

        # Send command and wait for prompt
        lines = await modem.execute_at(
            f'AT+CMGS="+{phone_number}"',
            timeout=10,
            end_markers=[">", "ERROR", "+CME ERROR"]
        )
        reply = " ".join(lines)
        _LOGGER.debug(f"Modem replied with {reply}")
        if ">" not in reply:
            raise HomeAssistantError(f"Failed to initiate SMS: {reply}")

        # Send message body with \r + Ctrl+Z terminator
        lines = await modem.execute_at(
            message,
            timeout=30,
            end_markers=["+CMGS:", "OK", "ERROR", "+CME ERROR"],
            terminator=Modem.SMS_TERMINATOR,
        )
        reply = " ".join(lines)
        _LOGGER.debug(f"Modem replied with {reply}")
        if "+CMGS" not in reply:
            raise HomeAssistantError(f"Failed to send SMS: {reply}")

        _LOGGER.info(f"SMS sent to +{phone_number}")
