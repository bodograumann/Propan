import inspect
from functools import wraps
from typing import Awaitable, Callable, List, TypeVar, cast

from fast_depends.injector import run_async as call_or_await
from typing_extensions import ParamSpec

__all__ = (
    "call_or_await",
    "to_async",
)

T = TypeVar("T")
P = ParamSpec("P")


def to_async(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        r = await call_or_await(func, *args, **kwargs)
        return cast(T, r)

    return wrapper


def get_function_arguments(func: Callable[P, T]) -> List[str]:
    signature = inspect.signature(func)

    arg_kinds = [
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    ]

    return [
        param.name for param in signature.parameters.values() if param.kind in arg_kinds
    ]
