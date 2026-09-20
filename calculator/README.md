# calculator

A small infix expression evaluator with operator precedence — a real
shunting-yard-style parser, not `eval()`. This is the sandboxed project the
Jarvis agent (one directory up) reads, runs, and edits; it isn't part of
the agent itself and has no dependency on it.

```bash
python main.py "3 + 4 * 2"
```

```
python -m unittest tests.py
```

`lorem.txt` and `pkg/morelorem.txt` are placeholder files the agent
overwrites when asked to edit something in demos — their content isn't
meaningful.