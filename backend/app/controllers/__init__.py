"""
Controllers package for EasyLaw API endpoints.
"""

from .auth_controller import router as auth_router

__all__ = ["auth_router"]