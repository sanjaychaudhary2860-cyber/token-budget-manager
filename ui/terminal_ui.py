from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich.align import Align
from rich import box
from datetime import datetime
from core.token_tracker import get_token_summary
from core.budget_manager import check_budget_status, get_savings_report
from database.db import get_usage_history

console = Console()

def get_time_theme():
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return {
            "name": "Morning",
            "emoji": "🌅",
            "greeting": "How can I help you\nthis morning?",
            "primary": "bright_blue",
            "secondary": "cyan",
            "border": "bright_blue",
            "dim": "blue",
            "input_arrow": "bright_blue",
        }
    elif 12 <= hour < 17:
        return {
            "name": "Afternoon",
            "emoji": "☀️",
            "greeting": "How can I help you\nthis afternoon?",
            "primary": "yellow",
            "secondary": "bright_yellow",
            "border": "yellow",
            "dim": "dark_orange",
            "input_arrow": "yellow",
        }
    elif 17 <= hour < 21:
        return {
            "name": "Evening",
            "emoji": "🌆",
            "greeting": "How can I help you\nthis evening?",
            "primary": "magenta",
            "secondary": "bright_magenta",
            "border": "magenta",
            "dim": "purple4",
            "input_arrow": "magenta",
        }
    else:
        return {
            "name": "Night",
            "emoji": "🌙",
            "greeting": "How can I help you\ntonight?",
            "primary": "bright_cyan",
            "secondary": "cyan",
            "border": "dark_cyan",
            "dim": "grey50",
            "input_arrow": "cyan",
        }

THEME = get_time_theme()

def _make_grid():
    grid = Table.grid(padding=(0, 3))
    grid.add_column(justify="right", style="dim white", width=20)
    grid.add_column(style="bold white")
    return grid

def show_welcome():
    console.clear()
    t = THEME
    import time

    for _ in range(5):
        console.print()

    # Animated star logo — line by line, timtimaye
    logo_lines = [
        "        ·          ",
        "      · ✦ ·        ",
        "    · ✦ ✦ ✦ ·      ",
        "  · ✦ ✦ ✦ ✦ ✦ ·    ",
        "    · ✦ ✦ ✦ ·      ",
        "      · ✦ ·        ",
        "        ·          ",
    ]

    # Pehli baar line by line aaye
    for line in logo_lines:
        console.print(Align.center(
            Text(line, style="bold magenta")
        ))
        time.sleep(0.04)

    console.print()

    # Dev Ai — title
    title = Text(justify="center")
    title.append("Dev ", style="bold white")
    title.append("Ai", style=f"bold magenta")
    console.print(Align.center(title))

    console.print()

    # Timtimane wala effect — 3 baar
    for blink in range(3):
        # Clear logo area aur redraw
        # Move cursor up
        print(f"\033[{len(logo_lines) + 3}A", end="")

        # Dim version
        for line in logo_lines:
            console.print(Align.center(
                Text(line, style="dim magenta")
            ))
        console.print()
        console.print(Align.center(
            Text.assemble(
                ("Dev ", "bold white"),
                ("Ai", "dim magenta")
            )
        ))
        console.print()
        time.sleep(0.15)

        # Move cursor up phir
        print(f"\033[{len(logo_lines) + 3}A", end="")

        # Bright version
        for line in logo_lines:
            console.print(Align.center(
                Text(line, style="bold magenta")
            ))
        console.print()
        console.print(Align.center(
            Text.assemble(
                ("Dev ", "bold white"),
                ("Ai", "bold magenta")
            )
        ))
        console.print()
        time.sleep(0.15)

    console.print()

    # Greeting — Claude jaisa bada
    lines = t["greeting"].split("\n")
    for i, line in enumerate(lines):
        console.print(Align.center(
            Text(line, style="bold white", justify="center")
        ))
        time.sleep(0.05)

    for _ in range(5):
        console.print()

    # Bahut zyada space — Claude jaisa feel
    for _ in range(6):
        console.print()

    # Anthropic jaisa star icon — text se banana
    star = Text(justify="center")
    star.append("  ✦  ", style=f"bold {t['primary']}")
    console.print(Align.center(star))
    console.print()

    # Badi greeting — bilkul Claude jaisi
    lines = t["greeting"].split("\n")
    for line in lines:
        greeting = Text(line, justify="center", style="bold white")
        greeting.stylize(f"bold {t['primary']}", 0, 3)
        console.print(Align.center(
            Text(line, style="bold white", justify="center")
        ))

    console.print()

    # Chhoti status line — barely visible
    status = Text(justify="center")
    status.append("⚡ Groq  ", style=f"dim {t['dim']}")
    status.append("·  ", style="dim white")
    status.append("🧠 Memory  ", style=f"dim {t['dim']}")
    status.append("·  ", style="dim white")
    status.append("🌐 Web", style=f"dim {t['dim']}")
    console.print(Align.center(status))

    # Space phir input
    for _ in range(6):
        console.print()

def show_help():
    t = THEME
    console.print()
    console.print(Rule(
        f"[bold {t['primary']}] ✦ Commands ✦ [/bold {t['primary']}]",
        style=f"dim {t['dim']}"
    ))
    console.print()

    table = Table(
        box=box.SIMPLE,
        show_header=False,
        padding=(0, 3),
        expand=True
    )
    table.add_column("CMD", style=f"bold {t['primary']}", width=12)
    table.add_column("DESC", style="white", width=22)
    table.add_column("CMD", style=f"bold {t['secondary']}", width=12)
    table.add_column("DESC", style="white", width=22)

    rows = [
        ("/stats",       "📊 Aaj ka usage",      "/memory",      "🧠 Meri yaadein"),
        ("/monthly",     "📅 Monthly report",     "/forget",      "🗑  Sab bhool jao"),
        ("/history",     "📜 7 din history",      "/clear",       "🔄 Chat clear"),
        ("/savings",     "💰 Token savings",      "/status",      "⚙  System info"),
        ("/chathistory", "💾 Chat history dekho", "/search",      "🔍 Search karo"),
        ("/clearchat",   "🗑  History delete",    "/voice",       "🎤 Voice mode"),
        ("/text",        "⌨️  Text mode",          "/help",        "❓ Commands"),
        ("/exit",        "👋 Band karo",           "",             ""),
    ]
    for r in rows:
        table.add_row(*r)

    console.print(table)
    console.print()

def show_stats():
    summary = get_token_summary()
    today = summary["today"]
    used = today["request_count"]
    percent = min(100, int((used / 1500) * 100))
    filled = percent // 5

    if percent < 50:
        bar_style = "bold green"
        status = "✅ Safe zone"
    elif percent < 80:
        bar_style = "bold yellow"
        status = "⚠  Watch out"
    else:
        bar_style = "bold red"
        status = "🔴 Almost full"

    bar = Text()
    bar.append("━" * filled, style=bar_style)
    bar.append("╌" * (20 - filled), style="dim")
    bar.append(f"  {percent}%", style=bar_style)

    grid = _make_grid()
    grid.add_row("Input",    Text(str(today["total_input"]),  style="cyan"))
    grid.add_row("Output",   Text(str(today["total_output"]), style="blue"))
    grid.add_row("Total",    Text(str(today["total_tokens"]), style=f"bold {THEME['primary']}"))
    grid.add_row("Requests", Text(str(used), style="white"))
    grid.add_row("Status",   Text(status))
    grid.add_row("Limit",    bar)

    console.print()
    console.print(Panel(
        grid,
        title=f"[bold {THEME['primary']}] 📊  Aaj Ka Usage [/bold {THEME['primary']}]",
        title_align="center",
        border_style=THEME["border"],
        box=box.ROUNDED,
        padding=(1, 4),
    ))
    console.print()

def show_monthly():
    monthly = get_token_summary()["monthly"]
    grid = _make_grid()
    grid.add_row("Input",    Text(str(monthly["total_input"]),   style="cyan"))
    grid.add_row("Output",   Text(str(monthly["total_output"]),  style="blue"))
    grid.add_row("Total",    Text(str(monthly["total_tokens"]),  style=f"bold {THEME['primary']}"))
    grid.add_row("Requests", Text(str(monthly["request_count"]), style="white"))

    console.print()
    console.print(Panel(
        grid,
        title=f"[bold {THEME['primary']}] 📅  Monthly Usage [/bold {THEME['primary']}]",
        title_align="center",
        border_style=THEME["border"],
        box=box.ROUNDED,
        padding=(1, 4),
    ))
    console.print()

def show_history():
    history = get_usage_history(7)
    if not history:
        console.print(Panel(
            Align.center(Text("📭 Koi history nahi abhi.", style="dim")),
            border_style="dim",
            box=box.ROUNDED,
            padding=(1, 2),
        ))
        return

    table = Table(
        box=box.SIMPLE_HEAD,
        header_style=f"bold {THEME['primary']}",
        padding=(0, 2),
        expand=True,
    )
    table.add_column("Date",     style="white")
    table.add_column("Tokens",   justify="right", style=f"{THEME['secondary']}")
    table.add_column("Requests", justify="right", style="white")
    table.add_column("Bar",      width=22)

    mx = max((r["total_tokens"] for r in history), default=1)
    for row in history:
        pct = int((row["total_tokens"] / mx) * 20)
        bar = Text()
        bar.append("━" * pct,        style=f"bold {THEME['primary']}")
        bar.append("╌" * (20 - pct), style="dim")
        table.add_row(
            row["date"],
            str(row["total_tokens"]),
            str(row["requests"]),
            bar
        )

    console.print()
    console.print(Panel(
        table,
        title=f"[bold {THEME['primary']}] 📜  Pichle 7 Din [/bold {THEME['primary']}]",
        title_align="center",
        border_style=THEME["border"],
        box=box.ROUNDED,
        padding=(1, 1),
    ))
    console.print()

def show_savings():
    report = get_savings_report()
    eff = report["efficiency_percent"]
    eff_style = "bold green" if eff >= 60 else "bold yellow" if eff >= 30 else "bold red"
    eff_icon  = "🔥" if eff >= 60 else "💡" if eff >= 30 else "📉"

    grid = _make_grid()
    grid.add_row("Used",       Text(str(report["tokens_used"]), style="white"))
    grid.add_row("Without AI", Text(str(report["estimated_without_optimization"]), style="dim red"))
    grid.add_row("Saved",      Text(str(report["tokens_saved"]), style="bold green"))
    grid.add_row("Efficiency", Text(f"{eff_icon}  {eff}%", style=eff_style))

    console.print()
    console.print(Panel(
        grid,
        title=f"[bold {THEME['primary']}] 💰  Savings Report [/bold {THEME['primary']}]",
        title_align="center",
        border_style=THEME["border"],
        box=box.ROUNDED,
        padding=(1, 4),
    ))
    console.print()

def show_response(result: dict):
    model    = result.get("model", "unknown")
    response = result.get("response", "")
    stats    = result.get("stats", {})
    alert    = result.get("alert")

    if "70b" in model:
        badge  = f"🧠  {model}"
        bcolor = "magenta"
    elif "error" in model:
        badge  = f"❌  {model}"
        bcolor = "red"
    else:
        badge  = f"⚡  {model}"
        bcolor = THEME["border"]

    console.print()
    console.print(Panel(
        Text(f"  {response}", style="white"),
        title=f"[bold {bcolor}]  {badge}  [/bold {bcolor}]",
        title_align="left",
        border_style=bcolor,
        box=box.ROUNDED,
        padding=(1, 3),
    ))

    info = Text()
    info.append(f"   📥 {stats.get('input_tokens', 0)}", style="dim")
    info.append(" in  ",                                  style="dim white")
    info.append(f"📤 {stats.get('output_tokens', 0)}",    style="dim")
    info.append(" out  ",                                 style="dim white")
    info.append(
        f"⚡ {stats.get('total_tokens', 0)} tokens",
        style=f"bold {THEME['primary']}"
    )
    console.print(info)

    if alert:
        console.print()
        console.print(Panel(
            Text(f"  {alert}", style="bold red"),
            border_style="red",
            box=box.ROUNDED,
            padding=(0, 2),
        ))
    console.print()

def show_status():
    status    = check_budget_status()
    today_req = status["today_requests"]
    pct       = min(100, int((today_req / 1500) * 100))
    filled    = pct // 5

    bar = Text()
    bar.append("━" * filled,        style="bold green")
    bar.append("╌" * (20 - filled), style="dim")
    bar.append(f"  {pct}%",          style="green")

    grid = _make_grid()
    grid.add_row("System",      Text("✅ Running", style="bold green"))
    grid.add_row("Theme",       Text(f"{THEME['emoji']} {THEME['name']} Mode", style=f"bold {THEME['primary']}"))
    grid.add_row("AI Engine",   Text("⚡ Groq",    style=f"bold {THEME['secondary']}"))
    grid.add_row("Web Search",  Text("✅ Active",  style="green"))
    grid.add_row("Memory",      Text("✅ Active",  style="green"))
    grid.add_row("Calculator",  Text("✅ Active",  style="green"))
    grid.add_row("Multi Model", Text("✅ Active",  style="green"))
    grid.add_row("Upgrader",    Text("✅ Active",  style="green"))
    grid.add_row("",            Text(""))
    grid.add_row("Aaj Req",     Text(str(today_req),                   style="cyan"))
    grid.add_row("Monthly Req", Text(str(status["monthly_requests"]),  style="cyan"))
    grid.add_row("Aaj Tokens",  Text(str(status["today_tokens_used"]), style=f"{THEME['primary']}"))
    grid.add_row("Daily",       bar)

    console.print()
    console.print(Panel(
        grid,
        title=f"[bold {THEME['primary']}] ⚙  System Status [/bold {THEME['primary']}]",
        title_align="center",
        border_style=THEME["border"],
        box=box.ROUNDED,
        padding=(1, 4),
    ))
    console.print()

def get_user_input() -> str:
    now = datetime.now().strftime("%H:%M")
    console.print(Rule(style=f"dim {THEME['dim']}"))
    return console.input(
        f"[dim]{now}[/dim]  "
        f"[bold {THEME['input_arrow']}]You ▶[/bold {THEME['input_arrow']}]  "
    ).strip()
