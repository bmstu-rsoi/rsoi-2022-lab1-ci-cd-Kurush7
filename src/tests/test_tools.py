from qr_server.Server import QRContext


def equal_dicts(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    shared_keys = d1_keys.intersection(d2_keys)
    same = set(o for o in shared_keys if d1[o] == d2[o])
    return len(same) == len(d1)


class ContextCreator:
    def __init__(self):
        self.data = None
        self.managers = []
        self.repo = None

    def context(self, json_data=None, params=None, headers=None, form=None, files=None):
        json_data = dict() if json_data is None else json_data
        params = dict() if params is None else params
        headers = dict() if headers is None else headers
        form = dict() if form is None else form
        files = dict() if files is None else files
        self.data = [json_data, params, headers, form, files]
        return self

    def with_repository(self, repository):
        self.repo = repository
        return self

    def build(self):
        ctx = QRContext(*self.data, repository=self.repo)
        for m in self.managers:
            ctx.add_manager(m.get_name(), m)
        return ctx
