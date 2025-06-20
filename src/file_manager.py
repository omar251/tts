# file_manager.py
import os
import logging
from .logging_utils import VERBOSE, vprint

logger = logging.getLogger(__name__)

class FileManager:
    def create_output_directory(self, directory: str) -> None:
        vprint(f"[FileManager] Creating output directory: {directory}")
        os.makedirs(directory, exist_ok=True)
        vprint(f"[FileManager] Output directory ready.")

    def cleanup_temp_files(self, output_file: str) -> None:
        try:
            directory = os.path.dirname(output_file)
            vprint(f"[FileManager] Cleaning up temporary files in: {directory} (prefix: {os.path.basename(output_file)})")
            for file in os.listdir(directory):
                if file.startswith(os.path.basename(output_file)):
                    vprint(f"[FileManager] Removing file: {file}")
                    os.remove(os.path.join(directory, file))
            vprint(f"[FileManager] Cleanup complete.")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    manager = FileManager()

    # Test creating directory
    test_dir = "test_output"
    manager.create_output_directory(test_dir)
    print(f"Created directory: {test_dir}")

    # Test cleanup
    test_files = ["test_output_1.txt", "test_output_2.txt", "unrelated_file.txt"]
    for file in test_files:
        with open(os.path.join(test_dir, file), 'w') as f:
            f.write("Test content")

    print("Created test files:")
    print(os.listdir(test_dir))

    manager.cleanup_temp_files(os.path.join(test_dir, "test_output"))

    print("After cleanup:")
    print(os.listdir(test_dir))

    # Clean up the test directory
    import shutil
    shutil.rmtree(test_dir)
