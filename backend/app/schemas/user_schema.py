from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreationRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=12,
        max_length=20,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not any(char.islower() for char in value):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        if not any(char.isdigit() for char in value):
            raise ValueError(
                "Password must contain at least one digit"
            )

        if not any(
            char in r"""!@#$%^&*()-_=+[{]}\|;:'",<.>/?`~"""
            for char in value
        ):
            raise ValueError(
                "Password must contain at least one special character"
            )

        return value


class UserResponse(BaseModel):
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)