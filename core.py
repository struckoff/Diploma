import logging
import pychrome
import time

logger = logging.getLogger('main debug log')
logger.setLevel(logging.DEBUG)
log = logging.StreamHandler()
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(lineno)d: %(module)s -> %(funcName)s: %(message)s')
log.setFormatter(formatter)
logger.addHandler(log)


# TODO tab limit
class JSExecutor:
    def __init__(self, browser, tabs_pool, script_timeout=60, is_network_enable=False):
        self.script_timeout = script_timeout
        self.is_network_enable = is_network_enable

        self.__browser = browser
        self.__tabs_pool = tabs_pool
        self.__tab = None

    def __get_tab(self):
        print('Pool ', len(self.__tabs_pool))
        if self.__tab is None:
            self.__tab = self.__tab_init(self.__tab)
        elif self.__tab.status != self.__tab.status_started:
            self.__tab = self.__tab_init(self.__tab)

        if self.__tab is None:
            logger.debug('No tabs in a pool')
            time.sleep(10)
            self.__tab = self.__get_tab()

        return self.__tab

    def __tab_init(self, tab):
        if not isinstance(tab, pychrome.Tab):
            if len(self.__tabs_pool) > 0:
                tab = self.__tabs_pool.pop()
            else:
                return None

        tab.start()
        tab.call_method("Network.enable", _timeout=60)
        tab.call_method("Runtime.enable", _timeout=60)
        tab.call_method("Performance.enable", _timeout=60)

        if not self.is_network_enable:
            tab.call_method("Network.emulateNetworkConditions", offline=True, latency=0, downloadThroughput=-1,
                            uploadThroughput=-1, _timeout=60)

        return tab

#   TODO Exceptions
    def __assert(self, script, tests, expects):
        try:
            def is_equal(params, expect):
                func = self.__js_compile(self.__get_tab(), script)
                got = func(self.__args_parse(self.__get_tab(), params))
                expect = self.__js_compile(self.__get_tab(), expect)()
                logger.debug(self.__args_parse(self.__get_tab(), params))
                logger.debug(expect)
                try:
                    got = got['result']['value']
                    expect = expect['result']['value']
                except Exception as e:
                    logger.debug(expect)
                wanted = got == expect
                logger.debug({'params':params, 'got': got, 'expect': expect, 'state': wanted})
                return {'got': got, 'expect': expect, 'state': wanted}

            return [is_equal(params, expect) for params, expect in zip(tests, expects)]
        except Exception as e:
            raise e

    def __args_parse(self, tab, arg_string):
        '''
            Parse string of arguments written in JS syntax to Python list

            arg_string - string representation of JS function arguments
        '''
        def conv_value(val):
            return val.replace('"%F%', '').replace('%F%"', '').replace("%F%'", '').replace("'%F%", '')

        func_raw = "(function(){var args = []; var conv = function(key, val) {if (typeof val === 'function') {return '%F%'+val.toString()+'%F%';} return val}; for (var i = 0; i < arguments.length; i++) {args[i] = {'value':JSON.stringify(arguments[i], conv)}}return args})(" + str(arg_string) + ")"
        args = tab.Runtime.evaluate(expression=func_raw, sourceURL='about:blank', returnByValue=True, _timeout=self.script_timeout)
        args = [{'value': conv_value(v['value'])} for v in args['result']['value']]
        return args


        # print(50, tab.Runtime.getProperties(objectId=args['result']['objectId']))
        # return [{'value': v} for k, v in args['result']['value'].items()]

    def __js_compile(self, tab, script):
        code_raw = "(typeof({code}) == 'function')?({code}).apply(this, arguments):({code})".format(code=script)
        func_raw = "function run(){var ar = []; for (var i = 0; i < arguments.length; i++) {arguments[i] = eval('(' + arguments[i] + ')')};  return " + code_raw + "};"
        logger.debug(script)
        try:
            namespace = tab.Runtime.evaluate(expression='document')
            tab.Runtime.evaluate(expression=func_raw, sourceURL='about:blank', objectId=namespace['result']['objectId'], _timeout=self.script_timeout)

            def compiled(args=[]):
                logger.debug(args)
                return tab.call_method("Runtime.callFunctionOn", functionDeclaration='run', arguments=args, objectId=namespace['result']['objectId'], returnByValue=True, _timeout=self.script_timeout)
            return compiled
        except Exception as e:
            raise e

    def run(self, script, tests, expects):
        try:
            results = self.__assert(script, tests, expects)
        finally:
            self.__browser.close_tab(self.__get_tab())
            self.__tabs_pool.append(self.__browser.new_tab())

        return results
