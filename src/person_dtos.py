from qr_server.dto_converter import *


@dataclass
class PersonDTO(QRDTO):
    id: int
    name: str
    age: str
    address: str
    work: str


class PersonsDTO(ArrayQRDTO(PersonDTO)):
    pass
