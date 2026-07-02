"""
TSP calling CIM example
"""
import kaiwu as kw
import numpy as np
from kaiwu.common import CheckpointManager as ckpt

# Define edges using conditional functions
def is_edge_used(var_x, var_u, var_v):
    """
    Determine whether the edge (u, v) is used in the path.

    Args:
        var_x (ndarray): Decision variable matrix.

        var_u (int): Start node.

        var_v (int): End node.

    Returns:
        ndarray: Decision variable corresponding to the edge (u, v).
    """
    return kw.core.quicksum([var_x[var_u, j] * var_x[var_v, j + 1] for j in range(-1, n - 1)])


if __name__ == "__main__":
    # Set the save path for intermediate files 设置中间文件的保存路径
    kw.common.CheckpointManager.save_dir = '/tmp'
    # Define distance matrix 定义距离矩阵
    w = np.array([[0, 0, 1, 1, 0],
                  [0, 0, 1, 0, 1],
                  [1, 1, 0, 0, 1],
                  [1, 0, 0, 0, 1],
                  [0, 1, 1, 1, 0]])

    n = w.shape[0]  # Number of nodes 节点数

    # Create a QUBO variable matrix (n x n) 建立一个QUBO变量矩阵(n*n)
    x = kw.core.ndarray((n, n), "x", kw.core.Binary)

    # Generate the set of edges and the set of non-edges 生成边和非边集合
    edges = [(u, v) for u in range(n) for v in range(n) if w[u, v] != 0]
    no_edges = [(u, v) for u in range(n) for v in range(n) if w[u, v] == 0]

    # Initialize the QUBO model 初始化QUBO模型
    qubo_model = kw.qubo.QuboModel()

    # Set the objective function: minimize path cost 设置目标函数：最小化路径长度
    path_cost = kw.core.quicksum([w[u, v] * is_edge_used(x, u, v) for u, v in edges])
    qubo_model.set_objective(path_cost)

    # Add constraints
    # Node constraints: Each node must occupy one position
    qubo_model.add_constraint((x.sum(axis=0) - 1) ** 2 == 0, "node_cons", penalty=5.0)

    # Location constraint: Each location must have at least one node.
    qubo_model.add_constraint((x.sum(axis=1) - 1) ** 2 == 0, "pos_cons", penalty=5.0)

    # Edge constraint: Non-connecting edges must not appear
    qubo_model.add_constraint(
        kw.core.quicksum([is_edge_used(x, u, v) for u, v in no_edges])==0,
        "edge_cons", penalty=5
    )

    # Configure the solver
    ckpt.save_dir = './tmp'
    optimizer = kw.cim.CIMOptimizer(task_name="tsp")
    optimizer = kw.cim.PrecisionReducer(optimizer, 8)
    solver = kw.solver.SimpleSolver(optimizer)
    sol_dict, qubo_val = solver.solve_qubo(qubo_model)

    if sol_dict is not None:
        # Verification Results
        unsatisfied, res_dict = qubo_model.verify_constraint(sol_dict)
        print(f"Number of unsatisfied constraints: {unsatisfied}")
        print(f"constraint value: {res_dict}")

        # Calculate path cost
        path_cost = kw.core.get_val(qubo_model.objective, sol_dict)
        print(f"Actual path cost: {path_cost}")
    else:
        print("Try again later")