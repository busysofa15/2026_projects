import numpy as np
input = np.array([[1, 1], [2, 2], [3, 0]])
weight = np.random.randn(2, 1)
output = np.array([[1], [1], [0]])
learning_rate = 1
bias = np.random.randn(1)
for epoch in range(10000):
    supposedtobeoutput = np.dot(input, weight)+bias
    squishification = 1/(1+np.exp(-supposedtobeoutput))
    error = output - squishification
    slope = error*(squishification*(1-squishification))
    weight += np.dot(input.T, slope)*learning_rate
    bias += np.sum(slope)*learning_rate
    if epoch % 100 == 0:
        print(f"Error at epoch {epoch}: {np.mean(np.abs(error)):.4f}")
print(squishification)
