from BotUtil import *  
import asyncio

class CustomHandler(MessageHandler):
	def __init__(self, receiveQ, messageQ):
		self.receiveQ = receiveQ
		self.messageQ = messageQ

	async def handleMessage(self, msg):
		if msg.type=='Image':
			imgpath = await msg.getImage()
		if isinstance(msg, FriendMessage):
			reply_str = 'Hello world!'
			reply_msg = self.pack_msg(msg.sender_qq, reply_str, 'F')
			await self.messageQ.put(reply_msg)
		if isinstance(msg, GroupMessage):
			received_str = msg.msg
			if len(received_str)<=2:
				reply_str = msg.msg
				reply_msg = self.pack_msg(msg.group_id, reply_str, 'G')
				await self.messageQ.put(reply_msg)
			elif '我' in received_str:
				reply_str = received_str.replace('我', '你')
				reply_msg = self.pack_msg(msg.group_id, reply_str, 'G')
				await self.messageQ.put(reply_msg)

async def main():
	async with Bot(255930889, '1234567890', 'localhost', 8080, CustomHandler) as bot:
		await bot.mainLoop()

if __name__=='__main__':
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		exit()
