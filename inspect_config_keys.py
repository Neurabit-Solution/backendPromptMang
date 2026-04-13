import os
from jproperties import Properties

def test_config():
    configs = Properties()
    config_path = '/home/mritunjay/Desktop/backendPromptMang/config.properties'
    
    if os.path.exists(config_path):
        with open(config_path, 'rb') as config_file:
            configs.load(config_file)
            
    print("Keys found in properties:")
    for key in configs.keys():
        print(f"'{key}'")

if __name__ == "__main__":
    test_config()
