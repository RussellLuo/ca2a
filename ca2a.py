import argparse
import asyncio
import json
import re
import sys
from typing import Any
from uuid import uuid4

from a2a.client import A2AClient
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
    SendMessageSuccessResponse,
    SendStreamingMessageRequest,
    SendStreamingMessageSuccessResponse,
    JSONRPCErrorResponse,
    JSONRPCResponse,
)
import httpx
from pydantic import BaseModel
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter


METHODS = (
    "message/send",
    "message/stream",
)


class Client(BaseModel):
    url: str
    method: str
    params: dict[str, Any]

    headers: dict[str, str]
    """Additional HTTP headers."""

    async def invoke(self, verbose: bool) -> None:
        httpx_client = httpx.AsyncClient(headers=self.headers or None)
        client = A2AClient(httpx_client=httpx_client, url=self.url)

        match self.method:
            case "message/send":
                params = MessageSendParams.model_validate(self.params)
                request = SendMessageRequest(id=str(uuid4()), params=params)
                await self.show_request(request, verbose)

                response = await client.send_message(request)
                await self.show_response(response, verbose)

            case "message/stream":
                params = MessageSendParams.model_validate(self.params)
                request = SendStreamingMessageRequest(id=str(uuid4()), params=params)
                await self.show_request(request, verbose)

                response = client.send_message_streaming(request)
                await self.show_response(response, verbose)

            case _:
                raise ValueError(f"Unsupported method: {self.method}")

    async def show_request(self, request: BaseModel, verbose: bool) -> None:
        if verbose:
            print("Request:")
            print_json(request)

    async def show_response(self, response: BaseModel, verbose: bool) -> None:
        def get_result(resp: JSONRPCResponse) -> BaseModel:
            match resp.root:
                case JSONRPCErrorResponse():
                    return resp.root.error
                case SendMessageSuccessResponse():
                    return resp.root.result
                case SendStreamingMessageSuccessResponse():
                    return resp.root.result
                case _:
                    raise ValueError(
                        f"Unsupported A2A response: {resp.root.model_dump_json(exclude_none=True)}"
                    )

        if verbose:
            print("Response:")
            if is_async_iterator(response):
                async for chunk in response:
                    print_json(chunk)
            else:
                print_json(response)
        else:
            if is_async_iterator(response):
                async for chunk in response:
                    result = get_result(chunk)
                    print_json(result)
            else:
                result = get_result(response)
                print_json(result)


def is_async_iterator(obj) -> bool:
    """Check if obj is an async-iterator."""
    return hasattr(obj, "__aiter__") and hasattr(obj, "__anext__")


def print_json(result: BaseModel) -> None:
    """Print the given result object with syntax highlighting."""
    json_str = result.model_dump_json(indent=2, exclude_none=True)
    if not sys.stdout.isatty():
        print(json_str)
    else:
        highlighted = highlight(json_str, JsonLexer(), TerminalFormatter())
        print(highlighted)


def parse_items(items: list[str]) -> tuple[dict[str, Any], dict[str, str]]:
    """Parse items in the form of `key:value`, `key=string_value` or `key:=json_value`."""

    # Regular expression pattern
    PATTERN = re.compile(r"^([^:=]+)(=|:=|:)(.+)$", re.DOTALL)

    params: dict[str, Any] = {}
    headers: dict[str, str] = {}

    def parse(item: str) -> None:
        match = PATTERN.match(item)
        if not match:
            raise ValueError(f"Invalid item: {item!r}")

        key, separator, value = match.groups()
        match separator:
            case "=":  # String field
                params[key] = value
            case ":=":  # Raw JSON field
                try:
                    parsed_value = json.loads(value)
                    params[key] = parsed_value
                except json.JSONDecodeError:
                    raise ValueError(f"Invalid JSON value: {value!r}")
            case ":":  # Header field
                headers[key] = value
            case _:
                raise ValueError(f"Unsupported separator: {separator!r}")

    for item in items:
        parse(item)

    return params, headers


def main() -> None:
    parser = argparse.ArgumentParser(
        description="A command-line utility for interacting with A2A agents."
    )
    parser.add_argument(
        "url",
        help="The URL to connect to the A2A agent",
    )
    parser.add_argument("method", help="The method to be invoked")
    parser.add_argument(
        "items",
        nargs="*",
        help="""\
The parameter values (in the form of `key=string_value` or `key:=json_value`), \
or the header values (in the form of `key:value`)\
""",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output showing the JSON-RPC request/response",
    )
    args = parser.parse_args()

    if args.method not in METHODS:
        parser.error(
            f"Invalid method: {args.method} (choose from {', '.join(METHODS)})."
        )

    try:
        params, headers = parse_items(args.items)
    except ValueError as exc:
        parser.error(str(exc))

    client = Client(
        url=args.url,
        method=args.method,
        params=params,
        headers=headers,
    )
    asyncio.run(client.invoke(args.verbose))


if __name__ == "__main__":
    main()
