import os

from motor.motor_asyncio import AsyncIOMotorClient

DATABASE_NAME = os.environ.get("MONGO_DATABASE", "yorigin")

client = AsyncIOMotorClient()
db = client[DATABASE_NAME]

# # 버전 정보 가져오기
# import asyncio
# async def print_mongo_version() -> None:
#     status = await client.test.command("serverStatus")
#     print(status["version"])
#     asyncio.run(print_mongo_version())
