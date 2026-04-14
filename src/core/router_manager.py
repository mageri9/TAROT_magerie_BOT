from aiogram import Router

import handlers.user.message as user_message
import handlers.user.callback as user_query
import handlers.admin.message as admin_message
import handlers.admin.callback as admin_query




def setup_routers():
    router = Router()

    routers = [user_message, user_query, admin_message, admin_query]

    for _router in routers:
        _router.register_handlers()

    router.include_routers(*[_router.router for _router in routers])
    return router
