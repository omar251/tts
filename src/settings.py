import os
import yaml

class AppSettings:
    def __init__(self):
        # Default values - these can be overridden by config file or environment variables
        self.input_file = 'examples/input.txt'
        self.translated_file = 'temp/translated.txt'
        self.output_directory = 'temp'
        # Default for special_characters - make it a list
        self.special_characters = ['.', '?', '!', ';', ':', '\n']
        self.delimiter = '***WORD_BOUNDARY***'
        # Default for a new setting: Default TTS voice
        self.tts_voice = ''
        # Default maximum characters per translation chunk
        self.max_translate_chars = 5000

        # Load configuration from file and environment variables
        self._load_config_file()
        self._load_env_variables()

    def _load_config_file(self, config_path='config.yaml'):
        """Loads settings from the config.yaml file."""
        # Look for config file in the project root (parent of src directory)
        src_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(src_dir)
        absolute_config_path = os.path.join(project_root, config_path)
        absolute_config_path = os.path.abspath(absolute_config_path)

        if os.path.exists(absolute_config_path):
            try:
                with open(absolute_config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if config:
                        # Use .get() with a default value to prevent KeyErrors
                        self.input_file = config.get('input_file', self.input_file)
                        self.translated_file = config.get('translated_file', self.translated_file)
                        self.output_directory = config.get('output_directory', self.output_directory)
                        # Ensure special_characters is treated as a list if specified
                        if isinstance(config.get('special_characters'), list):
                             self.special_characters = config.get('special_characters', self.special_characters)
                        self.delimiter = config.get('delimiter', self.delimiter)
                        self.tts_voice = config.get('tts_voice', self.tts_voice)
                        self.max_translate_chars = config.get('max_translate_chars', self.max_translate_chars)
            except yaml.YAMLError as e:
                print(f"Error reading config file {absolute_config_path}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while loading config file {absolute_config_path}: {e}")
        else:
            print(f"Configuration file not found at {absolute_config_path}. Using default settings.")


    def _load_env_variables(self):
        """Overrides settings with environment variables."""
        # Use specific prefixes for environment variables to avoid conflicts
        self.input_file = os.environ.get('TTS_INPUT_FILE', self.input_file)
        self.translated_file = os.environ.get('TTS_TRANSLATED_FILE', self.translated_file)
        self.output_directory = os.environ.get('TTS_OUTPUT_DIRECTORY', self.output_directory)
        # Handling environment variables for lists or complex types requires specific parsing logic
        # For simplicity, only overriding simple string types here.
        # To override special_characters from an env var, you'd need a format like ".,?,!,;"
        # and then split it into a list. This is more complex and left out for basic implementation.
        # Example (requires parsing):
        # env_special_chars = os.environ.get('TTS_SPECIAL_CHARACTERS')
        # if env_special_chars:
        #     self.special_characters = env_special_chars.split(',') # Assuming comma-separated
        self.delimiter = os.environ.get('TTS_DELIMITER', self.delimiter)
        self.tts_voice = os.environ.get('TTS_VOICE', self.tts_voice)
        self.max_translate_chars = int(os.environ.get('TTS_MAX_TRANSLATE_CHARS', str(self.max_translate_chars)))


# Instantiate settings to be imported and used throughout the application
settings = AppSettings()
