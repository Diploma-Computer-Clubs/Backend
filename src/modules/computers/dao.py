from src.shared.dao.base import BaseDAO
from src.modules.computers.model import Computer

class ComputerDAO(BaseDAO):
    model = Computer