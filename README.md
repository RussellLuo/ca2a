# cA2A

`ca2a` is a command-line utility that helps you interact with [A2A][1] agents. It's basically `curl` for A2A agents.

## Installation

```bash
pip install ca2a
```

## Usage

```bash
$ ca2a -h
usage: ca2a [-h] [-v] url method [items ...]

A command-line utility for interacting with A2A agents.

positional arguments:
  url            The URL to connect to the A2A agent
  method         The method to be invoked
  items          The parameter values (in the form of `key=string_value` or `key:=json_value`), or the header values (in the form of `key:value`)

options:
  -h, --help     show this help message and exit
  -v, --verbose  Enable verbose output showing JSON-RPC request/response
```

## Quick Start

Run an A2A agent (see [Helloworld Example](https://github.com/a2aproject/a2a-python#helloworld-example)):

```bash
git clone https://github.com/a2aproject/a2a-samples.git
cd a2a-samples/samples/python/agents/helloworld
uv run .
```

Send a message to the agent:

```bash
ca2a http://localhost:9999 message/send message:='{
  "role": "user",
  "parts": [{"kind": "text", "text": "Hello"}],
  "messageId": "msg_123",
  "taskId": "task_123"
}'
```

Send a streaming message to the agent:

```bash
ca2a http://localhost:9999 message/stream message:='{
  "role": "user",
  "parts": [{"kind": "text", "text": "Hello"}],
  "messageId": "msg_123",
  "taskId": "task_123"
}'
```

[1]: https://a2a-protocol.org/
