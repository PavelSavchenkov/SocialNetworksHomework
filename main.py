from telepot import glance
import telepot.aio
import sys
import asyncio
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
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

def runInlineBot(TOKEN):
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

    bot = telepot.aio.DelegatorBot(TOKEN, [
        intercept_callback_query_origin(
            pave_event_space())(
            per_inline_from_id(), create_open, UserDescriptionHandler, timeout=1),
    ])

    loop = asyncio.get_event_loop()
    loop.create_task(MessageLoop(bot).run_forever())
    print('Listening ...')

    loop.run_forever()


def runUsualBot(TOKEN):
    class MessageCounter(telepot.aio.helper.ChatHandler):
        def __init__(self, *args, **kwargs):
            super(MessageCounter, self).__init__(*args, **kwargs)
            self._count = 0

        async def on_chat_message(self, msg):
            content_type, chat_type, chat_id = telepot.glance(msg)

            if content_type != 'text':
                await self.sender.sendMessage('Give me text, please.')
                return

            text = msg['text']
            responses = list(dataHandler.getBestResponses(text))
            if not responses:
                await self.sender.sendMessage('No results was found')
                return

            key, value = responses[-1]
            await self.sender.sendMessage(value)

    bot = telepot.aio.DelegatorBot(TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, MessageCounter, timeout=10),
    ])

    loop = asyncio.get_event_loop()
    loop.create_task(MessageLoop(bot).run_forever())
    print('Listening ...')

    loop.run_forever()


TOKEN = sys.argv[1]  # get token from command-line

runUsualBot(TOKEN)
