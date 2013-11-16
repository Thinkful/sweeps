
"""
Cmd-line interface to *sweep* the system, running tasks!
"""

def main():
    asof = datetime.utcnow()
    for task in AbstractTask.__subclasses__():
        task.run_all(asof)

if __name__ == '__main__':
    main()
