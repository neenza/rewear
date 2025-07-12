import asyncio
from init_db import init_db
from add_demo_items import add_demo_items

async def setup_demo_db():
    # Initialize the database first
    await init_db()
    # Then add demo items
    await add_demo_items()

if __name__ == "__main__":
    asyncio.run(setup_demo_db())
