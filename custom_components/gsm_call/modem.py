# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio as aio

from .const import _LOGGER

READ_LIMIT = 2**16  # 64 KiB


class Modem:
    def __init__(self, reader: aio.StreamReader, writer: aio.StreamWriter):
        self.reader = reader
        self.writer = writer

    async def execute_at(self, command: str, timeout: float, end_markers: list[str]) -> list[str]:
        self.send_command(command)
        return await self._read_response(timeout, end_markers)

    def send_command(self, command: str) -> None:
        _LOGGER.debug(f"Sending command: {command}")
        self.writer.write(f"{command}\r\n".encode())
        # No await drain() needed here as it's synchronous, but for completeness:
        # await modem.writer.drain()  # Optional, as write is buffered

    async def _read_response(self, timeout: float, end_markers: list[str]) -> list[str]:
        lines = []
        async with aio.timeout(timeout):
            while True:
                line = await self.reader.readline()
                decoded = line.decode(errors='ignore').strip()
                if not decoded:
                    continue

                lines.append(decoded)
                if any(decoded == m or decoded.startswith(m) for m in end_markers):
                    return lines
