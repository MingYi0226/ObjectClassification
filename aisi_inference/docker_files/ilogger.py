import json
import logging
from datetime import datetime
import os

path = '/app/logs'

# Check whether the specified path exists or not
isExist = os.path.exists(path)

if not isExist:
    # Create a new directory because it does not exist
    os.makedirs(path)
    print("The new directory is created!")


class Logger():
    """Implementing the Modified logs using logging Module."""

    def __init__(self):
        """Initializing logger."""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        timestamp = datetime.now().strftime('%Y-%m-%d')
        self.filename = path+"/file"+timestamp+".log"

    def jsonwriter(self, message):
        """Save json to file."""
        f = open(self.filename, "a")
        f.write(json.dumps(message)+"\n")
        f.close()

    def parse_input(self, message_dict, log_type):
        """Extracting Input and adding Parameters."""
        message_dict["Type"] = log_type
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message_dict["Timestamp"] = timestamp
        self.jsonwriter(message_dict)
        return message_dict

    def info(self, message):
        """Log a info-level message."""
        input_json = {"Message": message}
        message = self.parse_input(input_json, "Info")
        logging.info(message)

    def debug(self, message):
        """Log a debug-level message."""
        input_json = {"Message": message}
        message = self.parse_input(input_json, "Debug")
        logging.debug(message)

    def warning(self, message):
        """Log a warning-level message."""
        input_json = {"Message": message}
        message = self.parse_input(input_json, "Warning")
        logging.warning(message)

    def error(self, message):
        """Log an error-level message."""
        input_json = {"Message": message}
        message = self.parse_input(input_json, "Error")
        logging.error(message)

logger = Logger()