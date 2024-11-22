from aiogram.filters import BaseFilter
from aiogram.types import Message


class CommaSeparatedDigitsFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return all(part.strip().isdigit() for part in message.text.split(","))