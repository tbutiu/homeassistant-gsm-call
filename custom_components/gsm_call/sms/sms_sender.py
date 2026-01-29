import asyncio
from homeassistant.exceptions import HomeAssistantError
from ..const import _LOGGER
from ..modem import Modem

class SmsSender:
    async def send(self, modem: Modem, phone_number: str, message: str) -> None:
        # 1. Resetare buffer (Escape) - Lecția din shell
        _LOGGER.debug("Sending Escape/Cancel to clear modem buffer")
        await modem.execute_at("\x1B", timeout=2, end_markers=[])
        await asyncio.sleep(1)

        # 2. Setare mod text
        lines = await modem.execute_at("AT+CMGF=1", timeout=5, end_markers=["OK", "ERROR", "+CME ERROR"])
        reply = " ".join(lines)
        if "OK" not in reply:
            _LOGGER.warning(f"Text mode might not be set, but continuing: {reply}")
        
        await asyncio.sleep(1)

        # 3. Trimitere număr - LOGICA "SHELL" (Ignorăm timeout-ul promptului)
        clean_number = phone_number.replace("+", "")
        _LOGGER.debug(f"Initiating SMS to +{clean_number}...")
        
        try:
            # Reducem timeout-ul; pe Huawei, promptul ">" nu vine cu newline, deci va da timeout oricum
            lines = await modem.execute_at(
                f'AT+CMGS="+{clean_number}"',
                timeout=3, 
                end_markers=[">", "ERROR", "+CME ERROR"]
            )
            reply = " ".join(lines)
        except Exception:
            # În shell nu verificăm răspunsul, deci nici aici nu ne oprim dacă e doar timeout
            reply = ""
            _LOGGER.debug("Prompt '>' not detected via newline, proceeding by faith (shell style)")

        if "ERROR" in reply:
            raise HomeAssistantError(f"Modem rejected SMS command: {reply}")

        # 4. PAUZA CRITICĂ (2 secunde) - Exact ca în shell-ul tău
        # Îi oferim modemului timp să deschidă bufferul de text, chiar dacă nu am "văzut" simbolul >
        await asyncio.sleep(2)

        # 5. Trimitere mesaj cu terminatorul Ctrl+Z (\x1A)
        _LOGGER.debug(f"Sending message body: {message}")
        lines = await modem.execute_at(
            message,
            timeout=25,
            end_markers=["+CMGS:", "OK", "ERROR", "+CME ERROR"],
            terminator=Modem.SMS_TERMINATOR,
        )
        reply = " ".join(lines)
        _LOGGER.debug(f"Modem final reply: {reply}")
        
        if "+CMGS" not in reply and "OK" not in reply:
            # Încercăm un reset la final în caz de eșec
            await modem.execute_at("\x1B", timeout=1, end_markers=[])
            raise HomeAssistantError(f"Failed to send SMS body: {reply}")

        _LOGGER.info(f"SMS sent successfully to +{clean_number}")