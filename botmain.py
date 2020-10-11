from BotUtil import *  
import asyncio

async def message_handler(bot, msg):
	if msg.type=='Image':
		imgpath = await msg.getImage()
	if isinstance(msg, FriendMessage):
		reply_str = 'Hello world!'
		await bot.sendFriendMessage(msg.sender_qq, reply_str)
	if isinstance(msg, GroupMessage):
		reply_str = 'Hello worlD'
		await bot.sendGroupMessage(msg.group_id, reply_str)

async def main():
	async with Bot(255930889, '1234567890', 'localhost', 8080) as bot:
		bot.registerEventHandler(message_handler)
		await bot.mainLoop()

if __name__=='__main__':
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		exit()
