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
        # 1. Resetare buffer modem (Escape) - Verificată în shell pentru deblocare
        _LOGGER.debug("Clearing modem buffer with Escape (\x1B) before dialing")
        await modem.execute_at("\x1B", timeout=2, end_markers=[])
        await asyncio.sleep(1) # Pauză de stabilitate după resetare

        # 2. Curățăm numărul de telefon
        clean_number = phone_number.replace("+", "")
        _LOGGER.debug(f"Dialing +{clean_number}...")

        try:
            # 3. Trimitere comandă de apel (ATD) cu ";" obligatoriu pentru voce
            lines = await modem.execute_at(
                f"{self.at_command}+{clean_number};",
                timeout=10,
                end_markers=["OK", "ERROR", "BUSY", "NO CARRIER", "+CME ERROR"]
            )
            reply = " ".join(lines)
            _LOGGER.debug(f"Modem replied with {reply}")

            if "BUSY" in reply:
                raise HomeAssistantError("Busy")

            if "ERROR" in reply or "NO CARRIER" in reply:
                raise HomeAssistantError(f"Modem replied with an error: {reply}")

            try:
                ended_reason = await self._wait_for_answer(modem)
            except asyncio.TimeoutError:
                ended_reason = EndedReason.NOT_ANSWERED

            # 4. Închidere apel - Logica îmbunătățită pentru eliberarea liniei
            _LOGGER.debug(f"Call finished with reason: {ended_reason}. Starting hangup sequence...")
            
            # Oferim modemului o secundă să proceseze starea finală înainte de CHUP
            await asyncio.sleep(1) 

            # AT+CHUP este comanda specifică pentru a închide toate apelurile active
            _LOGGER.debug("Sending AT+CHUP (Release all calls)...")
            await modem.execute_at("AT+CHUP", timeout=5, end_markers=["OK", "ERROR"])
            
            # ATH ca măsură de siguranță finală pentru a pune "receptorul în furcă"
            _LOGGER.debug("Sending ATH (Hang-up fallback)...")
            await modem.execute_at("ATH", timeout=2, end_markers=["OK", "ERROR"])
            
            _LOGGER.info(f"Call ended and line cleared: {ended_reason}")
            return ended_reason
            
        except asyncio.TimeoutError:
            raise HomeAssistantError(f"Timeout while dialing +{clean_number}")

    async def _wait_for_answer(self, modem: Modem):
        _LOGGER.debug(f"Waiting up to {self._dial_sec} seconds for answer...")

        is_ringing = False
        async with asyncio.timeout(self._dial_sec) as timeout:
            while True:
                # Monitorizăm starea apelului
                lines = await modem.execute_at(
                    "AT+CLCC",
                    timeout=2,
                    end_markers=["OK", "ERROR", "+CME ERROR"]
                )
                reply = " ".join(lines)
                _LOGGER.debug(f"Modem replied with {reply}")

                if not is_ringing and "+CLCC: 1,0,3" in reply:
                    is_ringing = True
                    _LOGGER.info(f"Callee's phone started ringing...")
                    new_deadline = asyncio.get_running_loop().time() + self._call_sec
                    timeout.reschedule(new_deadline)
                    continue

                # Cifra 0 în +CLCC înseamnă apel activ (răspuns)
                if "+CLCC: 1,0,0" in reply:
                    _LOGGER.info("Call answered by target.")
                    return EndedReason.ANSWERED

                if "+CLCC: 1,0" not in reply:
                    return EndedReason.DECLINED

                await asyncio.sleep(1)