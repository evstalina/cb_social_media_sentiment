import time
import datetime
import pandas as pd

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest

api_id =
api_hash = ''
phone_number = '+79303602290'


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
    channel_entity = client.get_entity(channel_username)
    delta = date + datetime.timedelta(days=span + 1)
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
    return min_id + 1, max_id


def convert_messag(message):
    return {"text": message.message, "date": message.date, "id": message.id}


def convert_messages(messages):
    return [convert_messag(m) for m in messages]


def get_posts_in_span(date, span, client, channel_username, batch=100):
    channel_entity = client.get_entity(channel_username)
    res = []
    min_id, max_id = get_min_max_id_for_span(date, span, client, channel_username)
    for i in range(min_id, max_id, batch):
        mx_id = i + batch if i + batch <= max_id else max_id
        posts = get_posts(client, channel_entity, min_id=i, max_id=mx_id, offset_id=mx_id, limit=batch)
        res += convert_messages(posts)
    return res


mega_df = pd.DataFrame([])
channels = ['moscowmap', 'u_now', 'DavydovIn', 'bbbreaking','rusich_army',
            'voynareal', 'rezident_ua', 'nexta_live', 'varlamov_news', 'readovkanews', 'epoddubny', 'bazabazon',
            'neoficialniybezsonov', 'pravdadirty', 'vysokygovorit', 'dvachannel', 'meduzalive', 'milchronicles',
            'moscowach', 'Cbpub', 'voenacher', 'topor', 'opersvodki', 'shot_shot', 'grey_zone', 'UkraineNow',
            'milinfolive', 'itsdonetsk', 'lentachold', 'AteoBreaking', 'ru2ch_news', 'zhest_belgorod', 'zerkalo_io']

dates = ['09.02.2018', '23.03.2018', '27.04.2018', '15.06.2018', '27.07.2018', '14.09.2018', '26.09.2018', '14.12.2018',
         '08.02.2019', '22.03.2019', '26.04.2019', '14.06.2019', '26.07.2019', '06.09.2019', '25.10.2019', '13.12.2019',
         '07.02.2020', '20.03.2020', '24.04.2020', '19.06.2020', '24.07.2020', '18.09.2020', '23.10.2020', '18.12.2020',
         '12.02.2021', '19.03.2021', '23.04.2021', '11.06.2021', '23.07.2021', '10.09.2021', '22.10.2021', '17.12.2021',
         '11.02.2022', '28.02.2022', '18.03.2022', '08.04.2022', '29.04.2022', '26.05.2022', '10.06.2022', '22.07.2022', '16.09.2022', '28.10.2022']

client = TelegramClient(phone_number, api_id, api_hash)
client.start()

for channel_username in channels:
    for date in dates:
        if __name__ == "__main__":

            date = datetime.datetime(int(date[6:]), int(date[3:5]), int(date[:2]))

            res = get_posts_in_span(date, 7, client, channel_username)

            df = pd.DataFrame(res)

            #костыль, чтобы код не ломался при отсутсвии сообщений
            if str(df.shape) != '(0, 0)':
                df = df.sort_values(by=['date'])
            df['channel_username'] = channel_username

            mega_df = pd.concat([mega_df, df])

            time.sleep(10)

            #прогрессбар лень делать
            print(date, channel_username)
    mega_df.to_csv("out" + channel_username + ".csv")
