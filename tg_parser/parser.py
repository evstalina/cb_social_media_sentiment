import yaml
import datetime
import pandas as pd

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest, GetRepliesRequest
from telethon.tl.functions.channels import GetFullChannelRequest


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
    n_comments = 0
    max_offset = 0
    if message.replies is not None:
        n_comments = message.replies.replies
        max_offset = message.replies.max_id
    return {
        "text": message.message,
        "date": message.date,
        "id": message.id,
        "n_comments": n_comments,
        "max_offset": max_offset,
        }

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
    if len(res) == 0:
        return 0, len(res)

    df = pd.DataFrame(res)
    df['channel_username'] = channel_username
    return df, len(res)

def get_client(number):
    with open("../tg_keys.yaml", 'r') as f:
        tg_keys = yaml.safe_load(f)
        tg_key = {}
        for k in tg_keys["keys"]:
            if k["phone_number"] == number:
                tg_key = k
                break
        return TelegramClient(tg_key["phone_number"], tg_key["api_id"], tg_key["api_hash"])

def get_replies(client, peer, msg_id=0, limit=0, offset_id=0, add_offset=0, max_id=0, min_id=0, hash=0, offset_date=None):
    return client(GetRepliesRequest(
        peer=peer,
        msg_id=msg_id, #channel post id
        offset_id=offset_id,
        offset_date=offset_date,
        add_offset=add_offset,
        limit=limit,
        max_id=max_id,
        min_id=min_id,
        hash=hash
    )).messages


def convert_comment(comment, channel_username, post_id):
    return {
        "text": comment.message,
        "date": comment.date,
        "channel_username": channel_username,
        "post_id": post_id,
        "id": comment.id,
        }

def convert_comments(comments, channel_username, post_id):
    return [convert_comment(c, channel_username, post_id) for c in comments]


def get_comments(client, channel_username, post_id, batch=100):
    channel_entity=client.get_entity(channel_username)
    p = get_posts(client, channel_entity, limit=1, offset_id=post_id+1)[-1]
    if p.replies is None:
        return []
    
    max_offset = p.replies.max_id
    n_comments = p.replies.replies
    print(max_offset, n_comments)
    res = []
    
    for i in range(int(n_comments/batch)+1):
        comments = get_replies(client, channel_entity, msg_id=post_id, limit=100, offset_id=max_offset+1)
        max_offset = comments[-1].id - 1
        res += convert_comments(comments, channel_username, post_id)
    
    return pd.DataFrame(res)