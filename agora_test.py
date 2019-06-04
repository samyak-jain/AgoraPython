from agora import AgoraRTC
import asyncio
client = AgoraRTC('6a6faf60981942e98d234a18a4f5313d','channel-x')

async def main():
    await client.open()
    x = await client.get_users()

asyncio.run(main())
