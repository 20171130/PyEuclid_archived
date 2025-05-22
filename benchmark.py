import numpy as np
from scipy import linalg
import time

# Example: Solve a system Ax = b
def solve_system(A, b, method='numpy'):
    """
    Solve a linear system using optimized implementations
    
    Parameters:
    - A: coefficient matrix
    - b: right-hand side vector
    - method: which implementation to use
    
    Returns:
    - x: solution vector
    - time_taken: execution time
    """
    start_time = time.time()
    
    if method == 'numpy':
        # NumPy's implementation (uses LAPACK under the hood)
        x = np.linalg.solve(A, b)
    
    elif method == 'scipy_lu':
        # SciPy's LU decomposition (optimized Gaussian elimination)
        lu, piv = linalg.lu_factor(A)
        x = linalg.lu_solve((lu, piv), b)
    
    elif method == 'scipy_direct':
        # Direct solver from SciPy
        x = linalg.solve(A, b)
        
    time_taken = time.time() - start_time
    return x, time_taken

# Demonstration with different sizes
def benchmark_solvers(sizes=[5000, 10000, 20000, 50000]):
    results = {}
    
    for n in sizes:
        print(f"\nBenchmarking with matrix size {n}x{n}")
        
        # Generate random system
        A = np.random.rand(n, n)
        b = np.random.rand(n)
        
        # Make diagonally dominant for numerical stability
        A = A + n * np.eye(n)
        
        # Test different methods
        for method in ['numpy', 'scipy_lu', 'scipy_direct']:
            x, t = solve_system(A, b, method)
            print(f"  {method}: {t:.6f} seconds")
            
            # Verify solution
            error = np.linalg.norm(A @ x - b)
            print(f"    Error: {error:.2e}")
            
            results.setdefault(method, []).append(t)
    
    return results

# Run benchmark
if __name__ == "__main__":
    benchmark_solvers()