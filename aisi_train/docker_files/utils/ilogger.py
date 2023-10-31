import os
import sys
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from time import time

class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, logfile_prefix="file", log_dir="./", datetime_suffix_format="%Y-%m-%d_%H:%M", when='midnight', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None):
        self.datetime_suffix_format = datetime_suffix_format
        self.log_dir = log_dir
        self.logfile_prefix = logfile_prefix
        super().__init__(
            filename=os.path.join(self.log_dir, f"{self.logfile_prefix}{datetime.now().strftime(self.datetime_suffix_format)}.log"),
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
            utc=utc,
            atTime=atTime
        )
        def custom_rotator(current_logfile_path, new_logfile_path):
            # Generate new Filename for log outputs
            self.baseFilename = os.path.join(self.log_dir, f"{self.logfile_prefix}{datetime.now().strftime(self.datetime_suffix_format)}.log")
            # Close previous Stream
            self.close()
            # Open new Stream with updated baseFilename
            self._open()
        # Set rotator value as a callable
        self.rotator = custom_rotator

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.

    @param dict fmt_dict: Key: logging format attribute pairs. Defaults to {"message": "message"}.
    @param str time_format: time.strftime() format string. Default: "%Y-%m-%dT%H:%M:%S"
    @param str msec_format: Microsecond formatting. Appended at the end. Default: "%s.%03d"
    """
    def __init__(self, fmt_dict: dict = None, time_format: str = "%Y-%m-%dT%H:%M:%S", msec_format: str = "%s.%03d"):
        self.fmt_dict = fmt_dict if fmt_dict is not None else {"message": "message"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def usesTime(self) -> bool:
        """
        Overwritten to look for the attribute in the format dict values instead of the fmt string.
        """
        return "asctime" in self.fmt_dict.values()

    def formatMessage(self, record) -> dict:
        """
        Overwritten to return a dictionary of the relevant LogRecord attributes instead of a string. 
        KeyError is raised if an unknown attribute is provided in the fmt_dict. 
        """
        return {fmt_key: record.__dict__[fmt_val] for fmt_key, fmt_val in self.fmt_dict.items()}

    def format(self, record) -> str:
        """
        Mostly the same as the parent's class method, the difference being that a dict is manipulated and dumped as JSON
        instead of a string.
        """
        record.message = record.getMessage()
        
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)

path = '/app/logs'

# Check whether the specified path exists or not
isExist = os.path.exists(path)

if not isExist:
    # Create a new directory because it does not exist
    os.makedirs(path)
    print("The new directory is created!")

timed_file_handler = CustomTimedRotatingFileHandler(
    logfile_prefix="file",
    log_dir=path,
    datetime_suffix_format="%Y-%m-%d",
    when="midnight",
    interval=1
)
json_formatter = JsonFormatter(
    { 
        "Message": "message",
        "Type": "levelname",
        "Timestamp": "asctime"
    },
    time_format="%Y-%m-%d %H:%M:%S"
)
timed_file_handler.setFormatter(json_formatter)

stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_formatter = logging.Formatter("%(levelname)s: [%(asctime)s] %(module)s => %(message)s")
stream_handler.setFormatter(stream_formatter)

logging.basicConfig(
    level=logging.WARNING,
    handlers=[stream_handler, timed_file_handler],
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.getLogger("app_wide").setLevel(logging.DEBUG)
logger = logging.getLogger("app_wide")