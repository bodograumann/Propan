import json
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Sequence, Tuple, Union
from uuid import uuid4

from fast_depends.construct import get_dependant
from pydantic import BaseModel, Field, Json, create_model
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing_extensions import TypeAlias, assert_never

from propan.asyncapi.channels import AsyncAPIChannel
from propan.asyncapi.utils import add_example_to_model
from propan.types import AnyDict, DecodedMessage, DecoratedCallable, SendableMessage

ContentType: TypeAlias = str


@dataclass
class BaseHandler:
    callback: DecoratedCallable
    description: str = field(default="", kw_only=True)  # type: ignore

    @abstractmethod
    def get_schema(self) -> Dict[str, AsyncAPIChannel]:
        raise NotImplementedError()

    @property
    def title(self) -> str:
        return self.callback.__name__.replace("_", " ").title().replace(" ", "")

    def get_message_object(self) -> Tuple[str, AnyDict]:
        dependant = get_dependant(path="", call=self.callback)
        custom = tuple(c.param_name for c in dependant.custom)
        dependant.params = tuple(
            filter(lambda x: x.name not in custom, dependant.params)
        )
        schema_title = f"{self.title}Message"

        # TODO: recursive schema generation
        # TODO: return RPC response class too
        params_number = len(dependant.params)

        gen_examples: bool
        if params_number == 0:
            model = None

        elif params_number == 1:
            param = dependant.params[0]

            if issubclass(param.annotation, BaseModel):
                model = param.annotation
                gen_examples = model.Config.schema_extra.get("example") is None

            else:
                model = create_model(
                    schema_title,
                    **{
                        param.name: (param.annotation, ... if param.required else param.default)
                    },
                )
                gen_examples = True

        else:
            model = create_model(  # type: ignore
                schema_title,
                **{
                    p.name: (p.annotation, ... if p.required else p.default)
                    for p in dependant.params
                },
            )
            gen_examples = True

        if model is None:
            body = {"title": schema_title, "type": "null"}
        else:
            if gen_examples is True:
                model = add_example_to_model(model)
            body = model.schema()

        return body.get("title", schema_title), body


class ContentTypes(str, Enum):
    text = "text/plain"
    json = "application/json"


class NameRequired(BaseModel):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)


class Queue(NameRequired):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)


class SendableModel(BaseModel):
    message: DecodedMessage

    @classmethod
    def to_send(cls, msg: SendableMessage) -> Tuple[bytes, Optional[ContentType]]:
        if msg is None:
            return b"", None

        if isinstance(msg, bytes):
            return msg, None

        m = cls(message=msg).message  # type: ignore

        if isinstance(m, str):
            return m.encode(), ContentTypes.text.value

        if isinstance(m, (Dict, Sequence)):
            return json.dumps(m).encode(), ContentTypes.json.value

        assert_never()  # pragma: no cover


class RawDecoced(BaseModel):
    message: Union[Json[Any], str]


@pydantic_dataclass
class PropanMessage:
    body: bytes
    raw_message: Any
    content_type: Optional[str] = None
    reply_to: str = ""
    headers: AnyDict = Field(default_factory=dict)
    message_id: str = Field(default_factory=lambda: str(uuid4()))
