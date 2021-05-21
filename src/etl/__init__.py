import abc
import json
import logging
import os
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Dict, Generator, List, Tuple

import backoff
import coloredlogs
import psycopg2
import psycopg2.extras
from elasticsearch import Elasticsearch, helpers
from pydantic import BaseSettings
from redis import Redis

logger = logging.getLogger("ETL")

coloredlogs.install(level="DEBUG", logger=logger)


class ETLConfig(BaseSettings):
    db_url: str = "postgresql://{user}:{password}@{host}:5432/{db}".format(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        db=os.getenv("POSTGRES_DB"),
    )
    run_once: bool = os.getenv("RUN_ONCE")
    elasticsearch_hosts: str = os.getenv("ELASTICSEARCH_HOSTS")


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    @backoff.on_exception(backoff.expo, Exception)
    def save_state(self, state: dict, path: str = None) -> None:
        self.redis_adapter.set(path or 'data', json.dumps(state))

    @backoff.on_exception(backoff.expo, Exception)
    def retrieve_state(self, path: str = None) -> dict:
        raw_data = self.redis_adapter.get(path or 'data')
        if raw_data is None:
            return {}
        return json.loads(raw_data)


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage, path: str = None):
        self.storage = storage
        self.path = path
        self.state = self.retrieve_state()

    def retrieve_state(self) -> dict:
        data = self.storage.retrieve_state(path=self.path)
        if not data:
            return {}
        return data

    def set_key(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.state[key] = value

        self.storage.save_state(self.state, path=self.path)

    def get_key(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        return self.state.get(key)


def coroutine(func):
    @wraps(func)
    def inner(*args, **kwargs):
        fn = func(*args, **kwargs)
        next(fn)
        return fn

    return inner


@dataclass
class PostgresDatabase:
    url: str

    @backoff.on_exception(backoff.expo, Exception)
    def query(self, template: str, params: Dict[str, Any]) -> List[dict]:
        results = []
        with psycopg2.connect(self.url) as connection:
            with connection.cursor(
                    cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:
                cursor.execute(template, params)
                results = [dict(r) for r in cursor.fetchall()]
        return results


@dataclass
class Lookup:
    db: PostgresDatabase
    storage: Any
    path_redis: str = None

    @property
    def state(self):
        return State(
            self.storage,
            path=self.path_redis or self.__class__.__name__ + '_state'
        )

    def get_updated_rows(self, table, modified, column_return=None):

        def inner(target: Generator):
            batch_num = 0
            batch_size = 500
            last_updated_at = "0001-01-01 00:00:00.992496+00"
            while True and batch_num == 0:

                state = self.state
                last_updated_at = state.get_key(
                    'last_updated_at') or last_updated_at
                last_id = state.get_key('last_id')

                if column_return:
                    select_columns = ",".join(["id", modified, column_return])
                else:
                    select_columns = ",".join(["id", modified])

                modified_rows: List[Dict] = self.db.query(
                    f'''
                    SELECT {select_columns} from {table}
                    '''
                    +
                    f'''
                    WHERE  {modified} = %(last_updated_at)s and id > %(last_id)s::uuid
                    or {modified} > %(last_updated_at)s
                    ''' * bool(last_updated_at)
                    + f'''
                    ORDER BY {modified}, id
                    LIMIT %(batch_size)s;
                    ''', {
                        'last_updated_at': last_updated_at,
                        'batch_size': batch_size,
                        'last_id': last_id
                    }
                )
                time.sleep(0.5)
                if not modified_rows:
                    logger.info(
                        f'No updated rows in {table} since {last_updated_at}')
                    break
                first, last = modified_rows[0], modified_rows[-1]
                logger.info(
                    '\n'
                    f'    Found {len(modified_rows)} updated rows in {table} - Batch #{batch_num}:\n'
                    f"        {first['id']} (at {first[modified]})\n"
                    '        ...\n'
                    f"        {last['id']} (at {last[modified]})"
                )
                if column_return:
                    results_: List[str] = [row[column_return]
                                           for row in modified_rows]
                else:
                    results_: List[str] = [row["id"] for row in modified_rows]

                target.send(results_)
                state.set_key('last_updated_at', str(last[modified]))
                state.set_key('last_id', last['id'])
                batch_num += 1

        return inner


@dataclass
class PersonLookupPersonETL(Lookup):
    def produce(self, target: Generator):
        get_updated_persons = self.get_updated_rows(
            'content.person', 'modified')
        get_updated_persons(
            target=target
        )


@dataclass
class PersonLookup(Lookup):
    def produce(self, target: Generator):
        get_updated_persons = self.get_updated_rows(
            'content.person', 'modified')
        get_updated_persons(
            self._get_person_films(
                target=target
            )
        )

    @coroutine
    def _get_person_films(self, target: Generator):
        updated_persons: List[dict]
        while person_ids := (yield):
            person_films: List[dict] = self.db.query(
                '''
                SELECT pfr.film_id as id
                FROM content.person_film_role pfr
                where pfr.person_id = ANY(%(person_ids)s::uuid[])
                ''',
                {
                    'person_ids': person_ids
                }
            )
            film_ids: List[str] = [film['id'] for film in person_films]
            time.sleep(0.5)
            if film_ids:
                target.send(film_ids)


@dataclass
class PersonFilmRoleLookup(Lookup):
    def produce(self, target: Generator):
        get_updated_person_role = self.get_updated_rows(
            'content.person_film_role', 'modified', column_return='film_id')
        get_updated_person_role(
            target
        )


@dataclass
class GenreLookup(Lookup):
    def produce(self, target: Generator):
        get_updated_person_role = self.get_updated_rows(
            'content.genre', 'modified')
        get_updated_person_role(
            self._get_updated_genre_films(
                target
            )
        )

    @coroutine
    def _get_updated_genre_films(self, target: Generator):
        updated_persons: List[dict]
        while genre_ids := (yield):
            genre_films: List[dict] = self.db.query(
                '''
                SELECT fwr.filmwork_id as id
                FROM content.film_work_genre fwr
                where fwr.genre_id = ANY(%(genre_ids)s::uuid[])
                ''',
                {
                    'genre_ids': genre_ids
                }
            )
            film_ids: List[str] = [film['id'] for film in genre_films]
            time.sleep(0.5)
            target.send(film_ids)


@dataclass
class FilmWorkLookup(Lookup):
    def produce(self, target: Generator):
        get_update_film_work = self.get_updated_rows(
            'content.film_work', 'modified')
        get_update_film_work(
            target=target
        )


@dataclass
class ETLProcess:
    db: PostgresDatabase
    config: ETLConfig
    lookup: Lookup
    index: str

    @abc.abstractmethod
    def extract(self):
        pass

    @backoff.on_exception(backoff.expo, Exception, )
    def _bulk_update_elastic(self, docs: List[dict]) -> Tuple[int, list]:
        elastic_settings = dict(
            hosts=self.config.elasticsearch_hosts,
            sniff_on_start=True,
            sniff_on_connection_fail=True,
            sniffer_timeout=100
        )

        def generate_doc(docs):
            for doc in docs:
                yield {
                    '_index': self.index,
                    '_id': doc['id'],
                    '_source': doc
                }

        with Elasticsearch(**elastic_settings) as es:
            return helpers.bulk(
                es,
                generate_doc(docs)
            )

    @coroutine
    def load_to_elastic(self):
        docs: List[dict]
        while docs := (yield):
            docs_updated, _ = self._bulk_update_elastic(docs)
            logger.info(
                f"Updated {docs_updated} documents in '{self.index}' index")
            time.sleep(0.5)

    def run(self):
        self.lookup.produce(
            self.extract(
                self.transform_for_elastic(
                    self.load_to_elastic()
                )
            )
        )


@dataclass
class ETLProcessPerson(ETLProcess):

    @coroutine
    def extract(self, target: Generator):
        film_ids: List[str]
        while person_ids := (yield):
            persons: List[dict] = self.db.query(
                '''
                SELECT
                    person.id,
                    person.full_name,
                    role.role AS roles
	            FROM content.person person
	            LEFT JOIN LATERAL (
	                SELECT
	                    pfr.person_id,
	                    array_agg(jsonb_build_object('id', pfr.film_id, 'role', pfr.role)) AS role
	                FROM content.person_film_role pfr
	                where person.id=pfr.person_id group by person_id
	                ) AS role ON role.person_id=person.id
                WHERE person.id = ANY(%(person_ids)s::uuid[]);
                ''',
                {
                    'person_ids': person_ids
                }
            )
            logger.info(f'Extracted {len(persons)} persons from database')
            time.sleep(0.5)
            target.send(persons)

    @coroutine
    def transform_for_elastic(self, target: Generator):
        persons: List[dict]
        while persons := (yield):
            persons_docs = []
            for person in persons:
                person_doc = {
                    'id': person['id'],
                    'full_name': person['full_name'],
                    'film_ids': set(),
                    'role': set()
                }
                if person.get('roles'):
                    for role in person['roles']:
                        person_doc['film_ids'].add(role['id'])
                        person_doc['role'].add(role['role'])

                person_doc['film_ids'] = list(person_doc['film_ids'])
                person_doc['role'] = list(person_doc['role'])
                persons_docs.append(person_doc)
            target.send(persons_docs)


@dataclass
class ETLProcessFilmWork(ETLProcess):

    @coroutine
    def extract(self, target: Generator):
        film_ids: List[str]
        while film_ids := (yield):
            films: List[dict] = self.db.query(
                '''
                SELECT
                    fw.id AS id,
                    fw.title,
                    fw.description,
                    fw.rating,
                    fwt.name,
                    fwp.persons,
                    fwg.genres
                FROM "content".film_work fw
				INNER JOIN content.film_work_type fwt on fwt.id=fw.type_id
                LEFT JOIN LATERAL (
                    SELECT
                        pfw.film_id,
                        array_agg(jsonb_build_object(
                            'id', p.id,
                            'full_name', p.full_name,
                            'role', pfw.role
                        )) AS persons
                    FROM "content".person_film_role pfw
                    JOIN "content".person p ON p.id = pfw.person_id
                    WHERE pfw.film_id = fw.id
                    GROUP BY 1
                    ) fwp ON TRUE
                LEFT JOIN LATERAL (
                    SELECT
                        gfw.filmwork_id,
                        array_agg(jsonb_build_object(
                            'id', g.id,
                            'name', g.name,
                            'description', g.description
                        )) AS genres
                    FROM "content".film_work_genre gfw
                    JOIN "content".genre g ON g.id = gfw.genre_id
                    WHERE gfw.filmwork_id = fw.id
                    GROUP BY 1
                    ) fwg ON TRUE
                WHERE fw.id = ANY(%(film_ids)s::uuid[]);
                ''',
                {
                    'film_ids': film_ids
                }
            )
            logger.info(f'Extracted {len(films)} film works from database')
            time.sleep(0.5)
            target.send(films)

    @coroutine
    def transform_for_elastic(self, target: Generator):
        film_works: List[dict]
        while film_works := (yield):
            film_work_docs = []
            genre_docs_raw = dict()
            persons_docs_raw = dict()
            for film in film_works:

                for genre in film['genres']:
                    genre_docs_raw[genre['id']] = {
                        'id': genre['id'],
                        'name': genre['name'],
                        'description': genre['description']
                    }

                film_work_doc = {
                    k: v for k, v in film.items()
                    if k in ('id', 'title', 'description', 'type')
                }
                film_work_doc['genres_names'] = [g['name']
                                                 for g in film['genres']]
                film_work_doc['genres'] = [
                    {'id': g['id'], 'name': g['name']} for g in film['genres']]

                film_work_doc['imdb_rating'] = film['rating']
                film_work_doc.update({
                    'actors': [],
                    'writers': [],
                    'directors': [],
                    'actors_names': [],
                    'writers_names': [],
                    'directors_names': []
                })
                if film['persons'] is not None:
                    for person in film['persons']:
                        if person['id'] in persons_docs_raw:
                            persons_docs_raw[person['id']
                                             ]['role'].add(person['role'])
                            persons_docs_raw[person['id']
                                             ]['film_ids'].add(film['id'])
                        else:
                            persons_docs_raw[person['id']] = {
                                'id': person['id'],
                                'full_name': person['full_name'],
                                'role': set([person['role']]),
                                'film_ids': set([film['id']])
                            }

                        if person['role'] == 'director':
                            film_work_doc['directors_names'].append(
                                person['full_name'])
                            film_work_doc['directors'].append(
                                {'id': person['id'],
                                    'name': person['full_name']}
                            )
                        if person['role'] == 'actor':
                            film_work_doc['actors_names'].append(
                                person['full_name'])
                            film_work_doc['actors'].append(
                                {'id': person['id'],
                                    'name': person['full_name']}
                            )
                        if person['role'] == 'writer':
                            film_work_doc['writers_names'].append(
                                person['full_name'])
                            film_work_doc['writers'].append(
                                {'id': person['id'],
                                    'name': person['full_name']}
                            )
                film_work_docs.append(film_work_doc)
            genre_docs = [genre_doc for genre_doc in genre_docs_raw.values()]

            if self.index == 'genre':
                target.send(genre_docs)
            elif self.index == 'movies':
                target.send(film_work_docs)


@dataclass
class ETLManager:
    processes: List[ETLProcess]
    run_once: bool = False

    def loop_processes(self):
        while True:
            logger.debug("start")
            for process in self.processes:
                process.run()

            if self.run_once:
                break
            logger.debug("end")
            time.sleep(3)


if __name__ == "__main__":
    config = ETLConfig()

    db = PostgresDatabase(url=config.db_url)
    redis = Redis(host='redis', db=1)
    
    # если нужно сбросить кэш
    # redis.flushdb()

    storage = RedisStorage(
        redis
    )

    lookup_params = {'db': db, 'storage': storage}
    processes = [
        ETLProcessFilmWork(db=db, config=config, lookup=PersonLookup(
            **lookup_params), index='movies'),
        ETLProcessFilmWork(db=db, config=config, lookup=GenreLookup(
            **lookup_params), index='movies'),
        ETLProcessFilmWork(db=db, config=config, lookup=PersonFilmRoleLookup(
            **lookup_params), index='movies'),
        ETLProcessFilmWork(db=db, config=config, lookup=FilmWorkLookup(
            **lookup_params), index='movies'),
        ETLProcessFilmWork(db=db, config=config,
                           lookup=GenreLookup(
                               **lookup_params, path_redis='index_genre_lookup_state'),
                           index='genre'),
        ETLProcessPerson(db=db, config=config, lookup=PersonLookupPersonETL(
            **lookup_params), index='persons')
    ]

    manager = ETLManager(processes=processes, run_once=config.run_once)
    manager.loop_processes()
