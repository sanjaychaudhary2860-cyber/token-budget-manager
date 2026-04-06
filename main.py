import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.panel  import Panel
from rich.rule   import Rule
from rich.table  import Table
from rich        import box
from database.db import initialize_db
from core.assistant import Assistant
from core.memory import show_memory, forget_memory
from core.chat_history import (
    get_recent_history,
    show_history_summary,
    search_history,
    get_all_dates,
    get_history_by_date,
    clear_history as clear_chat_history
)
from core.voice_input import listen_once
from ui.terminal_ui import (
    console, show_welcome, show_help, show_stats,
    show_monthly, show_history, show_savings,
    show_response, show_status, get_user_input
)

def show_full_history():
    dates = get_all_dates()
    if not dates:
        console.print(
            "\n[bold yellow]📭 Koi history nahi abhi.[/bold yellow]\n"
        )
        return

    console.print()
    console.print(Rule(
        "[bold cyan] 💾 Chat History [/bold cyan]",
        style="dim cyan"
    ))
    console.print(f"\n[bold cyan]{show_history_summary()}[/bold cyan]\n")

    # Dates dikhao
    console.print("[bold white]📅 Available Dates:[/bold white]")
    for i, date in enumerate(dates):
        msgs = get_history_by_date(date)
        user_msgs = [m for m in msgs if m["role"] == "user"]
        console.print(
            f"  [bold cyan]{i+1}.[/bold cyan] "
            f"[white]{date}[/white] "
            f"[dim]({len(user_msgs)} conversations)[/dim]"
        )

    console.print()
    choice = console.input(
        "[bold cyan]Kaun sa date dekhna hai (number) ya Enter skip: [/bold cyan]"
    ).strip()

    if not choice:
        # Recent 15 messages dikhao
        _show_recent_messages(15)
        return

    try:
        idx  = int(choice) - 1
        date = dates[idx]
        _show_date_history(date)
    except (ValueError, IndexError):
        console.print("[yellow]Galat number — recent history dikh rahi hai[/yellow]")
        _show_recent_messages(15)

def _show_date_history(date: str):
    msgs = get_history_by_date(date)
    if not msgs:
        console.print(f"[yellow]{date} ki koi history nahi[/yellow]")
        return

    console.print()
    console.print(Rule(
        f"[bold cyan] {date} [/bold cyan]",
        style="dim cyan"
    ))
    console.print()

    for h in msgs:
        is_user    = h["role"] == "user"
        role_style = "bold cyan"   if is_user else "bold green"
        role_icon  = "👤 You"      if is_user else "🤖 AI"
        time_str   = h.get("timestamp", "")[-8:-3]  # HH:MM

        msg = h["message"]
        if len(msg) > 120:
            msg = msg[:120] + "..."

        console.print(
            f"[dim]{time_str}[/dim]  "
            f"[{role_style}]{role_icon}[/{role_style}]  "
            f"[white]{msg}[/white]"
        )

        # AI ke liye model aur tokens dikhao
        if not is_user and h.get("model"):
            console.print(
                f"         [dim]⚡ {h['model']} "
                f"• {h.get('tokens', 0)} tokens[/dim]"
            )
        console.print()

def _show_recent_messages(limit: int = 15):
    recent = get_recent_history(limit)
    if not recent:
        console.print("[yellow]Koi history nahi[/yellow]")
        return

    console.print()
    console.print(Rule(
        f"[bold cyan] Recent {limit} Messages [/bold cyan]",
        style="dim cyan"
    ))
    console.print()

    for h in recent:
        is_user    = h["role"] == "user"
        role_style = "bold cyan"  if is_user else "bold green"
        role_icon  = "👤 You"     if is_user else "🤖 AI"
        time_str   = h.get("timestamp", "")

        msg = h["message"]
        if len(msg) > 120:
            msg = msg[:120] + "..."

        console.print(
            f"[dim]{time_str}[/dim]  "
            f"[{role_style}]{role_icon}[/{role_style}]  "
            f"[white]{msg}[/white]"
        )
        if not is_user and h.get("model"):
            console.print(
                f"         [dim]⚡ {h['model']} "
                f"• {h.get('tokens', 0)} tokens[/dim]"
            )
        console.print()

def do_search():
    keyword = console.input(
        "\n[bold cyan]🔍 Search keyword likho: [/bold cyan]"
    ).strip()

    if not keyword:
        console.print("[yellow]Kuch likho pehle![/yellow]")
        return

    results = search_history(keyword)
    console.print()

    if results:
        console.print(
            f"[bold green]🔍 {len(results)} results mile "
            f"'{keyword}' ke liye:[/bold green]\n"
        )
        for h in results:
            is_user   = h["role"] == "user"
            role_icon = "👤 You" if is_user else "🤖 AI"
            msg = h["message"]
            if len(msg) > 100:
                msg = msg[:100] + "..."
            console.print(
                f"  [dim]{h['timestamp']}[/dim]  "
                f"[bold cyan]{role_icon}[/bold cyan]  "
                f"[white]{msg}[/white]"
            )
            console.print()
    else:
        console.print(
            f"[yellow]'{keyword}' — koi result nahi mila.[/yellow]"
        )
    console.print()

def main():
    initialize_db()
    show_welcome()

    assistant  = Assistant()
    voice_mode = False

    while True:
        try:
            if voice_mode:
                console.print(Rule(style="dim magenta"))
                console.print(
                    "[bold magenta]🎤 Voice Mode[/bold magenta]  "
                    "[dim]Bolo — 5 sec ruke tab band hoga[/dim]  "
                    "[dim]('text' bolke wapas aao)[/dim]"
                )
                user_input = listen_once(timeout=15)

                if not user_input:
                    console.print(
                        "[dim]  Kuch nahi suna — dobara bolo[/dim]\n"
                    )
                    continue

                lower = user_input.lower()
                if any(x in lower for x in [
                    "text mode", "text", "/text",
                    "band karo", "exit", "alvida"
                ]):
                    voice_mode = False
                    console.print(
                        "\n[bold cyan]⌨️  Text Mode ON![/bold cyan]\n"
                    )
                    continue

                console.print(
                    f"\n[bold cyan]You (voice) ▶[/bold cyan]  {user_input}\n"
                )
            else:
                user_input = get_user_input()

            if not user_input:
                continue

            cmd = user_input.lower().strip()

            if cmd == "/exit":
                console.print(
                    "\n[bold red]👋 Alvida Prem![/bold red]\n"
                )
                break

            elif cmd == "/help":
                show_help()

            elif cmd == "/stats":
                show_stats()

            elif cmd == "/monthly":
                show_monthly()

            elif cmd == "/history":
                show_history()

            elif cmd == "/savings":
                show_savings()

            elif cmd == "/status":
                show_status()

            elif cmd == "/clear":
                msg = assistant.clear_history()
                console.print(f"\n[bold green]{msg}[/bold green]\n")

            elif cmd == "/memory":
                mem = show_memory()
                console.print(f"\n[bold cyan]{mem}[/bold cyan]\n")

            elif cmd == "/forget":
                msg = forget_memory()
                console.print(f"\n[bold red]{msg}[/bold red]\n")

            elif cmd == "/voice":
                voice_mode = True
                console.print()
                console.print(Panel(
                    "[bold magenta]🎤  Voice Mode ON!\n\n"
                    "[white]Ab bolke poocho — AI jawab dega!\n\n"
                    "[dim]Wapas aane ke liye 'text' bolo[/dim]",
                    border_style="magenta",
                    padding=(1, 4),
                ))
                console.print()

            elif cmd == "/text":
                voice_mode = False
                console.print(
                    "\n[bold cyan]⌨️  Text Mode ON![/bold cyan]\n"
                )

            # ✅ Chat History — Date wise
            elif cmd == "/chathistory":
                show_full_history()

            # ✅ Search History
            elif cmd == "/search":
                do_search()

            # ✅ Clear Chat History
            elif cmd == "/clearchat":
                msg = clear_chat_history()
                console.print(f"\n[bold red]{msg}[/bold red]\n")

            else:
                console.print("[dim]  🤔 Soch raha hun...[/dim]")
                result = assistant.chat(user_input)
                show_response(result)

        except KeyboardInterrupt:
            console.print(
                "\n[bold red]👋 Band ho raha hai...[/bold red]\n"
            )
            break
        except Exception as e:
            console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")

if __name__ == "__main__":
    main()