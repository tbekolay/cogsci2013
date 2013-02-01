from __future__ import with_statement
import hashlib


class Builder(object):
    def __init__(self):
        self.net = None

    def view(self, iplot=True):
        if self.net is None:
            self.make()
        self.net.add_to_nengo()
        if iplot:
            self.net.view()

    @staticmethod
    def parse_params(p_list):
        # We expect parameters to come in the following order:
        #  name type value
        # where name is the parameter name,
        # type is the type (one of str, int, float, bool),
        # and value is the value.
        p = {}
        for name, typ, val in zip(*(iter(p_list),) * 3):
            if typ == 'bool':
                val = val.lower() == 'true'
            elif typ == 'int':
                val = int(val)
            elif typ == 'float':
                val = float(val)
            p[name] = val
        return p

    @staticmethod
    def write_param_file(name, params, logdir):
        fn = Builder.name_hash(name, params)
        with open('%s/%s.txt' % (logdir, fn), 'w') as fp:
            fp.write(Builder.format_params(params))
        return fn

    @staticmethod
    def format_params(params):
        keys = sorted(params.keys())
        l = ["%s = %s" % (k, params[k]) for k in keys]
        return '\n'.join(l) + '\n'

    @staticmethod
    def name_hash(name, params, chars=8):
        param_s = Builder.format_params(params)
        param_h = hashlib.sha1(param_s).hexdigest()[:chars]
        return name + '-' + param_h
