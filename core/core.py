import execjs
import logging

logger = logging.getLogger('main debug log')
logger.setLevel(logging.DEBUG)
log = logging.StreamHandler()
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(lineno)d: %(module)s -> %(funcName)s: %(message)s')
log.setFormatter(formatter)
logger.addHandler(log)

JS = execjs.get()


def args_parse(arg_string):
    logger.debug(arg_string)
    func_raw = "(function (){return arguments})(" + str(arg_string) + ")"
    logger.debug(func_raw)
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
            logger.debug(type(func.call('run', *args)))
            logger.debug(func.call('run', *args))
            logger.debug(args)
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
