"""
Authentication Routes - Signup, Login, Logout

This module provides FastAPI routes for user authentication:
1. POST /auth/signup - Create new user account
2. POST /auth/login - Login and get access token
3. POST /auth/logout - Logout (token invalidation)
4. GET /auth/me - Get current user info

For Beginners:
- Routes = URL endpoints your frontend can call
- Request = Data sent from frontend
- Response = Data sent back to frontend
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from src.database.connection import get_db
from src.database.models import User
from src.utils.auth import PasswordHasher, TokenManager, AuthValidator

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme for token authentication
security = HTTPBearer()


# ==================== REQUEST/RESPONSE MODELS ====================

class SignupRequest(BaseModel):
    """
    Signup request model
    
    Example JSON:
    {
        "email": "john@example.com",
        "username": "john_doe",
        "password": "SecurePass123",
        "full_name": "John Doe"
    }
    """
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    """
    Login request model
    
    Example JSON:
    {
        "email": "john@example.com",
        "password": "SecurePass123"
    }
    """
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """
    Authentication response model
    
    Example JSON:
    {
        "success": true,
        "message": "Login successful",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": "john@example.com",
            "username": "john_doe",
            "full_name": "John Doe"
        }
    }
    """
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    user: Optional[dict] = None


class UserResponse(BaseModel):
    """User information response"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]


# ==================== HELPER FUNCTIONS ====================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from token
    
    This function:
    1. Extracts token from Authorization header
    2. Verifies token is valid
    3. Gets user from database
    4. Returns user object
    
    Args:
        credentials: Bearer token from request header
        db: Database session
        
    Returns:
        User object if authenticated
        
    Raises:
        HTTPException if token is invalid or user not found
    """
    token = credentials.credentials
    
    # Verify token
    user_id = TokenManager.decode_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


# ==================== ROUTES ====================

@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    Create new user account
    
    Process:
    1. Validate email, username, password
    2. Check if user already exists
    3. Hash password
    4. Create user in database
    5. Generate access token
    6. Return token and user info
    
    Example:
        POST /auth/signup
        Body: {
            "email": "john@example.com",
            "username": "john_doe",
            "password": "SecurePass123",
            "full_name": "John Doe"
        }
        
        Response: {
            "success": true,
            "message": "Account created successfully",
            "access_token": "eyJhbGc...",
            "user": {...}
        }
    """
    
    # Validate email
    if not AuthValidator.validate_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Validate username
    is_valid, error_msg = AuthValidator.validate_username(request.username)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Validate password
    is_valid, error_msg = AuthValidator.validate_password(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Hash password
    password_hash = PasswordHasher.hash_password(request.password)
    
    # Create new user
    new_user = User(
        email=request.email,
        username=request.username,
        password_hash=password_hash,
        full_name=request.full_name,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate access token
    access_token = TokenManager.create_access_token(
        data={"user_id": new_user.id, "username": new_user.username}
    )
    
    return AuthResponse(
        success=True,
        message="Account created successfully",
        access_token=access_token,
        token_type="bearer",
        user={
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "full_name": new_user.full_name,
            "created_at": new_user.created_at,
            "last_login": new_user.last_login
        }
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    
    Process:
    1. Find user by email
    2. Verify password
    3. Update last login time
    4. Generate access token
    5. Return token and user info
    
    Example:
        POST /auth/login
        Body: {
            "email": "john@example.com",
            "password": "SecurePass123"
        }
        
        Response: {
            "success": true,
            "message": "Login successful",
            "access_token": "eyJhbGc...",
            "user": {...}
        }
    """
    
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not PasswordHasher.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Generate access token
    access_token = TokenManager.create_access_token(
        data={"user_id": user.id, "username": user.username}
    )
    
    return AuthResponse(
        success=True,
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    
    This endpoint requires authentication (Bearer token in header)
    
    Example:
        GET /auth/me
        Headers: {
            "Authorization": "Bearer eyJhbGc..."
        }
        
        Response: {
            "id": 1,
            "email": "john@example.com",
            "username": "john_doe",
            "full_name": "John Doe",
            "created_at": "2026-01-27T10:30:00",
            "last_login": "2026-01-27T12:45:00"
        }
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user
    
    Note: Since we're using stateless JWT tokens, logout is handled client-side
    by removing the token. This endpoint is mainly for logging purposes.
    
    For production, you might want to implement token blacklisting.
    
    Example:
        POST /auth/logout
        Headers: {
            "Authorization": "Bearer eyJhbGc..."
        }
        
        Response: {
            "success": true,
            "message": "Logged out successfully"
        }
    """
    return {
        "success": True,
        "message": "Logged out successfully",
        "note": "Please remove the token from client-side storage"
    }


@router.post("/verify-token")
async def verify_token(current_user: User = Depends(get_current_user)):
    """
    Verify if token is valid
    
    Useful for checking authentication status without getting full user info
    
    Example:
        POST /auth/verify-token
        Headers: {
            "Authorization": "Bearer eyJhbGc..."
        }
        
        Response: {
            "valid": true,
            "user_id": 1,
            "username": "john_doe"
        }
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username
    }
