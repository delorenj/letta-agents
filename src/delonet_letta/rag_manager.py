"""Manager for RAG folder synchronization with Letta."""

import logging
from pathlib import Path
from typing import Optional
from letta_client import Letta

from .config import RAGConfig
from .utils import handle_already_exists

logger = logging.getLogger(__name__)


class RAGManager:
    """Manages RAG folder synchronization for semantic search."""

    def __init__(self, client: Letta, config: RAGConfig):
        """
        Initialize the RAG manager.

        Args:
            client: Letta client instance
            config: RAG configuration
        """
        self.client = client
        self.config = config

    def get_or_create_folder(self, folder_name: Optional[str] = None) -> str:
        """
        Get existing folder or create a new one.

        Args:
            folder_name: Name of the folder (uses config default if None)

        Returns:
            Folder ID
        """
        folder_name = folder_name or self.config.folder_name

        # Try to find existing folder
        try:
            folders = self.client.folders.list()
            for folder in folders:
                if folder.name == folder_name:
                    logger.info(f"Found existing folder '{folder_name}' (ID: {folder.id})")
                    return folder.id
        except Exception as e:
            logger.warning(f"Could not list folders: {e}")

        # Create new folder
        logger.info(f"Creating new folder '{folder_name}'...")

        try:
            folder = self.client.folders.create(name=folder_name)
            logger.info(f"✅ Created folder '{folder_name}' (ID: {folder.id})")
            return folder.id
        except Exception as e:
            if handle_already_exists(str(e)):
                logger.info(f"🔹 Folder '{folder_name}' already exists")
                # Try to get the ID again
                folders = self.client.folders.list()
                for folder in folders:
                    if folder.name == folder_name:
                        return folder.id
            raise

    def should_include_file(self, file_path: Path) -> bool:
        """
        Check if a file should be included based on patterns.

        Args:
            file_path: Path to the file

        Returns:
            True if file should be included
        """
        # Check exclude patterns first
        for pattern in self.config.exclude_patterns:
            if file_path.match(pattern):
                return False

        # If no include patterns specified, include all
        if not self.config.include_patterns:
            return True

        # Check include patterns
        for pattern in self.config.include_patterns:
            if file_path.match(pattern):
                return True

        return False

    def sync_folder(
        self,
        local_folder: Optional[Path] = None,
        folder_name: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> tuple[int, int]:
        """
        Sync a local folder to Letta RAG storage.

        Args:
            local_folder: Local folder to sync (uses config default if None)
            folder_name: Letta folder name (uses config default if None)
            progress_callback: Optional callback(current, total, file_path)

        Returns:
            Tuple of (successful_uploads, failed_uploads)
        """
        local_folder = local_folder or self.config.local_folder
        folder_name = folder_name or self.config.folder_name

        if not local_folder:
            raise ValueError("No local folder specified")

        if not local_folder.exists():
            raise ValueError(f"Local folder does not exist: {local_folder}")

        # Get or create the Letta folder
        folder_id = self.get_or_create_folder(folder_name)

        # Collect all files to upload
        files_to_upload = []
        for file_path in local_folder.rglob("*"):
            if file_path.is_file() and self.should_include_file(file_path):
                files_to_upload.append(file_path)

        logger.info(f"Found {len(files_to_upload)} files to sync")

        # Upload files
        successful = 0
        failed = 0

        for idx, file_path in enumerate(files_to_upload, 1):
            try:
                # Calculate relative path for organization
                relative_path = file_path.relative_to(local_folder)

                # Upload to Letta (pass open file handle directly)
                with open(file_path, 'rb') as f:
                    self.client.folders.files.upload(
                        folder_id=folder_id,
                        file=f,
                    )

                successful += 1
                logger.debug(f"  ✅ Uploaded: {relative_path}")

                if progress_callback:
                    progress_callback(idx, len(files_to_upload), relative_path)

            except Exception as e:
                failed += 1
                logger.warning(f"  ❌ Failed to upload {file_path}: {e}")

        logger.info(
            f"✅ Folder sync complete: "
            f"{successful} uploaded, {failed} failed"
        )

        return successful, failed
