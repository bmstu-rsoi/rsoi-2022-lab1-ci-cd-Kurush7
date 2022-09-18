from abc import abstractmethod
from functools import reduce

import qr_server.Repository as rep


class IPersonRepository:
    @abstractmethod
    def get_persons(self): pass

    @abstractmethod
    def get_person(self, id): pass

    @abstractmethod
    def create_person(self, data): pass

    @abstractmethod
    def update_person(self, id, data): pass

    @abstractmethod
    def delete_person(self, id): pass


class PersonRepository(IPersonRepository, rep.QRRepository):
    def __init__(self):
        super().__init__()

    def get_persons(self):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')
        persons = self.db.select(self.db.persons).all()
        return persons

    def get_person(self, id):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')
        person = self.db.select(self.db.persons).where(id=id).one()
        return person

    def create_person(self, data):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')
        if not self._check_fields(data, need_full=True):
            raise Exception('Can\'t create person: missing or incorrect fields')

        p = self.db.persons
        fields = list(p.meta['fields'].keys())
        fields.remove('id')
        data = self.db.insert(p, *[p.__dict__[f] for f in fields], auto_commit=True) \
            .values([data[f] for f in fields]) \
            .returning(p.id).one()
        return data['id']

    def update_person(self, id, data):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')
        if not self._check_fields(data):
            raise Exception('Can\'t update person: incorrect fields')

        p = self.db.persons
        ok = self.db.update(p, auto_commit=True).set(**data).where(id=id).exec()
        if not ok:
            raise Exception('Failed to update person')
        return ok

    def delete_person(self, id):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')

        ok = self.db.delete(self.db.persons, auto_commit=True).where(id=id).exec()
        return ok

    def _check_fields(self, data, need_full=False):
        fields = self.db.persons.meta['fields']
        field_names = list(fields.keys())
        field_names.remove('id')
        ok = reduce(lambda ok, f: ok & (f in field_names), data, True)
        if need_full:
            ok &= len(data) == len(field_names)
        return ok
