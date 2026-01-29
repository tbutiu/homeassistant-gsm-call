import asyncio
from homeassistant.exceptions import HomeAssistantError
from ..const import _LOGGER
from ..modem import Modem

class SmsSender:
    async def send(self, modem: Modem, phone_number: str, message: str) -> None:
        # 1. Trimitere CANCEL (\x1B) pentru a debloca portul, exact ca în shell
        _LOGGER.debug("Sending Escape/Cancel to clear modem buffer")
        await modem.execute_at("\x1B", timeout=2, end_markers=[])
        await asyncio.sleep(1) # Pauza necesară pentru procesare

        # 2. Setare mod text
        lines = await modem.execute_at("AT+CMGF=1", timeout=5, end_markers=["OK", "ERROR", "+CME ERROR"])
        reply = " ".join(lines)
        _LOGGER.debug(f"Modem replied with {reply}")
        if "OK" not in reply:
            raise HomeAssistantError(f"Failed to set text mode: {reply}")
        
        await asyncio.sleep(1) # Pauza după setarea modului

        # 3. Trimitere comandă AT+CMGS (pregătim numărul)
        # Curățăm numărul pentru a evita situația "++"
        clean_number = phone_number.replace("+", "")
        lines = await modem.execute_at(
            f'AT+CMGS="+{clean_number}"',
            timeout=10,
            end_markers=[">", "ERROR", "+CME ERROR"]
        )
        reply = " ".join(lines)
        _LOGGER.debug(f"Modem replied with {reply}")
        
        if ">" not in reply:
            # Dacă nu primim promptul, trimitem iar un Cancel pentru a nu bloca modemul
            await modem.execute_at("\x1B", timeout=1, end_markers=[])
            raise HomeAssistantError(f"Failed to initiate SMS (no prompt >): {reply}")

        # 4. Pauză critică de 2 secunde înainte de a trimite corpul mesajului
        # Aceasta îi oferă timp modemului Huawei să deschidă fereastra de editare
        await asyncio.sleep(2)

        # 5. Trimitere mesaj cu terminatorul Ctrl+Z (\x1A)
        lines = await modem.execute_at(
            message,
            timeout=30,
            end_markers=["+CMGS:", "OK", "ERROR", "+CME ERROR"],
            terminator=Modem.SMS_TERMINATOR,
        )
        reply = " ".join(lines)
        _LOGGER.debug(f"Modem replied with {reply}")
        
        if "+CMGS" not in reply and "OK" not in reply:
            raise HomeAssistantError(f"Failed to send SMS body: {reply}")

        _LOGGER.info(f"SMS sent successfully to +{clean_number}")
