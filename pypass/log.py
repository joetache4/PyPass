import logging

def configure_logging(file):		
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.propagate = 0
    
	# Format
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y/%m/%d %H:%M:%S")
    
	# Setup console logging
    #ch = logging.StreamHandler()
    #ch.setLevel(logging.DEBUG)
    #ch.setFormatter(formatter)
    #logger.addHandler(ch)
    
	# Setup file logging as well
    fh = logging.FileHandler(file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)