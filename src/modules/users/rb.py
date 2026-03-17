from pygments.lexers import data


class RBUser:
    def __init__(self, phone_number: str | None = None):
        self.phone_number = phone_number


    def to_dict(self) -> dict:
        data = {'phone_number': self.phone_number}
        # Создаем копию словаря, чтобы избежать изменения словаря во время итерации
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data