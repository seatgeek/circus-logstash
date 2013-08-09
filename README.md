# Circus-Logstash

A logger to be used in Circus that ships logs via a Redis queue to Logstash. If there is interest in other brokers they should be able to be added to this project

# Installation

```
  pip install circus-logstash
```

# Usage

In your Circus config add the stream class and some info

```
  stdout_stream.class = circus_logstash.circus_logstash.LogstashRedisLogger
  stdout_stream.refresh_time = 0.3
  stdout_stream.urls = redis://localhost:6379/0
  stdout_stream.service = service_name
  stdout_stream.redis_namespace = logstash:app:production

  stdout_stream.subclass = FileStream
  stdout_stream.subclass_filename = '/var/log/...'

  stdout_stream.field_extra_field = 'field_value'
```

`urls` is a comma separated list of Redis urls to connect to. These are done in round robin if there are any failures connection/writing.

`service` Used throughout for namespacing the log lines

`redis_namespace` The list to write logs to

`subclass` A class to use as well (like writing files still)

Any options prefixed with `subclass_` will be passed to the init of the subclass

Any options prefixed with `field_` can be used to include extra field:value pairs in the Logstash events. This is useful to include extra metadata about this process.
