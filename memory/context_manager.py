"""
Context Manager - Terry v6.1
Tracks conversation context for pronoun resolution and entity tracking
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger(__name__)


class ContextManager:
    """Manages conversation context for implicit understanding."""

    def __init__(self, context_timeout_minutes: int = 5):
        """
        Initialize Context Manager.

        Args:
            context_timeout_minutes: Minutes before context expires
        """
        self.context_timeout = timedelta(minutes=context_timeout_minutes)

        # Current entities in context
        self.entities = {}  # {entity_type: {name, value, timestamp}}

        # Last mentioned subject
        self.last_subject = None
        self.last_subject_time = None

        # Conversation history for pronoun resolution
        self.recent_commands = []  # List of recent command texts
        self.recent_responses = []  # List of recent responses

        # Last action performed
        self.last_action = None
        self.last_action_params = {}

        logger.info("Context Manager initialized")

    def update_context(self, command: str, response: str,
                      actions: Optional[List[Dict]] = None):
        """
        Update context from a command-response interaction.

        Args:
            command: User command
            response: Assistant response
            actions: Actions performed
        """
        now = datetime.now()

        # Store recent commands and responses (keep last 5)
        self.recent_commands.append(command)
        if len(self.recent_commands) > 5:
            self.recent_commands.pop(0)

        self.recent_responses.append(response)
        if len(self.recent_responses) > 5:
            self.recent_responses.pop(0)

        # Extract and store entities from command
        self._extract_entities(command, now)

        # Update last action if any
        if actions:
            self.last_action = actions[-1].get('type')
            self.last_action_params = actions[-1].get('params', {})

        # Clean expired context
        self._clean_expired_context(now)

    def resolve_pronouns(self, text: str) -> str:
        """
        Resolve pronouns and implicit references in text.

        Args:
            text: Text with potential pronouns

        Returns:
            Text with pronouns resolved
        """
        resolved = text.lower()

        # Resolve "eso" / "that" / "it"
        if any(word in resolved for word in ['eso', 'that', 'it', 'esto', 'this']):
            if self.last_subject:
                # Replace with last subject
                resolved = resolved.replace('eso', self.last_subject)
                resolved = resolved.replace('that', self.last_subject)
                resolved = resolved.replace('it', self.last_subject)
                resolved = resolved.replace('esto', self.last_subject)
                resolved = resolved.replace('this', self.last_subject)

        # Resolve "la/el anterior" / "the previous one"
        if 'anterior' in resolved or 'previous' in resolved:
            if self.last_subject:
                resolved = resolved.replace('la anterior', self.last_subject)
                resolved = resolved.replace('el anterior', self.last_subject)
                resolved = resolved.replace('the previous', self.last_subject)

        # Resolve "siguiente" with implicit context
        if resolved.strip() in ['siguiente', 'next', 'skip']:
            # If last action was media-related, assume media next
            if self.last_action and 'media' in self.last_action:
                resolved = 'siguiente canción'
            else:
                resolved = 'siguiente'

        # Resolve app references
        if 'abr' in resolved or 'open' in resolved:
            # "abre eso" with last app mentioned
            if any(word in resolved for word in ['eso', 'that', 'it']):
                if 'app' in self.entities:
                    app_name = self.entities['app']['value']
                    resolved = f"abre {app_name}"

        # Log resolution if changed
        if resolved != text.lower():
            logger.debug(f"Resolved: '{text}' → '{resolved}'")

        return resolved

    def get_context_for_command(self, command: str) -> Dict[str, Any]:
        """
        Get relevant context for processing a command.

        Args:
            command: User command

        Returns:
            Dictionary with context information
        """
        return {
            'last_subject': self.last_subject,
            'last_action': self.last_action,
            'last_action_params': self.last_action_params,
            'recent_commands': self.recent_commands[-3:],  # Last 3
            'recent_responses': self.recent_responses[-3:],
            'entities': self.entities,
            'has_music_context': self._has_music_context(),
            'has_app_context': 'app' in self.entities
        }

    def add_entity(self, entity_type: str, entity_name: str,
                   entity_value: Any = None):
        """
        Explicitly add an entity to context.

        Args:
            entity_type: Type of entity (app, song, person, location, etc.)
            entity_name: Name/description of entity
            entity_value: Optional value
        """
        self.entities[entity_type] = {
            'name': entity_name,
            'value': entity_value or entity_name,
            'timestamp': datetime.now()
        }

        # Update last subject
        self.last_subject = entity_name
        self.last_subject_time = datetime.now()

    def clear_context(self):
        """Clear all context (useful for explicit reset)."""
        self.entities.clear()
        self.last_subject = None
        self.last_subject_time = None
        self.recent_commands.clear()
        self.recent_responses.clear()
        self.last_action = None
        self.last_action_params = {}
        logger.info("Context cleared")

    def _extract_entities(self, text: str, timestamp: datetime):
        """
        Extract entities from text and add to context.

        Args:
            text: Text to extract from
            timestamp: When this was said
        """
        text_lower = text.lower()

        # Extract app names
        common_apps = ['safari', 'chrome', 'firefox', 'music', 'spotify',
                      'notes', 'mail', 'calendar', 'messages', 'vscode',
                      'code', 'terminal', 'iterm']

        for app in common_apps:
            if app in text_lower:
                self.entities['app'] = {
                    'name': app,
                    'value': app,
                    'timestamp': timestamp
                }
                self.last_subject = app
                self.last_subject_time = timestamp
                break

        # Extract song/artist mentions (simple heuristic)
        if any(word in text_lower for word in ['canción', 'song', 'artista', 'artist', 'álbum', 'album']):
            # Try to extract the name after these keywords
            for keyword in ['canción', 'song']:
                if keyword in text_lower:
                    parts = text_lower.split(keyword)
                    if len(parts) > 1:
                        potential_name = parts[1].strip().split()[0:3]  # First 3 words
                        name = ' '.join(potential_name)
                        if name:
                            self.entities['song'] = {
                                'name': name,
                                'value': name,
                                'timestamp': timestamp
                            }

    def _has_music_context(self) -> bool:
        """Check if current context is music-related."""
        if self.last_action and 'media' in self.last_action:
            return True

        if 'song' in self.entities:
            age = datetime.now() - self.entities['song']['timestamp']
            if age < self.context_timeout:
                return True

        return False

    def _clean_expired_context(self, now: datetime):
        """
        Remove expired entities from context.

        Args:
            now: Current time
        """
        expired_keys = []

        for key, entity in self.entities.items():
            age = now - entity['timestamp']
            if age > self.context_timeout:
                expired_keys.append(key)

        for key in expired_keys:
            del self.entities[key]
            logger.debug(f"Expired entity: {key}")

        # Clean last subject if too old
        if self.last_subject_time:
            age = now - self.last_subject_time
            if age > self.context_timeout:
                self.last_subject = None
                self.last_subject_time = None


# Singleton instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """
    Get the singleton ContextManager instance.

    Returns:
        ContextManager instance
    """
    global _context_manager

    if _context_manager is None:
        try:
            from config.settings import settings
            timeout = settings.get("context_tracking", {}).get("timeout_minutes", 5)
            _context_manager = ContextManager(context_timeout_minutes=timeout)
        except Exception as e:
            logger.warning(f"Could not load settings for context manager: {e}")
            _context_manager = ContextManager()

    return _context_manager
