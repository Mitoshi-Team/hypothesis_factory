"""Declarative SQLAlchemy models for the API Gateway service."""

import bcrypt
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import Base


class User(Base):
    """User database model representation.

    Inherits audit fields (created_at, updated_at) from the Base model.
    Stores the user credentials with the password stored securely as a bcrypt hash.

    Attributes:
        id_user: Unique primary key identifier for the user.
        login: Unique username/login handle.
        password: Hashed bcrypt representation of the user password.
    """

    __tablename__ = "users"

    id_user: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    def set_password(self, password: str) -> None:
        """Hash a plain text password and update the password column.

        Args:
            password: Clear text password to be hashed and stored.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        self.password = hashed.decode("utf-8")

    def verify_password(self, password: str) -> bool:
        """Verify a plain text password against the stored bcrypt hash.

        Args:
            password: Clear text password to verify.

        Returns:
            bool: True if password matches the hash, False otherwise.
        """
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))
