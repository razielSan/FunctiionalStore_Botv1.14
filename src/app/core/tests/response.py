from dataclasses import dataclass


@dataclass
class PasswordTest:
    type_passwrod: str
    step: int
    count_password: int
    len_password: int
