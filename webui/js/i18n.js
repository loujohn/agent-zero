// 国际化系统 - Agent Zero
// 遵循 Linus 原则：简单、实用、零破坏性

class I18n {
  constructor() {
    this.currentLang = this.getStoredLanguage() || "en-US";
    this.translations = {};
    this.fallbackLang = "en-US";

    // 初始化翻译数据
    this.initTranslations();

    // 从后端加载语言设置
    this.loadLanguageFromBackend();
  }

  // 获取存储的语言设置
  getStoredLanguage() {
    return localStorage.getItem("agent-zero-language");
  }

  // 设置语言
  setLanguage(lang) {
    this.currentLang = lang;
    localStorage.setItem("agent-zero-language", lang);

    // 触发语言变更事件
    window.dispatchEvent(
      new CustomEvent("language-changed", {
        detail: { language: lang },
      })
    );

    // 更新页面文本
    this.updatePageTexts();

    // 同步到后端设置
    this.syncLanguageToBackend(lang);
  }

  // 同步语言设置到后端
  async syncLanguageToBackend(lang) {
    try {
      const response = await fetch("/api/settings_set", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ui_language: lang,
        }),
      });

      if (!response.ok) {
        console.warn("Failed to sync language setting to backend");
      }
    } catch (error) {
      console.warn("Error syncing language to backend:", error);
    }
  }

  // 翻译函数 - 核心功能
  t(key, fallback = null, params = {}) {
    // 获取当前语言的翻译
    let translation = this.translations[this.currentLang]?.[key];

    // 如果没有找到，尝试使用备用语言
    if (!translation && this.currentLang !== this.fallbackLang) {
      translation = this.translations[this.fallbackLang]?.[key];
    }

    // 如果还是没有找到，使用fallback或key本身
    if (!translation) {
      translation = fallback || key;
    }

    // 处理参数替换
    if (params && typeof translation === "string") {
      Object.keys(params).forEach((param) => {
        translation = translation.replace(`{${param}}`, params[param]);
      });
    }

    return translation;
  }

  // 初始化翻译数据
  initTranslations() {
    // 英文翻译（默认/备用）
    this.translations["en-US"] = {
      // 通用
      "common.save": "Save",
      "common.cancel": "Cancel",
      "common.close": "Close",
      "common.delete": "Delete",
      "common.edit": "Edit",
      "common.create": "Create",
      "common.browse": "Browse",
      "common.loading": "Loading...",
      "common.error": "Error",
      "common.success": "Success",
      "common.warning": "Warning",
      "common.info": "Info",
      "common.yes": "Yes",
      "common.no": "No",
      "common.ok": "OK",
      "common.copy": "Copy",

      // 设置
      "settings.title": "Settings",
      "settings.language": "Language",
      "settings.language.description": "Choose your preferred language",
      "settings.title": "Settings",
      "settings.agent": "Agent Settings",
      "settings.external": "External Services",
      "settings.mcp": "MCP/A2A",
      "settings.developer": "Developer",
      "settings.scheduler": "Task Scheduler",
      "settings.backup": "Backup & Restore",

      // 仪表板
      "dashboard.title": "Dashboard",
      "settings.configure_description": "Configure Agent Zero",

      // 聊天界面
      "chat.input.placeholder": "Type your message here...",
      "chat.attachment.tooltip": "Add attachments to the message",
      "chat.send": "Send",
      "chat.new": "New Chat",
      "chat.new_description": "Start a new conversation",
      "chat.history": "Chat History",
      "chat.clear": "Clear Chat",
      "chat.reset": "Reset Chat",
      "chat.load": "Load Chat",
      "chat.save": "Save Chat",
      "chat.restart": "Restart",

      // 任务调度器
      "scheduler.title": "Task Scheduler",
      "scheduler.new_task": "New Task",
      "scheduler.task_name": "Task Name",
      "scheduler.task_type": "Type",
      "scheduler.schedule": "Schedule",
      "scheduler.state": "State",
      "scheduler.project": "Project",
      "scheduler.last_run": "Last Run",
      "scheduler.actions": "Actions",
      "scheduler.create_new_task": "Create New Task",
      "scheduler.edit_task": "Edit Task",
      "scheduler.task_management": "Task Management",

      // 登录
      "login.title": "Agent Zero",
      "login.username": "Username",
      "login.password": "Password",
      "login.button": "Login",

      // 侧边栏
      "sidebar.chats": "Chats",
      "sidebar.tasks": "Tasks",
      "sidebar.new_chat": "New Chat",
      "sidebar.settings": "Settings",
      "sidebar.projects": "Projects",
      "sidebar.no_chats": "No chats to list.",
      "sidebar.no_tasks": "No tasks to list.",

      // 消息类型
      "message.user": "User",
      "message.agent": "Agent",
      "message.response": "Response",
      "message.tool": "Tool",
      "message.code_exe": "Code Execution",
      "message.browser": "Browser",
      "message.warning": "Warning",
      "message.error": "Error",
      "message.info": "Info",
      "message.util": "Utility",
      "message.hint": "Hint",

      // 状态和操作
      "status.connected": "Connected",
      "status.disconnected": "Disconnected",
      "status.loading": "Loading",
      "status.idle": "Idle",
      "status.running": "Running",
      "status.disabled": "Disabled",
      "status.error": "Error",
      "status.completed": "Completed",

      // 操作按钮
      "action.run": "Run",
      "action.stop": "Stop",
      "action.pause": "Pause",
      "action.resume": "Resume",
      "action.reset": "Reset",
      "action.clear": "Clear",
      "action.refresh": "Refresh",
      "action.upload": "Upload",
      "action.download": "Download",
      "action.export": "Export",
      "action.import": "Import",
      "action.view_details": "View task details",
      "action.clear_chat": "Clear task chat",
      "action.delete_task": "Delete task",

      // 文件和附件
      "file.upload": "Upload File",
      "file.download": "Download File",
      "file.delete": "Delete File",
      "file.rename": "Rename File",
      "file.size": "File Size",
      "file.type": "File Type",
      "file.modified": "Last Modified",
      "attachment.add": "Add Attachment",
      "attachment.remove": "Remove Attachment",
      "attachment.preview": "Preview Attachment",

      // 时间和日期
      "time.now": "Now",
      "time.today": "Today",
      "time.yesterday": "Yesterday",
      "time.last_week": "Last Week",
      "time.last_month": "Last Month",
      "time.never": "Never",

      // 通知和提示
      "notification.new_message": "New Message",
      "notification.task_completed": "Task Completed",
      "notification.error_occurred": "Error Occurred",
      "tooltip.expand": "Expand",
      "tooltip.collapse": "Collapse",
      "tooltip.minimize": "Minimize",
      "tooltip.maximize": "Maximize",

      // 搜索和过滤
      "search.placeholder": "Search...",
      "search.no_results": "No results found",
      "filter.all": "All",
      "filter.active": "Active",
      "filter.inactive": "Inactive",
      "filter.recent": "Recent",

      // 偏好设置
      "preferences.title": "Preferences",
      "preferences.autoscroll": "Autoscroll",
      "preferences.dark_mode": "Dark mode",
      "preferences.speech": "Speech",
      "preferences.show_thoughts": "Show thoughts",
      "preferences.show_json": "Show JSON",
      "preferences.show_utils": "Show utility messages",

      // 历史和上下文
      "history.loading": "Loading history…",
      "context.loading": "Loading context window…",

      // 模态框
      "modal.done_ctrl_enter": "Done (Ctrl+Enter)",
      "modal.file_browser": "File Browser",
      "modal.loading_files": "Loading files...",
      "modal.navigate_up": "Navigate Up",
      "modal.up": "Up",
      "modal.name": "Name",
      "modal.size": "Size",
      "modal.modified": "Modified",
      "modal.no_files": "No files found",
      "modal.upload_files": "Upload Files",
      "modal.image_viewer": "Image Viewer",
      "modal.loading_image": "Loading image...",
      "modal.failed_load_image": "Failed to load image",
      "modal.zoom_out": "Zoom Out",
      "modal.reset": "Reset",
      "modal.zoom_in": "Zoom In",

      // 项目管理
      "project.no_project": "No project",
      "project.projects": "Projects",
      "project.edit": "Edit",
      "project.deactivate": "Deactivate",
      "project.activate": "Activate",
      "project.create": "Create project",
      "project.create_new": "Create a new project",
      "project.create_continue": "Create and continue",
      "project.delete": "Delete",
      "project.intro":
        "Projects in Agent Zero are used to separate different use cases with custom instructions and files. You can create projects for your tasks and switch between them easily.",
      "project.active": "Active:",
      "project.no_projects": "There are no projects yet",
      "project.basic_data": "Project basic data",
      "project.folder_name": "Folder name",
      "project.files_location": "Project files and settings are located in",
      "project.title": "Title",
      "project.title_description":
        "Title and description are visible to both you and the agent and can help it understand the project.",
      "project.optional_title": "Optional title",
      "project.color": "Color",
      "project.non_sensitive_vars": "Non-sensitive variables",
      "project.non_sensitive_vars_desc": "Store non-sensitive variables in .env format e.g. EMAIL_IMAP_SERVER=\"imap.gmail.com\", one item per line. You can use comments starting with # to add descriptions for the agent. See example. These variables are visible to LLMs and in chat history, they are not being masked.",
      "project.sensitive_vars": "Sensitive variables", 
      "project.sensitive_vars_desc": "Store secrets and credentials in .env format e.g. EMAIL_PASSWORD=\"s3cret-p4$$w0rd\", one item per line. You can use comments starting with # to add descriptions for the agent. See example. These variables are not visible to LLMs and in chat history, they are being masked. ⚠️ only values with length >= 4 are being masked to prevent false positives.",
      "project.enter_variables": "Enter project variables",
      "project.enter_secrets": "Enter project secrets",

      // 备份和恢复
      "backup.create_title": "Create Backup",
      "backup.restore_title": "Restore Backup",
      "backup.config_json": "Backup Configuration JSON",
      "backup.restore_config_json": "Restore Configuration JSON",
      "backup.format": "Format",
      "backup.reset": "Reset",
      "backup.dry_run": "Dry Run",
      "backup.create": "Create Backup",
      "backup.restore_files": "Restore Files",
      "backup.file_operations": "File Operations",
      "backup.operations_placeholder":
        "File operations will be displayed here...",
      "backup.processing": "Processing...",
      "backup.select_file": "Select Backup File (.zip)",
      "backup.restart_warning":
        "After restoring a backup you will have to restart Agent-Zero to fully load the backed-up configuration (button in the left pane).",
      "backup.conflict_policy": "File Conflict Policy:",
      "backup.overwrite": "Overwrite existing files",
      "backup.skip": "Skip existing files",
      "backup.backup_existing": "Backup existing files (.backup.timestamp)",
      "backup.clean_before":
        "Clean before restore (delete existing files matching original backup patterns)",
      "backup.clean_description":
        "When enabled, all existing files matching the original backup patterns will be deleted before restoring files from the archive. This ensures a completely clean restore state.",
      "backup.restore_complete": "Restore Complete",
      "backup.deleted": "Deleted:",
      "backup.restored": "Restored:",
      "backup.skipped": "Skipped:",
      "backup.errors": "Errors:",

      // 通知
      "notification.toast_stack": "Notification Toast Stack",
      "notification.dismiss": "Dismiss",
      "notification.notifications": "Notifications",
      "notification.clear_all": "Clear All",
      "notification.expand_details": "Expand Details",
      "notification.collapse_details": "Collapse Details",
      "notification.show_details": "▶ Show Details",
      "notification.hide_details": "▼ Hide Details",
      "notification.no_notifications": "No notifications to display",

      // 操作按钮
      "action.pause_agent": "Pause Agent",
      "action.resume_agent": "Resume Agent",
      "action.import_knowledge": "Import knowledge",
      "action.files": "Files",
      "action.history": "History",
      "action.context": "Context",
      "action.nudge": "Nudge",
      "action.copy_text": "Copy text",

      // 项目和内存
      "projects.manage_description": "Manage your projects",
      "memory.title": "Memory",
      "memory.dashboard_description": "Open Memory Dashboard",

      // 错误消息
      // 调度器
      "scheduler.task_required": "Task name and prompt are required",
      "scheduler.confirm_delete":
        "Are you sure you want to delete this task? This action cannot be undone.",
      "scheduler.select_valid_date": "Please select a valid date and time",

      "error.connection": "Connection Error",
      "error.network": "Network Error",
      "error.unknown": "Unknown Error",
      "error.file_not_found": "File Not Found",
      "error.permission_denied": "Permission Denied",
      "error.invalid_input": "Invalid Input",
      "error.server_error": "Server Error",
      "error.csrf_token": "Failed to get CSRF token",
    };

    // 中文翻译
    this.translations["zh-CN"] = {
      // 通用
      "common.save": "保存",
      "common.cancel": "取消",
      "common.close": "关闭",
      "common.delete": "删除",
      "common.edit": "编辑",
      "common.create": "创建",
      "common.browse": "浏览",
      "common.loading": "加载中...",
      "common.error": "错误",
      "common.success": "成功",
      "common.warning": "警告",
      "common.info": "信息",
      "common.yes": "是",
      "common.no": "否",
      "common.ok": "确定",
      "common.copy": "复制",

      // 设置
      "settings.title": "设置",
      "settings.language": "语言",
      "settings.language.description": "选择您的首选语言",
      "settings.agent": "智能体设置",
      "settings.external": "外部服务",
      "settings.mcp": "MCP/A2A",
      "settings.developer": "开发者",
      "settings.scheduler": "任务调度器",
      "settings.backup": "备份与恢复",
      "settings.configure_description": "配置 Agent Zero",

      // 仪表板
      "dashboard.title": "仪表板",

      // 聊天界面
      "chat.input.placeholder": "在此输入您的消息...",
      "chat.attachment.tooltip": "为消息添加附件",
      "chat.send": "发送",
      "chat.new": "新建聊天",
      "chat.new_description": "开始新的对话",
      "chat.history": "聊天历史",
      "chat.clear": "清空聊天",
      "chat.reset": "重置聊天",
      "chat.load": "加载聊天",
      "chat.save": "保存聊天",
      "chat.restart": "重启",

      // 任务调度器
      "scheduler.title": "任务调度器",
      "scheduler.new_task": "新建任务",
      "scheduler.task_name": "任务名称",
      "scheduler.task_type": "类型",
      "scheduler.schedule": "调度",
      "scheduler.state": "状态",
      "scheduler.project": "项目",
      "scheduler.last_run": "最后运行",
      "scheduler.actions": "操作",
      "scheduler.create_new_task": "创建新任务",
      "scheduler.edit_task": "编辑任务",
      "scheduler.task_management": "任务管理",

      // 登录
      "login.title": "Agent Zero",
      "login.username": "用户名",
      "login.password": "密码",
      "login.button": "登录",

      // 侧边栏
      "sidebar.chats": "聊天",
      "sidebar.tasks": "任务",
      "sidebar.new_chat": "新建聊天",
      "sidebar.settings": "设置",
      "sidebar.projects": "项目",
      "sidebar.no_chats": "没有聊天记录。",
      "sidebar.no_tasks": "没有任务。",

      // 消息类型
      "message.user": "用户",
      "message.agent": "智能体",
      "message.response": "响应",
      "message.tool": "工具",
      "message.code_exe": "代码执行",
      "message.browser": "浏览器",
      "message.warning": "警告",
      "message.error": "错误",
      "message.info": "信息",
      "message.util": "实用工具",
      "message.hint": "提示",

      // 状态和操作
      "status.connected": "已连接",
      "status.disconnected": "已断开",
      "status.loading": "加载中",
      "status.idle": "空闲",
      "status.running": "运行中",
      "status.disabled": "已禁用",
      "status.error": "错误",
      "status.completed": "已完成",

      // 操作按钮
      "action.run": "运行",
      "action.stop": "停止",
      "action.pause": "暂停",
      "action.resume": "继续",
      "action.reset": "重置",
      "action.clear": "清空",
      "action.refresh": "刷新",
      "action.upload": "上传",
      "action.download": "下载",
      "action.export": "导出",
      "action.import": "导入",
      "action.view_details": "查看任务详情",
      "action.clear_chat": "清空任务聊天",
      "action.delete_task": "删除任务",

      // 文件和附件
      "file.upload": "上传文件",
      "file.download": "下载文件",
      "file.delete": "删除文件",
      "file.rename": "重命名文件",
      "file.size": "文件大小",
      "file.type": "文件类型",
      "file.modified": "最后修改",
      "attachment.add": "添加附件",
      "attachment.remove": "移除附件",
      "attachment.preview": "预览附件",

      // 时间和日期
      "time.now": "现在",
      "time.today": "今天",
      "time.yesterday": "昨天",
      "time.last_week": "上周",
      "time.last_month": "上个月",
      "time.never": "从未",

      // 通知和提示
      "notification.new_message": "新消息",
      "notification.task_completed": "任务已完成",
      "notification.error_occurred": "发生错误",
      "tooltip.expand": "展开",
      "tooltip.collapse": "折叠",
      "tooltip.minimize": "最小化",
      "tooltip.maximize": "最大化",

      // 搜索和过滤
      "search.placeholder": "搜索...",
      "search.no_results": "未找到结果",
      "filter.all": "全部",
      "filter.active": "活跃",
      "filter.inactive": "非活跃",
      "filter.recent": "最近",

      // 偏好设置
      "preferences.title": "偏好设置",
      "preferences.autoscroll": "自动滚动",
      "preferences.dark_mode": "深色模式",
      "preferences.speech": "语音",
      "preferences.show_thoughts": "显示思考过程",
      "preferences.show_json": "显示JSON",
      "preferences.show_utils": "显示实用消息",

      // 历史和上下文
      "history.loading": "正在加载历史记录…",
      "context.loading": "正在加载上下文窗口…",

      // 模态框
      "modal.done_ctrl_enter": "完成 (Ctrl+Enter)",
      "modal.file_browser": "文件浏览器",
      "modal.loading_files": "正在加载文件...",
      "modal.navigate_up": "向上导航",
      "modal.up": "向上",
      "modal.name": "名称",
      "modal.size": "大小",
      "modal.modified": "修改时间",
      "modal.no_files": "未找到文件",
      "modal.upload_files": "上传文件",
      "modal.image_viewer": "图像查看器",
      "modal.loading_image": "正在加载图像...",
      "modal.failed_load_image": "加载图像失败",
      "modal.zoom_out": "缩小",
      "modal.reset": "重置",
      "modal.zoom_in": "放大",

      // 项目管理
      "project.no_project": "无项目",
      "project.projects": "项目",
      "project.edit": "编辑",
      "project.deactivate": "停用",
      "project.activate": "激活",
      "project.create": "创建项目",
      "project.create_new": "创建新项目",
      "project.create_continue": "创建并继续",
      "project.delete": "删除",
      "project.intro":
        "Agent Zero 中的项目用于分离不同的用例，具有自定义指令和文件。您可以为任务创建项目并轻松切换。",
      "project.active": "活跃：",
      "project.no_projects": "还没有项目",
      "project.basic_data": "项目基本数据",
      "project.folder_name": "文件夹名称",
      "project.files_location": "项目文件和设置位于",
      "project.title": "标题",
      "project.title_description":
        "标题和描述对您和代理都可见，可以帮助它理解项目。",
      "project.optional_title": "可选标题",
      "project.color": "颜色",
      "project.non_sensitive_vars": "非敏感变量",
      "project.non_sensitive_vars_desc": "以 .env 格式存储非敏感变量，例如 EMAIL_IMAP_SERVER=\"imap.gmail.com\"，每行一个项目。您可以使用以 # 开头的注释为代理添加描述。查看示例。这些变量对 LLM 和聊天历史可见，不会被遮罩。",
      "project.sensitive_vars": "敏感变量",
      "project.sensitive_vars_desc": "以 .env 格式存储密钥和凭据，例如 EMAIL_PASSWORD=\"s3cret-p4$$w0rd\"，每行一个项目。您可以使用以 # 开头的注释为代理添加描述。查看示例。这些变量对 LLM 和聊天历史不可见，会被遮罩。⚠️ 只有长度 >= 4 的值才会被遮罩以防止误报。",
      "project.enter_variables": "输入项目变量",
      "project.enter_secrets": "输入项目密钥",

      // 备份和恢复
      "backup.create_title": "创建备份",
      "backup.restore_title": "恢复备份",
      "backup.config_json": "备份配置 JSON",
      "backup.restore_config_json": "恢复配置 JSON",
      "backup.format": "格式化",
      "backup.reset": "重置",
      "backup.dry_run": "试运行",
      "backup.create": "创建备份",
      "backup.restore_files": "恢复文件",
      "backup.file_operations": "文件操作",
      "backup.operations_placeholder": "文件操作将在此处显示...",
      "backup.processing": "处理中...",
      "backup.select_file": "选择备份文件 (.zip)",
      "backup.restart_warning":
        "恢复备份后，您需要重启 Agent-Zero 以完全加载备份的配置（左侧面板中的按钮）。",
      "backup.conflict_policy": "文件冲突策略：",
      "backup.overwrite": "覆盖现有文件",
      "backup.skip": "跳过现有文件",
      "backup.backup_existing": "备份现有文件 (.backup.timestamp)",
      "backup.clean_before": "恢复前清理（删除与原始备份模式匹配的现有文件）",
      "backup.clean_description":
        "启用后，所有与原始备份模式匹配的现有文件将在从存档恢复文件之前被删除。这确保了完全干净的恢复状态。",
      "backup.restore_complete": "恢复完成",
      "backup.deleted": "已删除：",
      "backup.restored": "已恢复：",
      "backup.skipped": "已跳过：",
      "backup.errors": "错误：",

      // 通知
      "notification.toast_stack": "通知提示栈",
      "notification.dismiss": "关闭",
      "notification.notifications": "通知",
      "notification.clear_all": "清除全部",
      "notification.expand_details": "展开详情",
      "notification.collapse_details": "收起详情",
      "notification.show_details": "▶ 显示详情",
      "notification.hide_details": "▼ 隐藏详情",
      "notification.no_notifications": "没有通知显示",

      // 操作按钮
      "action.pause_agent": "暂停代理",
      "action.resume_agent": "恢复代理",
      "action.import_knowledge": "导入知识",
      "action.files": "文件",
      "action.history": "历史",
      "action.context": "上下文",
      "action.nudge": "提示",
      "action.copy_text": "复制文本",

      // 项目和内存
      "projects.manage_description": "管理您的项目",
      "memory.title": "内存",
      "memory.dashboard_description": "打开内存仪表板",

      // 调度器
      "scheduler.task_required": "任务名称和提示是必需的",
      "scheduler.confirm_delete": "您确定要删除此任务吗？此操作无法撤销。",
      "scheduler.select_valid_date": "请选择有效的日期和时间",

      // 错误消息
      "error.connection": "连接错误",
      "error.network": "网络错误",
      "error.unknown": "未知错误",
      "error.file_not_found": "文件未找到",
      "error.permission_denied": "权限被拒绝",
      "error.invalid_input": "输入无效",
      "error.server_error": "服务器错误",
      "error.csrf_token": "获取 CSRF 令牌失败",
    };
  }

  // 更新页面中的文本
  updatePageTexts() {
    console.log("Updating page texts to language:", this.currentLang); // Debug log

    // 更新所有带有 data-i18n 属性的元素
    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const key = element.getAttribute("data-i18n");
      const fallback =
        element.getAttribute("data-i18n-fallback") || element.textContent;
      const newText = this.t(key, fallback);
      element.textContent = newText;
      console.log(`Updated element with key "${key}" to: "${newText}"`); // Debug log
    });

    // 更新所有带有 data-i18n-placeholder 属性的输入框
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
      const key = element.getAttribute("data-i18n-placeholder");
      const fallback = element.getAttribute("placeholder");
      const newPlaceholder = this.t(key, fallback);
      element.setAttribute("placeholder", newPlaceholder);
      console.log(
        `Updated placeholder with key "${key}" to: "${newPlaceholder}"`
      ); // Debug log
    });

    // 更新所有带有 data-i18n-title 属性的元素
    document.querySelectorAll("[data-i18n-title]").forEach((element) => {
      const key = element.getAttribute("data-i18n-title");
      const fallback = element.getAttribute("title");
      const newTitle = this.t(key, fallback);
      element.setAttribute("title", newTitle);
      console.log(`Updated title with key "${key}" to: "${newTitle}"`); // Debug log
    });

    console.log("Page text update completed"); // Debug log
  }

  // 获取可用语言列表
  getAvailableLanguages() {
    return [
      { code: "en-US", name: "English", nativeName: "English" },
      { code: "zh-CN", name: "Chinese (Simplified)", nativeName: "简体中文" },
    ];
  }

  // 获取当前语言
  getCurrentLanguage() {
    return this.currentLang;
  }

  // 从后端加载语言设置
  async loadLanguageFromBackend() {
    try {
      const response = await fetch("/api/settings_get");
      if (response.ok) {
        const data = await response.json();
        console.log("Settings data from backend:", data); // Debug log

        // Try to find ui_language in the settings structure
        let backendLang = null;

        if (data.settings && data.settings.sections) {
          for (const section of data.settings.sections) {
            if (section.fields) {
              const langField = section.fields.find(
                (field) => field.id === "ui_language"
              );
              if (langField) {
                backendLang = langField.value;
                break;
              }
            }
          }
        }

        console.log("Backend language setting:", backendLang); // Debug log

        if (backendLang && backendLang !== this.currentLang) {
          console.log("Updating language from backend:", backendLang); // Debug log
          this.currentLang = backendLang;
          localStorage.setItem("agent-zero-language", backendLang);
          this.updatePageTexts();
        }
      }
    } catch (error) {
      console.warn("Failed to load language from backend:", error);
    }
  }
}

// 创建全局实例
const i18n = new I18n();

// 导出全局函数
window.t = (key, fallback, params) => i18n.t(key, fallback, params);
window.i18n = i18n;

// 页面加载完成后初始化
document.addEventListener("DOMContentLoaded", () => {
  i18n.updatePageTexts();

  // 监听设置页面的语言选择器变化
  setTimeout(() => {
    const languageSelects = document.querySelectorAll(
      'select[x-model*="ui_language"], select[id*="ui_language"]'
    );
    languageSelects.forEach((select) => {
      select.addEventListener("change", (event) => {
        const newLang = event.target.value;
        if (newLang && newLang !== i18n.getCurrentLanguage()) {
          console.log("Language select changed to:", newLang);
          i18n.setLanguage(newLang);
        }
      });
    });
  }, 1000); // Wait for Alpine.js to render
});

export default i18n;
