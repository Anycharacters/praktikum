import sqlite3
import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def extract():
    """
    extract data from sql-db
    :return:
    """
    with sqlite3.connect("db.sqlite") as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT 
                                name
                            FROM 
                                sqlite_schema
                            WHERE 
                                type ='table' 
                            AND 
                                name 
                            IN ('movies',
                                'movie_actors', 
                                'actors', 
                                'writers');""")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"SELECT * FROM {table[0]} LIMIT 1")
            #print(table[0],cursor.fetchall())

        cursor.execute("""SELECT m.name as tableName, 
                               p.name as columnName
                        FROM sqlite_master m
                        left outer join pragma_table_info((m.name)) p
                             on m.name <> p.name
                        WHERE tableName IN ('movies',
                                            'movie_actors', 
                                            'actors', 
                                            'writers')     
                        order by tableName, columnName
                        ;""")
        # print(cursor.fetchall())
        # cursor.execute('pragma table_info(movies)')
        # print(cursor.fetchall())
        #
        # for one_table in cursor.fetchall():
        #     print(one_table[1])


    # Наверняка это пилится в один sql - запрос, но мне как-то лениво)

    # Получаем все поля для индекса, кроме списка актеров и сценаристов, для них только id
    cursor.execute("""
        select id, imdb_rating, genre, title, plot, director,
        -- comma-separated actor_id's
        (
            select GROUP_CONCAT(actor_id) from
            (
                select actor_id
                from movie_actors
                where movie_id = movies.id
            )
        ),

        max(writer, writers)
        from movies
    """)

    raw_data = cursor.fetchall()
    print("raw_data"*80)
    #print(raw_data)
    print("raw_data" * 80)
    # cursor.execute('pragma table_info(movies)')
    # pprint(cursor.fetchall())


    # Нужны для соответсвия идентификатора и человекочитаемого названия
    actors = {row[0]: row[1] for row in cursor.execute('select * from actors where name != "N/A"')}
    writers = {row[0]: row[1] for row in cursor.execute('select * from writers where name != "N/A"')}

    return actors, writers, raw_data


def transform(__actors, __writers, __raw_data):
    """

    :param __actors:
    :param __writers:
    :param __raw_data:
    :return:
    """
    documents_list = []
    for movie_info in __raw_data:
        # Разыменование списка
        movie_id, imdb_rating, genre, title, description, director, raw_actors, raw_writers = movie_info

        if raw_writers[0] == '[':
            parsed = json.loads(raw_writers)
            new_writers = ','.join([writer_row['id'] for writer_row in parsed])
        else:
            new_writers = raw_writers

        writers_list = [(writer_id, __writers.get(writer_id)) for writer_id in new_writers.split(',')]
        actors_list = [(actor_id, __actors.get(int(actor_id))) for actor_id in raw_actors.split(',')]

        document = {
            "_index": "movies",
            "_id": movie_id,
            "id": movie_id,
            "imdb_rating": imdb_rating,
            "genre": genre.split(', '),
            "title": title,
            "description": description,
            "director": director,
            "actors": [
                {
                    "id": actor[0],
                    "name": actor[1]
                }
                for actor in set(actors_list) if actor[1]
            ],
            "writers": [
                {
                    "id": writer[0],
                    "name": writer[1]
                }
                for writer in set(writers_list) if writer[1]
            ]
        }

        for key in document.keys():
            if document[key] == 'N/A':
                # print('hehe')
                document[key] = None

        document['actors_names'] = ", ".join([actor["name"] for actor in document['actors'] if actor]) or None
        document['writers_names'] = ", ".join([writer["name"] for writer in document['writers'] if writer]) or None

        import pprint
        pprint.pprint(document)

        documents_list.append(document)

    return documents_list


def load(acts):
    """

    :param acts:
    :return:
    """
    es = Elasticsearch([{'host': '10.1.0.39', 'port': 9200,'scheme': "http"}])

    bulk(es, acts)

    return True


if __name__ == '__main__':
    load(transform(*extract()))