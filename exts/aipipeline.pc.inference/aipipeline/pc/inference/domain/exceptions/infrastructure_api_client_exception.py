class ApplicationError(Exception):
    def __init__(self, message = "An error occured"):
        self.message = message
        super().__init__(self.message)
        
class ClientException(ApplicationError):

    def __init__(self, message = "Client Exception", additional_info = ""):
        self.message = message + " " + additional_info
        self.status_code : int = 400
        super().__init__(message=self.message)

class NotFoundException(ApplicationError):
        def __init__(self, message : str, additional_info = ""):
            self.message = message + " " + additional_info
            self.status_code = 404
            super.__init__(message=self.message)
