import copy
import json

import pytest
from qr_server import IQRRepository

from src.repository import IPersonRepository
from .test_tools import ContextCreator, equal_dicts

import main as service


class MockPersonRepository(IPersonRepository, IQRRepository):
    def __init__(self, filename='src/tests/data/persons.json'):
        with open(filename) as f:
            self.data = json.load(f)
        self.max_id = max([x['id'] for x in self.data])

    def connect_repository(self, config):
        pass

    def get_persons(self):
        return copy.deepcopy(self.data)

    def get_person(self, id):
        for x in self.data:
            if x['id'] == id:
                return copy.deepcopy(x)
        return None

    def create_person(self, data):
        if len(data) != 4:
            return None

        d = copy.deepcopy(data)
        d['id'] = self.max_id + 1
        self.max_id += 1
        self.data.append(d)
        return d['id']

    def update_person(self, id, data):
        if id not in [x['id'] for x in self.data]:
            return False

        for x in self.data:
            if x['id'] == id:
                x.update(data)

        return True

    def delete_person(self, id):
        if id not in [x['id'] for x in self.data]:
            return False
        self.data.pop(id)
        return True


def create_context(json_data=None):
    ctx = ContextCreator() \
        .context(json_data) \
        .with_repository(MockPersonRepository()) \
        .build()
    return ctx


# @pytest.mark.parametrize("float_input", [-10, -1, -0.001, -1e-8, 1+1e-8,2, 1000])
# @pytest.fixture(params=[0., 1e-10, 1e-7, 1e-5, 0.12345678, 0.1234567891234, 0.125, 1/3., 0.35564123, 0.5, 0.75, 0.9, 0.9999999, 1.])
# def float_input(request):
#    return request.param


@pytest.mark.unit
class TestGetAll:
    def test_success(self):
        ctx = create_context()
        res = service.list_persons(ctx)
        assert res.status_code == 200
        assert len(res.result) == 4


@pytest.mark.unit
class TestGet:
    def test_existing_id(self):
        ctx = create_context()
        res = service.get_person(ctx, 1)
        assert res.status_code == 200
        assert set(res.result.keys()) == set(['id', 'age', 'name', 'address', 'work'])

    def test_not_found_id(self):
        ctx = create_context()
        res = service.get_person(ctx, 100)
        assert res.status_code == 400


@pytest.mark.unit
class TestCreate:
    def test_success(self):
        ctx = create_context({'name': 'a', 'age': 1, 'address': 'a', 'work': 'a'})
        res = service.create_person(ctx)
        assert res.status_code == 201
        assert res.headers['Location'] == '/api/v1/persons/5'

    def test_missing_data(self):
        ctx = create_context({'name': 'a', 'age': 1})
        res = service.get_person(ctx, 100)
        assert res.status_code == 400

    def test_empty_body(self):
        ctx = create_context()
        res = service.get_person(ctx, 100)
        assert res.status_code == 400


@pytest.mark.unit
class TestDelete:
    def test_deleted(self):
        ctx = create_context()
        res = service.delete_person(ctx, 1)
        assert res.status_code == 204

        res = service.list_persons(ctx)
        assert res.status_code == 200
        assert len(res.result) == 3

    def test_not_found(self):
        ctx = create_context()
        res = service.delete_person(ctx, 100)
        assert res.status_code == 404


@pytest.mark.unit
class TestUpdate:
    user1 = {
        "id": 1,
        "name": "user1",
        "age": 10,
        "address": "address1",
        "work": "work1"
    }

    def test_update_ok(self):
        upd = {'name': 'updated'}
        ctx = create_context(upd)
        res = service.update_person(ctx, 1)

        assert res.status_code == 200
        user2 = copy.deepcopy(self.user1)
        user2.update(upd)
        assert equal_dicts(res.result, user2)

    def test_bad_id(self):
        ctx = create_context({'name': 'a', 'age': 1})
        res = service.update_person(ctx, 100)
        assert res.status_code == 400

    def test_empty_body(self):
        ctx = create_context({})
        res = service.update_person(ctx, 1)
        assert res.status_code == 200
        assert equal_dicts(res.result, self.user1)
