from sqlalchemy import Update
from telegram.ext import BaseFilter
from aiolimiter import AsyncLimiter

class RateLimitMiddleware(BaseFilter):
    def __init__(self):
        self.limiter = AsyncLimiter(10, 60)

    async def filter(self, update: Update):
        user_id = update.effective_user.id
        async with self.limiter(user_id):
            return True