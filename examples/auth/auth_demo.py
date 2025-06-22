#!/usr/bin/env python3
"""
Authentication example for DIGY.
This script demonstrates how to use DIGY's authentication system.

Run with different authentication methods:
  SQL Auth:    digy --auth sql --auth-config dbconfig.json run examples/auth/auth_demo.py
  Web Auth:     digy --auth web run examples/auth/auth_demo.py
  IO Auth:      digy --auth io run examples/auth/auth_demo.py
  Socket Auth:  digy --auth socket run examples/auth/auth_demo.py
"""
import json
import os
import sys
from typing import Any, Dict, Optional


class AuthDemo:
    """Demonstration of DIGY authentication features."""

    def __init__(self):
        """Initialize the authentication demo."""
        self.authenticated = False
        self.user_info: Dict[str, Any] = {}
        self.auth_method: Optional[str] = None

    def check_auth(self) -> bool:
        """Check if authentication is available through environment variables."""
        # In a real application, these would be set by DIGY after authentication
        self.auth_method = os.environ.get("DIGY_AUTH_METHOD")

        if not self.auth_method:
            print("[yellow]No authentication method detected.[/yellow]")
            print("Run with: digy --auth <method> run examples/auth/auth_demo.py")
            return False

        # Check for user info in environment (set by DIGY after auth)
        user_info_json = os.environ.get("DIGY_USER_INFO")
        if user_info_json:
            try:
                self.user_info = json.loads(user_info_json)
                self.authenticated = True
                return True
            except json.JSONDecodeError:
                print("[red]Error: Invalid user info in environment[/red]")
                return False

        return False

    def show_auth_info(self) -> None:
        """Display authentication information."""
        print("\n[bold blue]Authentication Information[/bold blue]")
        print("=" * 30)

        if not self.auth_method:
            print("[yellow]No authentication method detected.[/yellow]")
            return

        print(f"Authentication Method: [bold]{self.auth_method.upper()}[/bold]")

        if self.authenticated and self.user_info:
            print("\n[green]✓ Authenticated Successfully[/green]")
            print("\nUser Information:")
            for key, value in self.user_info.items():
                print(f"  {key}: {value}")
        else:
            print("\n[red]✗ Not authenticated[/red]")
            print("\nMake sure to run with the appropriate authentication method:")
            print("  digy --auth <method> run examples/auth/auth_demo.py")
            print("\nAvailable methods: sql, web, io, socket")


def main():
    """Run the authentication demo."""
    print("\n[bold]DIGY Authentication Demo[/bold]")
    print("This example shows how to use DIGY's authentication system.")

    demo = AuthDemo()
    demo.check_auth()
    demo.show_auth_info()

    print("\n[green]Authentication demo complete![/green]")
    print("Try running with different authentication methods to see the results.")


if __name__ == "__main__":
    try:
        from rich import print
    except ImportError:
        pass  # Fall back to standard print if rich is not available

    main()
