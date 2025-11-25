import base64
import hashlib
import json
import os
import re
import subprocess
from typing import Any, Literal, TypedDict, cast

import models
from python.helpers import runtime, whisper, defer, git
from . import files, dotenv
from python.helpers.print_style import PrintStyle
from python.helpers.providers import get_providers
from python.helpers.secrets import get_default_secrets_manager
from python.helpers import dirty_json


# 设置翻译字典
SETTINGS_TRANSLATIONS = {
    "en-US": {
        # 主要部分标题
        "User Interface": "User Interface",
        "Chat Model": "Chat Model",
        "Utility model": "Utility model",
        "Browser Model": "Browser Model",
        "Web Browser Model": "Web Browser Model",
        "Embedding Model": "Embedding Model",
        "Code Execution": "Code Execution",
        "Additional Settings": "Additional Settings",
        "Authentication": "Authentication",
        "LiteLLM Global Settings": "LiteLLM Global Settings",
        "Agent Config": "Agent Config",
        "External Services": "External Services",
        "MCP/A2A": "MCP/A2A",
        "Developer": "Developer",
        "Task Scheduler": "Task Scheduler",
        "Backup & Restore": "Backup & Restore",
        
        # 字段标题
        "Language": "Language",
        "Chat model provider": "Chat model provider",
        "Chat model name": "Chat model name",
        "Chat model API base URL": "Chat model API base URL",
        "Chat model context length": "Chat model context length",
        "Context window space for chat history": "Context window space for chat history",
        "Supports Vision": "Supports Vision",
        "Use Vision": "Use Vision",
        "Requests per minute limit": "Requests per minute limit",
        "Input tokens per minute limit": "Input tokens per minute limit",
        "Output tokens per minute limit": "Output tokens per minute limit",
        "Chat model additional parameters": "Chat model additional parameters",
        "Utility model provider": "Utility model provider",
        "Utility model name": "Utility model name",
        "Utility model API base URL": "Utility model API base URL",
        "Utility model additional parameters": "Utility model additional parameters",
        "Embedding model provider": "Embedding model provider",
        "Embedding model name": "Embedding model name",
        "Embedding model API base URL": "Embedding model API base URL",
        "Embedding model additional parameters": "Embedding model additional parameters",
        "Web Browser model provider": "Web Browser model provider",
        "Web Browser model name": "Web Browser model name",
        "Web Browser model API base URL": "Web Browser model API base URL",
        "Web Browser model rate limit requests": "Web Browser model rate limit requests",
        "Web Browser model rate limit input": "Web Browser model rate limit input",
        "Web Browser model rate limit output": "Web Browser model rate limit output",
        "Web Browser model additional parameters": "Web Browser model additional parameters",
        "HTTP Headers": "HTTP Headers",
        "UI Login": "UI Login",
        "UI Password": "UI Password",
        "API Keys": "API Keys",
        "LiteLLM global parameters": "LiteLLM global parameters",
        "Default agent profile": "Default agent profile",
        "Knowledge subdirectory": "Knowledge subdirectory",
        "Memory Subdirectory": "Memory Subdirectory",
        "Memory Dashboard": "Memory Dashboard",
        "Memory auto-recall enabled": "Memory auto-recall enabled",
        "Memory auto-recall delayed": "Memory auto-recall delayed",
        "Auto-recall AI query preparation": "Auto-recall AI query preparation",
        "Auto-recall AI post-filtering": "Auto-recall AI post-filtering",
        "Memory auto-recall interval": "Memory auto-recall interval",
        "Memory auto-recall history length": "Memory auto-recall history length",
        
        # 描述文本
        "Select provider for main chat model used by Agent Zero": "Select provider for main chat model used by Agent Zero",
        "Customize the user interface settings": "Customize the user interface settings",
        "Select your preferred language": "Select your preferred language",
        "Set user name for web UI": "Set user name for web UI",
        "Set password for web UI": "Set password for web UI",
        "Set user password for web UI": "Set user password for web UI",
        "Smaller, cheaper, faster model for handling utility tasks like organizing memory, preparing prompts, summarizing.": "Smaller, cheaper, faster model for handling utility tasks like organizing memory, preparing prompts, summarizing.",
        "Agent parameters.": "Agent parameters.",
        "Subdirectory of /agents folder to be used by default agent no. 0. Subordinate agents can be spawned with other profiles, that is on their superior agent to decide. This setting affects the behaviour of the top level agent you communicate with.": "Subdirectory of /agents folder to be used by default agent no. 0. Subordinate agents can be spawned with other profiles, that is on their superior agent to decide. This setting affects the behaviour of the top level agent you communicate with.",
        "Subdirectory of /knowledge folder to use for agent knowledge import. 'default' subfolder is always imported and contains framework knowledge.": "Subdirectory of /knowledge folder to use for agent knowledge import. 'default' subfolder is always imported and contains framework knowledge.",
    },
    "zh-CN": {
        # 主要部分标题
        "User Interface": "用户界面",
        "Chat Model": "聊天模型",
        "Utility model": "实用模型",
        "Browser Model": "浏览器模型",
        "Web Browser Model": "网页浏览器模型",
        "Embedding Model": "嵌入模型",
        "Code Execution": "代码执行",
        "Additional Settings": "附加设置",
        "Authentication": "身份验证",
        "LiteLLM Global Settings": "LiteLLM 全局设置",
        "Agent Config": "代理配置",
        "External Services": "外部服务",
        "MCP/A2A": "MCP/A2A",
        "Developer": "开发者",
        "Task Scheduler": "任务调度器",
        "Backup & Restore": "备份与恢复",
        
        # 字段标题
        "Language": "语言",
        "Chat model provider": "聊天模型提供商",
        "Chat model name": "聊天模型名称",
        "Chat model API base URL": "聊天模型 API 基础 URL",
        "Chat model context length": "聊天模型上下文长度",
        "Context window space for chat history": "聊天历史的上下文窗口空间",
        "Supports Vision": "支持视觉",
        "Use Vision": "使用视觉",
        "Requests per minute limit": "每分钟请求限制",
        "Input tokens per minute limit": "每分钟输入令牌限制",
        "Output tokens per minute limit": "每分钟输出令牌限制",
        "Chat model additional parameters": "聊天模型附加参数",
        "Utility model provider": "实用模型提供商",
        "Utility model name": "实用模型名称",
        "Utility model API base URL": "实用模型 API 基础 URL",
        "Utility model additional parameters": "实用模型附加参数",
        "Embedding model provider": "嵌入模型提供商",
        "Embedding model name": "嵌入模型名称",
        "Embedding model API base URL": "嵌入模型 API 基础 URL",
        "Embedding model additional parameters": "嵌入模型附加参数",
        "Web Browser model provider": "网页浏览器模型提供商",
        "Web Browser model name": "网页浏览器模型名称",
        "Web Browser model API base URL": "网页浏览器模型 API 基础 URL",
        "Web Browser model rate limit requests": "网页浏览器模型请求速率限制",
        "Web Browser model rate limit input": "网页浏览器模型输入速率限制",
        "Web Browser model rate limit output": "网页浏览器模型输出速率限制",
        "Web Browser model additional parameters": "网页浏览器模型附加参数",
        "HTTP Headers": "HTTP 头部",
        "UI Login": "UI 登录",
        "UI Password": "UI 密码",
        "API Keys": "API 密钥",
        "LiteLLM global parameters": "LiteLLM 全局参数",
        "Default agent profile": "默认代理配置文件",
        "Knowledge subdirectory": "知识子目录",
        "Memory Subdirectory": "记忆子目录",
        "Memory Dashboard": "记忆仪表板",
        "Memory auto-recall enabled": "记忆自动回忆已启用",
        "Memory auto-recall delayed": "记忆自动回忆延迟",
        "Auto-recall AI query preparation": "自动回忆 AI 查询准备",
        "Auto-recall AI post-filtering": "自动回忆 AI 后过滤",
        "Memory auto-recall interval": "记忆自动回忆间隔",
        "Memory auto-recall history length": "记忆自动回忆历史长度",
        "Memory auto-recall similarity threshold": "记忆自动回忆相似度阈值",
        "Memory auto-recall max memories to search": "记忆自动回忆最大搜索记忆数",
        "Memory auto-recall max memories to use": "记忆自动回忆最大使用记忆数",
        "Memory auto-recall max solutions to search": "记忆自动回忆最大搜索解决方案数",
        "Memory auto-recall max solutions to use": "记忆自动回忆最大使用解决方案数",
        "Auto-memorize enabled": "自动记忆已启用",
        "Auto-memorize AI consolidation": "自动记忆 AI 整合",
        "Auto-memorize replacement threshold": "自动记忆替换阈值",
        "Memory": "记忆",
        "Speech": "语音",
        "Speech-to-text model size": "语音转文本模型大小",
        "Speech-to-text language code": "语音转文本语言代码",
        "Microphone device": "麦克风设备",
        "Microphone silence threshold": "麦克风静音阈值",
        "Microphone silence duration (ms)": "麦克风静音持续时间 (毫秒)",
        "Microphone waiting timeout (ms)": "麦克风等待超时 (毫秒)",
        "Enable Kokoro TTS": "启用 Kokoro TTS",
        "External MCP Servers": "外部 MCP 服务器",
        "MCP Servers Configuration": "MCP 服务器配置",
        "MCP Servers": "MCP 服务器",
        "MCP Client Init Timeout": "MCP 客户端初始化超时",
        "MCP Client Tool Timeout": "MCP 客户端工具超时",
        "Secrets Management": "密钥管理",
        "Variables Store": "变量存储",
        "Secrets Store": "密钥存储",
        "A0 MCP Server": "A0 MCP 服务器",
        "Enable A0 MCP Server": "启用 A0 MCP 服务器",
        "MCP Server Token": "MCP 服务器令牌",
        "A0 A2A Server": "A0 A2A 服务器",
        "Enable A2A server": "启用 A2A 服务器",
        "External API": "外部 API",
        "API Examples": "API 示例",
        "Update Checker": "更新检查器",
        "Enable Update Checker": "启用更新检查器",
        "Development": "开发",
        "Shell Interface": "Shell 接口",
        "RFC Destination URL": "RFC 目标 URL",
        "RFC Password": "RFC 密码",
        "RFC HTTP port": "RFC HTTP 端口",
        "RFC SSH port": "RFC SSH 端口",
        
        # 描述文本 - MCP 和其他服务
        "External MCP servers can be configured here.": "可以在此处配置外部 MCP 服务器。",
        "Timeout for MCP client initialization (in seconds). Higher values might be required for complex MCPs, but might also slowdown system startup.": "MCP 客户端初始化超时（秒）。复杂的 MCP 可能需要更高的值，但也可能会减慢系统启动。",
        "Timeout for MCP client tool execution. Higher values might be required for complex tools, but might also result in long responses with failing tools.": "MCP 客户端工具执行超时。复杂的工具可能需要更高的值，但也可能导致失败工具的响应时间过长。",
        "Agent Zero can use external MCP servers, local or remote as tools.": "Agent Zero 可以使用外部 MCP 服务器，本地或远程作为工具。",
        "Manage secrets and credentials that agents can use without exposing values to LLMs, chat history or logs. Placeholders are automatically replaced with values just before tool calls. If bare passwords occur in tool results, they are masked back to placeholders.": "管理代理可以使用的密钥和凭据，而不向 LLM、聊天历史或日志暴露值。在工具调用之前，占位符会自动替换为值。如果在工具结果中出现裸密码，它们会被遮罩回占位符。",
        "Store non-sensitive variables in .env format e.g. EMAIL_IMAP_SERVER=\"imap.gmail.com\", one item per line. You can use comments starting with # to add descriptions for the agent. See <a href=\"javascript:openModal('settings/secrets/example-vars.html')\">example</a>.<br>These variables are visible to LLMs and in chat history, they are not being masked.": "以 .env 格式存储非敏感变量，例如 EMAIL_IMAP_SERVER=\"imap.gmail.com\"，每行一个项目。您可以使用以 # 开头的注释为代理添加描述。查看 <a href=\"javascript:openModal('settings/secrets/example-vars.html')\">\u793a\u4f8b</a>。<br>这些变量对 LLM 和聊天历史可见，不会被遮罩。",
        "Store secrets and credentials in .env format e.g. EMAIL_PASSWORD=\"s3cret-p4$$w0rd\", one item per line. You can use comments starting with # to add descriptions for the agent. See <a href=\"javascript:openModal('settings/secrets/example-secrets.html')\">example</a>.<br>These variables are not visile to LLMs and in chat history, they are being masked. ⚠️ only values with length >= 4 are being masked to prevent false positives. ": "以 .env 格式存储密钥和凭据，例如 EMAIL_PASSWORD=\"s3cret-p4$$w0rd\"，每行一个项目。您可以使用以 # 开头的注释为代理添加描述。查看 <a href=\"javascript:openModal('settings/secrets/example-secrets.html')\">\u793a\u4f8b</a>。<br>这些变量对 LLM 和聊天历史不可见，会被遮罩。⚠️ 只有长度 >= 4 的值才会被遮罩以防止误报。",
        "Expose Agent Zero as an SSE/HTTP MCP server. This will make this A0 instance available to MCP clients.": "将 Agent Zero 暴露为 SSE/HTTP MCP 服务器。这将使此 A0 实例对 MCP 客户端可用。",
        "Token for MCP server authentication.": "MCP 服务器身份验证令牌。",
        "Agent Zero can be exposed as an SSE MCP server. See <a href=\"javascript:openModal('settings/mcp/server/example.html')\">connection example</a>.": "Agent Zero 可以被暴露为 SSE MCP 服务器。查看 <a href=\"javascript:openModal('settings/mcp/server/example.html')\">连接示例</a>。",
        "Expose Agent Zero as A2A server. This allows other agents to connect to A0 via A2A protocol.": "将 Agent Zero 暴露为 A2A 服务器。这允许其他代理通过 A2A 协议连接到 A0。",
        "Agent Zero can be exposed as an A2A server. See <a href=\"javascript:openModal('settings/a2a/a2a-connection.html')\">connection example</a>.": "Agent Zero 可以被暴露为 A2A 服务器。查看 <a href=\"javascript:openModal('settings/a2a/a2a-connection.html')\">连接示例</a>。",
        "API keys for model providers and services used by Agent Zero. You can set multiple API keys separated by a comma (,). They will be used in round-robin fashion.<br>For more information abou Agent Zero Venice provider, see <a href='http://agent-zero.ai/?community/api-dashboard/about' target='_blank'>Agent Zero Venice</a>.": "Agent Zero 使用的模型提供商和服务的 API 密钥。您可以设置多个由逗号 (,) 分隔的 API 密钥。它们将以轮询方式使用。<br>有关 Agent Zero Venice 提供商的更多信息，请参阅 <a href='http://agent-zero.ai/?community/api-dashboard/about' target='_blank'>Agent Zero Venice</a>。",
        "Global LiteLLM params (e.g. timeout, stream_timeout) in .env format: one KEY=VALUE per line. Example: <code>stream_timeout=30</code>. Applied to all LiteLLM calls unless overridden. See <a href='https://docs.litellm.ai/docs/set_keys' target='_blank'>LiteLLM</a> and <a href='https://docs.litellm.ai/docs/proxy/timeout' target='_blank'>timeouts</a>.": "全局 LiteLLM 参数（例如 timeout、stream_timeout），以 .env 格式：每行一个 KEY=VALUE。示例：<code>stream_timeout=30</code>。除非被覆盖，否则应用于所有 LiteLLM 调用。参阅 <a href='https://docs.litellm.ai/docs/set_keys' target='_blank'>LiteLLM</a> 和 <a href='https://docs.litellm.ai/docs/proxy/timeout' target='_blank'>超时</a>。",
        "Configure global parameters passed to LiteLLM for all providers.": "配置传递给所有提供商的 LiteLLM 的全局参数。",
        "Terminal interface used for Code Execution Tool. Local Python TTY works locally in both dockerized and development environments. SSH always connects to dockerized environment (automatically at localhost or RFC host address).": "用于代码执行工具的终端接口。本地 Python TTY 在容器化和开发环境中都可以本地工作。SSH 始终连接到容器化环境（自动在 localhost 或 RFC 主机地址）。",
        "URL of dockerized A0 instance for remote function calls. Do not specify port here.": "用于远程函数调用的容器化 A0 实例的 URL。不要在此处指定端口。",
        "Password for remote function calls. Passwords must match on both instances. RFCs can not be used with empty password.": "远程函数调用的密码。两个实例上的密码必须匹配。RFC 不能使用空密码。",
        "HTTP port for dockerized instance of A0.": "容器化 A0 实例的 HTTP 端口。",
        "SSH port for dockerized instance of A0.": "容器化 A0 实例的 SSH 端口。",
        "Parameters for A0 framework development. RFCs (remote function calls) are used to call functions on another A0 instance. You can develop and debug A0 natively on your local system while redirecting some functions to A0 instance in docker. This is crucial for development as A0 needs to run in standardized environment to support all features.": "A0 框架开发参数。RFC（远程函数调用）用于在另一个 A0 实例上调用函数。您可以在本地系统上本地开发和调试 A0，同时将一些函数重定向到 docker 中的 A0 实例。这对于开发至关重要，因为 A0 需要在标准化环境中运行以支持所有功能。",
        "View examples for using Agent Zero's external API endpoints with API key authentication.": "查看使用 Agent Zero 外部 API 端点和 API 密钥身份验证的示例。",
        "Agent Zero provides external API endpoints for integration with other applications. These endpoints use API key authentication and support text messages and file attachments.": "Agent Zero 提供外部 API 端点用于与其他应用程序集成。这些端点使用 API 密钥身份验证，并支持文本消息和文件附件。",
        "Enable update checker to notify about newer versions of Agent Zero.": "启用更新检查器以通知 Agent Zero 的新版本。",
        "Update checker periodically checks for new releases of Agent Zero and will notify when an update is recommended.<br>No personal data is sent to the update server, only randomized+anonymized unique ID and current version number, which help us evaluate the importance of the update in case of critical bug fixes etc.": "更新检查器定期检查 Agent Zero 的新版本，并在建议更新时通知。<br>不会向更新服务器发送个人数据，只发送随机化+匿名化的唯一 ID 和当前版本号，这有助于我们在关键错误修复等情况下评估更新的重要性。",
        "Create Backup": "创建备份",
        "Create a backup archive of selected files and configurations using customizable patterns.": "使用可自定义模式创建所选文件和配置的备份存档。",
        "Restore from Backup": "从备份恢复",
        "Restore files and configurations from a backup archive with pattern-based selection.": "从备份存档中恢复文件和配置，使用基于模式的选择。",
        "Backup and restore Agent Zero data and configurations using glob pattern-based file selection.": "使用基于 glob 模式的文件选择备份和恢复 Agent Zero 数据和配置。",
        "Settings for authentication to use Agent Zero Web UI.": "使用 Agent Zero Web UI 的身份验证设置。",
        "Change linux root password in docker container. This password can be used for SSH access. Original password was randomly generated during setup.": "更改 docker 容器中的 linux root 密码。此密码可用于 SSH 访问。原始密码在设置期间随机生成。",
        "root Password": "root 密码",
        "Exact name of model from selected provider": "所选提供商的确切模型名称",
        "API base URL for main chat model. Leave empty for default. Only relevant for Azure, local and custom (other) providers.": "主聊天模型的 API 基础 URL。留空使用默认值。仅对 Azure、本地和自定义（其他）提供商相关。",
        "Maximum number of tokens in the context window for LLM. System prompt, chat history, RAG and response all count towards this limit.": "LLM 上下文窗口中的最大令牌数。系统提示、聊天历史、RAG 和响应都计入此限制。",
        "Portion of context window dedicated to chat history visible to the agent. Chat history will automatically be optimized to fit. Smaller size will result in shorter and more summarized history. The remaining space will be used for system prompt, RAG and response.": "专用于代理可见聊天历史的上下文窗口部分。聊天历史将自动优化以适应。较小的尺寸将导致更短和更简洁的历史。剩余空间将用于系统提示、RAG 和响应。",
        "Models capable of Vision can for example natively see the content of image attachments.": "具有视觉能力的模型可以原生查看图像附件的内容。",
        "Limits the number of requests per minute to the chat model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.": "限制每分钟对聊天模型的请求数。如果超出限制则等待。设置为 0 禁用速率限制。",
        "Limits the number of input tokens per minute to the chat model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.": "限制每分钟对聊天模型的输入令牌数。如果超出限制则等待。设置为 0 禁用速率限制。",
        "Limits the number of output tokens per minute to the chat model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.": "限制每分钟对聊天模型的输出令牌数。如果超出限制则等待。设置为 0 禁用速率限制。",
        "Any other parameters supported by <a href='https://docs.litellm.ai/docs/set_keys' target='_blank'>LiteLLM</a>. Format is KEY=VALUE on individual lines, like .env file. Value can also contain JSON objects - when unquoted, it is treated as object, number etc., when quoted, it is treated as string.": "<a href='https://docs.litellm.ai/docs/set_keys' target='_blank'>LiteLLM</a> 支持的任何其他参数。格式是各行上的 KEY=VALUE，像 .env 文件一样。值也可以包含 JSON 对象 - 当不加引号时，它被视为对象、数字等，当加引号时，它被视为字符串。",
        "Selection and settings for main chat model used by Agent Zero": "Agent Zero 使用的主聊天模型的选择和设置",
        "Select provider for utility model used by the framework": "选择框架使用的实用模型提供商",
        "API base URL for utility model. Leave empty for default. Only relevant for Azure, local and custom (other) providers.": "实用模型的 API 基础 URL。留空使用默认值。仅对 Azure、本地和自定义（其他）提供商相关。",
        "Limits the number of requests per minute to the utility model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.": "限制每分钟对实用模型的请求数。如果超出限制则等待。设置为 0 禁用速率限制。",
        "Limits the number of input tokens per minute to the utility model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.": "限制每分钟对实用模型的输入令牌数。如果超出限制则等待。设置为 0 禁用速率限制。",
        "Limits the number of output tokens per minute to the utility model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.": "限制每分钟对实用模型的输出令牌数。如果超出限制则等待。设置为 0 禁用速率限制。",
        
        # 嵌入模型相关翻译
        "Select provider for embedding model used by the framework": "选择框架使用的嵌入模型提供商",
        "API base URL for embedding model. Leave empty for default. Only relevant for Azure, local and custom (other) providers.": "嵌入模型的 API 基础 URL。留空使用默认值。仅对 Azure、本地和自定义（其他）提供商相关。",
        "Limits the number of requests per minute to the embedding model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.": "限制每分钟对嵌入模型的请求数。如果超出限制则等待。设置为 0 禁用速率限制。",
        "Limits the number of input tokens per minute to the embedding model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.": "限制每分钟对嵌入模型的输入令牌数。如果超出限制则等待。设置为 0 禁用速率限制。",
        
        # 浏览器模型相关翻译
        "Select provider for web browser model used by <a href='https://github.com/browser-use/browser-use' target='_blank'>browser-use</a> framework": "选择 <a href='https://github.com/browser-use/browser-use' target='_blank'>browser-use</a> 框架使用的网页浏览器模型提供商",
        "API base URL for web browser model. Leave empty for default. Only relevant for Azure, local and custom (other) providers.": "网页浏览器模型的 API 基础 URL。留空使用默认值。仅对 Azure、本地和自定义（其他）提供商相关。",
        "Models capable of Vision can use it to analyze web pages from screenshots. Increases quality but also token usage.": "具有视觉能力的模型可以使用它来从截图分析网页。提高质量但也增加令牌使用量。",
        "Rate limit requests for web browser model.": "网页浏览器模型的请求速率限制。",
        "Rate limit input for web browser model.": "网页浏览器模型的输入速率限制。",
        "Rate limit output for web browser model.": "网页浏览器模型的输出速率限制。",
        "HTTP headers to include with all browser requests. Format is KEY=VALUE on individual lines, like .env file. Value can also contain JSON objects - when unquoted, it is treated as object, number etc., when quoted, it is treated as string. Example: Authorization=Bearer token123": "所有浏览器请求中包含的 HTTP 头部。格式是各行上的 KEY=VALUE，像 .env 文件一样。值也可以包含 JSON 对象 - 当不加引号时，它被视为对象、数字等，当加引号时，它被视为字符串。示例：Authorization=Bearer token123",
        "Settings for the web browser model. Agent Zero uses <a href='https://github.com/browser-use/browser-use' target='_blank'>browser-use</a> agentic framework to handle web interactions.": "网页浏览器模型的设置。Agent Zero 使用 <a href='https://github.com/browser-use/browser-use' target='_blank'>browser-use</a> 代理框架来处理网络交互。",
        "(JSON list of) >> RemoteServer <<: [name, url, headers, timeout (opt), sse_read_timeout (opt), disabled (opt)] / >> Local Server <<: [name, command, args, env, encoding (opt), encoding_error_handler (opt), disabled (opt)]": "(JSON 列表) >> 远程服务器 <<: [name, url, headers, timeout (可选), sse_read_timeout (可选), disabled (可选)] / >> 本地服务器 <<: [name, command, args, env, encoding (可选), encoding_error_handler (可选), disabled (可选)]",
        
        # 按钮文本
        "Open Dashboard": "打开仪表板",
        "Show API Examples": "显示 API 示例",
        "Create Backup": "创建备份",
        "Restore Backup": "恢复备份",
        "Open": "打开",
        "Settings for the embedding model used by Agent Zero.": "Agent Zero 使用的嵌入模型设置。",
        "No need to change": "无需更改",
        "The default HuggingFace model": "默认的 HuggingFace 模型",
        "is preloaded and runs locally within the docker container and there is no need to change it unless you have specific requirements for embedding.": "已预加载并在 docker 容器内本地运行，除非您对嵌入有特定要求，否则无需更改。",
        "Local Python TTY": "本地 Python TTY",
        "SSH": "SSH",
        "Tiny (39M, English)": "微型 (39M, 英文)",
        "Base (74M, English)": "基础 (74M, 英文)",
        "Small (244M, English)": "小型 (244M, 英文)",
        "Medium (769M, English)": "中型 (769M, 英文)",
        "Large (1.5B, Multilingual)": "大型 (1.5B, 多语言)",
        "Turbo (Multilingual)": "极速 (Turbo, 多语言)",
        
        # 描述文本
        "Select provider for main chat model used by Agent Zero": "选择 Agent Zero 使用的主聊天模型提供商",
        "Settings for the embedding model used by Agent Zero.<br><h4>⚠️ No need to change</h4>The default HuggingFace model {default_settings['embed_model_name']} is preloaded and runs locally within the docker container and there's no need to change it unless you have a specific requirements for embedding.": "Agent Zero 使用的嵌入模型设置。<br><h4>⚠️ 无需更改</h4>默认的 HuggingFace 模型 {default_settings['embed_model_name']} 已预加载并在 docker 容器内本地运行，除非您对嵌入有特定要求，否则无需更改。",
        "Customize the user interface settings": "自定义用户界面设置",
        "Select your preferred language": "选择您的首选语言",
        "Set user name for web UI": "设置 Web UI 的用户名",
        "Set password for web UI": "设置 Web UI 的密码",
        "Set user password for web UI": "设置 Web UI 的用户密码",
        "Smaller, cheaper, faster model for handling utility tasks like organizing memory, preparing prompts, summarizing.": "更小、更便宜、更快的模型，用于处理实用任务，如组织记忆、准备提示、总结。",
        "Agent parameters.": "代理参数。",
        "Subdirectory of /agents folder to be used by default agent no. 0. Subordinate agents can be spawned with other profiles, that is on their superior agent to decide. This setting affects the behaviour of the top level agent you communicate with.": "/agents 文件夹的子目录，用于默认代理编号 0。下级代理可以使用其他配置文件生成，这由其上级代理决定。此设置影响您与之通信的顶级代理的行为。",
        "Subdirectory of /knowledge folder to use for agent knowledge import. 'default' subfolder is always imported and contains framework knowledge.": "/knowledge 文件夹的子目录，用于代理知识导入。'default' 子文件夹始终被导入并包含框架知识。",
        "Subdirectory of /memory folder to use for agent memory storage. Used to separate memory storage between different instances.": "/memory 文件夹的子目录，用于代理记忆存储。用于在不同实例之间分离记忆存储。",
        "View and explore all stored memories in a table format with filtering and search capabilities.": "以表格格式查看和探索所有存储的记忆，具有过滤和搜索功能。",
        "Agent Zero will automatically recall memories based on convesation context.": "Agent Zero 将根据对话上下文自动回忆记忆。",
        "The agent will not wait for auto memory recall. Memories will be delivered one message later. This speeds up agent's response time but may result in less relevant first step.": "代理不会等待自动记忆回忆。记忆将在下一条消息中传递。这加快了代理的响应时间，但可能导致第一步不太相关。",
        "Enables vector DB query preparation from conversation context by utility LLM for auto-recall. Improves search quality, adds 1 utility LLM call per auto-recall.": "启用实用 LLM 从对话上下文准备向量数据库查询以进行自动回忆。提高搜索质量，每次自动回忆增加 1 次实用 LLM 调用。",
        "Enables memory relevance filtering by utility LLM for auto-recall. Improves search quality, adds 1 utility LLM call per auto-recall.": "启用实用 LLM 对自动回忆进行记忆相关性过滤。提高搜索质量，每次自动回忆增加 1 次实用 LLM 调用。",
        "Memories are recalled after every user or superior agent message. During agent's monologue, memories are recalled every X turns based on this parameter.": "在每个用户或上级代理消息后回忆记忆。在代理独白期间，根据此参数每 X 轮回忆记忆。",
        "The length of conversation history passed to memory recall LLM for context (in characters).": "传递给记忆回忆 LLM 的对话历史长度（以字符为单位）。",
        "The threshold for similarity search in memory recall (0 = no similarity, 1 = exact match).": "记忆回忆中相似性搜索的阈值（0 = 无相似性，1 = 完全匹配）。",
        "The maximum number of memories returned by vector DB for further processing.": "向量数据库返回的用于进一步处理的最大记忆数。",
        "The maximum number of memories to inject into A0's context window.": "注入到 A0 上下文窗口的最大记忆数。",
        "The maximum number of solutions returned by vector DB for further processing.": "向量数据库返回的用于进一步处理的最大解决方案数。",
        "The maximum number of solutions to inject into A0's context window.": "注入到 A0 上下文窗口的最大解决方案数。",
        "A0 will automatically memorize facts and solutions from conversation history.": "A0 将自动从对话历史中记忆事实和解决方案。",
        "A0 will automatically consolidate similar memories using utility LLM. Improves memory quality over time, adds 2 utility LLM calls per memory.": "A0 将使用实用 LLM 自动整合相似的记忆。随着时间的推移提高记忆质量，每个记忆增加 2 次实用 LLM 调用。",
        "Only applies when AI consolidation is disabled. Replaces previous similar memories with new ones based on this threshold. 0 = replace even if not similar at all, 1 = replace only if exact match.": "仅在禁用 AI 整合时适用。根据此阈值用新记忆替换以前的相似记忆。0 = 即使完全不相似也替换，1 = 仅在完全匹配时替换。",
        "Configuration of A0's memory system. A0 memorizes and recalls memories automatically to help it's context awareness.": "A0 记忆系统的配置。A0 自动记忆和回忆记忆以帮助其上下文感知。",
        "Voice transcription and speech synthesis settings.": "语音转录和语音合成设置。",
        "Select the speech-to-text model size": "选择语音转文本模型大小",
        "Language code (e.g. en, fr, it)": "语言代码（例如 en, fr, it）",
        "Select the microphone device to use for speech-to-text.": "选择用于语音转文本的麦克风设备。",
        "Silence detection threshold. Lower values are more sensitive to noise.": "静音检测阈值。较低的值对噪音更敏感。",
        "Duration of silence before the system considers speaking to have ended.": "系统认为说话结束前的静音持续时间。",
        "Duration of silence before the system closes the microphone.": "系统关闭麦克风前的静音持续时间。",
        "Enable higher quality server-side AI (Kokoro) instead of browser-based text-to-speech.": "启用更高质量的服务器端 AI (Kokoro) 而不是基于浏览器的文本转语音。"
    }
}

def translate_setting(text: str, language: str = "en-US") -> str:
    """翻译设置文本"""
    if language in SETTINGS_TRANSLATIONS and text in SETTINGS_TRANSLATIONS[language]:
        return SETTINGS_TRANSLATIONS[language][text]
    return text


class Settings(TypedDict):
    version: str

    chat_model_provider: str
    chat_model_name: str
    chat_model_api_base: str
    chat_model_kwargs: dict[str, Any]
    chat_model_ctx_length: int
    chat_model_ctx_history: float
    chat_model_vision: bool
    chat_model_rl_requests: int
    chat_model_rl_input: int
    chat_model_rl_output: int

    util_model_provider: str
    util_model_name: str
    util_model_api_base: str
    util_model_kwargs: dict[str, Any]
    util_model_ctx_length: int
    util_model_ctx_input: float
    util_model_rl_requests: int
    util_model_rl_input: int
    util_model_rl_output: int

    embed_model_provider: str
    embed_model_name: str
    embed_model_api_base: str
    embed_model_kwargs: dict[str, Any]
    embed_model_rl_requests: int
    embed_model_rl_input: int

    browser_model_provider: str
    browser_model_name: str
    browser_model_api_base: str
    browser_model_vision: bool
    browser_model_rl_requests: int
    browser_model_rl_input: int
    browser_model_rl_output: int
    browser_model_kwargs: dict[str, Any]
    browser_http_headers: dict[str, Any]

    agent_profile: str
    agent_memory_subdir: str
    agent_knowledge_subdir: str

    memory_recall_enabled: bool
    memory_recall_delayed: bool
    memory_recall_interval: int
    memory_recall_history_len: int
    memory_recall_memories_max_search: int
    memory_recall_solutions_max_search: int
    memory_recall_memories_max_result: int
    memory_recall_solutions_max_result: int
    memory_recall_similarity_threshold: float
    memory_recall_query_prep: bool
    memory_recall_post_filter: bool
    memory_memorize_enabled: bool
    memory_memorize_consolidation: bool
    memory_memorize_replace_threshold: float

    api_keys: dict[str, str]

    auth_login: str
    auth_password: str
    root_password: str

    rfc_auto_docker: bool
    rfc_url: str
    rfc_password: str
    rfc_port_http: int
    rfc_port_ssh: int

    shell_interface: Literal['local','ssh']

    stt_model_size: str
    stt_language: str
    stt_silence_threshold: float
    stt_silence_duration: int
    stt_waiting_timeout: int

    tts_kokoro: bool

    ui_language: str

    mcp_servers: str
    mcp_client_init_timeout: int
    mcp_client_tool_timeout: int
    mcp_server_enabled: bool
    mcp_server_token: str

    a2a_server_enabled: bool

    variables: str
    secrets: str

    # LiteLLM global kwargs applied to all model calls
    litellm_global_kwargs: dict[str, Any]

    update_check_enabled: bool

class PartialSettings(Settings, total=False):
    pass


class FieldOption(TypedDict):
    value: str
    label: str


class SettingsField(TypedDict, total=False):
    id: str
    title: str
    description: str
    type: Literal[
        "text",
        "number",
        "select",
        "range",
        "textarea",
        "password",
        "switch",
        "button",
        "html",
    ]
    value: Any
    min: float
    max: float
    step: float
    hidden: bool
    options: list[FieldOption]
    style: str


class SettingsSection(TypedDict, total=False):
    id: str
    title: str
    description: str
    fields: list[SettingsField]
    tab: str  # Indicates which tab this section belongs to


class SettingsOutput(TypedDict):
    sections: list[SettingsSection]


PASSWORD_PLACEHOLDER = "****PSWD****"
API_KEY_PLACEHOLDER = "************"

SETTINGS_FILE = files.get_abs_path("tmp/settings.json")
_settings: Settings | None = None


def convert_out(settings: Settings) -> SettingsOutput:
    default_settings = get_default_settings()
    
    # 获取当前语言设置
    current_language = settings.get("ui_language", "en-US")

    # main model section
    chat_model_fields: list[SettingsField] = []
    chat_model_fields.append(
        {
            "id": "chat_model_provider",
            "title": translate_setting("Chat model provider", current_language),
            "description": translate_setting("Select provider for main chat model used by Agent Zero", current_language),
            "type": "select",
            "value": settings["chat_model_provider"],
            "options": cast(list[FieldOption], get_providers("chat")),
        }
    )
    chat_model_fields.append(
        {
            "id": "chat_model_name",
            "title": translate_setting("Chat model name", current_language),
            "description": translate_setting("Exact name of model from selected provider", current_language),
            "type": "text",
            "value": settings["chat_model_name"],
        }
    )

    chat_model_fields.append(
        {
            "id": "chat_model_api_base",
            "title": translate_setting("Chat model API base URL", current_language),
            "description": translate_setting("API base URL for main chat model. Leave empty for default. Only relevant for Azure, local and custom (other) providers.", current_language),
            "type": "text",
            "value": settings["chat_model_api_base"],
        }
    )

    chat_model_fields.append(
        {
            "id": "chat_model_ctx_length",
            "title": translate_setting("Chat model context length", current_language),
            "description": translate_setting("Maximum number of tokens in the context window for LLM. System prompt, chat history, RAG and response all count towards this limit.", current_language),
            "type": "number",
            "value": settings["chat_model_ctx_length"],
        }
    )

    chat_model_fields.append(
        {
            "id": "chat_model_ctx_history",
            "title": translate_setting("Context window space for chat history", current_language),
            "description": translate_setting("Portion of context window dedicated to chat history visible to the agent. Chat history will automatically be optimized to fit. Smaller size will result in shorter and more summarized history. The remaining space will be used for system prompt, RAG and response.", current_language),
            "type": "range",
            "min": 0.01,
            "max": 1,
            "step": 0.01,
            "value": settings["chat_model_ctx_history"],
        }
    )

    chat_model_fields.append(
        {
            "id": "chat_model_vision",
            "title": translate_setting("Supports Vision", current_language),
            "description": translate_setting("Models capable of Vision can for example natively see the content of image attachments.", current_language),
            "type": "switch",
            "value": settings["chat_model_vision"],
        }
    )

    chat_model_fields.append(
        {
            "id": "chat_model_rl_requests",
            "title": translate_setting("Requests per minute limit", current_language),
            "description": translate_setting("Limits the number of requests per minute to the chat model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.", current_language),
            "type": "number",
            "value": settings["chat_model_rl_requests"],
        }
    )

    chat_model_fields.append(
        {
            "id": "chat_model_rl_input",
            "title": translate_setting("Input tokens per minute limit", current_language),
            "description": translate_setting("Limits the number of input tokens per minute to the chat model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.", current_language),
            "type": "number",
            "value": settings["chat_model_rl_input"],
        }
    )

    chat_model_fields.append(
        {
            "id": "chat_model_rl_output",
            "title": translate_setting("Output tokens per minute limit", current_language),
            "description": translate_setting("Limits the number of output tokens per minute to the chat model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.", current_language),
            "type": "number",
            "value": settings["chat_model_rl_output"],
        }
    )

    chat_model_fields.append(
        {
            "id": "chat_model_kwargs",
            "title": translate_setting("Chat model additional parameters", current_language),
            "description": translate_setting("Any other parameters supported by <a href='https://docs.litellm.ai/docs/set_keys' target='_blank'>LiteLLM</a>. Format is KEY=VALUE on individual lines, like .env file. Value can also contain JSON objects - when unquoted, it is treated as object, number etc., when quoted, it is treated as string.", current_language),
            "type": "textarea",
            "value": _dict_to_env(settings["chat_model_kwargs"]),
        }
    )

    chat_model_section: SettingsSection = {
        "id": "chat_model",
        "title": translate_setting("Chat Model", current_language),
        "description": translate_setting("Selection and settings for main chat model used by Agent Zero", current_language),
        "fields": chat_model_fields,
        "tab": "agent",
    }

    # main model section
    util_model_fields: list[SettingsField] = []
    util_model_fields.append(
        {
            "id": "util_model_provider",
            "title": translate_setting("Utility model provider", current_language),
            "description": translate_setting("Select provider for utility model used by the framework", current_language),
            "type": "select",
            "value": settings["util_model_provider"],
            "options": cast(list[FieldOption], get_providers("chat")),
        }
    )
    util_model_fields.append(
        {
            "id": "util_model_name",
            "title": translate_setting("Utility model name", current_language),
            "description": translate_setting("Exact name of model from selected provider", current_language),
            "type": "text",
            "value": settings["util_model_name"],
        }
    )

    util_model_fields.append(
        {
            "id": "util_model_api_base",
            "title": translate_setting("Utility model API base URL", current_language),
            "description": translate_setting("API base URL for utility model. Leave empty for default. Only relevant for Azure, local and custom (other) providers.", current_language),
            "type": "text",
            "value": settings["util_model_api_base"],
        }
    )

    util_model_fields.append(
        {
            "id": "util_model_rl_requests",
            "title": translate_setting("Requests per minute limit", current_language),
            "description": translate_setting("Limits the number of requests per minute to the utility model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.", current_language),
            "type": "number",
            "value": settings["util_model_rl_requests"],
        }
    )

    util_model_fields.append(
        {
            "id": "util_model_rl_input",
            "title": translate_setting("Input tokens per minute limit", current_language),
            "description": translate_setting("Limits the number of input tokens per minute to the utility model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.", current_language),
            "type": "number",
            "value": settings["util_model_rl_input"],
        }
    )

    util_model_fields.append(
        {
            "id": "util_model_rl_output",
            "title": translate_setting("Output tokens per minute limit", current_language),
            "description": translate_setting("Limits the number of output tokens per minute to the utility model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.", current_language),
            "type": "number",
            "value": settings["util_model_rl_output"],
        }
    )

    util_model_fields.append(
        {
            "id": "util_model_kwargs",
            "title": translate_setting("Utility model additional parameters", current_language),
            "description": translate_setting("Any other parameters supported by <a href='https://docs.litellm.ai/docs/set_keys' target='_blank'>LiteLLM</a>. Format is KEY=VALUE on individual lines, like .env file. Value can also contain JSON objects - when unquoted, it is treated as object, number etc., when quoted, it is treated as string.", current_language),
            "type": "textarea",
            "value": _dict_to_env(settings["util_model_kwargs"]),
        }
    )

    util_model_section: SettingsSection = {
        "id": "util_model",
        "title": translate_setting("Utility model", current_language),
        "description": translate_setting("Smaller, cheaper, faster model for handling utility tasks like organizing memory, preparing prompts, summarizing.", current_language),
        "fields": util_model_fields,
        "tab": "agent",
    }

    # embedding model section
    embed_model_fields: list[SettingsField] = []
    embed_model_fields.append(
        {
            "id": "embed_model_provider",
            "title": translate_setting("Embedding model provider", current_language),
            "description": translate_setting("Select provider for embedding model used by the framework", current_language),
            "type": "select",
            "value": settings["embed_model_provider"],
            "options": cast(list[FieldOption], get_providers("embedding")),
        }
    )
    embed_model_fields.append(
        {
            "id": "embed_model_name",
            "title": translate_setting("Embedding model name", current_language),
            "description": translate_setting("Exact name of model from selected provider", current_language),
            "type": "text",
            "value": settings["embed_model_name"],
        }
    )

    embed_model_fields.append(
        {
            "id": "embed_model_api_base",
            "title": translate_setting("Embedding model API base URL", current_language),
            "description": translate_setting("API base URL for embedding model. Leave empty for default. Only relevant for Azure, local and custom (other) providers.", current_language),
            "type": "text",
            "value": settings["embed_model_api_base"],
        }
    )

    embed_model_fields.append(
        {
            "id": "embed_model_rl_requests",
            "title": translate_setting("Requests per minute limit", current_language),
            "description": translate_setting("Limits the number of requests per minute to the embedding model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.", current_language),
            "type": "number",
            "value": settings["embed_model_rl_requests"],
        }
    )

    embed_model_fields.append(
        {
            "id": "embed_model_rl_input",
            "title": translate_setting("Input tokens per minute limit", current_language),
            "description": translate_setting("Limits the number of input tokens per minute to the embedding model. Waits if the limit is exceeded. Set to 0 to disable rate limiting.", current_language),
            "type": "number",
            "value": settings["embed_model_rl_input"],
        }
    )

    embed_model_fields.append(
        {
            "id": "embed_model_kwargs",
            "title": translate_setting("Embedding model additional parameters", current_language),
            "description": translate_setting("Any other parameters supported by <a href='https://docs.litellm.ai/docs/set_keys' target='_blank'>LiteLLM</a>. Format is KEY=VALUE on individual lines, like .env file. Value can also contain JSON objects - when unquoted, it is treated as object, number etc., when quoted, it is treated as string.", current_language),
            "type": "textarea",
            "value": _dict_to_env(settings["embed_model_kwargs"]),
        }
    )

    embed_model_section: SettingsSection = {
        "id": "embed_model",
        "title": translate_setting("Embedding Model", current_language),
        "description": translate_setting("Settings for the embedding model used by Agent Zero.", current_language) + f"<br><h4>⚠️ {translate_setting('No need to change', current_language)}</h4>{translate_setting('The default HuggingFace model', current_language)} {default_settings['embed_model_name']} {translate_setting('is preloaded and runs locally within the docker container and there is no need to change it unless you have specific requirements for embedding.', current_language)}",
        "fields": embed_model_fields,
        "tab": "agent",
    }

    # embedding model section
    browser_model_fields: list[SettingsField] = []
    browser_model_fields.append(
        {
            "id": "browser_model_provider",
            "title": translate_setting("Web Browser model provider", current_language),
            "description": translate_setting("Select provider for web browser model used by <a href='https://github.com/browser-use/browser-use' target='_blank'>browser-use</a> framework", current_language),
            "type": "select",
            "value": settings["browser_model_provider"],
            "options": cast(list[FieldOption], get_providers("chat")),
        }
    )
    browser_model_fields.append(
        {
            "id": "browser_model_name",
            "title": translate_setting("Web Browser model name", current_language),
            "description": translate_setting("Exact name of model from selected provider", current_language),
            "type": "text",
            "value": settings["browser_model_name"],
        }
    )

    browser_model_fields.append(
        {
            "id": "browser_model_api_base",
            "title": translate_setting("Web Browser model API base URL", current_language),
            "description": translate_setting("API base URL for web browser model. Leave empty for default. Only relevant for Azure, local and custom (other) providers.", current_language),
            "type": "text",
            "value": settings["browser_model_api_base"],
        }
    )

    browser_model_fields.append(
        {
            "id": "browser_model_vision",
            "title": translate_setting("Use Vision", current_language),
            "description": translate_setting("Models capable of Vision can use it to analyze web pages from screenshots. Increases quality but also token usage.", current_language),
            "type": "switch",
            "value": settings["browser_model_vision"],
        }
    )

    browser_model_fields.append(
        {
            "id": "browser_model_rl_requests",
            "title": translate_setting("Web Browser model rate limit requests", current_language),
            "description": translate_setting("Rate limit requests for web browser model.", current_language),
            "type": "number",
            "value": settings["browser_model_rl_requests"],
        }
    )

    browser_model_fields.append(
        {
            "id": "browser_model_rl_input",
            "title": translate_setting("Web Browser model rate limit input", current_language),
            "description": translate_setting("Rate limit input for web browser model.", current_language),
            "type": "number",
            "value": settings["browser_model_rl_input"],
        }
    )

    browser_model_fields.append(
        {
            "id": "browser_model_rl_output",
            "title": translate_setting("Web Browser model rate limit output", current_language),
            "description": translate_setting("Rate limit output for web browser model.", current_language),
            "type": "number",
            "value": settings["browser_model_rl_output"],
        }
    )

    browser_model_fields.append(
        {
            "id": "browser_model_kwargs",
            "title": translate_setting("Web Browser model additional parameters", current_language),
            "description": translate_setting("Any other parameters supported by <a href='https://docs.litellm.ai/docs/set_keys' target='_blank'>LiteLLM</a>. Format is KEY=VALUE on individual lines, like .env file. Value can also contain JSON objects - when unquoted, it is treated as object, number etc., when quoted, it is treated as string.", current_language),
            "type": "textarea",
            "value": _dict_to_env(settings["browser_model_kwargs"]),
        }
    )

    browser_model_fields.append(
        {
            "id": "browser_http_headers",
            "title": translate_setting("HTTP Headers", current_language),
            "description": translate_setting("HTTP headers to include with all browser requests. Format is KEY=VALUE on individual lines, like .env file. Value can also contain JSON objects - when unquoted, it is treated as object, number etc., when quoted, it is treated as string. Example: Authorization=Bearer token123", current_language),
            "type": "textarea",
            "value": _dict_to_env(settings.get("browser_http_headers", {})),
        }
    )

    browser_model_section: SettingsSection = {
        "id": "browser_model",
        "title": translate_setting("Web Browser Model", current_language),
        "description": translate_setting("Settings for the web browser model. Agent Zero uses <a href='https://github.com/browser-use/browser-use' target='_blank'>browser-use</a> agentic framework to handle web interactions.", current_language),
        "fields": browser_model_fields,
        "tab": "agent",
    }

    # UI settings section
    ui_fields: list[SettingsField] = []
    
    ui_fields.append(
        {
            "id": "ui_language",
            "title": translate_setting("Language", current_language),
            "description": translate_setting("Select your preferred language", current_language),
            "type": "select",
            "value": settings["ui_language"],
            "options": [
                {"value": "en-US", "label": "English"},
                {"value": "zh-CN", "label": "简体中文 (Chinese Simplified)"}
            ],
        }
    )

    ui_section: SettingsSection = {
        "id": "ui_settings",
        "title": translate_setting("User Interface", current_language),
        "description": translate_setting("Customize the user interface settings", current_language),
        "fields": ui_fields,
        "tab": "agent",
    }

    # basic auth section
    auth_fields: list[SettingsField] = []

    auth_fields.append(
        {
            "id": "auth_login",
            "title": translate_setting("UI Login", current_language),
            "description": translate_setting("Set user name for web UI", current_language),
            "type": "text",
            "value": dotenv.get_dotenv_value(dotenv.KEY_AUTH_LOGIN) or "",
        }
    )

    auth_fields.append(
        {
            "id": "auth_password",
            "title": translate_setting("UI Password", current_language),
            "description": translate_setting("Set password for web UI", current_language),
            "type": "password",
            "value": (
                PASSWORD_PLACEHOLDER
                if dotenv.get_dotenv_value(dotenv.KEY_AUTH_PASSWORD)
                else ""
            ),
        }
    )

    if runtime.is_dockerized():
        auth_fields.append(
            {
                "id": "root_password",
                "title": translate_setting("root Password", current_language),
                "description": translate_setting("Change linux root password in docker container. This password can be used for SSH access. Original password was randomly generated during setup.", current_language),
                "type": "password",
                "value": "",
            }
        )

    auth_section: SettingsSection = {
        "id": "auth",
        "title": translate_setting("Authentication", current_language),
        "description": translate_setting("Settings for authentication to use Agent Zero Web UI.", current_language),
        "fields": auth_fields,
        "tab": "external",
    }

    # api keys model section
    api_keys_fields: list[SettingsField] = []

    # Collect unique providers from both chat and embedding sections
    providers_seen: set[str] = set()
    for p_type in ("chat", "embedding"):
        for provider in get_providers(p_type):
            pid_lower = provider["value"].lower()
            if pid_lower in providers_seen:
                continue
            providers_seen.add(pid_lower)
            api_keys_fields.append(
                _get_api_key_field(settings, pid_lower, provider["label"])
            )

    api_keys_section: SettingsSection = {
        "id": "api_keys",
        "title": translate_setting("API Keys", current_language),
        "description": translate_setting("API keys for model providers and services used by Agent Zero. You can set multiple API keys separated by a comma (,). They will be used in round-robin fashion.<br>For more information abou Agent Zero Venice provider, see <a href='http://agent-zero.ai/?community/api-dashboard/about' target='_blank'>Agent Zero Venice</a>.", current_language),
        "fields": api_keys_fields,
        "tab": "external",
    }

    # LiteLLM global config section
    litellm_fields: list[SettingsField] = []

    litellm_fields.append(
        {
            "id": "litellm_global_kwargs",
            "title": translate_setting("LiteLLM global parameters", current_language),
            "description": translate_setting("Global LiteLLM params (e.g. timeout, stream_timeout) in .env format: one KEY=VALUE per line. Example: <code>stream_timeout=30</code>. Applied to all LiteLLM calls unless overridden. See <a href='https://docs.litellm.ai/docs/set_keys' target='_blank'>LiteLLM</a> and <a href='https://docs.litellm.ai/docs/proxy/timeout' target='_blank'>timeouts</a>.", current_language),
            "type": "textarea",
            "value": _dict_to_env(settings["litellm_global_kwargs"]),
            "style": "height: 12em",
        }
    )

    litellm_section: SettingsSection = {
        "id": "litellm",
        "title": translate_setting("LiteLLM Global Settings", current_language),
        "description": translate_setting("Configure global parameters passed to LiteLLM for all providers.", current_language),
        "fields": litellm_fields,
        "tab": "external",
    }

    # Agent config section
    agent_fields: list[SettingsField] = []

    agent_fields.append(
        {
            "id": "agent_profile",
            "title": translate_setting("Default agent profile", current_language),
            "description": translate_setting("Subdirectory of /agents folder to be used by default agent no. 0. Subordinate agents can be spawned with other profiles, that is on their superior agent to decide. This setting affects the behaviour of the top level agent you communicate with.", current_language),
            "type": "select",
            "value": settings["agent_profile"],
            "options": [
                {"value": subdir, "label": subdir}
                for subdir in files.get_subdirectories("agents")
                if subdir != "_example"
            ],
        }
    )

    agent_fields.append(
        {
            "id": "agent_knowledge_subdir",
            "title": translate_setting("Knowledge subdirectory", current_language),
            "description": translate_setting("Subdirectory of /knowledge folder to use for agent knowledge import. 'default' subfolder is always imported and contains framework knowledge.", current_language),
            "type": "select",
            "value": settings["agent_knowledge_subdir"],
            "options": [
                {"value": subdir, "label": subdir}
                for subdir in files.get_subdirectories("knowledge", exclude="default")
            ],
        }
    )

    agent_section: SettingsSection = {
        "id": "agent",
        "title": translate_setting("Agent Config", current_language),
        "description": translate_setting("Agent parameters.", current_language),
        "fields": agent_fields,
        "tab": "agent",
    }

    memory_fields: list[SettingsField] = []

    memory_fields.append(
        {
            "id": "agent_memory_subdir",
            "title": translate_setting("Memory Subdirectory", current_language),
            "description": translate_setting("Subdirectory of /memory folder to use for agent memory storage. Used to separate memory storage between different instances.", current_language),
            "type": "text",
            "value": settings["agent_memory_subdir"],
            # "options": [
            #     {"value": subdir, "label": subdir}
            #     for subdir in files.get_subdirectories("memory", exclude="embeddings")
            # ],
        }
    )

    memory_fields.append(
        {
            "id": "memory_dashboard",
            "title": translate_setting("Memory Dashboard", current_language),
            "description": translate_setting("View and explore all stored memories in a table format with filtering and search capabilities.", current_language),
            "type": "button",
            "value": translate_setting("Open Dashboard", current_language),
        }
    )

    memory_fields.append(
        {
            "id": "memory_recall_enabled",
            "title": translate_setting("Memory auto-recall enabled", current_language),
            "description": translate_setting("Agent Zero will automatically recall memories based on convesation context.", current_language),
            "type": "switch",
            "value": settings["memory_recall_enabled"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_recall_delayed",
            "title": translate_setting("Memory auto-recall delayed", current_language),
            "description": translate_setting("The agent will not wait for auto memory recall. Memories will be delivered one message later. This speeds up agent's response time but may result in less relevant first step.", current_language),
            "type": "switch",
            "value": settings["memory_recall_delayed"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_recall_query_prep",
            "title": translate_setting("Auto-recall AI query preparation", current_language),
            "description": translate_setting("Enables vector DB query preparation from conversation context by utility LLM for auto-recall. Improves search quality, adds 1 utility LLM call per auto-recall.", current_language),
            "type": "switch",
            "value": settings["memory_recall_query_prep"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_recall_post_filter",
            "title": translate_setting("Auto-recall AI post-filtering", current_language),
            "description": translate_setting("Enables memory relevance filtering by utility LLM for auto-recall. Improves search quality, adds 1 utility LLM call per auto-recall.", current_language),
            "type": "switch",
            "value": settings["memory_recall_post_filter"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_recall_interval",
            "title": translate_setting("Memory auto-recall interval", current_language),
            "description": translate_setting("Memories are recalled after every user or superior agent message. During agent's monologue, memories are recalled every X turns based on this parameter.", current_language),
            "type": "range",
            "min": 1,
            "max": 10,
            "step": 1,
            "value": settings["memory_recall_interval"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_recall_history_len",
            "title": translate_setting("Memory auto-recall history length", current_language),
            "description": translate_setting("The length of conversation history passed to memory recall LLM for context (in characters).", current_language),
            "type": "number",
            "value": settings["memory_recall_history_len"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_recall_similarity_threshold",
            "title": translate_setting("Memory auto-recall similarity threshold", current_language),
            "description": translate_setting("The threshold for similarity search in memory recall (0 = no similarity, 1 = exact match).", current_language),
            "type": "range",
            "min": 0,
            "max": 1,
            "step": 0.01,
            "value": settings["memory_recall_similarity_threshold"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_recall_memories_max_search",
            "title": translate_setting("Memory auto-recall max memories to search", current_language),
            "description": translate_setting("The maximum number of memories returned by vector DB for further processing.", current_language),
            "type": "number",
            "value": settings["memory_recall_memories_max_search"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_recall_memories_max_result",
            "title": translate_setting("Memory auto-recall max memories to use", current_language),
            "description": translate_setting("The maximum number of memories to inject into A0's context window.", current_language),
            "type": "number",
            "value": settings["memory_recall_memories_max_result"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_recall_solutions_max_search",
            "title": translate_setting("Memory auto-recall max solutions to search", current_language),
            "description": translate_setting("The maximum number of solutions returned by vector DB for further processing.", current_language),
            "type": "number",
            "value": settings["memory_recall_solutions_max_search"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_recall_solutions_max_result",
            "title": translate_setting("Memory auto-recall max solutions to use", current_language),
            "description": translate_setting("The maximum number of solutions to inject into A0's context window.", current_language),
            "type": "number",
            "value": settings["memory_recall_solutions_max_result"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_memorize_enabled",
            "title": translate_setting("Auto-memorize enabled", current_language),
            "description": translate_setting("A0 will automatically memorize facts and solutions from conversation history.", current_language),
            "type": "switch",
            "value": settings["memory_memorize_enabled"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_memorize_consolidation",
            "title": translate_setting("Auto-memorize AI consolidation", current_language),
            "description": translate_setting("A0 will automatically consolidate similar memories using utility LLM. Improves memory quality over time, adds 2 utility LLM calls per memory.", current_language),
            "type": "switch",
            "value": settings["memory_memorize_consolidation"],
        }
    )

    memory_fields.append(
        {
            "id": "memory_memorize_replace_threshold",
            "title": translate_setting("Auto-memorize replacement threshold", current_language),
            "description": translate_setting("Only applies when AI consolidation is disabled. Replaces previous similar memories with new ones based on this threshold. 0 = replace even if not similar at all, 1 = replace only if exact match.", current_language),
            "type": "range",
            "min": 0,
            "max": 1,
            "step": 0.01,
            "value": settings["memory_memorize_replace_threshold"],
        }
    )

    memory_section: SettingsSection = {
        "id": "memory",
        "title": translate_setting("Memory", current_language),
        "description": translate_setting("Configuration of A0's memory system. A0 memorizes and recalls memories automatically to help it's context awareness.", current_language),
        "fields": memory_fields,
        "tab": "agent",
    }

    dev_fields: list[SettingsField] = []

    dev_fields.append(
        {
            "id": "shell_interface",
            "title": translate_setting("Shell Interface", current_language),
            "description": translate_setting("Terminal interface used for Code Execution Tool. Local Python TTY works locally in both dockerized and development environments. SSH always connects to dockerized environment (automatically at localhost or RFC host address).", current_language),
            "type": "select",
            "value": settings["shell_interface"],
            "options": [{"value": "local", "label": translate_setting("Local Python TTY", current_language)}, {"value": "ssh", "label": translate_setting("SSH", current_language)}],
        }
    )

    if runtime.is_development():
        # dev_fields.append(
        #     {
        #         "id": "rfc_auto_docker",
        #         "title": "RFC Auto Docker Management",
        #         "description": "Automatically create dockerized instance of A0 for RFCs using this instance's code base and, settings and .env.",
        #         "type": "text",
        #         "value": settings["rfc_auto_docker"],
        #     }
        # )

        dev_fields.append(
            {
                "id": "rfc_url",
                "title": translate_setting("RFC Destination URL", current_language),
                "description": translate_setting("URL of dockerized A0 instance for remote function calls. Do not specify port here.", current_language),
                "type": "text",
                "value": settings["rfc_url"],
            }
        )

    dev_fields.append(
        {
            "id": "rfc_password",
            "title": translate_setting("RFC Password", current_language),
            "description": translate_setting("Password for remote function calls. Passwords must match on both instances. RFCs can not be used with empty password.", current_language),
            "type": "password",
            "value": (
                PASSWORD_PLACEHOLDER
                if dotenv.get_dotenv_value(dotenv.KEY_RFC_PASSWORD)
                else ""
            ),
        }
    )

    if runtime.is_development():
        dev_fields.append(
            {
                "id": "rfc_port_http",
                "title": translate_setting("RFC HTTP port", current_language),
                "description": translate_setting("HTTP port for dockerized instance of A0.", current_language),
                "type": "text",
                "value": settings["rfc_port_http"],
            }
        )

        dev_fields.append(
            {
                "id": "rfc_port_ssh",
                "title": translate_setting("RFC SSH port", current_language),
                "description": translate_setting("SSH port for dockerized instance of A0.", current_language),
                "type": "text",
                "value": settings["rfc_port_ssh"],
            }
        )

    dev_section: SettingsSection = {
        "id": "dev",
        "title": translate_setting("Development", current_language),
        "description": translate_setting("Parameters for A0 framework development. RFCs (remote function calls) are used to call functions on another A0 instance. You can develop and debug A0 natively on your local system while redirecting some functions to A0 instance in docker. This is crucial for development as A0 needs to run in standardized environment to support all features.", current_language),
        "fields": dev_fields,
        "tab": "developer",
    }

    # code_exec_fields: list[SettingsField] = []

    # code_exec_fields.append(
    #     {
    #         "id": "code_exec_ssh_enabled",
    #         "title": "Use SSH for code execution",
    #         "description": "Code execution will use SSH to connect to the terminal. When disabled, a local python terminal interface is used instead. SSH should only be used in development environment or when encountering issues with the local python terminal interface.",
    #         "type": "switch",
    #         "value": settings["code_exec_ssh_enabled"],
    #     }
    # )

    # code_exec_fields.append(
    #     {
    #         "id": "code_exec_ssh_addr",
    #         "title": "Code execution SSH address",
    #         "description": "Address of the SSH server for code execution. Only applies when SSH is enabled.",
    #         "type": "text",
    #         "value": settings["code_exec_ssh_addr"],
    #     }
    # )

    # code_exec_fields.append(
    #     {
    #         "id": "code_exec_ssh_port",
    #         "title": "Code execution SSH port",
    #         "description": "Port of the SSH server for code execution. Only applies when SSH is enabled.",
    #         "type": "text",
    #         "value": settings["code_exec_ssh_port"],
    #     }
    # )

    # code_exec_section: SettingsSection = {
    #     "id": "code_exec",
    #     "title": "Code execution",
    #     "description": "Configuration of code execution by the agent.",
    #     "fields": code_exec_fields,
    #     "tab": "developer",
    # }

    # Speech to text section
    stt_fields: list[SettingsField] = []

    stt_fields.append(
        {
            "id": "stt_microphone_section",
            "title": translate_setting("Microphone device", current_language),
            "description": translate_setting("Select the microphone device to use for speech-to-text.", current_language),
            "value": "<x-component path='/settings/speech/microphone.html' />",
            "type": "html",
        }
    )

    stt_fields.append(
        {
            "id": "stt_model_size",
            "title": translate_setting("Speech-to-text model size", current_language),
            "description": translate_setting("Select the speech-to-text model size", current_language),
            "type": "select",
            "value": settings["stt_model_size"],
            "options": [
                {"value": "tiny", "label": translate_setting("Tiny (39M, English)", current_language)},
                {"value": "base", "label": translate_setting("Base (74M, English)", current_language)},
                {"value": "small", "label": translate_setting("Small (244M, English)", current_language)},
                {"value": "medium", "label": translate_setting("Medium (769M, English)", current_language)},
                {"value": "large", "label": translate_setting("Large (1.5B, Multilingual)", current_language)},
                {"value": "turbo", "label": translate_setting("Turbo (Multilingual)", current_language)},
            ],
        }
    )

    stt_fields.append(
        {
            "id": "stt_language",
            "title": translate_setting("Speech-to-text language code", current_language),
            "description": translate_setting("Language code (e.g. en, fr, it)", current_language),
            "type": "text",
            "value": settings["stt_language"],
        }
    )

    stt_fields.append(
        {
            "id": "stt_silence_threshold",
            "title": translate_setting("Microphone silence threshold", current_language),
            "description": translate_setting("Silence detection threshold. Lower values are more sensitive to noise.", current_language),
            "type": "range",
            "min": 0,
            "max": 1,
            "step": 0.01,
            "value": settings["stt_silence_threshold"],
        }
    )

    stt_fields.append(
        {
            "id": "stt_silence_duration",
            "title": translate_setting("Microphone silence duration (ms)", current_language),
            "description": translate_setting("Duration of silence before the system considers speaking to have ended.", current_language),
            "type": "text",
            "value": settings["stt_silence_duration"],
        }
    )

    stt_fields.append(
        {
            "id": "stt_waiting_timeout",
            "title": translate_setting("Microphone waiting timeout (ms)", current_language),
            "description": translate_setting("Duration of silence before the system closes the microphone.", current_language),
            "type": "text",
            "value": settings["stt_waiting_timeout"],
        }
    )

    # TTS fields
    tts_fields: list[SettingsField] = []

    tts_fields.append(
        {
            "id": "tts_kokoro",
            "title": translate_setting("Enable Kokoro TTS", current_language),
            "description": translate_setting("Enable higher quality server-side AI (Kokoro) instead of browser-based text-to-speech.", current_language),
            "type": "switch",
            "value": settings["tts_kokoro"],
        }
    )

    speech_section: SettingsSection = {
        "id": "speech",
        "title": translate_setting("Speech", current_language),
        "description": translate_setting("Voice transcription and speech synthesis settings.", current_language),
        "fields": stt_fields + tts_fields,
        "tab": "agent",
    }

    # MCP section
    mcp_client_fields: list[SettingsField] = []

    mcp_client_fields.append(
        {
            "id": "mcp_servers_config",
            "title": translate_setting("MCP Servers Configuration", current_language),
            "description": translate_setting("External MCP servers can be configured here.", current_language),
            "type": "button",
            "value": translate_setting("Open", current_language),
        }
    )

    mcp_client_fields.append(
        {
            "id": "mcp_servers",
            "title": translate_setting("MCP Servers", current_language),
            "description": translate_setting("(JSON list of) >> RemoteServer <<: [name, url, headers, timeout (opt), sse_read_timeout (opt), disabled (opt)] / >> Local Server <<: [name, command, args, env, encoding (opt), encoding_error_handler (opt), disabled (opt)]", current_language),
            "type": "textarea",
            "value": settings["mcp_servers"],
            "hidden": True,
        }
    )

    mcp_client_fields.append(
        {
            "id": "mcp_client_init_timeout",
            "title": translate_setting("MCP Client Init Timeout", current_language),
            "description": translate_setting("Timeout for MCP client initialization (in seconds). Higher values might be required for complex MCPs, but might also slowdown system startup.", current_language),
            "type": "number",
            "value": settings["mcp_client_init_timeout"],
        }
    )

    mcp_client_fields.append(
        {
            "id": "mcp_client_tool_timeout",
            "title": translate_setting("MCP Client Tool Timeout", current_language),
            "description": translate_setting("Timeout for MCP client tool execution. Higher values might be required for complex tools, but might also result in long responses with failing tools.", current_language),
            "type": "number",
            "value": settings["mcp_client_tool_timeout"],
        }
    )

    mcp_client_section: SettingsSection = {
        "id": "mcp_client",
        "title": translate_setting("External MCP Servers", current_language),
        "description": translate_setting("Agent Zero can use external MCP servers, local or remote as tools.", current_language),
        "fields": mcp_client_fields,
        "tab": "mcp",
    }

   # Secrets section
    secrets_fields: list[SettingsField] = []

    secrets_manager = get_default_secrets_manager()
    try:
        secrets = secrets_manager.get_masked_secrets()
    except Exception:
        secrets = ""

    secrets_fields.append({
        "id": "variables",
        "title": translate_setting("Variables Store", current_language),
        "description": translate_setting("Store non-sensitive variables in .env format e.g. EMAIL_IMAP_SERVER=\"imap.gmail.com\", one item per line. You can use comments starting with # to add descriptions for the agent. See <a href=\"javascript:openModal('settings/secrets/example-vars.html')\">example</a>.<br>These variables are visible to LLMs and in chat history, they are not being masked.", current_language),
        "type": "textarea",
        "value": settings["variables"].strip(),
        "style": "height: 20em",
    })

    secrets_fields.append({
        "id": "secrets",
        "title": translate_setting("Secrets Store", current_language),
        "description": translate_setting("Store secrets and credentials in .env format e.g. EMAIL_PASSWORD=\"s3cret-p4$$w0rd\", one item per line. You can use comments starting with # to add descriptions for the agent. See <a href=\"javascript:openModal('settings/secrets/example-secrets.html')\">example</a>.<br>These variables are not visile to LLMs and in chat history, they are being masked. ⚠️ only values with length >= 4 are being masked to prevent false positives. ", current_language),
        "type": "textarea",
        "value": secrets,
        "style": "height: 20em",
    })

    secrets_section: SettingsSection = {
        "id": "secrets",
        "title": translate_setting("Secrets Management", current_language),
        "description": translate_setting("Manage secrets and credentials that agents can use without exposing values to LLMs, chat history or logs. Placeholders are automatically replaced with values just before tool calls. If bare passwords occur in tool results, they are masked back to placeholders.", current_language),
        "fields": secrets_fields,
        "tab": "external",
    }

    mcp_server_fields: list[SettingsField] = []

    mcp_server_fields.append(
        {
            "id": "mcp_server_enabled",
            "title": translate_setting("Enable A0 MCP Server", current_language),
            "description": translate_setting("Expose Agent Zero as an SSE/HTTP MCP server. This will make this A0 instance available to MCP clients.", current_language),
            "type": "switch",
            "value": settings["mcp_server_enabled"],
        }
    )

    mcp_server_fields.append(
        {
            "id": "mcp_server_token",
            "title": translate_setting("MCP Server Token", current_language),
            "description": translate_setting("Token for MCP server authentication.", current_language),
            "type": "text",
            "hidden": True,
            "value": settings["mcp_server_token"],
        }
    )

    mcp_server_section: SettingsSection = {
        "id": "mcp_server",
        "title": translate_setting("A0 MCP Server", current_language),
        "description": translate_setting("Agent Zero can be exposed as an SSE MCP server. See <a href=\"javascript:openModal('settings/mcp/server/example.html')\">connection example</a>.", current_language),
        "fields": mcp_server_fields,
        "tab": "mcp",
    }

    # -------- A2A Section --------
    a2a_fields: list[SettingsField] = []

    a2a_fields.append(
        {
            "id": "a2a_server_enabled",
            "title": translate_setting("Enable A2A server", current_language),
            "description": translate_setting("Expose Agent Zero as A2A server. This allows other agents to connect to A0 via A2A protocol.", current_language),
            "type": "switch",
            "value": settings["a2a_server_enabled"],
        }
    )

    a2a_section: SettingsSection = {
        "id": "a2a_server",
        "title": translate_setting("A0 A2A Server", current_language),
        "description": translate_setting("Agent Zero can be exposed as an A2A server. See <a href=\"javascript:openModal('settings/a2a/a2a-connection.html')\">connection example</a>.", current_language),
        "fields": a2a_fields,
        "tab": "mcp",
    }


    # External API section
    external_api_fields: list[SettingsField] = []

    external_api_fields.append(
        {
            "id": "external_api_examples",
            "title": translate_setting("API Examples", current_language),
            "description": translate_setting("View examples for using Agent Zero's external API endpoints with API key authentication.", current_language),
            "type": "button",
            "value": translate_setting("Show API Examples", current_language),
        }
    )

    external_api_section: SettingsSection = {
        "id": "external_api",
        "title": translate_setting("External API", current_language),
        "description": translate_setting("Agent Zero provides external API endpoints for integration with other applications. These endpoints use API key authentication and support text messages and file attachments.", current_language),
        "fields": external_api_fields,
        "tab": "external",
    }

    # update checker section
    update_checker_fields: list[SettingsField] = []

    update_checker_fields.append(
        {
            "id": "update_check_enabled",
            "title": translate_setting("Enable Update Checker", current_language),
            "description": translate_setting("Enable update checker to notify about newer versions of Agent Zero.", current_language),
            "type": "switch",
            "value": settings["update_check_enabled"],
        }
    )

    update_checker_section: SettingsSection = {
        "id": "update_checker",
        "title": translate_setting("Update Checker", current_language),
        "description": translate_setting("Update checker periodically checks for new releases of Agent Zero and will notify when an update is recommended.<br>No personal data is sent to the update server, only randomized+anonymized unique ID and current version number, which help us evaluate the importance of the update in case of critical bug fixes etc.", current_language),
        "fields": update_checker_fields,
        "tab": "external",
    }

    # Backup & Restore section
    backup_fields: list[SettingsField] = []

    backup_fields.append(
        {
            "id": "backup_create",
            "title": translate_setting("Create Backup", current_language),
            "description": translate_setting("Create a backup archive of selected files and configurations using customizable patterns.", current_language),
            "type": "button",
            "value": translate_setting("Create Backup", current_language),
        }
    )

    backup_fields.append(
        {
            "id": "backup_restore",
            "title": translate_setting("Restore from Backup", current_language),
            "description": translate_setting("Restore files and configurations from a backup archive with pattern-based selection.", current_language),
            "type": "button",
            "value": translate_setting("Restore Backup", current_language),
        }
    )

    backup_section: SettingsSection = {
        "id": "backup_restore",
        "title": translate_setting("Backup & Restore", current_language),
        "description": translate_setting("Backup and restore Agent Zero data and configurations using glob pattern-based file selection.", current_language),
        "fields": backup_fields,
        "tab": "backup",
    }

    # Add the section to the result
    result: SettingsOutput = {
        "sections": [
            ui_section,
            agent_section,
            chat_model_section,
            util_model_section,
            browser_model_section,
            embed_model_section,
            memory_section,
            speech_section,
            api_keys_section,
            litellm_section,
            secrets_section,
            auth_section,
            mcp_client_section,
            mcp_server_section,
            a2a_section,
            external_api_section,
            update_checker_section,
            backup_section,
            dev_section,
            # code_exec_section,
        ]
    }
    return result


def _get_api_key_field(settings: Settings, provider: str, title: str) -> SettingsField:
    key = settings["api_keys"].get(provider, models.get_api_key(provider))
    # For API keys, use simple asterisk placeholder for existing keys
    return {
        "id": f"api_key_{provider}",
        "title": title,
        "type": "text",
        "value": (API_KEY_PLACEHOLDER if key and key != "None" else ""),
    }


def convert_in(settings: dict) -> Settings:
    current = get_settings()
    for section in settings["sections"]:
        if "fields" in section:
            for field in section["fields"]:
                # Skip saving if value is a placeholder
                should_skip = (
                    field["value"] == PASSWORD_PLACEHOLDER or
                    field["value"] == API_KEY_PLACEHOLDER
                )

                if not should_skip:
                    # Special handling for browser_http_headers
                    if field["id"] == "browser_http_headers" or field["id"].endswith("_kwargs"):
                        current[field["id"]] = _env_to_dict(field["value"])
                    elif field["id"].startswith("api_key_"):
                        current["api_keys"][field["id"]] = field["value"]
                    else:
                        current[field["id"]] = field["value"]
    return current

def get_settings() -> Settings:
    global _settings
    if not _settings:
        _settings = _read_settings_file()
    if not _settings:
        _settings = get_default_settings()
    norm = normalize_settings(_settings)
    return norm


def set_settings(settings: Settings, apply: bool = True):
    global _settings
    previous = _settings
    _settings = normalize_settings(settings)
    _write_settings_file(_settings)
    if apply:
        _apply_settings(previous)


def set_settings_delta(delta: dict, apply: bool = True):
    current = get_settings()
    new = {**current, **delta}
    set_settings(new, apply)  # type: ignore


def merge_settings(original: Settings, delta: dict) -> Settings:
    merged = original.copy()
    merged.update(delta)
    return merged


def normalize_settings(settings: Settings) -> Settings:
    copy = settings.copy()
    default = get_default_settings()

    # adjust settings values to match current version if needed
    if "version" not in copy or copy["version"] != default["version"]:
        _adjust_to_version(copy, default)
        copy["version"] = default["version"]  # sync version

    # remove keys that are not in default
    keys_to_remove = [key for key in copy if key not in default]
    for key in keys_to_remove:
        del copy[key]

    # add missing keys and normalize types
    for key, value in default.items():
        if key not in copy:
            copy[key] = value
        else:
            try:
                copy[key] = type(value)(copy[key])  # type: ignore
                if isinstance(copy[key], str):
                    copy[key] = copy[key].strip()  # strip strings
            except (ValueError, TypeError):
                copy[key] = value  # make default instead

    # mcp server token is set automatically
    copy["mcp_server_token"] = create_auth_token()

    return copy


def _adjust_to_version(settings: Settings, default: Settings):
    # starting with 0.9, the default prompt subfolder for agent no. 0 is agent0
    # switch to agent0 if the old default is used from v0.8
    if "version" not in settings or settings["version"].startswith("v0.8"):
        if "agent_profile" not in settings or settings["agent_profile"] == "default":
            settings["agent_profile"] = "agent0"


def _read_settings_file() -> Settings | None:
    if os.path.exists(SETTINGS_FILE):
        content = files.read_file(SETTINGS_FILE)
        parsed = json.loads(content)
        return normalize_settings(parsed)


def _write_settings_file(settings: Settings):
    settings = settings.copy()
    _write_sensitive_settings(settings)
    _remove_sensitive_settings(settings)

    # write settings
    content = json.dumps(settings, indent=4)
    files.write_file(SETTINGS_FILE, content)


def _remove_sensitive_settings(settings: Settings):
    settings["api_keys"] = {}
    settings["auth_login"] = ""
    settings["auth_password"] = ""
    settings["rfc_password"] = ""
    settings["root_password"] = ""
    settings["mcp_server_token"] = ""
    settings["secrets"] = ""


def _write_sensitive_settings(settings: Settings):
    for key, val in settings["api_keys"].items():
        dotenv.save_dotenv_value(key.upper(), val)

    dotenv.save_dotenv_value(dotenv.KEY_AUTH_LOGIN, settings["auth_login"])
    if settings["auth_password"]:
        dotenv.save_dotenv_value(dotenv.KEY_AUTH_PASSWORD, settings["auth_password"])
    if settings["rfc_password"]:
        dotenv.save_dotenv_value(dotenv.KEY_RFC_PASSWORD, settings["rfc_password"])

    if settings["root_password"]:
        dotenv.save_dotenv_value(dotenv.KEY_ROOT_PASSWORD, settings["root_password"])
    if settings["root_password"]:
        set_root_password(settings["root_password"])

    # Handle secrets separately - merge with existing preserving comments/order and support deletions
    secrets_manager = get_default_secrets_manager()
    submitted_content = settings["secrets"]
    secrets_manager.save_secrets_with_merge(submitted_content)



def get_default_settings() -> Settings:
    return Settings(
        version=_get_version(),
        chat_model_provider="openrouter",
        chat_model_name="openai/gpt-4.1",
        chat_model_api_base="",
        chat_model_kwargs={"temperature": "0"},
        chat_model_ctx_length=100000,
        chat_model_ctx_history=0.7,
        chat_model_vision=True,
        chat_model_rl_requests=0,
        chat_model_rl_input=0,
        chat_model_rl_output=0,
        util_model_provider="openrouter",
        util_model_name="openai/gpt-4.1-mini",
        util_model_api_base="",
        util_model_ctx_length=100000,
        util_model_ctx_input=0.7,
        util_model_kwargs={"temperature": "0"},
        util_model_rl_requests=0,
        util_model_rl_input=0,
        util_model_rl_output=0,
        embed_model_provider="huggingface",
        embed_model_name="sentence-transformers/all-MiniLM-L6-v2",
        embed_model_api_base="",
        embed_model_kwargs={},
        embed_model_rl_requests=0,
        embed_model_rl_input=0,
        browser_model_provider="openrouter",
        browser_model_name="openai/gpt-4.1",
        browser_model_api_base="",
        browser_model_vision=True,
        browser_model_rl_requests=0,
        browser_model_rl_input=0,
        browser_model_rl_output=0,
        browser_model_kwargs={"temperature": "0"},
        browser_http_headers={},
        memory_recall_enabled=True,
        memory_recall_delayed=False,
        memory_recall_interval=3,
        memory_recall_history_len=10000,
        memory_recall_memories_max_search=12,
        memory_recall_solutions_max_search=8,
        memory_recall_memories_max_result=5,
        memory_recall_solutions_max_result=3,
        memory_recall_similarity_threshold=0.7,
        memory_recall_query_prep=True,
        memory_recall_post_filter=True,
        memory_memorize_enabled=True,
        memory_memorize_consolidation=True,
        memory_memorize_replace_threshold=0.9,
        api_keys={},
        auth_login="",
        auth_password="",
        root_password="",
        agent_profile="agent0",
        agent_memory_subdir="default",
        agent_knowledge_subdir="custom",
        rfc_auto_docker=True,
        rfc_url="localhost",
        rfc_password="",
        rfc_port_http=55080,
        rfc_port_ssh=55022,
        shell_interface="local" if runtime.is_dockerized() else "ssh",
        stt_model_size="base",
        stt_language="en",
        stt_silence_threshold=0.3,
        stt_silence_duration=1000,
        stt_waiting_timeout=2000,
        tts_kokoro=True,
        ui_language="en-US",
        mcp_servers='{\n    "mcpServers": {}\n}',
        mcp_client_init_timeout=10,
        mcp_client_tool_timeout=120,
        mcp_server_enabled=False,
        mcp_server_token=create_auth_token(),
        a2a_server_enabled=False,
        variables="",
        secrets="",
        litellm_global_kwargs={},
        update_check_enabled=True,
    )


def _apply_settings(previous: Settings | None):
    global _settings
    if _settings:
        from agent import AgentContext
        from initialize import initialize_agent

        config = initialize_agent()
        for ctx in AgentContext._contexts.values():
            ctx.config = config  # reinitialize context config with new settings
            # apply config to agents
            agent = ctx.agent0
            while agent:
                agent.config = ctx.config
                agent = agent.get_data(agent.DATA_NAME_SUBORDINATE)

        # reload whisper model if necessary
        if not previous or _settings["stt_model_size"] != previous["stt_model_size"]:
            task = defer.DeferredTask().start_task(
                whisper.preload, _settings["stt_model_size"]
            )  # TODO overkill, replace with background task

        # force memory reload on embedding model change
        if not previous or (
            _settings["embed_model_name"] != previous["embed_model_name"]
            or _settings["embed_model_provider"] != previous["embed_model_provider"]
            or _settings["embed_model_kwargs"] != previous["embed_model_kwargs"]
        ):
            from python.helpers.memory import reload as memory_reload

            memory_reload()

        # update mcp settings if necessary
        if not previous or _settings["mcp_servers"] != previous["mcp_servers"]:
            from python.helpers.mcp_handler import MCPConfig

            async def update_mcp_settings(mcp_servers: str):
                PrintStyle(
                    background_color="black", font_color="white", padding=True
                ).print("Updating MCP config...")
                AgentContext.log_to_all(
                    type="info", content="Updating MCP settings...", temp=True
                )

                mcp_config = MCPConfig.get_instance()
                try:
                    MCPConfig.update(mcp_servers)
                except Exception as e:
                    AgentContext.log_to_all(
                        type="error",
                        content=f"Failed to update MCP settings: {e}",
                        temp=False,
                    )
                    (
                        PrintStyle(
                            background_color="red", font_color="black", padding=True
                        ).print("Failed to update MCP settings")
                    )
                    (
                        PrintStyle(
                            background_color="black", font_color="red", padding=True
                        ).print(f"{e}")
                    )

                PrintStyle(
                    background_color="#6734C3", font_color="white", padding=True
                ).print("Parsed MCP config:")
                (
                    PrintStyle(
                        background_color="#334455", font_color="white", padding=False
                    ).print(mcp_config.model_dump_json())
                )
                AgentContext.log_to_all(
                    type="info", content="Finished updating MCP settings.", temp=True
                )

            task2 = defer.DeferredTask().start_task(
                update_mcp_settings, config.mcp_servers
            )  # TODO overkill, replace with background task

        # update token in mcp server
        current_token = (
            create_auth_token()
        )  # TODO - ugly, token in settings is generated from dotenv and does not always correspond
        if not previous or current_token != previous["mcp_server_token"]:

            async def update_mcp_token(token: str):
                from python.helpers.mcp_server import DynamicMcpProxy

                DynamicMcpProxy.get_instance().reconfigure(token=token)

            task3 = defer.DeferredTask().start_task(
                update_mcp_token, current_token
            )  # TODO overkill, replace with background task

        # update token in a2a server
        if not previous or current_token != previous["mcp_server_token"]:

            async def update_a2a_token(token: str):
                from python.helpers.fasta2a_server import DynamicA2AProxy

                DynamicA2AProxy.get_instance().reconfigure(token=token)

            task4 = defer.DeferredTask().start_task(
                update_a2a_token, current_token
            )  # TODO overkill, replace with background task


def _env_to_dict(data: str):
    result = {}
    for line in data.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if '=' not in line:
            continue
            
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # If quoted, treat as string
        if value.startswith('"') and value.endswith('"'):
            result[key] = value[1:-1].replace('\\"', '"')  # Unescape quotes
        elif value.startswith("'") and value.endswith("'"):
            result[key] = value[1:-1].replace("\\'", "'")  # Unescape quotes
        else:
            # Not quoted, try JSON parse
            try:
                result[key] = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                result[key] = value
    
    return result


def _dict_to_env(data_dict):
    lines = []
    for key, value in data_dict.items():
        if isinstance(value, str):
            # Quote strings and escape internal quotes
            escaped_value = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped_value}"')
        elif isinstance(value, (dict, list, bool)) or value is None:
            # Serialize as unquoted JSON
            lines.append(f'{key}={json.dumps(value, separators=(",", ":"))}')
        else:
            # Numbers and other types as unquoted strings
            lines.append(f'{key}={value}')
    
    return "\n".join(lines)


def set_root_password(password: str):
    if not runtime.is_dockerized():
        raise Exception("root password can only be set in dockerized environments")
    _result = subprocess.run(
        ["chpasswd"],
        input=f"root:{password}".encode(),
        capture_output=True,
        check=True,
    )
    dotenv.save_dotenv_value(dotenv.KEY_ROOT_PASSWORD, password)


def get_runtime_config(set: Settings):
    if runtime.is_dockerized():
        return {
            "code_exec_ssh_enabled": set["shell_interface"] == "ssh",
            "code_exec_ssh_addr": "localhost",
            "code_exec_ssh_port": 22,
            "code_exec_ssh_user": "root",
        }
    else:
        host = set["rfc_url"]
        if "//" in host:
            host = host.split("//")[1]
        if ":" in host:
            host, port = host.split(":")
        if host.endswith("/"):
            host = host[:-1]
        return {
            "code_exec_ssh_enabled": set["shell_interface"] == "ssh",
            "code_exec_ssh_addr": host,
            "code_exec_ssh_port": set["rfc_port_ssh"],
            "code_exec_ssh_user": "root",
        }


def create_auth_token() -> str:
    runtime_id = runtime.get_persistent_id()
    username = dotenv.get_dotenv_value(dotenv.KEY_AUTH_LOGIN) or ""
    password = dotenv.get_dotenv_value(dotenv.KEY_AUTH_PASSWORD) or ""
    # use base64 encoding for a more compact token with alphanumeric chars
    hash_bytes = hashlib.sha256(f"{runtime_id}:{username}:{password}".encode()).digest()
    # encode as base64 and remove any non-alphanumeric chars (like +, /, =)
    b64_token = base64.urlsafe_b64encode(hash_bytes).decode().replace("=", "")
    return b64_token[:16]


def _get_version():
    return git.get_version()
