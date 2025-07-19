# cA2A

`ca2a` is a command-line utility that helps you interact with [A2A][1] agents. It's basically `curl` for A2A agents.

## Installation

```bash
pip install ca2a
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
