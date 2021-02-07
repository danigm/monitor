Simple tool to monitor website availability
===========================================

System that monitors website availability over the network, produces metrics
about this and passes these events through an Aiven Kafka instance into an
Aiven PostgreSQL database.

## Producer

The producer is a script that checks a website and sends the result to a kafka
topic.

The producer can be run as a only once command:

```
python -m monitor.producer http://danigm.net
```

Or as a daemon that will do a check every N seconds:

```
python -m monitor.producer -m 10 http://danigm.net
```

This script writes some small log information to the stdout and stderr so if
it's wrapped with a systemd service the output could be visible with
journalctl.

### Configure

To make it work you need a kafka instance with a kafka topic. By default it
uses these files to authenticate:
    * ca.pem
    * service.cert
    * service.key

So you need to create those files to make this work.
