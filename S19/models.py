from peewee import *

db = SqliteDatabase('resource_pool.db')


class ResourcePool(Model):
    id = AutoField()
    name = CharField(max_length=200, null=False)
    type = CharField(max_length=100, null=False)
    quantity = IntegerField(null=False, default=1)
    location = CharField(max_length=255, null=True)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        database = db
        table_name = 'resource_pool'


def init_db():
    db.create_tables([ResourcePool], safe=True)


if __name__ == '__main__':
    init_db()