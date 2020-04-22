class Error(Exception):
    """ Error base class """
    pass

class FileNotFoundError(Error):
    """ Raised when the specified file cannot be found """
    pass

class FileNotCSVError(Error):
    """ Raised when a file's expected type is CSV but the actual type isn't """
    pass