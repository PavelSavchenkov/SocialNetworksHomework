import sys
import asyncio
from telepot import glance
import telepot.aio
from telepot.aio.loop import MessageLoop
from telepot.aio.helper import (
    InlineUserHandler, AnswererMixin, InterceptCallbackQueryMixin)
from telepot.namedtuple import (
    InlineQueryResultArticle, InputTextMessageContent, )
from telepot.aio.delegate import (
    per_inline_from_id, create_open, pave_event_space,
    intercept_callback_query_origin)
from dataHandler import DataHandler

dataHandler = DataHandler('data.csv')


class UserDescriptionHandler(InlineUserHandler,
                             AnswererMixin,
                             InterceptCallbackQueryMixin):
    def __init__(self, *args, **kwargs):
        super(UserDescriptionHandler, self).__init__(*args, **kwargs)

    def on_inline_query(self, msg):
        def compute():
            query_id, from_id, query_string = glance(msg, flavor='inline_query')
            print('Inline query:', query_id, from_id, query_string)
            responses = dataHandler.getBestResponses(query_string)
            results = []
            for key, value in responses:
                results.append(InlineQueryResultArticle(id=key,
                                                        title=key,
                                                        input_message_content=InputTextMessageContent(
                                                            message_text=value
                                                        ))
                               )

            return results

        self.answerer.answer(msg, compute)

    def on_close(self, ex):
        print('Closing!')


TOKEN = sys.argv[1]

bot = telepot.aio.DelegatorBot(TOKEN, [
    intercept_callback_query_origin(
        pave_event_space())(
        per_inline_from_id(), create_open, UserDescriptionHandler, timeout=1),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
