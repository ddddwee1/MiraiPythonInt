from Network import Network 
import asyncio
import time 

class MessageHandler():
	def __init__(self, receiveQ, messageQ):
		self.receiveQ = receiveQ
		self.messageQ = messageQ

	async def handleMessage(self, msg):
		return 1  

	async def mainLoop(self):
		print('Recursively processing the message...')
		while True:
			msg = await self.receiveQ.get()
			# print(msg)
			await self.handleMessage(msg)

	def pack_msg(self, target, reply_str, target_type):
		assert target_type in ['G','F'] # G for group; F for friend
		data = {'message': reply_str, 'target': target, 'target_type':target_type}
		return data 

class Bot():
	def __init__(self, qqnum, auth_key, ip, port, HandlerClass):
		self.qqnum = qqnum
		self.auth_key = auth_key
		self.ip = ip 
		self.port = port 
		self.messageQ = asyncio.Queue()
		self.receiveQ = asyncio.Queue()
		self.handler = HandlerClass(self.receiveQ, self.messageQ)

	async def addMessage(self, message, target, target_type):
		assert target_type in ['G','F']
		data = {'message': message, 'target': target, 'target_type':target_type}
		await self.messageQ.put(data)

	async def sendBufferedMessagesLoop(self):
		print('Listening to outward messages...')
		while True:
			await asyncio.sleep(0.5)
			m = await self.messageQ.get()
			if m['target_type'] == 'G':
				asyncio.create_task(self.sendGroupMessage(m['target'], m['message']))
			elif m['target_type'] == 'F':
				asyncio.create_task(self.sendFriendMessage(m['target'], m['message']))

	async def __aenter__(self):
		ret = await Network.post(f'http://{self.ip}:{self.port}/auth', {'authKey': self.auth_key})
		if self.retValue(ret)==0:
			print('Connected')
			self.session = ret['session']
			print('Session:', self.session)
		else:
			print('Connection error')

		ret = await Network.post(f'http://{self.ip}:{self.port}/verify', {'sessionKey':self.session, 'qq':self.qqnum})
		if self.retValue(ret)!=0:
			print('Error verify')
			print(ret)
		return self 

	def retValue(self, ret):
		# may not have code, so write an independent func 
		try: return ret['code']
		except: return 'error'

	async def messageReceivingLoop(self):
		print('Listening to coming messages...')
		while True:
			events = await Network.get(f'http://{self.ip}:{self.port}/fetchMessage?sessionKey={self.session}&count=10')
			print(events, type(events))
			messages = parse_messages(events)
			for m in messages:
				await self.receiveQ.put(m)
			await asyncio.sleep(1)

	async def mainLoop(self):
		asyncio.create_task(self.messageReceivingLoop())
		asyncio.create_task(self.sendBufferedMessagesLoop())
		await self.handler.mainLoop()

	async def releaseSession(self):
		if self.session != '':
			print('Exiting...')
			ret = await Network.post(f'http://{self.ip}:{self.port}/release', {
				"sessionKey": self.session,
				"qq": self.qqnum
			})
			if self.retValue(ret) == 0: 
				print('Session released.')
			else: 
				print(f'Session releasing failed, ret value: {self.retValue(ret)}.')

	async def __aexit__(self, *excinfo):
		await self.releaseSession()

	def handleError(self, ret):
		try:
			val = ret['code']
			errmsg = ret['msg']
			if val!=0:
				print(f'Error occured. Code: {val}. Message: {errmsg}')
		except:
			print(ret)
			print('Incomplete ret. (No error code)')

	async def sendFriendMessage(self, target, message, quote=None):
		data = {'sessionKey': self.session, 'target':target, 'messageChain':[{'type':'Plain', 'text':message}]}
		if quote is not None:
			data['quote'] = quote
		ret = await Network.post(f'http://{self.ip}:{self.port}/sendFriendMessage', data)
		self.handleError(ret)
		return self.retValue(ret)

	async def sendGroupMessage(self, target, message, quote=None):
		data = {'sessionKey': self.session, 'target':target, 'messageChain':[{'type':'Plain', 'text':message}]}
		if quote is not None:
			data['quote'] = quote
		ret = await Network.post(f'http://{self.ip}:{self.port}/sendGroupMessage', data)
		self.handleError(ret)
		return self.retValue(ret)

def parse_messages(event):
	msgs = []
	if event['code']==0:
		for msg in event['data']:
			if msg['type']=='FriendMessage':
				msgs.append(FriendMessage(msg['messageChain'], msg['sender']))
			elif msg['type']=='GroupMessage':
				msgs.append(GroupMessage(msg['messageChain'], msg['sender']))
	return msgs

# 这里是\r回车，没有\n
class FriendMessage():
	def __init__(self, msg_data, sender):
		for m in msg_data:
			if m['type']=='Source':
				self.msg_id = m['id']
			if m['type']=='Plain':
				self.msg = m['text']
				self.type = m['type']
			if m['type']=='Image':
				self.msg = m['url']
				self.type = m['type']
		self.sender_qq = sender['id']
		self.sender_name = sender['nickname']
		self.time = time.time()

	async def getImage(self):
		if self.type == 'Image':
			imgpath = await Network.downloadImage(self.msg)
		else:
			print('Cannot process a non-image message.')
			imgpath = None 
		return imgpath

class GroupMessage():
	def __init__(self, msg_data, sender):
		for m in msg_data:
			if m['type']=='Source':
				self.msg_id = m['id']
			if m['type']=='Plain':
				self.msg = m['text']
				self.type = m['type']
			if m['type']=='Image':
				self.msg = m['url']
				self.type = m['type']
		self.sender_qq = sender['id']
		self.sender_name = sender['memberName']
		self.group_id = sender['group']['id']
		self.group_name = sender['group']['name']
		self.time = time.time()

	async def getImage(self):
		if self.type == 'Image':
			imgpath = await Network.downloadImage(self.msg)
		else:
			print('Cannot process a non-image message.')
			imgpath = None 
		return imgpath
