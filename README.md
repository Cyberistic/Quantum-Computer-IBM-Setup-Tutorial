# Qiskit Setup — CpE414 Hello World

How to get the IBM Quantum hello-world running in this folder.

## Requirements

- [uv](https://docs.astral.sh/uv/) — the package manager. No pip needed.
- An IBM Quantum account with API key access: [dashboard](https://quantum.ibm.com) → **API keys** → *Create API key*.

## Setup

```bash
uv sync
```

This creates `.venv/` from `uv.lock`. Dependencies live in `pyproject.toml`.

## Credentials

Put your key in `.env` (already gitignored):

```bash
IBM_QUANTUM_TOKEN=<your 44-character key>

# Optional: pin a specific backend. Comment out to auto-select via least_busy.
QISKIT_BACKEND=ibm_kingston
```


The key is read at runtime via `python-dotenv`. **Do NOT hardcode or commit your key**.

## Run

**Script** — prints the circuit, then estimates ⟨ZZ⟩ on real hardware:

```bash
uv run python hello_world.py
```

**Notebook (marimo)**:

```bash
uv run marimo edit hello_world_marimo.py
```

## Type checking

```bash
uv run ty check hello_world.py
```


- **Every real run costs quantum compute.** For free iteration, comment out the
  `QISKIT_BACKEND` pin and let it fall through to `FakeBelemV2`.
- To undo a saved account: `QiskitRuntimeService.delete_account()`.



## Enabling jupyter (optional)

`hello_world.ipynb` needs jupyter, which isn't installed. To enable:

```bash
uv add jupyterlab
```

Then `uv run jupyter lab`.