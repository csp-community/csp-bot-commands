import io

import pytest
from PIL import Image


def _gif(colors):
    frames = [Image.new("RGB", (32, 32), color) for color in colors]
    output = io.BytesIO()
    frames[0].save(output, format="GIF", save_all=True, append_images=frames[1:], duration=100, loop=0)
    return output.getvalue()


def test_all_gif_frames_are_in_visual_review():
    from csp_bot_commands.gif import gif_review_images

    images, count = gif_review_images(_gif(["red", "blue", "green"]))
    assert count == 3
    assert images and all(data.startswith(b"\x89PNG\r\n\x1a\n") for data in images)
    sheet = Image.open(io.BytesIO(images[0]))
    assert sheet.getpixel((10, 10)) == (255, 0, 0)
    assert sheet.getpixel((250, 10)) == (0, 0, 255)
    assert sheet.getpixel((490, 10)) == (0, 128, 0)


def test_gif_review_rejects_non_gif_and_excess_frames():
    from csp_bot_commands.gif import gif_review_images

    with pytest.raises(ValueError):
        gif_review_images(b"not a GIF")
    with pytest.raises(ValueError, match="frame"):
        gif_review_images(_gif(["red", "blue", "green"]), max_frames=2)


@pytest.mark.parametrize(
    "url",
    [
        "http://media.giphy.com/file.gif",
        "https://localhost/file.gif",
        "https://127.0.0.1/file.gif",
        "https://giphy.com.evil.example/file.gif",
        "https://user:password@media.giphy.com/file.gif",
    ],
)
def test_gif_urls_reject_untrusted_targets(url):
    from csp_bot_commands.gif import validate_gif_url

    with pytest.raises(ValueError):
        validate_gif_url(url)


def test_safety_and_relevance_are_both_required():
    from csp_bot_commands.gif import GifAssessment

    assert GifAssessment(safe=True, relevant=True, reason="A cat dancing").approved
    assert not GifAssessment(safe=False, relevant=True, reason="Unsafe").approved
    assert not GifAssessment(safe=True, relevant=False, reason="Unrelated").approved


@pytest.mark.asyncio
@pytest.mark.parametrize("approved", [False, True])
@pytest.mark.parametrize("transport_failure", [False, True])
async def test_upload_occurs_only_after_visual_approval(monkeypatch, approved, transport_failure):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock

    from mcp.shared.exceptions import MCPError

    from csp_bot_commands import gif

    pages = [f"https://giphy.com/gifs/cat-{index}" for index in range(3)]

    class Server:
        attempts = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        @property
        def client(self):
            return self

        async def call_tool(self, name, args):
            if name == "web_search":
                return SimpleNamespace(structured_content={"results": "\n".join("URL: " + page for page in pages)})
            self.attempts += 1
            if transport_failure and self.attempts == 1:
                raise MCPError(-32603, "Server returned an error response")
            return SimpleNamespace(structured_content={"metadata": {"image_urls": ["https://media.giphy.com/test.gif"]}})

    servers = [SimpleNamespace(prefix=prefix, build_server=Server) for prefix in ("search", "fetch")]
    local = SimpleNamespace(call=AsyncMock(return_value={"ok": True, "message_id": "GIF1"}))
    verdicts = [
        gif.GifAssessment(safe=False, relevant=True, reason="Unsafe"),
        gif.GifAssessment(safe=True, relevant=False, reason="Unrelated"),
        gif.GifAssessment(safe=approved, relevant=approved, reason="Decision"),
    ]
    if transport_failure:
        verdicts = verdicts[1:]
    judge = SimpleNamespace(run=AsyncMock(side_effect=[SimpleNamespace(output=verdict) for verdict in verdicts]))
    factory = MagicMock()
    factory.__getitem__.return_value.return_value = judge
    monkeypatch.setattr(gif, "Agent", factory)
    monkeypatch.setattr(gif, "download_public_gif", AsyncMock(return_value=_gif(["red", "blue"])))
    result = await gif.GifRunner("test-model", local, servers, "C1").run("cat")
    assert judge.run.await_count == (2 if transport_failure else 3)
    if approved:
        local.call.assert_awaited_once()
        assert "Uploaded" in result.output
    else:
        local.call.assert_not_awaited()
        assert "No GIF passed" in result.output
