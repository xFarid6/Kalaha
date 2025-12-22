import numpy as np
import pickle

class NeuralNetwork:
    def __init__(self, input_size=4, hidden_size=8, output_size=1):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Weights (Random Init)
        self.w1 = np.random.randn(input_size, hidden_size) * 0.5
        self.b1 = np.zeros(hidden_size)
        self.w2 = np.random.randn(hidden_size, output_size) * 0.5
        self.b2 = np.zeros(output_size)

    def forward(self, inputs):
        # inputs shape: (4,)
        # Hidden
        z1 = np.dot(inputs, self.w1) + self.b1
        a1 = np.maximum(0, z1) # ReLU
        
        # Output
        z2 = np.dot(a1, self.w2) + self.b2
        a2 = np.tanh(z2) # Tanh (-1 to 1)
        
        return a2 # (1,)

    def copy(self):
        new_net = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)
        new_net.w1 = self.w1.copy()
        new_net.b1 = self.b1.copy()
        new_net.w2 = self.w2.copy()
        new_net.b2 = self.b2.copy()
        return new_net

    def mutate(self, rate=0.1, power=0.1):
        # Perturb weights
        # Mask for sparsity? Or apply to all? 
        # Usually apply small noise to all or subset.
        
        # W1
        mask1 = np.random.rand(*self.w1.shape) < rate
        self.w1[mask1] += np.random.randn(*self.w1[mask1].shape) * power
        
        # B1
        maskb1 = np.random.rand(*self.b1.shape) < rate
        self.b1[maskb1] += np.random.randn(*self.b1[maskb1].shape) * power
        
        # W2
        mask2 = np.random.rand(*self.w2.shape) < rate
        self.w2[mask2] += np.random.randn(*self.w2[mask2].shape) * power
        
        # B2
        maskb2 = np.random.rand(*self.b2.shape) < rate
        self.b2[maskb2] += np.random.randn(*self.b2[maskb2].shape) * power

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
