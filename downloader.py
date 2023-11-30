"""a downloader for pixiv pictures"""
import json
import os
import asyncio
import aiohttp
import requests
from datetime import datetime

class PixivDownloader():
  """a downloader for pixiv pictures

  Args:
      params (list): website request parameters.
  """

  def __init__(self, website_params):
    """init PixivDownloader"""
    self._url = 'https://api.lolicon.app/setu/v2'
    self._params = website_params
    self._picture_save_path = './pictures/'
    self._successful_count = 0
    self._fail_count = 0

  def get_url(self, website_params):
    """Send a request and receive a link to an image."""
    try:
      request = requests.get(self._url, params = website_params, timeout = 10)
      content = json.loads(request.content)
      return content['data']
    except requests.Timeout:
      return []

  async def download(self, picture):
    """download picture"""
    try:
      picture_path = f"{self._picture_save_path}{picture['pid']}.{picture['ext']}"
      if os.path.exists(picture_path):
        print(f"圖片已存在: {picture['pid']}.{picture['ext']}")
        return await self.download(self.get_url(self._params))

      print(f"正在下載圖片: {picture['pid']}.{picture['ext']}")
      async with aiohttp.ClientSession(timeout = aiohttp.ClientTimeout(total = 180)) as session:
        async with session.get(picture['urls']['original']) as r:
          with open(f'{self._picture_save_path}{picture["pid"]}.{picture["ext"]}', 'wb') as fd:
            fd.write(await r.read())

      print(f"下載圖片: {picture['pid']}.{picture['ext']} 完成")
      self._successful_count += 1
    except asyncio.TimeoutError:
      print(f"下載圖片: {picture['pid']}.{picture['ext']} 失敗")
      self._fail_count += 1
      os.remove(f'{self.picture_save_path}{picture["pid"]}.{picture["ext"]}')

  def start(self):
    """"start download pictures"""
    if not os.path.exists('./pictures'): os.mkdir('./pictures')
    try:
      pictures = self.get_url(self._params)
      if not pictures:
        return input('沒有獲取到圖片, 按任意鍵退出...')
      else:
        print(f'獲取到 {len(pictures)} 張圖片')

      print('開始下載圖片...')
      time_start = round(datetime.now().timestamp())

      # Non-blocking image download.
      loop = asyncio.new_event_loop()
      asyncio.set_event_loop(loop)
      tasks = [
          asyncio.ensure_future(self.download(picture), loop = loop)
          for picture in pictures
      ]
      loop.run_until_complete(asyncio.wait(tasks))

      time_end = round(datetime.now().timestamp())
      input(f'下載所有圖片完成 ({self._successful_count}/{self._successful_count - self._fail_count}), 耗時: {time_end - time_start} 秒, 按任意鍵退出...')
    except KeyboardInterrupt:
      print('已取消下載')

if __name__ == '__main__':
  print("""
    歡迎使用Pixiv圖片下載器 (API: https://api.lolicon.app/setu/v2)
  """)
  keyword = input('圖片關鍵詞: ')

  # if input('是否包含R18圖片 (y/N): ').lower() == 'y':
  #   r18 = 1
  # else:
  #   r18 = 0
  r18 = 0

  if input('是否包含AI作品 (y/N): ').lower() == 'y':
    ai = 1
  else:
    ai = 0

  num = int(input('獲取數量: '))
  if num > 20:
    num = 20
    print(f'數量過多，將只下載{num}張圖片')

  params = [
    ('keyword', keyword),
    ('r18', r18),
    ('excludeAI', ai),
    ('num', num)
  ]

  pixiv_downloader = PixivDownloader(params)
  pixiv_downloader.start()
    