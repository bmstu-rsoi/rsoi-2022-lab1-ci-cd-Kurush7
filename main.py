from qr_server.Server import MethodResult, QRContext
from qr_server.Config import QRYamlConfig
from qr_server.FlaskServer import FlaskServer

from src.repository import PersonRepository
from src.person_dtos import *


def list_persons(ctx: QRContext):
    persons = ctx.repository.get_persons()
    return MethodResult(PersonsDTO(persons))


def get_person(ctx: QRContext, id: int):
    person = ctx.repository.get_person(id)
    if person is None:
        return MethodResult('person not found', 400)
    return MethodResult(PersonDTO(**person))


def create_person(ctx: QRContext):
    data = ctx.json_data

    id = ctx.repository.create_person(data)
    if id is None:
        return MethodResult('failed to create person', 400)

    return MethodResult('ok', 201, headers={'Location': f'/api/v1/persons/{id}'})


def update_person(ctx: QRContext, id: int):
    data = ctx.json_data

    ok = ctx.repository.update_person(id, data)
    if not ok:
        return MethodResult('failed to update person', 400)
    person = ctx.repository.get_person(id)
    if person is None:
        return MethodResult('person not found', 404)

    return MethodResult(PersonDTO(**person))


def delete_person(ctx: QRContext, id: int):
    ok = ctx.repository.delete_person(id)
    if not ok:
        return MethodResult('failed to delete person', 404)
    return MethodResult('ok', 204)


class PersonServer(FlaskServer, PersonRepository):
    def __init__(self):
        super().__init__(400)


if __name__ == "__main__":
    config = QRYamlConfig()
    config.read_config('config.yaml')

    host = config['app']['host']
    port = config['app']['port']

    import os
    ON_HEROKU = os.environ.get('ITS_HEROKU')
    if ON_HEROKU:
        port = int(os.environ.get('PORT', 5000))

    server = PersonServer()
    server.init_server(config['app'])
    server.connect_repository(config['database'])

    if config['app']['logging']:
        server.configure_logger(config['app']['logging'])

    server.register_method('/api/v1/persons', list_persons, 'GET')
    server.register_method('/api/v1/persons/<id>', get_person, 'GET')
    server.register_method('/api/v1/persons', create_person, 'POST')
    server.register_method('/api/v1/persons/<id>', update_person, 'PATCH')
    server.register_method('/api/v1/persons/<id>', delete_person, 'DELETE')
    server.run(host, port)
