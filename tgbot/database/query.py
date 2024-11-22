from sqlalchemy import delete 
from database.engine import session_maker
from database.models import User


async def save_to_database(title, url, category, priority, timestamp):
    async with session_maker() as session: 
        obj = User(
            title=title,
            url=url,
            category=category,
            priority=priority,
            timestamp=timestamp
        )
        session.add(obj)
        await session.commit()  



async def delete_from_database(title: str):
    async with session_maker() as session: 
        query = delete(User).where(User.title == title)
        await session.execute(query)
        await session.commit()
