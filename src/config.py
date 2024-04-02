import json

class ConfigManager:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as config_file:
            return json.load(config_file)

    def save_config(self):
        with open(self.config_path, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)
        print("Configuration saved.")

    def update_username(self, user_name):
        new_user_name = input("Enter your new user name: ").strip()
        if new_user_name:  # Check if the user actually entered something
            user_name = new_user_name
            self.config['user_name'] = new_user_name
            self.save_config()  # Save the updated configuration
            print(f"Username updated to {new_user_name}.")
            
        else:
            print("Username update cancelled.")
        return user_name