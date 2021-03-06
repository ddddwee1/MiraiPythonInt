import aiofiles
import aiohttp
import json
import logging
import requests
import random 
import os 

logger = logging.getLogger(__name__)

class NetworkError(Exception):
    pass

class Network:
    @staticmethod
    async def post(url : str, data_map : json):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data_map) as response:
                logger.debug(
                    f"Posted [url::{response.url}], "
                    f"requested with [json={data_map}], "
                    f"server responsed [status::{response.status}], "
                    f"[data::{await response.text('utf-8')}]"
                )
                if response.status != 200:
                    logger.info('Post failed.')
                    return False
                data = await response.text(encoding="utf-8")
        return json.loads(data)

    @staticmethod
    async def uploadImage(url, file: str, session, friend_or_group):
        multipart_form_data = (
            ('img', (file, open(file, 'rb'))),
            ('type', (None, friend_or_group)),
            ('sessionKey', (None, session))
        )
        ret = requests.post(url, files=multipart_form_data)
        return ret.text

    @staticmethod
    async def get(url : str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.info('Get failed.')
                    return False
                data = await response.text(encoding="utf-8")
        return json.loads(data)

    @staticmethod
    async def downloadImage(url):
        if not os.path.exists('./temp/'):
            os.mkdir('./temp/')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                idx = random.randint(0, 10000)
                if resp.status == 200:
                    f = await aiofiles.open('./temp/%d.png'%idx, mode='wb')
                    await f.write(await resp.read())
                    await f.close()
                    return './temp/%d.png'%idx
        print('Download error.')
        return None 