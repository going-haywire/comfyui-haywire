# comfyui-haywire

ComfyUI custom nodes that let [haywire](https://github.com/going-haywire)'s *ComfyUI Workflow*
node drive a workflow you build in ComfyUI. Licence: GPL-3.0-or-later.

Build the workflow in ComfyUI as usual and mark what haywire should control:

| Node | In ComfyUI | In haywire |
|---|---|---|
| **Haywire Parameter** (`name`, `type`, `default`, `min`, `max`) | outputs `default`, parsed by `type` | an inlet: `number` FLOAT, `integer` INT, `toggle` BOOL, `text`/`prompt` STRING, `choice` (options of the input it feeds) |
| **Haywire Image** (`name`, optional `image`) | passes `image` on, or a grey 512×512 | an IMAGE inlet |
| **Haywire Output** (`images`, `name`) | sends the images over the websocket | an IMAGE outlet per name |

While the open workflow contains a Haywire Output, the page publishes it to the exchange on
every change, under the workflow's file name. The workflow still runs in ComfyUI on its own.

## Install

Clone or link this repository into `ComfyUI/custom_nodes/` and restart ComfyUI. No extra
Python packages are needed.

## Protocol (version 1)

All routes are under `/api/haywire`; bodies are JSON.

| Route | Body | Effect |
|---|---|---|
| `GET /version` | | `{protocol: 1, version}` |
| `GET /workflows` | | `[{publisher: {name, id}, nodes}]` |
| `POST /workflow/publish` | `{client_id, name, workflow}` | stores the publisher's current workflow (API format), sends it to every subscriber |
| `POST /workflow/subscribe` | `{client_id}` | sends every current workflow to `client_id`, then each new publish |
| `POST /workflow/unsubscribe` | `{client_id}` | |
| `POST /workflow/withdraw` | `{client_id}` | forgets that publisher's workflow |

Subscribers receive websocket JSON `{type: "haywire_workflow_published", data: {publisher:
{name, id}, workflow}}`; `publisher.name` is the workflow's file name.

To run a workflow, a client replaces each Haywire Parameter by its value at every input it
feeds, and each Haywire Image by `HaywireLoadImage` with `data` = base64 PNG under the same
node id. Haywire Output is never cached: every run sends a binary frame per image (8-byte header
`>II` = 1, 2, then PNG bytes), followed by `executed` with `output.info = [{name, index}]`, one
entry per image.

The exchange keeps state in memory; a ComfyUI restart empties it until the pages publish again.
