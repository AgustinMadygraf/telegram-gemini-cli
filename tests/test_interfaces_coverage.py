import pytest
import asyncio
from src.use_cases.ports import interfaces
from src.entities.ai import AIResponse
from src.entities.chat import ChatMessage

@pytest.mark.asyncio
async def test_interfaces_methods_coverage():
    """
    Este test asegura cobertura del 100% en interfaces.py tocando las líneas 'pass'
    a través de implementaciones mínimas y ejecuciones reales.
    """
    
    class DummyAI(interfaces.AIEngineGateway):
        async def ask(self, p, s=None, a=None): await super().ask(p, s, a)
        async def reset(self, s=None): await super().reset(s)
    
    class DummyPresenter(interfaces.MessagePresenter):
        def format_response(self, r): super().format_response(r)

    class DummyMessenger(interfaces.MessengerGateway):
        async def send_message(self, c, t, p=None): await super().send_message(c, t, p)
        async def set_typing(self, c): await super().set_typing(c)
        async def get_webhook_status(self): await super().get_webhook_status()
        async def set_webhook(self, u, s=None): await super().set_webhook(u, s)
        async def get_file_path(self, f): await super().get_file_path(f)
        async def download_file(self, f, d): await super().download_file(f, d)

    class DummyValidator(interfaces.CredentialValidatorGateway):
        async def validate(self): await super().validate()

    class DummyMCP(interfaces.MCPValidatorGateway):
        async def validate_servers(self): await super().validate_servers()

    class DummyTunnel(interfaces.TunnelGateway):
        async def validate_tunnel(self, u=None): await super().validate_tunnel(u)
        def start_tunnel(self): super().start_tunnel()
        def stop_tunnel(self): super().stop_tunnel()

    class DummyShell(interfaces.ShellGateway):
        async def execute(self, a, e=None, c=None, t=30.0, logger=None): await super().execute(a, e, c, t, logger)

    class DummyFS(interfaces.FileSystemGateway):
        def exists(self, p): super().exists(p)
        def write_file(self, p, c): super().write_file(p, c)
        def read(self, p): super().read(p)
        def delete(self, p): super().delete(p)
        def ensure_dir(self, p): super().ensure_dir(p)

    class DummyMarkdown(interfaces.MarkdownConverterPort):
        def to_html(self, t): super().to_html(t)

    class DummyHistory(interfaces.ChatHistoryGateway):
        async def save_message(self, m): await super().save_message(m)
        async def get_recent_history(self, c, l=10): await super().get_recent_history(c, l)

    class DummyLogger(interfaces.LoggerPort):
        def info(self, m): super().info(m)
        def error(self, m): super().error(m)
        def debug(self, m): super().debug(m)
        def warning(self, m): super().warning(m)
        def critical(self, m): super().critical(m)

    # Instanciar y llamar a todos los métodos para garantizar cobertura de las líneas 'pass'
    
    # AI
    ai = DummyAI()
    await ai.ask("hi")
    await ai.reset()

    # Presenter
    pres = DummyPresenter()
    pres.format_response(AIResponse(text="hi", success=True))

    # Messenger
    msg = DummyMessenger()
    await msg.send_message(1, "hi")
    await msg.set_typing(1)
    await msg.get_webhook_status()
    await msg.set_webhook("url")
    await msg.get_file_path("id")
    await msg.download_file("path", "dest")

    # Validator
    val = DummyValidator()
    await val.validate()

    # MCP
    mcp = DummyMCP()
    await mcp.validate_servers()

    # Tunnel
    tun = DummyTunnel()
    await tun.validate_tunnel()
    tun.start_tunnel()
    tun.stop_tunnel()

    # Shell
    sh = DummyShell()
    await sh.execute(["ls"])

    # FS
    fs = DummyFS()
    fs.exists("path")
    fs.write_file("path", "content")
    fs.read("path")
    fs.delete("path")
    fs.ensure_dir("path")

    # Markdown
    md = DummyMarkdown()
    md.to_html("text")

    # History
    hist = DummyHistory()
    await hist.save_message(ChatMessage(chat_id=1, user_id=1, role="user", text="hi"))
    await hist.get_recent_history(1)

    # Logger
    log = DummyLogger()
    log.info("msg")
    log.error("msg")
    log.debug("msg")
    log.warning("msg")
    log.critical("msg")
