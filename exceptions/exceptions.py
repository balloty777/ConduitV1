class ConduitException(Exception):
    def __init__(self,msg:str):
        self.message=msg
        super().__init__(msg)

class ResourceNotFoundException(ConduitException):
    def __init__(self,msg:str):
        super().__init__(msg)

class ResourceAlreadyExist(ConduitException):
    def __init__(self,msg:str):
        super().__init__(msg)

class InvalidStateTransitionException(ConduitException):
    def __init__(self,msg:str):
        super().__init__(msg)

