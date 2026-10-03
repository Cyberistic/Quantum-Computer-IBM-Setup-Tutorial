"""Qiskit hello world — Bell pair, <ZZ> on IBM Quantum hardware.

Mirrors hello_world_marimo.py. Credentials are read from `.env`, never hardcoded.

Run:  uv run python hello_world.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.executor_estimator import Estimator

# 1. Load credentials from `.env`. Resolved relative to this file so the
#    script works from any working directory, not just the project root.
load_dotenv(Path(__file__).parent / ".env")
token = os.environ.get("IBM_QUANTUM_TOKEN")
pinned = os.environ.get("IBM_QUANTUM_BACKEND") or None

if not token:
    raise SystemExit(
        "IBM_QUANTUM_TOKEN not found. Create a .env next to this script:\n"
        "  IBM_QUANTUM_TOKEN=<your 44-character key>\n"
        "  IBM_QUANTUM_BACKEND=ibm_kingston   # optional"
    )

# 2. Save the account. overwrite=True keeps this cell re-runnable, since
#    save_account raises AccountAlreadyExistsError on a second execution.
QiskitRuntimeService.save_account(
    # For `token`, use the 44-character API_KEY you created
    # and saved from the IBM Quantum Platform Home dashboard
    token=token,
    overwrite=True,
)

# 3. Authenticate. With credentials saved, no arguments are needed.
service = QiskitRuntimeService()
print("Connected to:", service.channel)

# Backends the account can reach.
for _backend in service.backends():
    try:
        _status = _backend.status()
        _pending = getattr(_status, "pending_jobs", "n/a")
        _msg = getattr(_status, "status_msg", "")
    except Exception:
        _pending, _msg = "n/a", ""
    print(f"{_backend.name:24} pending_jobs={_pending} {_msg}")

# Pick a backend: IBM_QUANTUM_BACKEND pins one, else least_busy, else a local fake.
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

# Fake backends have no .status(); real ones do.
_st = getattr(backend, "status", None)
if _st is not None:
    print("Num qubits:", backend.num_qubits, "| status:", getattr(_st(), "status_msg", "?"))
else:
    print("Num qubits:", backend.num_qubits)

# 4. Build the circuit: simple Bell pair — H on qubit 0, then CNOT onto qubit 1.
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

print()
print(qc.draw())
qc.draw("mpl").savefig("hello_world_circuit.png", dpi=150, bbox_inches="tight")

# Ideal state vector, computed locally — no hardware needed. Basis order is
# |00>, |01>, |10>, |11>.
sv = Statevector.from_instruction(qc)
print(f"\nStatevector: {sv.data}")
print(f"Probabilities: {dict(sv.probabilities_dict())}")

# Observable: <Z (x) Z> is +1 for |Phi+>, the perfectly correlated Bell pair.
observable = SparsePauliOp("ZZ")

# The exact noiseless answer, for comparison against the hardware result below.
print(f"Ideal <ZZ> (exact): {sv.expectation_value(observable).real}")

# 5. Transpile onto the backend's physical qubits.
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
isa_circuit = pm.run(qc)
isa_observable = observable.apply_layout(isa_circuit.layout)
isa_circuit.draw("mpl").savefig("hello_world_isa_circuit.png", dpi=150, bbox_inches="tight")

# 6. Run the estimator. This consumes real quantum compute on the account.
estimator = Estimator(mode=backend)
job = estimator.run([(isa_circuit, isa_observable)])
result = job.result()

# A 2-qubit ZZ expectation value is bounded by [-1, +1]. Anything outside that
# range means the estimator result is being read incorrectly. Real hardware
# returns slightly less than the ideal 1.0 above, due to gate and measurement
# error plus finite sampling.
print(f"\nExpectation value: {result[0].data.evs}")