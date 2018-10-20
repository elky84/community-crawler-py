""":mod:`crawler.serializers` ---  Serializer for crawler data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import datetime


def payload_serializer(*, type: str, id: int = None, link: str, count: int,
                       title: str) -> dict:
    dic = {'type': type,
            'link': link,
            'count': count,
            'title': title,
            'date': datetime.datetime.now(tz=datetime.timezone.utc)
            }
    
    dic['id'] = id
    return dic
