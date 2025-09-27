# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio

from ..const import _LOGGER, EndedReason
from ..modem import Modem
from .at_dialer import ATDialer


class ZTEDialer(ATDialer):
    async def dial(self, modem: Modem, phone_number: str) -> EndedReason:
        _LOGGER.debug("Sending ZTE's magic AT%icscall=1,0 command...")
        modem.send_command("AT%icscall=1,0")
        await asyncio.sleep(.5)

        return await super().dial(modem, phone_number)
