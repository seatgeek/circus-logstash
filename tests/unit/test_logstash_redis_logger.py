import unittest

from mock import patch, MagicMock

from circus_logstash.circus_logstash import get_fields, LogstashRedisLogger



class TestFields(unittest.TestCase):

    def test_extracts_field_prefixed_item(self):
        fields = get_fields(field_a='a')
        self.assertEqual(fields, {'a': 'a'})

    def test_does_not_extract_extra_field(self):
        fields = get_fields(extra='extra')
        self.assertEqual(fields, {})


class TestLogstashRedisLogger(unittest.TestCase):

    def test_single_line(self):
        instance, redis = self._create_instance()
        instance(self._callable_for_data('a line\n'))

    def _callable_for_data(self, data):
        return {
            'pid': 1,
            'data': data,
            'name': 'name',
        }

    def _create_instance(self):
        with patch('circus_logstash.circus_logstash.StrictRedis') as redis:
            return LogstashRedisLogger(
                urls='amqp://localhost:6379/0',
                service='test_service',
                redis_namespace='redis_namespace',
            ), redis
