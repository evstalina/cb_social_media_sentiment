import datetime
import pandas as pd

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest


api_id = 0
api_hash = ''
phone_number = ''

def get_posts(client, peer, limit=0, offset_id=0, add_offset=0, max_id=0, min_id=0, hash=0, offset_date=None):
    return client(GetHistoryRequest(
        peer=peer,
        limit=limit,
        offset_id=offset_id,
        add_offset=add_offset,
        max_id=max_id,
        min_id=min_id,
        hash=hash,
        offset_date=offset_date)).messages
    

def get_min_max_id_for_span(date, span, client, channel_username):
    channel_entity=client.get_entity(channel_username)
    delta = date + datetime.timedelta(days=span+1)
    posts = get_posts(client, channel_entity, offset_date=date, limit=1)
    if len(posts) == 0:
        print("No message for channel [{}] at date {}".format(channel_username, date.strftime("%d/%m/%Y")))
        return 0, 0

    min_id = posts[0].id
    
    posts = get_posts(client, channel_entity, offset_date=delta, limit=1)
    if len(posts) == 0:
        print("No message for channel [{}] at date {}".format(channel_username, date.strftime("%d/%m/%Y")))
        return 0, 0

    max_id = posts[0].id
    return min_id+1, max_id

def convert_messag(message):
    return {"text": message.message, "date": message.date, "id": message.id}

def convert_messages(messages):
    return [convert_messag(m) for m in messages]
    
def get_posts_in_span(date, span, client, channel_username, batch=100):
    channel_entity=client.get_entity(channel_username)
    res = []
    min_id, max_id = get_min_max_id_for_span(date, span, client, channel_username)
    for i in range(min_id, max_id, batch):
        mx_id = i + batch if i + batch <= max_id else max_id
        posts = get_posts(client, channel_entity, min_id=i, max_id=mx_id, offset_id=mx_id, limit=batch)
        res += convert_messages(posts)
    return res

if __name__ == "__main__":
    client = TelegramClient(phone_number, api_id, api_hash)
    client.start()

    channel_username='breakingmash'
    date = datetime.datetime(2022, 3, 18)

    res = get_posts_in_span(date, 7, client, channel_username)

    df = pd.DataFrame(res)
    df = df.sort_values(by=['date'])
    df.to_csv("out.parse")