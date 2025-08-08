import cupy as cp

# GPUの名前を表示
props = cp.cuda.runtime.getDeviceProperties(0)
print("使っているGPU:", props['name'])

# sin演算を実行
x = cp.arange(10000000)
y = cp.sin(x)
print("最初の5個:", y[:5])
