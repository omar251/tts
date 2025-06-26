# file_manager.py
import os
import shutil
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import logging
from .logging_utils import VERBOSE, vprint

logger = logging.getLogger(__name__)

class UnifiedFileManager:
    """
    Unified file management system for all TTS artifacts and outputs.
    
    This class centralizes all file operations to ensure better data management,
    consistent naming, and efficient cleanup of temporary files.
    
    This class implements a singleton pattern to ensure only one instance exists
    across the application, preventing multiple session directories.
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls, base_temp_dir: str = "temp"):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(UnifiedFileManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, base_temp_dir: str = "temp"):
        """
        Initialize the unified file manager.
        
        Args:
            base_temp_dir: Base directory for all temporary files
        """
        # Only initialize once (singleton pattern)
        if not getattr(self, '_initialized', False):
            self.base_temp_dir = Path(base_temp_dir)
            self.session_id = self._generate_session_id()
            self.session_dir = self.base_temp_dir / f"session_{self.session_id}"
            
            # Create subdirectories for different types of artifacts
            self.audio_dir = self.session_dir / "audio"
            self.text_dir = self.session_dir / "text"
            self.translation_dir = self.session_dir / "translation"
            self.cache_dir = self.session_dir / "cache"
            
            self._setup_directories()
            
            # Track all files created in this session
            self.created_files: List[Path] = []
            self.file_metadata: Dict[str, Dict[str, Any]] = {}
            
            vprint(f"[UnifiedFileManager] Initialized session: {self.session_id}")
            vprint(f"[UnifiedFileManager] Session directory: {self.session_dir}")
            
            self._initialized = True
        else:
            vprint(f"[UnifiedFileManager] Reusing existing session: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID for this file manager instance."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"
    
    def _setup_directories(self) -> None:
        """Create all required directories."""
        directories = [
            self.base_temp_dir,
            self.session_dir,
            self.audio_dir,
            self.text_dir,
            self.translation_dir,
            self.cache_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            vprint(f"[UnifiedFileManager] Created directory: {directory}")
    
    def create_audio_file_path(self, prefix: str = "audio", chunk_id: Optional[int] = None) -> Tuple[str, str]:
        """
        Create paths for audio and corresponding text files.
        
        Args:
            prefix: Prefix for the filename
            chunk_id: Optional chunk identifier for multi-part audio
            
        Returns:
            Tuple of (audio_file_path, text_file_path)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        if chunk_id is not None:
            base_name = f"{prefix}_{timestamp}_chunk_{chunk_id:06d}"
        else:
            base_name = f"{prefix}_{timestamp}"
        
        audio_file = self.audio_dir / f"{base_name}.wav"
        text_file = self.text_dir / f"{base_name}.txt"
        
        # Track these files
        self.created_files.extend([audio_file, text_file])
        
        # Store metadata
        file_id = f"{prefix}_{timestamp}_{chunk_id if chunk_id is not None else 'single'}"
        self.file_metadata[file_id] = {
            "audio_file": str(audio_file),
            "text_file": str(text_file),
            "prefix": prefix,
            "chunk_id": chunk_id,
            "created_at": datetime.now().isoformat(),
            "session_id": self.session_id
        }
        
        vprint(f"[UnifiedFileManager] Created file paths - Audio: {audio_file}, Text: {text_file}")
        return str(audio_file), str(text_file)
    
    def create_translation_file_path(self, source_language: str = "auto", target_language: str = "en") -> str:
        """
        Create path for translation files.
        
        Args:
            source_language: Source language code
            target_language: Target language code
            
        Returns:
            Path to translation file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"translation_{source_language}_to_{target_language}_{timestamp}.txt"
        translation_file = self.translation_dir / filename
        
        self.created_files.append(translation_file)
        
        vprint(f"[UnifiedFileManager] Created translation file path: {translation_file}")
        return str(translation_file)
    
    def create_cache_file_path(self, cache_type: str, extension: str = ".json") -> str:
        """
        Create path for cache files (voices, etc.).
        
        Args:
            cache_type: Type of cache (e.g., 'voices', 'settings')
            extension: File extension
            
        Returns:
            Path to cache file
        """
        filename = f"{cache_type}_cache{extension}"
        cache_file = self.cache_dir / filename
        
        # Cache files are not tracked for cleanup as they should persist
        vprint(f"[UnifiedFileManager] Created cache file path: {cache_file}")
        return str(cache_file)
    
    def get_web_audio_url(self, audio_file_path: str) -> str:
        """
        Generate web-accessible URL for audio files.
        
        Args:
            audio_file_path: Full path to audio file
            
        Returns:
            Web-accessible URL
        """
        audio_path = Path(audio_file_path)
        relative_path = audio_path.relative_to(self.base_temp_dir)
        return f"/audio/{relative_path}"
    
    def cleanup_session_files(self, keep_cache: bool = True) -> int:
        """
        Clean up all files created in this session.
        
        Args:
            keep_cache: Whether to keep cache files
            
        Returns:
            Number of files cleaned up
        """
        cleanup_count = 0
        
        try:
            vprint(f"[UnifiedFileManager] Starting cleanup for session: {self.session_id}")
            
            for file_path in self.created_files:
                if file_path.exists():
                    try:
                        file_path.unlink()
                        cleanup_count += 1
                        vprint(f"[UnifiedFileManager] Removed file: {file_path}")
                    except OSError as e:
                        logger.warning(f"Could not remove file {file_path}: {e}")
            
            # Clean up empty directories (except cache if keeping it)
            directories_to_clean = [self.audio_dir, self.text_dir, self.translation_dir]
            if not keep_cache:
                directories_to_clean.append(self.cache_dir)
            
            for directory in directories_to_clean:
                if directory.exists() and not any(directory.iterdir()):
                    try:
                        directory.rmdir()
                        vprint(f"[UnifiedFileManager] Removed empty directory: {directory}")
                    except OSError:
                        pass
            
            # Remove session directory if empty
            if self.session_dir.exists() and not any(self.session_dir.iterdir()):
                try:
                    self.session_dir.rmdir()
                    vprint(f"[UnifiedFileManager] Removed session directory: {self.session_dir}")
                except OSError:
                    pass
            
            vprint(f"[UnifiedFileManager] Cleanup complete. Removed {cleanup_count} files.")
            
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")
        
        return cleanup_count
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up old session directories.
        
        Args:
            max_age_hours: Maximum age of sessions to keep in hours
            
        Returns:
            Number of sessions cleaned up
        """
        cleanup_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            vprint(f"[UnifiedFileManager] Cleaning up sessions older than {max_age_hours} hours")
            
            if not self.base_temp_dir.exists():
                return 0
            
            for item in self.base_temp_dir.iterdir():
                if item.is_dir() and item.name.startswith("session_"):
                    try:
                        # Check if directory is old enough
                        dir_age = current_time - item.stat().st_mtime
                        if dir_age > max_age_seconds:
                            shutil.rmtree(item)
                            cleanup_count += 1
                            vprint(f"[UnifiedFileManager] Removed old session: {item}")
                    except OSError as e:
                        logger.warning(f"Could not remove old session {item}: {e}")
            
            vprint(f"[UnifiedFileManager] Cleaned up {cleanup_count} old sessions")
            
        except Exception as e:
            logger.error(f"Error during old session cleanup: {e}")
        
        return cleanup_count
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session.
        
        Returns:
            Dictionary with session information
        """
        return {
            "session_id": self.session_id,
            "session_dir": str(self.session_dir),
            "audio_dir": str(self.audio_dir),
            "text_dir": str(self.text_dir),
            "translation_dir": str(self.translation_dir),
            "cache_dir": str(self.cache_dir),
            "files_created": len(self.created_files),
            "file_metadata": self.file_metadata
        }
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """
        Get disk usage information for the temp directory.
        
        Returns:
            Dictionary with disk usage information
        """
        try:
            total_size = 0
            file_count = 0
            
            if self.base_temp_dir.exists():
                for file_path in self.base_temp_dir.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        file_count += 1
            
            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "base_dir": str(self.base_temp_dir)
            }
        
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {"error": str(e)}

# Backward compatibility class
class FileManager:
    """Legacy FileManager class for backward compatibility."""
    
    def __init__(self):
        # Use the singleton instance
        self.unified_manager = UnifiedFileManager()
    
    def create_output_directory(self, directory: str) -> None:
        """Create output directory (legacy method)."""
        vprint(f"[FileManager] Creating output directory: {directory}")
        os.makedirs(directory, exist_ok=True)
        vprint(f"[FileManager] Output directory ready.")
    
    def cleanup_temp_files(self, output_file: str) -> None:
        """Clean up temporary files (legacy method)."""
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
