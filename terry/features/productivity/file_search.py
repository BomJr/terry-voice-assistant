"""
File Search - Terry v6.1
Fast file search using macOS Spotlight
"""
import subprocess
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class FileSearch:
    """File search using macOS Spotlight (mdfind)."""

    def __init__(self, max_results: int = 10, use_spotlight: bool = True):
        """
        Initialize File Search.

        Args:
            max_results: Maximum number of results to return
            use_spotlight: Use Spotlight (mdfind) for search
        """
        self.max_results = max_results
        self.use_spotlight = use_spotlight

        logger.info("File Search initialized")

    def search(self, query: str, file_type: Optional[str] = None,
              directory: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for files.

        Args:
            query: Search query (filename or content)
            file_type: File extension filter (e.g., 'pdf', 'txt')
            directory: Limit search to directory

        Returns:
            List of file results with metadata
        """
        if self.use_spotlight:
            return self._search_with_spotlight(query, file_type, directory)
        else:
            return self._search_with_find(query, file_type, directory)

    def _search_with_spotlight(self, query: str, file_type: Optional[str] = None,
                               directory: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search using macOS Spotlight (mdfind).

        Args:
            query: Search query
            file_type: File extension filter
            directory: Limit search to directory

        Returns:
            List of file results
        """
        try:
            # Build mdfind command
            cmd = ['mdfind']

            # Add directory scope if specified
            if directory:
                cmd.extend(['-onlyin', os.path.expanduser(directory)])

            # Build query
            spotlight_query = f'kMDItemFSName == "*{query}*"cd'

            # Add file type filter if specified
            if file_type:
                file_type = file_type.lstrip('.')  # Remove leading dot
                spotlight_query += f' && kMDItemFSName == "*.{file_type}"cd'

            cmd.append(spotlight_query)

            # Execute search
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                logger.error(f"Spotlight search error: {result.stderr}")
                return []

            # Parse results
            paths = result.stdout.strip().split('\n')
            paths = [p for p in paths if p]  # Remove empty lines

            # Limit results
            paths = paths[:self.max_results]

            # Get file metadata
            results = []
            for path in paths:
                try:
                    file_path = Path(path)
                    if file_path.exists():
                        stat = file_path.stat()

                        results.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'directory': str(file_path.parent),
                            'size_bytes': stat.st_size,
                            'size_kb': round(stat.st_size / 1024, 2),
                            'modified': stat.st_mtime,
                            'extension': file_path.suffix
                        })
                except Exception as e:
                    logger.debug(f"Error getting metadata for {path}: {e}")

            logger.info(f"Spotlight found {len(results)} files for '{query}'")
            return results

        except subprocess.TimeoutExpired:
            logger.error("Spotlight search timeout")
            return []
        except Exception as e:
            logger.error(f"Error in Spotlight search: {e}")
            return []

    def _search_with_find(self, query: str, file_type: Optional[str] = None,
                         directory: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search using Unix find command (fallback).

        Args:
            query: Search query
            file_type: File extension filter
            directory: Limit search to directory

        Returns:
            List of file results
        """
        try:
            # Build find command
            search_dir = os.path.expanduser(directory) if directory else os.path.expanduser('~')

            cmd = ['find', search_dir, '-type', 'f', '-iname', f'*{query}*']

            # Add file type filter
            if file_type:
                file_type = file_type.lstrip('.')
                cmd.extend(['-name', f'*.{file_type}'])

            # Limit results
            cmd.extend(['-maxdepth', '5'])  # Don't go too deep

            # Execute search
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                logger.error(f"Find search error: {result.stderr}")
                return []

            # Parse results
            paths = result.stdout.strip().split('\n')
            paths = [p for p in paths if p][:self.max_results]

            # Get file metadata
            results = []
            for path in paths:
                try:
                    file_path = Path(path)
                    if file_path.exists():
                        stat = file_path.stat()

                        results.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'directory': str(file_path.parent),
                            'size_bytes': stat.st_size,
                            'size_kb': round(stat.st_size / 1024, 2),
                            'modified': stat.st_mtime,
                            'extension': file_path.suffix
                        })
                except Exception as e:
                    logger.debug(f"Error getting metadata for {path}: {e}")

            logger.info(f"Find found {len(results)} files for '{query}'")
            return results

        except subprocess.TimeoutExpired:
            logger.error("Find search timeout")
            return []
        except Exception as e:
            logger.error(f"Error in find search: {e}")
            return []

    def search_by_content(self, query: str, directory: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search file contents using Spotlight.

        Args:
            query: Content to search for
            directory: Limit search to directory

        Returns:
            List of files containing the query
        """
        try:
            # Build mdfind command for content search
            cmd = ['mdfind']

            # Add directory scope if specified
            if directory:
                cmd.extend(['-onlyin', os.path.expanduser(directory)])

            # Search in content
            spotlight_query = f'kMDItemTextContent == "*{query}*"cd'
            cmd.append(spotlight_query)

            # Execute search
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                logger.error(f"Content search error: {result.stderr}")
                return []

            # Parse results
            paths = result.stdout.strip().split('\n')
            paths = [p for p in paths if p][:self.max_results]

            # Get file metadata
            results = []
            for path in paths:
                try:
                    file_path = Path(path)
                    if file_path.exists():
                        stat = file_path.stat()

                        results.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'directory': str(file_path.parent),
                            'size_bytes': stat.st_size,
                            'size_kb': round(stat.st_size / 1024, 2),
                            'modified': stat.st_mtime,
                            'extension': file_path.suffix
                        })
                except Exception as e:
                    logger.debug(f"Error getting metadata for {path}: {e}")

            logger.info(f"Content search found {len(results)} files")
            return results

        except subprocess.TimeoutExpired:
            logger.error("Content search timeout")
            return []
        except Exception as e:
            logger.error(f"Error in content search: {e}")
            return []

    def open_file(self, file_path: str) -> bool:
        """
        Open file with default application.

        Args:
            file_path: Path to file

        Returns:
            True if successful, False otherwise
        """
        try:
            subprocess.run(
                ['open', file_path],
                capture_output=True,
                timeout=5
            )
            logger.info(f"Opened file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return False


# Singleton instance
_file_search: Optional[FileSearch] = None


def get_file_search() -> FileSearch:
    """
    Get the singleton FileSearch instance.

    Returns:
        FileSearch instance
    """
    global _file_search

    if _file_search is None:
        try:
            from terry.core.config.settings import settings
            config = settings.get("file_search", {})

            max_results = config.get("max_results", 10)
            use_spotlight = config.get("use_spotlight", True)

            _file_search = FileSearch(
                max_results=max_results,
                use_spotlight=use_spotlight
            )

        except Exception as e:
            logger.warning(f"Could not load file search settings: {e}")
            _file_search = FileSearch()

    return _file_search
