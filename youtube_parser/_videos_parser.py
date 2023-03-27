from googleapiclient.discovery import build
import time
import pandas as pd
from datetime import datetime, timedelta

def get_dates():
    dates = []
    for i in pd.read_csv('date.csv')['date'].values:
        date_start = datetime.strptime(i, '%d.%m.%Y').isoformat('T') + 'Z'
        date_end = (datetime.strptime(i, '%d.%m.%Y') + timedelta(days=14)).isoformat('T') + 'Z'
        dates += [{'date_start' : date_start, 'date_end' : date_end}]
    return dates

def parse_searh_item(item, id_):
    flag = 0
    if 'id' in item:
        if 'kind' in item['id']:
            if item['id']['kind'] == 'youtube#video':
                flag = 1
    
    if not flag:
        return None
    
    res = {
        'videoId' : item['id']['videoId'], 
        'title' : item['snippet']['title'],
        'description': item['snippet']['description'],
        'publicationDate' : item['snippet']['publishedAt'],
        'channelId': id_
    }
    
    return res


def search_items(youtube, id_, date_start, date_end):
    videos = []
    
    request = youtube.search().list(
        part='snippet, id',
        channelId=id_,
        maxResults = 50,
        publishedAfter = date_start,
        publishedBefore = date_end
    )
    
    response = request.execute()
    
    
    
    if 'items' in response:
        
        new_video = []
        for i in response['items']:
            new_item = parse_searh_item(i, id_)
            if new_item is not None:
                new_video += [new_item]
        
        print('+ ' + str(len(new_video)) + ' videos')
        videos += new_video
    
    while response.get('nextPageToken', None):
        # to avoid mistakes
        time.sleep(10)
        
        request = youtube.search().list(
            part='snippet, id',
            channelId=id_,
            maxResults = 50,
            publishedAfter = date_start,
            publishedBefore = date_end,
            pageToken=response['nextPageToken'],
        )
        
        response = request.execute()
        
        if 'items' in response:
        
            new_video = []
            for i in response['items']:
                new_item = parse_searh_item(i, id_)
                if new_item is not None:
                    new_video += [new_item]

            print('+ ' + str(len(new_video)) + ' videos')
            videos += new_video
        
    return videos

def get_description(youtube, id_):
    request = youtube.videos().list(
        part="snippet",
        id=id_
    )
    response = request.execute()
    
    res = ''
    res1 = []
    if 'items' in response:
        if 'snippet' in response['items'][0]:
            if 'description' in response['items'][0]['snippet']:
                res = response['items'][0]['snippet']['description']
            if 'tags' in response['items'][0]['snippet']:
                res1 = response['items'][0]['snippet']['tags']
    

    return (res, res1)
    

def enrich_full_description(youtube, videos):
    for i in range(len(videos)):
        desc = get_description(youtube, videos[i]['videoId'])
        videos[i]['fullDescription'] = desc[0]
        videos[i]['tags'] = desc[1]
    
    return videos


def process_channel_videos(youtube, id_):
    videos = []
    
    dates = get_dates()
    for i in dates:
        videos += search_items(youtube, id_, i['date_start'], i['date_end'])
    
        print(i)
    
    videos_ = enrich_full_description(youtube, videos)
    
    return videos_