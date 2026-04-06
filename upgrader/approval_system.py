from upgrader.logger import log

def ask_approval(title: str, description: str) -> bool:
    print("\n" + "="*50)
    print(f"🔔 APPROVAL REQUIRED")
    print("="*50)
    print(f"📋 Action : {title}")
    print(f"📝 Details: {description}")
    print("="*50)

    while True:
        answer = input("\n✅ Apply this? (yes/no): ").strip().lower()
        if answer in ['yes', 'y', 'haan', 'ha']:
            log(f"User approved: {title}")
            return True
        elif answer in ['no', 'n', 'nahi', 'na']:
            log(f"User rejected: {title}")
            return False
        else:
            print("❌ Sirf 'yes' ya 'no' likho!")

def ask_backup_approval() -> bool:
    return ask_approval(
        "Create Backup",
        "Update se pehle poora project backup hoga"
    )

def show_suggestions_menu(suggestions: list) -> list:
    print("\n" + "="*50)
    print("💡 AI SUGGESTIONS")
    print("="*50)

    approved = []
    for s in suggestions:
        priority_icon = (
            "🔴" if s["priority"] == "high"
            else "🟡" if s["priority"] == "medium"
            else "🟢"
        )
        print(f"\n{priority_icon} [{s['type'].upper()}] {s['title']}")
        print(f"   {s['description']}")

        if s.get("safe_to_auto_apply"):
            approved.append(s)
            print("   ✅ Auto-apply safe hai")
        else:
            apply = ask_approval(s["title"], s["description"])
            if apply:
                approved.append(s)

    return approved