"""
    Where the web app starts.
    - data pipeline project
    - author: eric yang
    - date: mar 31, 2017
"""

import os
import json
import tornado.web
import tornado.wsgi
import tornado.ioloop
import exceptions
import db_load
from concurrent.futures import ProcessPoolExecutor
from settings import settings
from iron_mq import IronMQ


class EventHandlers:
    """This class stores the mappings of a event and its handler class
        key: the event name, which could be crash report, purchase or
        install.
        value: the class of handler.
    """
    def __init__(self):
        self.handlers = dict()

    def register(self, evt, handler):
        """Register the mapping of event name and the handler"""
        if not (evt and handler):
            return None
        if not issubclass(handler, Event):
            return None
        self.handlers[evt] = handler
        return handler

    def get_handler(self, evt):
        """Get a handler or None if the event is not registered."""
        return self.handlers.get(evt, None)


event_handlers = EventHandlers()


class Event:
    """The base event class. All the other event classes are inherited from this one.
    """
    event_name = None
    content_name = None
    content_type = None

    def __init__(self, loaded_json):
        try:
            self.user_id = loaded_json['user_id']
            self.timestamp = loaded_json['timestamp']

            if not (isinstance(self.user_id, int)
                    and isinstance(self.user_id, int)):
                raise exceptions.ValueTypeErrException

            if self.content_name:
                content_value = loaded_json[self.content_name]
                if isinstance(content_value, self.content_type):
                    setattr(self, self.content_name, content_value)
                else:
                    raise exceptions.ValueTypeErrException

        except KeyError as e:
            raise exceptions.KeyMissingException(e)

    def __str__(self):
        """The event_name is not included on purpose, as it makes the queue
            message decoding easier."""
        evt = '{user_id},{timestamp}'.format(event_name=self.event_name,
                                             user_id=self.user_id,
                                             timestamp=self.timestamp)
        if self.content_name:
            evt += ',{}'.format(getattr(self, self.content_name))
        return evt


class CrashReportEvent(Event):
    """Class for the event: crash_report"""
    event_name = 'crash_report'
    content_name = 'message'
    content_type = str


event_handlers.register(CrashReportEvent.event_name, CrashReportEvent)


class PurchaseEvent(Event):
    """Class for the event: purchase"""
    event_name = 'purchase'
    content_name = 'sku'
    content_type = str


event_handlers.register(PurchaseEvent.event_name, PurchaseEvent)


class InstallEvent(Event):
    """Class for the event: install"""
    event_name = 'install'


event_handlers.register(InstallEvent.event_name, InstallEvent)


def pre_processing(raw_data):
    """The pre-processor before the data is sent to the real event
        handler. The pre-processor will check the length or the input,
        and convert it to json structure"""
    """Check the raw input from POST body, return the decoded json
    or throw an exception"""
    raw_data = raw_data or ''
    if isinstance(raw_data, bytes):
        raw_data = raw_data.decode(settings.ENCODING_SCHEME)
    elif not isinstance(raw_data, str):
        raw_data = str(raw_data)

    len_raw_data = len(raw_data)
    if len_raw_data == 0 or len_raw_data > settings.INPUT_MAX_LEN:
        raise exceptions.InputExceedLimitException

    try:
        output_json = json.loads(raw_data)
    except json.JSONDecodeError:
        raise exceptions.BadJsonStructureException
    return output_json


def init_iron_mq():
    """Initiate the Iron MQ, which is the message queue service of Heroku"""
    return IronMQ(host=settings.MQ_HOST,
                  project_id=settings.MQ_PROJECT_ID,
                  token=settings.MQ_TOKEN)


mq = init_iron_mq()


def init_queue_dict(mq, events):
    """The mappings of event_name and the queue name"""
    queue_dict = dict()
    for evt in events:
        queue_dict[evt] = mq.queue(evt)
    return queue_dict


queue_list = init_queue_dict(mq, event_handlers.handlers.keys())


def post_processing(queue, event):
    """The post-processor. This one should be pluggable and can be easily replaced
        by other post-processors."""
    """Insert the event into a message queue"""
    if queue and event:
        queue.post(str(event))


def get_ok_ret():
    ret_msg = '{"status_code": 0, "status_message": "ok"}'
    return ret_msg


def get_err_ret(e):
    ret_msg = '{{"status_code": {errno}, ' \
              '"status_message": "{msg}({supp})"}}'.format(errno=e.errno,
                                                           msg=e.msg,
                                                           supp=e.key)
    return ret_msg


def input_processing(raw_data):
    """In this function the corresponding handler is invoked based on the
        name of the event. The processors may throw exceptions if any error
        happens."""
    if raw_data is None:
        raise exceptions.NoContentException

    try:
        loaded_json = pre_processing(raw_data)
        if not isinstance(loaded_json, dict):
            raise exceptions.BadJsonStructureException(loaded_json)

        event_name = loaded_json.get('event_name', None)
        if not event_name:
            raise exceptions.KeyMissingException('event_name')

        evt_class = event_handlers.get_handler(event_name)
        if not evt_class:
            raise exceptions.UnsupportedEventException(event_name)

        evt = evt_class(loaded_json)
        post_processing(queue_list.get(evt.event_name), evt)
        ret = get_ok_ret()

    except exceptions.EventException as e:
        ret = get_err_ret(e)
    return ret


class RootPath(tornado.web.RequestHandler):
    """The handler of root path"""
    def post(self):
        raw_data = self.request.body
        self.write(input_processing(raw_data))


app = tornado.web.Application([
    (r"/", RootPath),
])

if __name__ == '__main__':

    tbl_quefile_dict = {}

    for tbl_name in event_handlers.handlers.keys():
        tbl_quefile_dict[tbl_name] = db_load.IronMQFile(mq.queue(tbl_name))

    db_parms = {'dbname': settings.DB_NAME,
                'user': settings.DB_USER,
                'password': settings.DB_PASSWORD,
                'host': settings.DB_HOST,
                'port': settings.DB_PORT
                }

    # Temporary solution, do not run a production system like this. A better solution would
    # be a standalone process monitored by tools like supervisord.
    with ProcessPoolExecutor(max_workers=settings.DB_LOAD_WORKER) as executor:
        for tbl_name, queue_file in tbl_quefile_dict.items():
            executor.submit(db_load.load_data_to_postgre,
                            tbl_quefile_dict[tbl_name],
                            db_parms, tbl_name)

        port = int(os.environ.get('PORT', settings.DEFAULT_APP_PORT))
        app.listen(port)  # no multi processes here as the Heroku VM has only one cpu
        tornado.ioloop.IOLoop.current().start()