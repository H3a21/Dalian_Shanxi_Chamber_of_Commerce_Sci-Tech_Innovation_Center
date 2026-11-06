"""
MongoDB 适配器层 - 提供类似 SQLAlchemy 的查询接口
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from .extensions import get_mongodb, init_mongodb
from flask import current_app


class MongoQuery:
    """模拟 SQLAlchemy 查询接口的适配器"""

    def __init__(self, collection, model_class=None):
        self.collection = collection
        self.model_class = model_class
        self._filter = {}
        self._sort = []
        self._limit = None
        self._skip = None

    def filter_by(self, **kwargs):
        """模拟 filter_by - 添加相等条件"""
        for key, value in kwargs.items():
            if value is not None:
                self._filter[key] = value
        return self

    def filter(self, *args):
        """
        模拟 filter（简化版）
        注意：这里不支持复杂的 SQLAlchemy 表达式，只支持基本条件
        对于复杂条件，需要在业务逻辑中直接使用 MongoDB 查询
        """
        # 这里可以扩展以支持简单表达式，但暂时留空
        # 调用者应直接使用 MongoDB 查询语法
        return self

    def order_by(self, *args):
        """模拟 order_by"""
        for arg in args:
            if hasattr(arg, 'desc'):
                # 例如：CustomerServiceSession.created_at.desc()
                field_name = arg.key if hasattr(arg, 'key') else str(arg)
                self._sort.append((field_name, DESCENDING))
            elif hasattr(arg, 'asc'):
                field_name = arg.key if hasattr(arg, 'key') else str(arg)
                self._sort.append((field_name, ASCENDING))
            else:
                # 假设是字符串字段名，默认升序
                self._sort.append((str(arg), ASCENDING))
        return self

    def limit(self, value):
        self._limit = value
        return self

    def offset(self, value):
        self._skip = value
        return self

    def all(self):
        """返回所有结果"""
        cursor = self.collection.find(self._filter)
        if self._sort:
            cursor = cursor.sort(self._sort)
        if self._skip:
            cursor = cursor.skip(self._skip)
        if self._limit:
            cursor = cursor.limit(self._limit)
        return [self._to_model(doc) for doc in cursor]

    def first(self):
        """返回第一个结果"""
        cursor = self.collection.find(self._filter)
        if self._sort:
            cursor = cursor.sort(self._sort)
        cursor = cursor.limit(1)
        try:
            doc = next(cursor)
            return self._to_model(doc)
        except StopIteration:
            return None

    def count(self):
        """返回计数"""
        return self.collection.count_documents(self._filter)

    def _to_model(self, doc):
        """将 MongoDB 文档转换为模型实例"""
        if self.model_class:
            return self.model_class.from_dict(doc)
        return doc

    def delete(self):
        """删除匹配的文档"""
        result = self.collection.delete_many(self._filter)
        return result.deleted_count


class MongoModel:
    """MongoDB 模型基类"""

    # 子类需要设置 _collection

    @classmethod
    def _ensure_collection_initialized(cls):
        """确保集合已初始化，如果未初始化则尝试初始化"""
        if hasattr(cls, '_collection') and cls._collection is not None:
            return True

        try:
            print(f"[WARN] MongoModel._ensure_collection_initialized: {cls.__name__} 的 _collection 未初始化，尝试初始化...")
            db = get_mongodb()
            print(f"[DEBUG] MongoModel._ensure_collection_initialized: 获取到数据库连接, db={db}, db.name={db.name if db else 'None'}")
            if hasattr(cls, 'init_collection'):
                cls.init_collection(db)
                print(f"[INFO] MongoModel._ensure_collection_initialized: {cls.__name__} 集合初始化成功")
                return True
            else:
                print(f"[ERROR] MongoModel._ensure_collection_initialized: {cls.__name__} 没有 init_collection 方法")
                return False
        except RuntimeError as e:
            # MongoDB未初始化错误，尝试使用current_app初始化MongoDB
            print(f"[WARN] MongoModel._ensure_collection_initialized: {e}，尝试使用current_app重新初始化MongoDB")
            try:
                app = current_app._get_current_object()
                print(f"[DEBUG] MongoModel._ensure_collection_initialized: 获取到current_app: {app}, config: {app.config.get('MONGODB_DB', '未设置')}")
                init_mongodb(app)
                print(f"[INFO] MongoModel._ensure_collection_initialized: 已重新初始化MongoDB")
                # 再次尝试获取数据库连接
                db = get_mongodb()
                if hasattr(cls, 'init_collection'):
                    cls.init_collection(db)
                    print(f"[INFO] MongoModel._ensure_collection_initialized: {cls.__name__} 集合初始化成功")
                    return True
            except Exception as inner_e:
                print(f"[ERROR] MongoModel._ensure_collection_initialized: 重新初始化MongoDB失败: {inner_e}")
                import traceback
                traceback.print_exc()
                return False
        except Exception as e:
            print(f"[ERROR] MongoModel._ensure_collection_initialized: 初始化集合失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def query(cls):
        """模拟 SQLAlchemy 的 query 属性"""
        cls._ensure_collection_initialized()
        return MongoQuery(cls._collection, cls)

    @classmethod
    def get(cls, id):
        """根据 ID 获取文档"""
        if not cls._ensure_collection_initialized():
            return None

        try:
            if isinstance(id, (int, str)):
                # 尝试转换为 ObjectId，如果失败则按原值查询
                try:
                    obj_id = ObjectId(str(id))
                    doc = cls._collection.find_one({'_id': obj_id})
                except (InvalidId, TypeError):
                    # 如果不是有效的 ObjectId，按原值查询
                    doc = cls._collection.find_one({'_id': id})
            else:
                doc = cls._collection.find_one({'_id': id})
            return cls.from_dict(doc) if doc else None
        except Exception as e:
            print(f"MongoModel.get error: {e}")
            return None

    @classmethod
    def find_one(cls, **kwargs):
        """根据条件查找单个文档"""
        if not cls._ensure_collection_initialized():
            return None

        doc = cls._collection.find_one(kwargs)
        return cls.from_dict(doc) if doc else None

    @classmethod
    def find(cls, **kwargs):
        """根据条件查找多个文档"""
        if not cls._ensure_collection_initialized():
            return []

        cursor = cls._collection.find(kwargs)
        return [cls.from_dict(doc) for doc in cursor]

    @classmethod
    def from_dict(cls, data):
        """从字典创建模型实例"""
        instance = cls()
        for key, value in data.items():
            # 将 created_at/updated_at 字符串统一转换为 datetime
            if key in ('created_at', 'updated_at') and isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                except (ValueError, TypeError):
                    pass
            setattr(instance, key, value)
        return instance

    def to_dict(self):
        """转换为字典（用于保存）"""
        data = {}
        for key in self.__dict__:
            # 排除以双下划线开头的 Python 内部属性
            if key.startswith('__'):
                continue
            value = getattr(self, key)
            if key == 'id' and value:
                # 将 'id' 属性映射到 '_id' 字段
                try:
                    data['_id'] = ObjectId(value)
                except (InvalidId, TypeError):
                    data['_id'] = value
            elif key == '_id':
                # 直接包含 '_id' 属性
                data['_id'] = value
            else:
                # 其他属性按原样包含
                data[key] = value
        return data

    def save(self):
        """保存文档（插入或更新）"""
        # 确保集合已初始化
        if not self.__class__._ensure_collection_initialized():
            return False

        data = self.to_dict()
        print(f"[DEBUG] MongoModel.save: 保存数据到集合 {self.__class__._collection.name if hasattr(self.__class__, '_collection') else 'None'}, 数据: {data}")
        if '_id' in data:
            # 使用 replace_one 并设置 upsert=True，确保无论文档是否存在都能正确保存
            result = self.__class__._collection.replace_one({'_id': data['_id']}, data, upsert=True)
            print(f"[DEBUG] MongoModel.save: 替换文档, matched_count={result.matched_count}, modified_count={result.modified_count}, upserted_id={result.upserted_id}")
            # 如果是新插入的文档（upserted_id存在），确保 self.id 被设置
            if result.upserted_id is not None:
                self.id = str(result.upserted_id)
            return result.matched_count > 0 or result.upserted_id is not None
        else:
            # 插入新文档
            result = self.__class__._collection.insert_one(data)
            self.id = str(result.inserted_id)
            print(f"[DEBUG] MongoModel.save: 插入新文档, inserted_id={result.inserted_id}")
            return True

    def delete(self):
        """删除当前文档"""
        doc_id = getattr(self, 'id', None) or getattr(self, '_id', None)
        if doc_id:
            try:
                obj_id = ObjectId(str(doc_id))
                result = self.__class__._collection.delete_one({'_id': obj_id})
                return result.deleted_count > 0
            except (InvalidId, TypeError):
                result = self.__class__._collection.delete_one({'_id': doc_id})
                return result.deleted_count > 0
        return False


# 全局 MongoDB 客户端（已迁移到 extensions.py）
# 请使用 extensions.init_mongodb() 和 extensions.get_mongodb()