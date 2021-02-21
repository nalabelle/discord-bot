from unittest import mock
import asynctest
import pytest
from .channel_notifier import ChannelNotifier

@pytest.mark.asyncio
async def test_on_guild_channel_update():
    channel_notifier = ChannelNotifier(None)

    old_channel = mock.MagicMock()
    old_channel.name = 'Old'
    new_channel = mock.MagicMock()
    new_channel.name = 'New'
    new_channel.send = asynctest.CoroutineMock()

    await channel_notifier.on_guild_channel_update(old_channel, new_channel)
    new_channel.send.assert_called_once()
    send_call = new_channel.send.call_args_list[0]
    expected_content = {'content':
            '_Channel name changed from_ "{}" _to_ "{}".'.format(
            old_channel.name, new_channel.name)
            }
    assert send_call == (expected_content,)
