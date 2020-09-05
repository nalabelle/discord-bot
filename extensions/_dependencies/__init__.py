import subprocess
import sys
import logging
from pathlib import Path
from discord.ext import commands

log = logging.getLogger('_dependencies')

def install_deps():
    packages = str(Path('data/ext-site-packages').resolve())
    requirements = str(Path('data/extensions/requirements.txt').resolve())
    cache_dir = str(Path('data/.pip-cache').resolve())
    install_cmd = [
        sys.executable, "-m", "pip", "install",
        "--quiet",
        "--cache-dir", cache_dir,
        "--upgrade",
        "-t", packages,
        "-r", requirements]
    log.info("running {}".format(" ".join(install_cmd)))
    output = subprocess.check_output(install_cmd, stderr=subprocess.STDOUT)
    log.info(output)
    if packages not in sys.path:
        sys.path.append(packages)
    log.debug("\n".join(sys.path))
    return output

class Dependencies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def upgrade(self, channel):
        o = install_deps
        await channel.send('Deps updated: ```{}```'.format(o))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def deps(self, ctx):
        await self.upgrade(ctx.message.channel)
        await ctx.message.channel.send('Updating..')

install_deps()
def setup(bot):
    bot.add_cog(Dependencies(bot))

def teardown(bot):
    bot.remove_cog('Dependencies')

