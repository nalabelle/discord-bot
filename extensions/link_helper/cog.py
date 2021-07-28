"""
Discord Cog for Link Helper
"""

import logging
import re
from abc import ABC

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from requests.exceptions import HTTPError, Timeout
from urllib3.exceptions import NewConnectionError

log = logging.getLogger("LinkHelper")
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)


HTTP_TIMEOUT = 1
HTTP_RETRIES = 2
HTTP_RETRY_EXCEPTIONS = (HTTPError, Timeout, NewConnectionError)

TWITTER_PREFIX = r"https?://(?:[\w]+\.)*twitter\.com"
TWITTER_RE = re.compile(r"{}/[\w/]+".format(TWITTER_PREFIX), re.I)
TWITTER_HOST_RE = re.compile(r"^{}".format(TWITTER_PREFIX), re.I)
TWITTER_API = "https://twiiit.com"

IMGUR_PREFIX = r"https?://imgur.com"
IMGUR_RE = re.compile(r"{}/[\w/]+".format(IMGUR_PREFIX), re.I)
IMGUR_IMAGE_RE = re.compile(r"^{}/([\w]+)$".format(IMGUR_PREFIX), re.I)
IMGUR_IMAGE_API = "https://api.imgur.com/3/image/{}?client_id=546c25a59c58ad7"


class WebClient(ABC):  # pylint: disable=too-few-public-methods
    """WebClient base class for HTTP Classes"""

    def _fetch(self, url):
        res = requests.get(url, timeout=HTTP_TIMEOUT)
        res.raise_for_status()
        return res

    def fetch(self, url):
        exception = None
        for _ in range(HTTP_RETRIES):
            try:
                return self._fetch(url)
            except requests.RequestException as err:
                if isinstance(err, HTTP_RETRY_EXCEPTIONS):
                    exception = err
                else:
                    raise
        if exception:
            raise exception
        return None


class Twitter(WebClient):
    """Twitter API Client"""

    def gallery_count(self, url):
        url = TWITTER_HOST_RE.sub(TWITTER_API, url)
        log.debug(url)
        try:
            res = self.fetch(url)
        except requests.RequestException as err:
            log.error(err)
            return 0
        soup = BeautifulSoup(res.text, features="html.parser")
        meta = soup.find_all("meta", property="og:image")
        return len(meta)


class Imgur(WebClient):
    """Imgur API Client"""

    def has_sound(self, url):
        url = IMGUR_IMAGE_API.format(url)
        log.debug(url)
        try:
            res = self.fetch(url)
        except requests.RequestException as err:
            log.error(err)
            return False
        info = res.json()
        if info.get("data") and info.get("data").get("has_sound"):
            return True
        return False


class LinkHelper(commands.Cog, name="LinkHelper"):
    """Link Helper

    Helps identify imgur posts with sound and twitter posts with galleries
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle new Message"""
        if self.bot.user.id == message.author.id:
            return True
        for match in TWITTER_RE.findall(message.content):
            if len(match) == 0:
                continue
            if Twitter().gallery_count(match) > 1:
                await message.add_reaction("🖼")
        for match in IMGUR_IMAGE_RE.findall(message.content):
            if len(match) == 0:
                continue
            if Imgur().has_sound(match):
                await message.add_reaction("🔊")


def setup(bot):
    """Cog creation"""
    bot.add_cog(LinkHelper(bot))


def teardown(bot):
    """Cog teardown"""
    bot.remove_cog("LinkHelper")
