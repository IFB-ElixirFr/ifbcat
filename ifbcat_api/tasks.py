import logging

import huey.contrib.djhuey
from tqdm import tqdm

from ifbcat_api import models

logger = logging.getLogger(__name__)


@huey.contrib.djhuey.periodic_task(huey.crontab(minute='0', hour='6', day='1'))
def update_tools_periodic_task():
    update_tools()


def update_tools():
    for tool in tqdm(models.Tool.objects.exclude(biotoolsID='')):
        try:
            tool.update_information_from_biotool()
        except Exception as e:
            logger.error(f'Failed with tool {tool}')
            break
