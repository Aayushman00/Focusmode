import argparse
import os
import sys
import time
import platform
import subprocess
import json
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeRemainingColumn

console = Console()

WINDOWS_TASKKILL_CMD = "taskkill /F /IM {}"
MAC_QUIT_CMD = "osascript -e 'quit app \"{}\"'"
HISTORY_FILE = ".focus_history.json"
APP_HISTORY_FILE = ".focus_apps.json"
HOSTS_FILE = r"C:\Windows\System32\drivers\etc\hosts" if platform.system().lower() == "windows" else "/etc/hosts"
REDIRECT_IP = "127.0.0.1"

APP_MAP = {
    "chrome": {
        "windows": "chrome.exe",
        "darwin": "Google Chrome"
    },
    "discord": {
        "windows": "Discord.exe",
        "darwin": "Discord"
    },
    "steam": {
        "windows": "steam.exe",
        "darwin": "Steam"
    },
    "spotify": {
        "windows": "Spotify.exe",
        "darwin": "Spotify"
    },
    "whatsapp": {
        "windows": "WhatsApp.exe",
        "darwin": "WhatsApp"
    }
}

def block_apps(apps):
    system = platform.system().lower()
    for app in apps:
        app = app.lower()
        app_proc = APP_MAP.get(app, {}).get(system)
        if not app_proc:
            console.print(f"[yellow]⚠️ Unsupported or unknown app: {app}[/yellow]")
            continue
        try:
            if system == "windows":
                subprocess.run(WINDOWS_TASKKILL_CMD.format(app_proc), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif system == "darwin":
                subprocess.run(MAC_QUIT_CMD.format(app_proc), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            console.print(f"[red]🛑 Blocked: {app}[/red]")
        except Exception as e:
            console.print(f"[red]Error blocking {app}: {e}[/red]")

def watchdog_killer(apps, stop_event):
    system = platform.system().lower()
    while not stop_event.is_set():
        block_apps(apps)
        time.sleep(10)

def block_websites(websites):
    if not os.access(HOSTS_FILE, os.W_OK):
        console.print("[red]❌ You need to run this script as administrator to block websites.[/red]")
        return
    with open(HOSTS_FILE, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        file.writelines(lines)
        for site in websites:
            entry = f"{REDIRECT_IP} {site}\n"
            if entry not in lines:
                file.write(entry)
    console.print(f"[red]🌐 Blocked websites: {', '.join(websites)}[/red]")

def unblock_websites(websites):
    try:
        with open(HOSTS_FILE, 'r') as file:
            lines = file.readlines()
        with open(HOSTS_FILE, 'w') as file:
            for line in lines:
                if not any(site in line for site in websites):
                    file.write(line)
    except Exception as e:
        console.print(f"[red]Error unblocking websites: {e}[/red]")

def focus_timer(minutes, strict, apps):
    stop_event = threading.Event()
    watchdog_thread = threading.Thread(target=watchdog_killer, args=(apps, stop_event))
    watchdog_thread.daemon = True
    watchdog_thread.start()

    seconds = minutes * 60
    with Progress(
        "[bold green]⏳ Focusing...[/bold green]",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Focus Time", total=seconds)
        try:
            for _ in range(seconds):
                time.sleep(1)
                progress.update(task, advance=1)
        except KeyboardInterrupt:
            if strict:
                console.print("[red]❌ Strict mode: Can't exit focus early.[/red]")
                focus_timer((seconds - progress.tasks[0].completed) // 60, strict, apps)
            else:
                console.print("[yellow]⚠️ Focus session interrupted.[/yellow]")
                stop_event.set()
                watchdog_thread.join()
                sys.exit(1)
    stop_event.set()
    watchdog_thread.join()

def end_summary(duration, apps, websites):
    console.print("\n[bold cyan]✅ Focus session complete![/bold cyan]")
    console.print(f"⏱ Duration: [green]{duration} minutes[/green]")
    console.print(f"🧹 Apps blocked: [red]{', '.join(apps)}[/red]")
    if websites:
        console.print(f"🌐 Websites blocked: [red]{', '.join(websites)}[/red]")
    console.print("[bold magenta]Well done. Time well used. 🧠🔥[/bold magenta]")

def log_session(duration, apps):
    entry = {
        "duration": duration,
        "apps": apps,
        "timestamp": datetime.now().isoformat()
    }
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = []
    history.append(entry)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def weekly_summary():
    if not os.path.exists(HISTORY_FILE):
        console.print("[yellow]No session history to summarize.[/yellow]")
        return
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    week_ago = datetime.now() - timedelta(days=7)
    totals = defaultdict(int)
    total_time = 0
    for session in history:
        ts = datetime.fromisoformat(session["timestamp"])
        if ts >= week_ago:
            total_time += session["duration"]
            for app in session["apps"]:
                totals[app] += session["duration"]
    console.print("\n[bold blue]📊 Weekly Focus Summary:[/bold blue]")
    console.print(f"Total time focused: [green]{total_time} minutes[/green]")
    for app, minutes in totals.items():
        console.print(f"- [cyan]{app}[/cyan]: {minutes} min blocked")

def main():
    parser = argparse.ArgumentParser(description="🧠 FocusMode - Kill distractions and enter deep work.")
    parser.add_argument("--duration", type=int, help="Focus session duration in minutes")
    parser.add_argument("--block", nargs="+", help="List of apps to block (e.g. chrome discord steam)")
    parser.add_argument("--strict", action="store_true", help="Enable strict mode: can't exit early")
    parser.add_argument("--log-history", action="store_true", help="Log focus sessions to history file")
    parser.add_argument("--websites", nargs="*", help="List of websites to block (e.g. youtube.com reddit.com)")
    parser.add_argument("--summary", action="store_true", help="Show weekly focus summary")
    args = parser.parse_args()

    if args.summary:
        weekly_summary()
        return

    if not args.duration or not args.block:
        console.print("[red]Please provide --duration and --block for a focus session or use --summary.[/red]")
        return

    apps = [app.lower() for app in args.block]
    websites = args.websites or []

    console.print("[bold]🔒 Starting Focus Mode...[/bold]")
    block_apps(apps)
    if websites:
        block_websites(websites)

    focus_timer(args.duration, args.strict, apps)
    end_summary(args.duration, apps, websites)

    if args.log_history:
        log_session(args.duration, apps)

    if websites:
        unblock_websites(websites)

if __name__ == "__main__":
    main()
