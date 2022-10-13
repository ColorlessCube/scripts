import time
import uuid

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Integer, String, Column, Float
import os
import re
from utils import get_dict_mapping

Session = sessionmaker(autocommit=False)
Base = declarative_base()

md_dir_path = ''
db_url = ''

db_papers = None
db_metas = None


def init_database():
    """
    Init database by given url.
    @return:
    """
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
        session.close()
        return res

    @classmethod
    def query_by_dict(cls, by_dict):
        session = Session()
        result = session.query(cls).filter_by(**by_dict).limit(1).first()
        session.close()
        if result:
            return result.to_dict()
        else:
            return None

    @classmethod
    def add(cls, data):
        session = Session()
        instance = cls()
        for key, value in data.items():
            setattr(instance, key, value)
        session.add(instance)
        session.commit()
        session.close()

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
    agree = Column(Integer())
    uuid = Column(Integer())

    @classmethod
    def update(cls, data):
        session = Session()
        session.query(cls).filter(cls.cid == data.get('cid')).update(data)
        session.commit()
        session.close()


class Metas(Base, ModelMixin):
    __tablename__ = 'blog_metas'

    mid = Column(Integer(), primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    type = Column(String(200), nullable=False)
    description = Column(String(255), nullable=False)
    count = Column(Integer(), nullable=True)
    order = Column(Integer(), nullable=True, default=0)
    parent = Column(Integer(), nullable=True, default=0)

    @classmethod
    def update(cls, data):
        session = Session()
        session.query(cls).filter(cls.mid == data.get('mid')).update(data)
        session.commit()
        session.close()


class Relationships(Base, ModelMixin):
    __tablename__ = 'blog_relationships'

    cid = Column(Integer(), nullable=True, primary_key=True)
    mid = Column(Integer(), nullable=True, primary_key=True)

    @classmethod
    def query_by_dict(cls, by_dict):
        res_list = []
        session = Session()
        result = session.query(cls).filter_by(**by_dict)
        session.close()
        for item in result:
            res_list.append(item.to_dict())
        return res_list

    @classmethod
    def delete(cls, by_dict):
        session = Session()
        session.query(cls).filter_by(**{
            'cid': by_dict.get('cid'),
            'mid': by_dict.get('mid')
        }).delete()
        session.commit()
        session.close()


class Fields(Base, ModelMixin):
    __tablename__ = 'blog_fields'

    cid = Column(Integer(), nullable=True, primary_key=True)
    name = Column(String(255), nullable=True)
    type = Column(String(255), nullable=True)
    str_value = Column(String(255), nullable=True)
    int_value = Column(Integer(), nullable=True, default=0)
    float_value = Column(Float(), nullable=True, default=0)

    @classmethod
    def add(cls, data):
        res = cls.query_by_dict({
            'cid': data.get('cid'),
            'name': data.get('name')
        })
        if res:
            if res.get('str_value') != data.get('str_value'):
                session = Session()
                session.query(cls).filter_by(**{
                    'cid': data.get('cid'),
                    'name': data.get('name')
                }).update(data)
                session.commit()
                session.close()
        else:
            super().add(data)


def get_md_info_list():
    md_list = []
    for dir_path, dir_names, file_names in os.walk(md_dir_path):
        for file in file_names:
            if file.endswith('.md'):
                file_path = os.path.join(dir_path, file)
                md_info = _get_md_info(file_path)
                if md_info:
                    md_list.append(md_info)
    return md_list


def _get_md_info(file_path):
    """
    Use RegExp to analysis markdown file.
    :param file_path:
    :return:
    """
    with open(file_path, 'r', encoding='utf-8') as md:
        text = md.read()
    pattern = re.compile(r'# (.*)\n\n>[ ]+标识符：(.*)\n>\n>[ ]+是否公开：(.*)\n>\n>[ ]+分类：(.*)\n>\n>[ ]+标签：(.*)\n\n([\s\S]*)')
    info = re.findall(pattern, text)
    if info:
        info = info[0]
        return {
            'title': info[0],
            'uuid': info[1],
            'publish': info[2] == '是',
            'category': re.split(r'[，, ]', info[3]),
            'tag': re.split(r'[，, ]', info[4]),
            'text': '<!--markdown-->' + info[5]
        }
    else:
        return None


def get_db_relation_dict():
    ls = Relationships.query_all()
    res_dict = {}
    for item in ls:
        cid = str(item.get('cid'))
        mid = item.get('mid')
        if res_dict.get(mid):
            res_dict[mid] += '-' + cid
        else:
            res_dict[mid] = cid
    return res_dict


def compare_paper(db_papers, local_papers):
    db_paper_uuid_dict = get_dict_mapping(db_papers, 'uuid')
    for local_paper in local_papers:
        if not local_paper.get('publish'):
            continue
        uuid_ = local_paper.get('uuid')
        db_paper = db_paper_uuid_dict.get(uuid_)
        update_content(db_paper, local_paper)
        update_meta(local_paper)
        update_field(local_paper)


def update_field(local_paper):
    tag_num = 0
    for tag in local_paper.get('tag'):
        if len(tag) >= 1:
            tag_num += 1
    db_content = Contents.query_by_dict({
        'uuid': local_paper.get('uuid')
    })
    cid = db_content.get('cid')

    Fields.add({'cid': cid, 'name': 'cover', 'type': 'str', 'str_value': ''})
    Fields.add({'cid': cid, 'name': 'hot', 'type': 'str', 'str_value': '1'})
    Fields.add({'cid': cid, 'name': 'copyright', 'type': 'str', 'str_value': '1'})
    Fields.add({'cid': cid, 'name': 'copyright_cc', 'type': 'str', 'str_value': 'one'})
    Fields.add({'cid': cid, 'name': 'tags', 'type': 'str', 'str_value': str(tag_num)})
    Fields.add({'cid': cid, 'name': 'excerpt', 'type': 'str', 'str_value': ''})
    Fields.add({'cid': cid, 'name': 'articleplo', 'type': 'str', 'str_value': '1'})
    Fields.add({'cid': cid, 'name': 'articleplonr', 'type': 'str', 'str_value': ''})
    Fields.add({'cid': cid, 'name': 'Overdue', 'type': 'str', 'str_value': 'close'})
    Fields.add({'cid': cid, 'name': 'Poster', 'type': 'str', 'str_value': '1'})


def update_meta(local_paper):
    db_content = Contents.query_by_dict({
        'uuid': local_paper.get('uuid')
    })
    local_categories = local_paper.get('category')
    local_tags = local_paper.get('tag')
    _update_meta(local_categories, db_content, 'category')
    _update_meta(local_tags, db_content, 'tag')


def _update_meta(meta_ls, db_content, meta_type):
    cid = db_content.get('cid')
    title = db_content.get('title')
    relation_dict = get_db_relation_dict()
    meta_name_dict = get_dict_mapping(db_metas, 'name')
    meta_mid_dict = get_dict_mapping(db_metas, 'mid')
    for meta in meta_ls:
        # 增加标签或分类信息
        if len(meta) <= 1:
            continue
        db_meta = meta_name_dict.get(meta)
        if db_meta:
            mid = db_meta.get('mid')
            cid_ls = relation_dict.get(mid)
            if cid_ls is None or str(cid) not in cid_ls:
                Relationships.add({
                    'cid': cid,
                    'mid': mid
                })
                db_meta['count'] += 1
                Metas.update(db_meta)
                print('Add ' + title + ' - ' + db_meta.get('name') + ' relation.')
        else:
            meta_data = {
                'name': meta,
                'slug': meta,
                'type': meta_type,
                'count': 1
            }
            Metas.add(meta_data)
            db_meta = Metas.query_by_dict({
                'name': meta
            })
            print('Add ' + meta + ' meta.')
            Relationships.add({
                'cid': cid,
                'mid': db_meta.get('mid')
            })
            print('Add ' + title + ' - ' + db_meta.get('name') + ' relation.')
    # 删除
    relations = Relationships.query_by_dict({
        'cid': cid
    })
    for relation in relations:
        db_meta = meta_mid_dict.get(relation.get('mid'))
        if db_meta.get('name') not in meta_ls and meta_type == db_meta.get('type'):
            Relationships.delete(relation)
            db_meta['count'] -= 1
            Metas.update(db_meta)
            print('Delete ' + title + ' - ' + db_meta.get('name') + ' relation.')


def update_content(db_content, local_content):
    local_text = local_content.get('text')
    local_title = local_content.get('title')
    if db_content:
        db_text = db_content.get('text')
        db_title = db_content.get('title')
        if local_text != db_text or db_title != local_title:
            db_content['title'] = local_title
            db_content['text'] = local_text
            db_content['modified'] = time.time()
            Contents.update(db_content)
            print('Update paper ' + local_title + '.')
    # 添加
    else:
        now = time.time()
        content_data = {
            'title': local_title,
            'created': now,
            'modified': now,
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
            'agree': 0,
            'uuid': local_content.get('uuid')
        }
        Contents.add(content_data)
        db_content = Contents.query_by_dict({
            'uuid': local_content.get('uuid')
        })
        db_content['slug'] = db_content.get('cid')
        Contents.update(db_content)
        print('Add paper ' + local_title + '.')
    return None


def main():
    init_database()
    local_papers = get_md_info_list()
    global db_papers, db_metas
    db_papers = Contents.query_all()
    db_metas = Metas.query_all()
    compare_paper(db_papers, local_papers)


# *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *

def init_uuid():
    """
    Add uuid for every paper in database.
    @return:
    """
    contents = Contents.query_all()
    for content in contents:
        if content.get('type') == 'post' and not content.get('uuid'):
            content['uuid'] = uuid.uuid4()
            Contents.update(content)


def sync_local_uuid():
    """
    @return:
    """
    for dir_path, dir_names, file_names in os.walk(md_dir_path):
        for file in file_names:
            if file.endswith('.md'):
                file_path = os.path.join(dir_path, file)
                with open(file_path, 'r', encoding='utf-8') as md:
                    text = md.read()
                pattern_without_uuid = re.compile(
                    r'# (.*)\n\n>[ ]+是否公开：(.*)\n>\n>[ ]+分类：(.*)\n>\n>[ ]+标签：(.*)\n\n([\s\S]*)')
                info = re.findall(pattern_without_uuid, text)
                if info:
                    md_info = info[0]
                    db_content = Contents.query_by_dict({
                        'title': md_info[0]
                    })
                    if db_content:
                        _uuid = db_content.get('uuid')
                        text = text.replace(md_info[0] + '\n\n> ', md_info[0] + '\n\n> ' + '标识符：' + _uuid + '\n>\n> ')
                        with open(file_path, 'w', encoding='utf-8') as md:
                            md.write(text)


if __name__ == '__main__':
    main()
