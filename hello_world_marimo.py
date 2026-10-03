# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.11.2",
#     "pylatexenc>=2.11",
#     "python-dotenv>=1.2.4",
#     "qiskit>=2.5.2",
#     "qiskit-ibm-runtime>=0.50.0",
# ]
# ///

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    from pathlib import Path

    import marimo as mo
    from dotenv import load_dotenv
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import SparsePauliOp, Statevector
    from qiskit.transpiler import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService
    from qiskit_ibm_runtime.executor_estimator import Estimator

    return (
        Estimator,
        Path,
        QiskitRuntimeService,
        QuantumCircuit,
        SparsePauliOp,
        Statevector,
        generate_preset_pass_manager,
        load_dotenv,
        mo,
        os,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Qiskit Hello World on IBM Quantum hardware
    Builds a Bell-pair circuit, then estimates the $\langle ZZ \rangle$ observable on it using the IBM Quantum Runtime Estimator.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. Load credentials from `.env`
    Credentials come from `.env` (`IBM_QUANTUM_TOKEN`), and optionally `IBM_QUANTUM_BACKEND`. Do NOT hardcode your token in source code or commit your `.env` file.
    """)
    return


@app.cell
def _(Path, load_dotenv, os):
    # Resolved relative to this file so the notebook works from any working
    # directory, not just the project root.
    load_dotenv(Path(__file__).parent / ".env")
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    pinned = os.environ.get("IBM_QUANTUM_BACKEND") or None
    return pinned, token


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. Save the account (one-time)

    `QiskitRuntimeService.save_account()` writes the credentials to disk so later sessions authenticate automatically.
     Once you run it, you don't need to call this cell every time.
    """)
    return


@app.cell
def _(QiskitRuntimeService, token):
    QiskitRuntimeService.save_account(
        # For `token`, use the 44-character API_KEY you created
        # and saved from the IBM Quantum Platform Home dashboard
        token=token,
        overwrite=True,
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Authenticate

    Run this every time you need the service. With credentials already saved,
    `QiskitRuntimeService()` picks them up with no arguments.
    """)
    return


@app.cell
def _(QiskitRuntimeService):
    service = QiskitRuntimeService()
    print("Connected to:", service.channel)
    return (service,)


@app.cell
def _(mo):
    mo.md(r"""
    ### Available backends

    Backends the account can reach.
    """)
    return


@app.cell
def _(service):
    for _backend in service.backends():
        try:
            _status = _backend.status()
            _pending = getattr(_status, "pending_jobs", "n/a")
            _msg = getattr(_status, "status_msg", "")
        except Exception:
            _pending, _msg = "n/a", ""
        print(f"{_backend.name:24} pending_jobs={_pending} {_msg}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Pick a backend

    Set `QISKIT_BACKEND` in `.env` to pin a specific device (e.g. `ibm_kingston`).
    Leave it unset to let `least_busy` choose the open-plan device with the
    shortest queue. Falls back to a local fake backend if neither works.
    """)
    return


@app.cell
def _(pinned, service):

    backend = None

    if pinned:
        try:
            backend = service.backend(pinned)
            print(f"Pinned backend: {backend.name}")
        except Exception as exc:
            print(f"Could not load '{pinned}' ({type(exc).__name__}); falling back.")

    if backend is None:
        try:
            backend = service.least_busy(operational=True, simulator=False)
            print("Auto-selected backend:", backend.name)
        except Exception as exc:  # no open-plan access
            print(f"No real backend available ({type(exc).__name__}); using a local fake.")

    if backend is None:
        from qiskit_ibm_runtime.fake_provider import FakeBelemV2

        backend = FakeBelemV2()
        print("Fake backend:", backend.name)

    try:
        _st = backend.status()
        print("Num qubits:", backend.num_qubits, "| status:", getattr(_st, "status_msg", "?"))
    except Exception:
        print("Num qubits:", backend.num_qubits)
    return (backend,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Build the circuit

    Simple Bell pair: A Hadamard on qubit 0 then a CNOT onto qubit 1
    """)
    return


@app.cell
def _(QuantumCircuit):
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return (qc,)


@app.cell
def _(qc):
    qc.draw("mpl")
    return


@app.cell
def _(Statevector, qc):
    # Ideal state vector, computed locally — no hardware needed.
    # Basis order is |00>, |01>, |10>, |11>.
    sv = Statevector.from_instruction(qc)
    print(f"Statevector: {sv.data}")
    print(f"Probabilities: {dict(sv.probabilities_dict())}")
    return (sv,)


@app.cell
def _(mo):
    mo.md(r"""
    ### Observable

    $\langle Z \otimes Z \rangle$ on the Bell pair. Expected value is $+1$ for
    $\lvert \Phi^+ \rangle$ — the qubits are perfectly correlated.
    """)
    return


@app.cell
def _(SparsePauliOp, sv):
    observable = SparsePauliOp("ZZ")

    # The exact noiseless answer, for comparison against the hardware result.
    print(f"Ideal <ZZ> (exact): {sv.expectation_value(observable).real}")
    return (observable,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 5. Transpile to the backend

    Maps the circuit and the observable onto the backend's physical qubits.
    """)
    return


@app.cell
def _(backend, generate_preset_pass_manager, observable, qc):
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuit = pm.run(qc)
    isa_observable = observable.apply_layout(isa_circuit.layout)

    isa_circuit.draw("mpl")
    return isa_circuit, isa_observable


@app.cell
def _(mo):
    mo.md(r"""
    ## 6. Run the estimator

    Submits to the backend and waits for the result. This consumes real
    quantum-compute time on your account.
    """)
    return


@app.cell
def _(Estimator, backend, isa_circuit, isa_observable):
    estimator = Estimator(mode=backend)
    job = estimator.run([(isa_circuit, isa_observable)])
    result = job.result()
    return (result,)


@app.cell
def _(result):
    # ty: ignore[unresolved-attribute]
    print(f"Expectation value: {result[0].data.evs}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Expectation value

    Should be $\approx +1$ — confirming the Bell pair is in the
    $\lvert \Phi^+ \rangle$ state with perfect $Z$-parity correlation.
    """)
    return


@app.cell
def _(result):
    # ty: ignore[unresolved-attribute]
    result[0].data.evs
    return


if __name__ == "__main__":
    app.run()
