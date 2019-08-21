"""
.. module:: Katna.decorators
    :platform: OS X
    :synopsis: This module has decorators for video and image modules 
"""
import os.path
import os
import sys
import errno
import functools
import inspect


class VideoDecorators(object):
    """File validation decorator
    
    Arguments:
        object {[type]} -- [description]
    
    Raises:
        FileNotFoundError: [Video File is missing]
    
    Returns:
        [boolean] -- [if the file exists and is valid]
    """

    @classmethod
    def validate_video(cls, decorated):
        """Validate if the input video is a valid file
        """

        @functools.wraps(decorated)
        def wrapper(*args, **kwargs):
            """ wrapper for decorated function
            
            Arguments:
                cls {VideoDecorators} -- [Video decorators class]
            
            Raises:
                FileNotFoundError: [If the file is missing]
            
            Returns:
                [function] -- [Decorated function]
            """
            func_args = inspect.getcallargs(decorated, *args, **kwargs)

            key = "file_path"

            if key not in func_args:
                raise Exception("File_path parameter is missing")
            else:
                f_path = func_args.get(key)

            if bool(f_path is None or os.path.isfile(f_path) is False):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f_path)
            else:
                return decorated(*args, **kwargs)

        return wrapper


class FileDecorators(object):
    """File validation decorator
    
    :raises FileNotFoundError: File or path is incorrect    
    """

    @classmethod
    def validate_file_path(cls, decorated):
        """Validate if the input path is a valid file or location

        :param decorated: decorated function
        :type decorated: function, required
        :return: function if the path is valid 
        :rtype: function object
        """

        @functools.wraps(decorated)
        def wrapper(*args, **kwargs):
            """ wrapper for decorated function. args and kwargs are standard function parameters.            
            """
            func_args = inspect.getcallargs(decorated, *args, **kwargs)

            key = "file_path"

            if key not in func_args:
                raise Exception("File_path parameter is missing")
            else:
                f_path = func_args.get(key)

            if bool(f_path is None or os.path.exists(f_path) is False):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f_path)
            else:
                return decorated(*args, **kwargs)

        return wrapper


def exception(logger):
    """
    A decorator that wraps the passed in function and logs 
    exceptions should one occur
    
    param logger: The logging object
    type logger: logger
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                # log the exception
                err = "There was an exception in  "
                err += func.__name__
                logger.exception(err, exc_info=True)
                # re-raise the exception
                raise

        return wrapper

    return decorator
