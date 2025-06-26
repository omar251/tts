# Singleton Pattern Implementation for Unified File Management

## Problem

The original implementation of the `UnifiedFileManager` class created multiple session directories for what should be a single logical session. This happened because each component (TTSApplication, TTSService, TTSGenerator) created its own instance of the file manager with a unique session ID.

## Solution

We implemented a singleton pattern to ensure that only one instance of `UnifiedFileManager` exists across the entire application, regardless of how many times it's instantiated.

### Key Changes

1. **Singleton Implementation**:
   ```python
   class UnifiedFileManager:
       # Singleton instance
       _instance = None
       
       def __new__(cls, base_temp_dir: str = "temp"):
           """Implement singleton pattern."""
           if cls._instance is None:
               cls._instance = super(UnifiedFileManager, cls).__new__(cls)
               cls._instance._initialized = False
           return cls._instance
   ```

2. **One-Time Initialization**:
   ```python
   def __init__(self, base_temp_dir: str = "temp"):
       # Only initialize once (singleton pattern)
       if not getattr(self, '_initialized', False):
           # Initialize directories, session ID, etc.
           self._initialized = True
       else:
           vprint(f"[UnifiedFileManager] Reusing existing session: {self.session_id}")
   ```

3. **Updated Tests**:
   - Added tests to verify the singleton pattern works correctly
   - Ensured the same session ID is used across different components

## Benefits

1. **Single Session Directory**: All components now use the same session directory
2. **Consistent File Organization**: All files are properly organized in one session
3. **Simplified Cleanup**: Only one session needs to be cleaned up
4. **Reduced Disk Usage**: No duplicate session directories
5. **Better Debugging**: All files from a run are in the same directory

## Testing

The singleton pattern was tested in two ways:

1. **Direct Testing**:
   ```python
   file_manager1 = UnifiedFileManager()
   file_manager2 = UnifiedFileManager()
   assert file_manager1.session_id == file_manager2.session_id
   ```

2. **Cross-Component Testing**:
   ```python
   service = TTSService()
   app = TTSApplication()
   assert app.file_manager.session_id == service.unified_file_manager.session_id
   ```

Both tests confirmed that the singleton pattern is working correctly, ensuring that all components use the same session directory.