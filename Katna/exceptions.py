class KatnaExceptions(Exception):
    """Base class fot other exceptions"""
    pass


class MediapipeAutoflipBuildNotFound(KatnaExceptions):
    """
    Exception raised when mediapipe autoflip build file not found.
    """
    _DEFAULT_AUTOFLIP_BUILD_LOCATION = "/path/to/mediapipe/repo/bazel-bin/examples/desktop/autoflip"
    _ERROR = "Mediapipe autflip build dir not found. Autoflip build dir can be located here : %s" % _DEFAULT_AUTOFLIP_BUILD_LOCATION

    def __init__(self):
        self.message = self._ERROR
        super().__init__(self.message)

