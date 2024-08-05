import pytest

from bookrank.models import WorkSet, Work


@pytest.fixture()
def workset():
    return WorkSet.objects.create(name='test work set')


@pytest.fixture()
def work(workset):
    return Work.objects.create(work_set=workset, name='test work', uid='aaa')
