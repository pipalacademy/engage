from typing import Union, List


class _SingleOrList:
    def __getitem__(self, typ):
        return Union[typ, List[typ]]


# to patch __getitem__, we need an object of a custom class
# (otherwise, we'd be performing [] on an object of type 'type')
SingleOrList = _SingleOrList()

PathString = Union[str, os.PathLike]
