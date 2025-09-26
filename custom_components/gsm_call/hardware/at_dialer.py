# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio

from homeassistant.exceptions import HomeAssistantError

from ..const import _LOGGER, EndedReason
from ..modem import Modem


class ATDialer:
    at_command = "ATD"

    def __init__(self, dial_timeout_sec: int, call_duration_sec: int):
        self._dial_sec = dial_timeout_sec
        self._call_sec = call_duration_sec

    async def dial(self, modem: Modem, phone_number: str) -> EndedReason:
        _LOGGER.debug(f"Dialing +{phone_number}...")
        try:
            lines = await self._execute_at(
                modem,
                f"{self.at_command}+{phone_number};",
                timeout=10,
                end_markers=["OK", "ERROR", "BUSY", "NO CARRIER"]
            )
            reply = "\n".join(lines)
            _LOGGER.debug(f"Modem replied with {reply}")

            if "BUSY" in reply:
                raise HomeAssistantError("Busy")

            if "ERROR" in reply or "NO CARRIER" in reply:
                raise HomeAssistantError(f"Modem replied with an error: {reply}")

            try:
                ended_reason = await self._wait_for_answer(modem)
            except asyncio.TimeoutError:
                ended_reason = EndedReason.NOT_ANSWERED

            _LOGGER.debug("Hanging up...")
            modem.writer.write(b"AT+CHUP\r\n")
            _LOGGER.info(f"Call ended: {ended_reason}")

            return ended_reason
        except asyncio.TimeoutError:
            raise HomeAssistantError(f"Timeout while dialing +{phone_number}")

    async def _wait_for_answer(self, modem: Modem):
        _LOGGER.debug(f"Waiting up to {self._dial_sec} seconds for answer...")

        is_ringing = False
        async with asyncio.timeout(self._dial_sec) as timeout:
            while True:
                # Provisioning:     +CLCC: 1,0,2…
                # Phone is ringing: +CLCC: 1,0,3…
                # Answered:         +CLCC: 1,0,0…
                # Declined:         Nothing, OK only
                lines = await self._execute_at(
                    modem,
                    "AT+CLCC",
                    timeout=2,
                    end_markers=["OK", "ERROR"]
                )
                reply = "\n".join(lines)
                _LOGGER.debug(f"Modem replied with {reply}")

                if not is_ringing and "+CLCC: 1,0,3" in reply:
                    is_ringing = True
                    _LOGGER.info(
                        f"Callee's phone started ringing, waiting for {self._call_sec} seconds..."
                    )
                    new_deadline = asyncio.get_running_loop().time() + self._call_sec
                    timeout.reschedule(new_deadline)
                    continue

                if "+CLCC: 1,0,0" in reply:
                    return EndedReason.ANSWERED

                if "+CLCC: 1,0" not in reply:
                    return EndedReason.DECLINED

                await asyncio.sleep(.5)

    async def _execute_at(self, modem: Modem, command: str, timeout: float, end_markers: list[str]) -> list[str]:
        self._send_command(modem, command)
        return await self._read_response(modem, timeout, end_markers)

    def _send_command(self, modem: Modem, command: str) -> None:
        _LOGGER.debug(f"Sending command: {command}")
        modem.writer.write(f"{command}\r\n".encode())
        # No await drain() needed here as it's synchronous, but for completeness:
        # await modem.writer.drain()  # Optional, as write is buffered

    async def _read_response(self, modem: Modem, timeout: float, end_markers: list[str]) -> list[str]:
        lines = []
        async with asyncio.timeout(timeout):
            while True:
                line = await modem.reader.readline()
                decoded = line.decode(errors='ignore').strip()
                if not decoded:
                    continue

                lines.append(decoded)
                if any(decoded == m or decoded.startswith(m) for m in end_markers):
                    return lines
