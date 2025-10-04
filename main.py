from agent import Agent
from rich import print


def run():
    ag = Agent(db_path="jarvis.db")
    print("[bold green]Jarvis‑Lite v0.1[/] — type 'exit' to quit")
    while True:
        q = input("\nYou: ")
        if q.strip().lower() in {"exit","quit"}: 
            break
        try:
            a = ag.step(q)
            print(f"\n[cyan]Agent:[/] {a}")
        except Exception as e:
            print(f"[red]Error:[/] {e}")


if __name__ == "__main__":
    run()
