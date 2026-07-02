from gjq_client import GJQRuntimeService, Estimator, generate_preset_pass_manager
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp

#api_key
with open('gjq-api-key.txt') as f:
    api_key=f.read().strip()

# 构造量子线路
bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)

# 构造算符并添加基旋转
M1 = SparsePauliOp.from_list([("XX", 1)])
for i, p in enumerate(M1.paulis[0].to_label()):  # 本示例仅演示单个 Pauli 项的期望值测量
    if p == 'X':
        bell.h(i)
    elif p == 'Y':
        bell.sdg(i)
        bell.h(i)
bell.measure_all()  #Estimator 需要线路包含显式测量位

# 获取后端并转译
service = GJQRuntimeService(api_key=api_key)
backend = service.backend('Baihua')
pm = generate_preset_pass_manager(backend=backend, optimization_level=0)
isa_circuit = pm.run(bell)

# 提交 Estimator 任务
estimator = Estimator(backend=backend)
job = estimator.run(isa_circuit, obs=M1)

# 获取结果
print(job.result())