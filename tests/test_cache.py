# -*- coding: utf-8 -*-
import pytest

from rc.cache import Cache, CacheCluster
from rc.testing import NullCache


def test_null_cache():
    cache = NullCache()
    with pytest.raises(NotImplementedError):
        cache.client
    assert cache.get('key') is None
    assert cache.set('key', 'value')
    assert cache.delete('key')
    assert cache.get_many('key1', 'key2') == [None, None]
    assert cache.set_many({'key1': 'value1', 'key2': 'value2'})
    assert cache.delete_many('key1', 'key2')


def test_cache_basic_apis(redis_unix_socket_path):
    cache = Cache(redis_options={'unix_socket_path': redis_unix_socket_path})
    assert cache.get('key') is None
    assert cache.set('key', 'value')
    assert cache.get('key') == 'value'
    assert cache.delete('key')
    assert cache.get('key') is None

    assert cache.get_many('key1', 'key2') == [None, None]
    assert cache.set_many({'key1': 'value1', 'key2': 'value2'})
    assert cache.get_many('key1', 'key2') == ['value1', 'value2']
    assert cache.delete_many('key1', 'key2')
    assert cache.get_many('key1', 'key2') == [None, None]

    assert cache.get('key') is None
    assert cache.set('key', ['value'])
    assert cache.get('key') == ['value']
    assert cache.delete('key')
    assert cache.get('key') is None

    # import time
    # assert cache.get('key') is None
    # cache.set('key', 'value', 1)
    # time.sleep(1)
    # assert cache.get('key') is None


def test_cache_namespace(redis_unix_socket_path):
    cache01 = Cache(redis_options={'unix_socket_path': redis_unix_socket_path})
    cache02 = Cache(
        namespace='test:',
        redis_options={'unix_socket_path': redis_unix_socket_path})
    assert cache01.set('key', 'value')
    assert cache01.get('key') == 'value'
    assert cache02.get('key') is None


def test_cache_decorator_basic_apis(redis_unix_socket_path):
    cache = Cache(redis_options={'unix_socket_path': redis_unix_socket_path})

    @cache.cache()
    def load(name, offset):
        return ' '.join(('load', name, offset))
    assert load('name', 'offset') == 'load name offset'
    assert load('name', offset='offset') == 'load name offset'

    @cache.cache()
    def load(name, offset):
        return ' '.join(('load02', name, offset))
    assert load('name', 'offset') == 'load name offset'
    assert load('name', offset='offset') == 'load name offset'
    assert cache.invalidate(load, 'name', 'offset')
    assert load('name', 'offset') == 'load02 name offset'
    assert load('name', offset='offset') == 'load name offset'
    assert cache.invalidate(load, 'name', offset='offset')
    assert load('name', offset='offset') == 'load02 name offset'

    class Foo(object):
        @cache.cache()
        def load_method(self, name, offset):
            return ' '.join(('load', name, str(offset)))
    foo = Foo()
    assert foo.load_method('name', 10) == 'load name 10'
    assert foo.load_method('name', offset=10) == 'load name 10'
    assert cache.invalidate(foo.load_method, 'name', 10)


def test_cache_cluster_basic_apis(redis_hosts):
    cache = CacheCluster(redis_hosts)
    assert cache.get('key') is None
    assert cache.set('key', 'value')
    assert cache.get('key') == 'value'
    assert cache.delete('key')
    assert cache.get('key') is None

    assert cache.get_many('key1', 'key2') == [None, None]
    assert cache.set_many({'key1': 'value1', 'key2': 'value2'})
    assert cache.get_many('key1', 'key2') == ['value1', 'value2']
    assert cache.delete_many('key1', 'key2')
    assert cache.get_many('key1', 'key2') == [None, None]

    assert cache.get('key') is None
    assert cache.set('key', ['value'])
    assert cache.get('key') == ['value']
    assert cache.delete('key')
    assert cache.get('key') is None

    # import time
    # assert cache.get('key') is None
    # cache.set('key', 'value', 1)
    # time.sleep(1)
    # assert cache.get('key') is None


def test_cache_cluster_namespace(redis_hosts):
    cache01 = CacheCluster(redis_hosts)
    cache02 = CacheCluster(redis_hosts, namespace='test:')
    assert cache01.set('key', 'value')
    assert cache01.get('key') == 'value'
    assert cache02.get('key') is None
