import execjs

JS = execjs.get()


class Result_obj:
    state = None
    __message = None

    def __init__(self, state, message=None):
        self.__state = state
        if message is not None:
            self.__message = str(message)

    def __str__(self):
        return self.__message or ''

    def __bool__(self):
        return self.__state

    def getstate(self):
        return self.__state

    def getmessage(self):
        return self.__message


def args_parse(arg_string):
    print(29, arg_string)
    func_raw = "(function (){return arguments})(" + str(arg_string) + ")"
    print(32, func_raw)
    args = JS.eval(func_raw)
    return [args[key] for key in sorted(args.keys())]


def code_compile(code):
    code_raw = "(typeof({code}) == 'function')?({code}).apply(this, arguments):({code})".format(code=code)
    func_raw = "function run(){return " + code_raw + "}"
    if JS.is_available():
        return JS.compile(func_raw)


def js_to_py(code):
    func = code_compile(str(code))

    def product(*args):
        try:
            print(type(func.call('run', *args)), func.call('run', *args), args)
            return func.call('run', *args)
        except execjs.RuntimeError:
            raise execjs.RuntimeError("SYNTAX ERROR")
    return product


def test_runner(code, tests, expects):
    case = js_to_py(code)
    try:
        return [{
                    "state": case(*args_parse(params)) == JS.eval(expect)
                } for params, expect in zip(tests, expects)]
    except execjs.RuntimeError as err:
        return [{
            "state": False,
            "message": str(err.with_traceback(None))
        }]
