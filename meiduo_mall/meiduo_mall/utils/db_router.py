
# 数据库读写路由
class MasterSlaveDBRouter(object):
    def db_for_read(self, model, **hints):
        # 读
        return 'slave'

    def db_for_write(self, model, **hints):
        # 写
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # 是否允许关联操作
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        #
        return None

class MasterSlaveDBRouter2(object):
    def db_for_read(self, model, **hints):
        # 读
        return 'slave'

    def db_for_write(self, model, **hints):
        # 写
        return 'default'

    def allow_relation(self, obj1, obj2, **hins):
        # 是否允许关联操作
        return True




