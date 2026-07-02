from gjq_client import GJQRuntimeService,generate_preset_pass_manager,Sampler
from qiskit import QuantumCircuit

#获取api_key
with open('gjq-api-key.txt') as f:
    api_key=f.read().strip()

#建立量子线路
qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0,1)
qc.ccx(0,1,2)
qc.rxx(0.5, 0, 1)

#转译
service = GJQRuntimeService(api_key=api_key)
backend = service.backend('SAS-CPU')  # 以云端单振幅模拟器为例；若使用 FAS-CPU，可直接替换后端名称
pm = generate_preset_pass_manager(optimization_level=2, backend=backend)
isa_circuit=pm.run(qc)

#创建Sampler并提交任务
sampler = Sampler(backend=backend)
job = sampler.run(isa_circuit, shots=1024, amplitude_index=[4])

#返回结果
print(job.result())