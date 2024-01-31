#!/usr/bin/env python3

from six import with_metaclass


class BorgMeta(type):
    def __repr__(cls):
        if hasattr(cls, '_class_repr'):
            return getattr(cls, '_class_repr')()
        else:
            return super(BorgMeta, cls).__repr__()


class Borg(with_metaclass(BorgMeta, object)):
    __shared_state = None
    __master = None
    __master_permitting_update = False

    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls)
        if cls.__shared_state is None:
            cls.__shared_state = {}
        self.__dict__ = cls.__shared_state
        return self

    def __init__(self, *args, **kwargs):

        def init(*a, **k):
            raise AttributeError('this borg class can be reinitialized after having reset the current one')

        master = kwargs.pop('master', False)
        master_permitting_update = kwargs.pop('master_permitting_update', False)
        if not self.master_exists():
            self.__set_master_internal(master, master_permitting_update)
            self.init(*args, **kwargs)
            if self.is_master():
                self.init = init
        else:
            if master or master_permitting_update:
                raise ValueError('a master already exists')
            if self.master_permitting_update_exists():
                self.init_update(*args, **kwargs)

    def __repr__(self):
        class_name = self.__class__.__name__
        dictionary = ', '.join('{}'.format(repr(key)) for key in self.__dict__.keys())
        return '{}({{{}}})'.format(class_name, dictionary)

    @classmethod
    def _class_repr(cls):
        class_name = cls.__name__
        dictionary = ', '.join('{}'.format(repr(key)) for key in cls.__dict__.keys())
        return '{}({{{}}})'.format(class_name, dictionary)

    def init(self, *args, **kwargs):
        pass

    def init_update(self, *args, **kwargs):
        pass

    def master_exists(self):
        to_return = False
        if self.__class__.__master is not None:
            to_return = True
        return to_return

    def is_master(self):
        to_return = False
        if self.__class__.__master == id(self):
            to_return = True
        return to_return

    def master_permitting_update_exists(self):
        return self.__class__.__master_permitting_update

    def set_master(self):
        if not self.master_exists():
            self.__set_master_internal(True, False)

    def set_master_permitting_update(self):
        if not self.master_exists() or self.is_master():
            self.__set_master_internal(True, True)

    def __set_master_internal(self, master, master_permitting_update):
        self.__class__.__master_permitting_update = master_permitting_update
        if master_permitting_update == True or master == True:
            self.__class__.__master = id(self)

    def reset(self):
        if self.master_exists() and not self.is_master():
            raise AttributeError('this object has not the right to reset')
        self.__class__.__master = None
        self.__class__.__master_permitting_update = False
        self.__dict__.clear()
