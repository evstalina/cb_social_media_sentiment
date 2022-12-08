# Парсинг каналов

1. Добавление ключей для tg.

Создаем файл `tg_keys.yaml` в корневой директории проекта в следующем формате. Так же есть пример `tg_keys_examples.yaml`
```
keys:
  - api_id: ""
    api_hash: ""
    phone_number: "+..."
  - api_id: ""
    api_hash: ""
    phone_number: "+..."
  ....  
```

2. Дамп постов.

```
python3 posts_parser.py -s 7d -b 100 -d date.csv -a +7******** -c moscowmap bazabazon
```

- -d, --dates - даты за которые нужны посты
- -a, --accaunt_n - номер аккаунта, который будет использоваться
- -с, --channels - список каналов для парсинга
- -s, --span - временной интервал для прасинга
- -b, --batch - кол-во постов для скачивания за один запрос(max=100)

Сохраняет посты в директорию `out_posts`.

3. Фильтрация постов.

```
python3 filter_post.py -p out_posts -f outrussianmacro.csv -w filter_words.csv
```

- -p, --path_dir - путь до директории 
- -f, --files - список файлов с постами
- -w, --words_filter - список слов для фильтрации

Сохраняет отфильтрованные посты в директорию `out_posts_filter`.


4. Дамп комментариев.

```
python3 comment_parcer.py -p /out_posts_filter -f moscowmap_filter.csv bazabazon_filter.csv -b 100 -a +7********
```
- -p, --path_dir - путь до директории 
- -f, --files - список файлов с постами
- -a, --accaunt_n - номер аккаунта, который будет использоваться
- -b, --batch - кол-во постов для скачивания за один запрос(max=100)

Сохраняет комментарии в директорию `out_comments`.