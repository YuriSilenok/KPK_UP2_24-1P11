"""
Сервис управления отделениями СПО (Department Service)
"""

from models import (
    init_db,
    create_department,
    get_department,
    update_department,
    delete_department,
    list_departments,
    Department
)

__all__ = [
    'init_db',
    'create_department',
    'get_department',
    'update_department',
    'delete_department',
    'list_departments',
    'Department'
]