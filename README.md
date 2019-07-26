# discord-bot
Python Discord Bot

![Image of Puppet](https://github.com/nalabelle/discord-bot/raw/master/puppet.jpg)

## Usage

### From source:

~~~
# Something like this
$ pip install \
     discord \
     geocoder \
     giphypop \
     python-forecastio
$ git clone https://github.com/nalabelle/discord-bot.git ~/discord-bot
$ GOOGLE_API_KEY="KEY1" FORECAST_API_KEY="KEY2" DISCORD_TOKEN="KEY3" python3 ~/discord-bot/bot.py
~~~

### Docker

[Docker Hub](https://hub.docker.com/r/nalabelle/discord-bot/)

~~~
docker create --name=discord-bot \
-e DISCORD_TOKEN=<discord_api_token>
-e GOOGLE_API_KEY=<google_api_key> \
-e FORECAST_API_KEY=<forecast_api_key> \
-e PGID=<gid> -e PUID=<uid> \
-e TZ=<timezone> \
nalabelle/discord-bot
~~~

## Functions
  - weather
  - giphy (because the built in one isn't random enough when you can choose it)
  - status (changes the bot's 'playing' status, limited to manage_webhook permissions)

## Uses
  - [discord.py](https://github.com/Rapptz/discord.py)
  - [giphypop](https://github.com/shaunduncan/giphypop)
  - [geocoder](https://github.com/DenisCarriere/geocoder)
  - [forecastio](https://github.com/ZeevG/python-forecast.io)
