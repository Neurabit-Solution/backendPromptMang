import os
from jproperties import Properties

def test_config():
    configs = Properties()
    config_path = '/home/mritunjay/Desktop/backendPromptMang/config.properties'
    
    if os.path.exists(config_path):
        with open(config_path, 'rb') as config_file:
            configs.load(config_file)
            
    def get_conf(key, default=None):
        env_val = os.environ.get(key.upper())
        if env_val is not None:
            return env_val.strip() if isinstance(env_val, str) else env_val
        
        prop_val = configs.get(key)
        if prop_val is not None and prop_val.data is not None:
            return prop_val.data.strip() if isinstance(prop_val.data, str) else prop_val.data
        
        return default

    print(f"RAZORPAY_KEY_ID: '{get_conf('razorpay_key_id')}'")
    print(f"RAZORPAY_KEY_SECRET: '{get_conf('razorpay_key_secret')}'")
    print(f"CREDIT_PRICE_INR: '{get_conf('credit_price_inr')}'")

if __name__ == "__main__":
    test_config()
