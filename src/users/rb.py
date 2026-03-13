from pygments.lexers import data


class RBUser:
    def __init__(self, user_id: int | None = None,
                phone_number: str | None = None,
                full_name: str | None = None,
                password_hash: str | None = None,
                reputation: int | None = None):
        self.id = user_id
        self.phone_number = phone_number
        self.full_name = full_name
        self.password_hash = password_hash
        self.reputation = reputation


    def to_dict(self) -> dict:
        data = {'id': self.id, 'phone_number': self.phone_number, 'full_name': self.full_name,
                'password_hash': self.password_hash, 'reputation': self.reputation}
        # Создаем копию словаря, чтобы избежать изменения словаря во время итерации
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data