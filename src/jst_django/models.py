from pydantic import BaseModel
from typing import Optional, Union


class BaseField(BaseModel):
    """Base Field"""
    verbose_name: Optional[str] = None
    default: Union[str, int] = None

class CharField(BaseField):
    """A simple field for storing a character."""
    max_length: Union[int] = 255

class IntegerField(BaseField):
    """Integer field"""
    min_value: Optional[int] = None

class ForeignKey(BaseField):
    """Foreign key field"""
    model: Union[str]
    related_name: Optional[str] = None

class ManyToManyField(BaseField):
    """Many to many field"""
    model: Union[str]
    related_name: Optional[str] = None

class TextField(BaseField):
    """Text field"""
    ...