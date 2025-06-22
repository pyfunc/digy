"""
Authentication module for DIGY
Handles different authentication methods (SQL, WEB, IO, socket, etc.)
"""
import os
import json
import socket
import sqlite3
from typing import Dict, Any, Optional, Union
from pathlib import Path
from getpass import getpass

import requests
from rich.console import Console

console = Console()

class AuthProvider:
    """Base class for authentication providers"""
    
    def __init__(self, **kwargs):
        self.config = kwargs
    
    def authenticate(self, **kwargs) -> bool:
        """Authenticate with the provider
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement authenticate()")
    
    def get_credentials(self) -> Dict[str, Any]:
        """Get credentials after successful authentication
        
        Returns:
            Dict[str, Any]: Dictionary containing credentials
        """
        return {}


class SQLAuthProvider(AuthProvider):
    """SQL-based authentication"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connection = None
    
    def authenticate(self, **kwargs) -> bool:
        """Authenticate using SQL database"""
        db_path = self.config.get('db_path')
        if not db_path:
            console.print("[red]Database path not provided[/red]")
            return False
            
        username = input("Username: ")
        password = getpass("Password: ")
        
        try:
            self.connection = sqlite3.connect(db_path)
            cursor = self.connection.cursor()
            
            # Simple parameterized query to prevent SQL injection
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
            
            user = cursor.fetchone()
            if user:
                self._user_data = {
                    'username': user[1],
                    'email': user[2],
                    'role': user[3] if len(user) > 3 else 'user'
                }
                return True
            
            console.print("[red]Invalid username or password[/red]")
            return False
            
        except sqlite3.Error as e:
            console.print(f"[red]Database error: {e}[/red]")
            return False
        
    def get_credentials(self) -> Dict[str, Any]:
        return getattr(self, '_user_data', {})


class WebAuthProvider(AuthProvider):
    """Web-based authentication (OAuth2/OpenID Connect)"""
    
    def authenticate(self, **kwargs) -> bool:
        """Authenticate using web-based OAuth2/OpenID Connect"""
        auth_url = self.config.get('auth_url')
        token_url = self.config.get('token_url')
        client_id = self.config.get('client_id')
        
        if not all([auth_url, token_url, client_id]):
            console.print("[red]Missing required configuration for web auth[/red]")
            return False
            
        # For CLI, we'll use device flow
        try:
            # Start device authorization
            response = requests.post(
                f"{auth_url}/device/authorize",
                data={
                    'client_id': client_id,
                    'scope': ' '.join(self.config.get('scopes', [])),
                }
            )
            response.raise_for_status()
            
            device_code_data = response.json()
            console.print(f"\nPlease visit: {device_code_data['verification_uri']}")
            console.print(f"And enter code: {device_code_data['user_code']}\n")
            
            # Poll for token
            while True:
                response = requests.post(
                    token_url,
                    data={
                        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                        'device_code': device_code_data['device_code'],
                        'client_id': client_id,
                    }
                )
                
                if response.status_code == 200:
                    self._token_data = response.json()
                    return True
                elif response.status_code == 400 and response.json().get('error') == 'authorization_pending':
                    import time
                    time.sleep(device_code_data.get('interval', 5))
                else:
                    console.print(f"[red]Authentication failed: {response.text}[/red]")
                    return False
                    
        except requests.RequestException as e:
            console.print(f"[red]Authentication error: {e}[/red]")
            return False
    
    def get_credentials(self) -> Dict[str, Any]:
        return getattr(self, '_token_data', {})


class IOAuthProvider(AuthProvider):
    """IO-based authentication (file, pipe, etc.)"""
    
    def authenticate(self, **kwargs) -> bool:
        """Authenticate using IO (file, pipe, etc.)"""
        auth_file = self.config.get('auth_file')
        if auth_file and os.path.exists(auth_file):
            try:
                with open(auth_file, 'r') as f:
                    self._auth_data = json.load(f)
                return True
            except (json.JSONDecodeError, OSError) as e:
                console.print(f"[red]Failed to read auth file: {e}[/red]")
                return False
        
        # Fall back to interactive input
        console.print("\nIO Authentication Required")
        console.print("Enter your credentials:")
        
        self._auth_data = {
            'username': input("Username: "),
            'api_key': getpass("API Key: "),
        }
        
        # Save to file if configured
        if auth_file and not os.path.exists(auth_file):
            try:
                os.makedirs(os.path.dirname(auth_file), exist_ok=True)
                with open(auth_file, 'w') as f:
                    json.dump(self._auth_data, f)
                os.chmod(auth_file, 0o600)  # Restrict permissions
            except OSError as e:
                console.print(f"[yellow]Warning: Failed to save credentials: {e}[/yellow]")
        
        return True
    
    def get_credentials(self) -> Dict[str, Any]:
        return getattr(self, '_auth_data', {})


class SocketAuthProvider(AuthProvider):
    """Socket-based authentication"""
    
    def authenticate(self, **kwargs) -> bool:
        """Authenticate using socket communication"""
        host = self.config.get('host', 'localhost')
        port = self.config.get('port', 8080)
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                
                # Simple challenge-response protocol
                challenge = s.recv(1024).decode().strip()
                if not challenge:
                    console.print("[red]No challenge received from server[/red]")
                    return False
                
                response = input(f"Challenge: {challenge}\nResponse: ")
                s.sendall(response.encode())
                
                result = s.recv(1024).decode().strip()
                if result == "AUTH_SUCCESS":
                    self._session_id = s.recv(1024).decode().strip()
                    return True
                else:
                    console.print(f"[red]Authentication failed: {result}[/red]")
                    return False
                    
        except (socket.error, ConnectionRefusedError) as e:
            console.print(f"[red]Socket error: {e}[/red]")
            return False
    
    def get_credentials(self) -> Dict[str, Any]:
        return {'session_id': getattr(self, '_session_id', '')}


def get_auth_provider(auth_type: str, **kwargs) -> Optional[AuthProvider]:
    """Factory function to get an authentication provider
    
    Args:
        auth_type: Type of authentication ('sql', 'web', 'io', 'socket')
        **kwargs: Additional configuration for the provider
        
    Returns:
        Optional[AuthProvider]: Configured authentication provider or None if invalid type
    """
    providers = {
        'sql': SQLAuthProvider,
        'web': WebAuthProvider,
        'io': IOAuthProvider,
        'socket': SocketAuthProvider,
    }
    
    provider_class = providers.get(auth_type.lower())
    if not provider_class:
        console.print(f"[red]Unknown authentication type: {auth_type}[/red]")
        return None
        
    return provider_class(**kwargs)


def interactive_auth_selector() -> Optional[AuthProvider]:
    """Interactively select and configure an authentication provider"""
    console.print("\n[bold]Select Authentication Method:[/bold]")
    console.print("1. SQL Database")
    console.print("2. Web (OAuth2/OpenID Connect)")
    console.print("3. File/API Key")
    console.print("4. Socket Authentication")
    console.print("0. Skip Authentication\n")
    
    try:
        choice = int(input("Enter your choice (0-4): "))
    except ValueError:
        return None
    
    auth_type = {
        1: 'sql',
        2: 'web',
        3: 'io',
        4: 'socket',
    }.get(choice)
    
    if not auth_type:
        return None
    
    provider = get_auth_provider(auth_type)
    if provider and provider.authenticate():
        return provider
        
    return None
