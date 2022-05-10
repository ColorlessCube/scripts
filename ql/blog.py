import time

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Integer, String, Boolean, Column, DateTime, ForeignKey
import os
import re

Session = sessionmaker(autocommit=False)
Base = declarative_base()
md_dir_path = ''
db_url = ''


def init_database():
    engine = create_engine(db_url)
    Session.configure(binds={Base: engine})


class ModelMixin:
    def to_dict(self):
        return {column.name: getattr(self, column.name, None) for column in self.__table__.columns}

    @classmethod
    def query_all(cls):
        res = []
        session = Session()
        all_items = session.query(cls).all()
        for item in all_items:
            res.append(item.to_dict())
        return res

    @classmethod
    def add(cls, data):
        session = Session()
        instance = cls()
        for key, value in data.items():
            setattr(instance, key, value)
        session.add(instance)
        session.commit()

    @classmethod
    def update(cls, data):
        pass


class Contents(Base, ModelMixin):
    __tablename__ = 'blog_contents'

    cid = Column(Integer(), primary_key=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    created = Column(Integer(), nullable=False)
    modified = Column(Integer(), nullable=False)
    text = Column(String(), nullable=False)
    order = Column(Integer(), nullable=False)
    authorId = Column(Integer(), nullable=False)
    template = Column(String(32), nullable=False)
    type = Column(String(16), nullable=False)
    status = Column(String(16), nullable=False)
    password = Column(String(32), nullable=False)
    commentsNum = Column(Integer(), nullable=False)
    allowComment = Column(String(), nullable=False)
    allowPing = Column(String(), nullable=False)
    allowFeed = Column(String(), nullable=False)
    parent = Column(Integer(), nullable=False)
    agree = Column(Integer(), nullable=False)

    @classmethod
    def update(cls, data):
        session = Session()
        session.query(cls).filter(cls.cid == data.get('cid')).update(data)
        session.commit()


def get_md_path():
    md_dict = {}
    for dir_path, dir_names, file_names in os.walk(md_dir_path):
        for file in file_names:
            if file.endswith('.md'):
                file_name = file.split('.')[0]
                file_path = os.path.join(dir_path, file)
                md_dict[file_name] = file_path
    return md_dict


def get_db_content_dict(ls):
    res_dict = {}
    for item in ls:
        res_dict[item.get('title')] = item
    return res_dict


def process_local_text(local_text):
    md_prefix = '<!--markdown-->'
    pattern = re.compile(r'# .*\n\n')
    text_title = re.findall(pattern, local_text)[0]
    if local_text.startswith(text_title):
        local_text = local_text.replace(text_title, '')
    local_text = md_prefix + local_text
    return local_text


def compare_paper(db_dict, dir_dict):
    for title, file_path in dir_dict.items():
        with open(file_path, 'r', encoding='utf-8') as md:
            local_text = md.read()
            local_text = process_local_text(local_text)
        db_content = db_dict.get(title)
        # 判断是否更新
        if db_content:
            db_text = db_content.get('text')
            if local_text != db_text:
                db_content['text'] = local_text
                db_content['modified'] = time.time()
                Contents.update(db_content)
        # 添加
        else:
            content_data = {
                'title': title,
                'created': time.time(),
                'modified': time.time(),
                'text': local_text,
                'order': 0,
                'authorId': 1,
                'type': 'post',
                'status': 'publish',
                'commentsNum': 0,
                'allowComment': 1,
                'allowPing': 1,
                'allowFeed': 1,
                'parent': 0,
                'agree': 0
            }
            Contents.add(content_data)


if __name__ == '__main__':
    init_database()
    db_list = Contents.query_all()
    dir_dict = get_md_path()
    db_dict = get_db_content_dict(db_list)
    compare_paper(db_dict, dir_dict)
