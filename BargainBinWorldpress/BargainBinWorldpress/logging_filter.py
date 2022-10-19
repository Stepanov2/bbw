import logging


class FirstLineFilter(logging.Filter):
    def filter(self, record):
        try:
            record.first_line_of_message = '#### ' + str(len(record.message.splitlines()[0]))
        except AttributeError:
            record.first_line_of_message = '???'
        return True
