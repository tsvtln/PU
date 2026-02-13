import os


def check_lists(function):
    def check(**kwargs):
        condition = kwargs.get("error_raise_condition", True)
        no_error = kwargs.get("do_not_raise_error", False)
        name = kwargs.get("name", True)
        attr1 = kwargs.get("attr1", str(name))
        name1 = kwargs.get("name1", str(name))
        att = kwargs.get("attr", str(name))
        excp = kwargs.get("exc", Exception)
        operator = kwargs.get("op", "==")
        operator2 = kwargs.get("op2", "==")
        ob = [value for value in kwargs["collection"] if
            function(getattr(value, att, name), name, op=operator) and function(getattr(value, attr1, name1), name1, op=operator2)]
        if condition:
            condition = bool(ob)
        else:
            condition = bool(not ob)
        if not no_error:
            exc(kwargs.get("error_message", ""), condition, excp)
        if kwargs.get("whole", False):
            return ob
        return ob[kwargs.get("item", 0)] if ob else False

    return check


@check_lists
def check_collections(cond, val, op="=="):
    """possible keyword arguments:\n
            collection: collection which will be checked for certain values\n
            error_raise_condition: bool, sets whether exception is being raised on found or empty result list\n
            do_not_raise_error: bool, sets whether method should raise error\n
            attr: str, first method name which value should be compared in search\n
            name: str, sets name for the first element to check for\n
            attr1: str, same as attr for the second argument looked for (if any given)\n
            name1: str, same as name for the second argument looked for (if any given)\n
            exc: exception object, exception method used for raising exception (Exception by default)\n
            op: compare operator
            whole: return the whole result list instead of single item"""
    if op == "==":
        return cond == val
    elif op == "!=":
        return cond != val
    elif op == ">=":
        return cond >= val
    elif op == "<=":
        return cond <= val
    elif op == "<":
        return cond < val
    elif op == ">":
        return cond > val


def raise_exception(function):
    def e_raise(message, condition, error=ValueError):
        if function(condition):
            raise error(message)

    return e_raise


@raise_exception
def exc(cond):
    if cond: return True


def zip_current_project():
    path = os.path.dirname(os.path.realpath(__file__))
    os.system("tar --exclude __pycache__ -acvf project.zip project")


def args_to_kwargs(*args, **kwargs):
    kwargs.update(dict(zip(["collection", "attr", "name", "error_message", "exc", "error_raise_condition"], args)))
    return kwargs


def get_from_collection_or_error(*args, **kwargs):
    """\npossible positional parameters "collection","att","name","message","exc","error_raise_condition" \n see check_collections for details"""
    arguments = args_to_kwargs(*args, **kwargs)
    return check_collections(**arguments, error_raise_condition=False)


def is_in_collection(*args, **kwargs):
    """\npossible positional parameters "collection","att","name","message","exc","error_raise_condition" \n see check_collections for details"""
    kwargs = args_to_kwargs(*args, **kwargs)
    return bool(check_collections(**kwargs, do_not_raise_error=True))


def is_not_in_collection(*args, **kwargs):
    """\npossible positional parameters "collection","att","name","message","exc","error_raise_condition" \n see check_collections for details"""
    kwargs = args_to_kwargs(*args, **kwargs)
    return False if is_in_collection(**kwargs) else True


def not_in_collection_or_error(*args, **kwargs):
    """\npossible positional parameters "collection","att","name","message","exc","error_raise_condition" \n see check_collections for details"""
    kwargs = args_to_kwargs(*args, **kwargs)
    return check_collections(**kwargs, error_raise_condition=True)


def add_to_collection_or_error(add, *args, **kwargs):
    kwargs = args_to_kwargs(*args, **kwargs)
    check_collections(**kwargs, error_raise_condition=True)
    kwargs["collection"].append(add)


def remove_from_collection_or_error(*args, once=True, **kwargs):
    """\npossible positional parameters "collection","att","name","message","exc","error_raise_condition" \n see check_collections for details"""
    kwargs = args_to_kwargs(*args, **kwargs)
    astronaut = check_collections(**kwargs, error_raise_condition=False)
    for i, v in enumerate(kwargs["collection"]):
        if getattr(v, kwargs["attr"]) == astronaut.name:
            kwargs["collection"].pop(i)
            if once:
                return True
    return True


sep = lambda message, new_lines=1, symbols=10, sym="#": print(
    ("\n" * new_lines) + (sym * symbols) + message.upper() + (sym * symbols), end="\n" * new_lines)
