import logging


class RemoveExcInfo(logging.Filter):
    def filter(self, record: logging.LogRecord):
        """Remove exception information.
        If exception information is present it will always be dumped to log, alongside msg which may be undesirable."""
        record.exc_info = None
        record.exc_text = None
        return True


class InfoOrLower(logging.Filter):
    def filter(self, record: logging.LogRecord):
        """Only allow messages with INFO or DEBUG level to get through."""
        if record.levelname in ('INFO', 'DEBUG'):
            return True
        else:
            return False



class WarningOrLower(logging.Filter):
    def filter(self, record: logging.LogRecord):
        """Only allow messages with WARNING, INFO or DEBUG level to get through."""
        if record.levelname in ('INFO', 'DEBUG', 'WARNING', 'WARN'):
            return True
        else:
            return False
