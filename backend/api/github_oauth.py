"""
GitHub OAuth Authentication Endpoints
Handles OAuth flow for accessing private repositories.
"""

import os
import logging
import httpx
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

router = APIRouter()


class GitHubAuthResponse(BaseModel):
    """Response model for GitHub auth URL"""
    auth_url: str
    state: str


class GitHubTokenResponse(BaseModel):
    """Response model for GitHub token exchange"""
    access_token: str
    token_type: str
    scope: str


class GitHubUserResponse(BaseModel):
    """Response model for GitHub user info"""
    login: str
    name: Optional[str]
    email: Optional[str]
    avatar_url: str
    bio: Optional[str]


# GitHub OAuth Configuration
# IMPORTANT: Set these as environment variables or in .env file
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:5173/auth/github/callback")

# OAuth URLs
GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API_URL = "https://api.github.com/user"


@router.get("/auth/github", response_model=GitHubAuthResponse)
async def get_github_auth_url():
    """
    Get GitHub OAuth authorization URL.

    Returns:
        auth_url: URL to redirect user for GitHub authorization
        state: Random state for CSRF protection
    """
    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="GitHub OAuth not configured. Please set GITHUB_CLIENT_ID environment variable."
        )

    # Generate random state for CSRF protection
    import secrets
    state = secrets.token_urlsafe(32)

    # Build authorization URL
    auth_url = (
        f"{GITHUB_AUTHORIZE_URL}?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={GITHUB_REDIRECT_URI}&"
        f"scope=repo,read:user,user:email&"  # Request repo access for private repos
        f"state={state}"
    )

    logger.info(f"Generated GitHub auth URL with state: {state}")

    return GitHubAuthResponse(auth_url=auth_url, state=state)


@router.get("/auth/github/callback")
async def github_oauth_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: Optional[str] = Query(None, description="State parameter for CSRF protection")
):
    """
    Handle GitHub OAuth callback and exchange code for access token.

    Args:
        code: Authorization code from GitHub
        state: State parameter for CSRF verification

    Returns:
        access_token: GitHub access token for API requests
        token_type: Type of token (usually 'bearer')
        scope: Granted scopes
    """
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="GitHub OAuth not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET."
        )

    logger.info(f"Received OAuth callback with code: {code[:10]}... and state: {state}")

    # Exchange code for access token
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GITHUB_TOKEN_URL,
                headers={
                    "Accept": "application/json"
                },
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": GITHUB_REDIRECT_URI,
                    "state": state
                },
                timeout=30.0
            )

            if response.status_code != 200:
                logger.error(f"GitHub token exchange failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to exchange code for token: {response.text}"
                )

            token_data = response.json()

            if "error" in token_data:
                logger.error(f"GitHub OAuth error: {token_data}")
                raise HTTPException(
                    status_code=400,
                    detail=f"OAuth error: {token_data.get('error_description', token_data['error'])}"
                )

            access_token = token_data.get("access_token")
            token_type = token_data.get("token_type", "bearer")
            scope = token_data.get("scope", "")

            if not access_token:
                raise HTTPException(
                    status_code=400,
                    detail="No access token received from GitHub"
                )

            logger.info(f"Successfully obtained GitHub access token with scopes: {scope}")

            return JSONResponse({
                "access_token": access_token,
                "token_type": token_type,
                "scope": scope
            })

    except httpx.RequestError as e:
        logger.error(f"Network error during token exchange: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Network error communicating with GitHub: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during OAuth callback: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during OAuth: {str(e)}"
        )


@router.get("/auth/github/user", response_model=GitHubUserResponse)
async def get_github_user(token: str = Query(..., description="GitHub access token")):
    """
    Get authenticated GitHub user information.

    Args:
        token: GitHub access token

    Returns:
        User information including login, name, email, avatar, etc.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Get user info
            response = await client.get(
                GITHUB_USER_API_URL,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=30.0
            )

            if response.status_code != 200:
                logger.error(f"Failed to get GitHub user: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to get user info: {response.text}"
                )

            user_data = response.json()

            logger.info(f"Retrieved GitHub user: {user_data.get('login')}")

            return GitHubUserResponse(
                login=user_data.get("login", ""),
                name=user_data.get("name"),
                email=user_data.get("email"),
                avatar_url=user_data.get("avatar_url", ""),
                bio=user_data.get("bio")
            )

    except httpx.RequestError as e:
        logger.error(f"Network error getting user info: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Network error communicating with GitHub: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting GitHub user: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user info: {str(e)}"
        )


@router.post("/auth/github/validate")
async def validate_github_token(token: str = Query(..., description="GitHub access token")):
    """
    Validate a GitHub access token.

    Args:
        token: GitHub access token to validate

    Returns:
        valid: True if token is valid, False otherwise
        scopes: List of scopes granted to the token
    """
    try:
        async with httpx.AsyncClient() as client:
            # Try to get user info to validate token
            response = await client.get(
                GITHUB_USER_API_URL,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=30.0
            )

            if response.status_code == 200:
                # Get scopes from response headers
                scopes = response.headers.get("X-OAuth-Scopes", "").split(", ")
                scopes = [s.strip() for s in scopes if s.strip()]

                return JSONResponse({
                    "valid": True,
                    "scopes": scopes
                })
            else:
                return JSONResponse({
                    "valid": False,
                    "scopes": []
                })

    except Exception as e:
        logger.error(f"Error validating token: {e}")
        return JSONResponse({
            "valid": False,
            "scopes": [],
            "error": str(e)
        })
