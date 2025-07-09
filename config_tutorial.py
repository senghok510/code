from configparser import ConfigParser
from collections.abc import Iterable





# allow us to parse the file(configuration file) that we pass to it and allow us to retrieve some information of the file easily


#file to parse
file = 'config.ini'
config = ConfigParser()
#read
config.read('config.ini')

# to access some information we can use:

config.sections()

# is_iterable = isinstance(config,Iterable)

# has len? 
# has_len = hasattr(config, "__len__")
 
 
config.add_section('bank')

config.set('bank', 'branch', 'hsbc')


with open(file,"w") as configfile:
    config.write(configfile)