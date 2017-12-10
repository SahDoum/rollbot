hack_dict = {}  # user_id: result


def roll_hack_decorator(user_id):
    """Fast written decorator to roll predicted results
    :param int user_id: Telegram id of user """
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            message = args[0]
            message.hack_result = None
            result = hack_dict.get(user_id)
            if result and message.from_user.id == user_id:
                message.hack_result = result
                hack_dict.pop(user_id)
            function(*args, **kwargs)
        return wrapper
    return real_decorator


def command_access_decorator(user_ids):
    """Decorator which allows us to permit only some users use a command
    :param ids user_ids: Permitted users to use command
    :type ids: list of integers which are Telegram users ids"""
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            message = args[0]
            user_id = message.from_user.id
            if user_id in user_ids:
                function(*args, **kwargs)
            else:
                return None
        return wrapper
    return real_decorator
