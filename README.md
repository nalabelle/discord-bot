# discord-bot
Python Discord Bot - Implemented with [discord.py](https://github.com/Rapptz/discord.py)

![Image of Puppet](https://github.com/nalabelle/discord-bot/raw/master/puppet.jpg)

## Functionality
The bot itself only has the basics needed to connect to discord and run. Functionality
can be provided via extensions, such as the ones provided in [discord-bot-extensions](https://github.com/nalabelle/discord-bot-extensions)

## Running
~~~
bot.py
  [--config]  Path to config.yml
  [--data]    Path to writable data directory for storage
~~~

### Configuration

On the initial run, the app will create and save a config.yml. See [data/config.yml](https://github.com/nalabelle/discord-bot/blob/master/data/config.yml) for an example.

### Secrets
Secrets should be stored in local files. The files should be named corresponding to the key specified in the code. In the core app, there's only one key `discord_api_token`. The app will automatically check for secrets in the following paths:

 - /run/secrets
 - /var/run/secrets

You can also specify a path to a secret file by setting an enviroment variable with the key name appended with `_FILE`, as in `DISCORD_API_TOKEN_FILE`.

### From source:

~~~
$ git clone https://github.com/nalabelle/discord-bot.git
$ pip install -r discord-bot/requirements.txt
$ DISCORD_API_TOKEN_FILE=/path/to/token ./discord-bot/bot.py
~~~

### Docker

[Docker Hub](https://hub.docker.com/r/nalabelle/discord-bot/)

#### Docker Compose
~~~
secrets:
  discord_api_token: /path/to/token
services:
  discord-bot:
    image: nalabelle/discord-bot
    secrets:
      - discord_api_token
    volumes:
      - discord-bot:/app/data
~~~

#### Docker Build
~~~
$ git clone https://github.com/nalabelle/discord-bot.git
$ docker build -t discord-bot:latest discord-bot
$ docker run \
  -v /path/to/token:/run/secrets/discord_api_token:ro
  --rm -it discord-bot
~~~

## Example Config
I checked out [discord-bot-extensions](https://github.com/nalabelle/discord-bot-extensions) into
`data/extensions`, and then I let the extensions manage my config as follows

~~~
command_prefix: '!'
discord_log_level: ERROR
extension_filters:
- .git
extensions:
- data.extensions._dependencies
- data.extensions.admin_config
- data.extensions.admin_extension
- data.extensions.status
- data.extensions.weather
log_level: debug
~~~


# discord-bot-extensions
Extensions for https://github.com/nalabelle/discord-bot

# Installation
Clone this repo into your discord-bot `/data/extensions` path, then load the basic extensions into config:
~~~
extensions:
  - data.extensions._dependencies
  - data.extensions.admin_extension
~~~

## Functions

## Dependencies
  - [giphypop](https://github.com/shaunduncan/giphypop)
  - [geocoder](https://github.com/DenisCarriere/geocoder)
  - [forecastio](https://github.com/ZeevG/python-forecast.io)
