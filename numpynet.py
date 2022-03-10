# OOP implenmentation of a neural network using pure numpy

import numpy as np
import matplotlib.pyplot as plt
from nn_utils import *

# pass a list of layer diminesions
# --> each index represents a layer with the specified number of neurons being
#     passed at each index.

# pass a list of activations
# --> each index corresponds to the indices of the layer dimensions
# --> contains a string specifying the activation funciton for each layer


class NumpyNet():

    # X --> array of input data
    # Y --> true label vector, true classification of input data
    #    size : numnber of examples
    # layers_dims -> list of dimensions for each layer, n-layers long
    # activations -> string list of activations to be used each layer
    # learning_rate -> alpha value update_params during gradient descent
    # num_iterations ->  num iterations for optimization loop
    # print_cost --> Boolean, if true prints the cost every 100 steps

    # params --> dictionary to hold weights and biases for each layer
    # grads --> dict for gradients during backpropagation

    def __init__(self, layers_dims, activations, learning_rate,
                 num_iterations, initializer, mini_batch):

        if len(layers_dims) != len(activations):
            print("There is a network mismatch...")
            print("Activation size: {}".format(len(activations)))
            print("layers_dims size: {}".format(len(layers_dims)))
            exit(1)

        self.layers_dims = layers_dims
        self.activations = activations
        self.learning_rate = learning_rate
        self.num_iterations = num_iterations
        self.initializer = initializer
        self.mini_batch = mini_batch
        self.num_layers = len(self.layers_dims) - 1
        self.params = dict()
        self.grads = dict()
        self.cache = dict()

    # Initialize parameters
    def initialize_params(self):
        if self.initializer == 'zeros':
            self.params = zero_params(self.layers_dims)
        elif self.initializer == 'random':
            self.params = random_params_params(self.layers_dims)
        elif self.initializer == 'he':
            self.params = he_params(self.layers_dims)

        # checking to make sure the dimensions of params matches input shape
        assert(self.params['W%s' % l].shape == (self.layers_dims[l],
                                                self.layers_dims[l-1]))
        assert(self.params['b%s' % l].shape == (self.layers_dims[l], 1))

        '''
        # start at 1 to avoide index/layer num confusion
        for l in range(1, self.num_layers + 1):
            # initializes the weights randomly
            self.params['W%s' % l] == np.random.randn(
                self.layers_dims[l],
                self.layers_dims[l-1]) * 0.01
            # initializes the biases as zero
            self.params['b%s' % l] == np.zeros((self.layers_dims[l],  1))

            # checking to make sure the dimensions of params matches the
            assert(self.params['W%s' % l].shape == (self.layers_dims[l],
                                                    self.layers_dims[l-1]))
            assert(self.params['b%s' % l].shape == (self.layers_dims[l], 1))
            '''
    # forward propagation through one layer.
    # linear forward step: Z[l] = np.dot(weights[l], activation[l-1] + bias[l]
    # activation forward step: A[l] = activation(Z[l])
    def layer_forward(self, A_prev, W, b, activation):
        # linear step through layer
        Z = np.dot(W, A_prev) + b
        # apply activation function to linear output
        if activation == 'sigmoid':
            A = sigmoid(Z)
        elif activation == 'relu':
            A = relu(Z)
        elif activation == 'tanh':
            A = tanh(Z)
        elif activation == 'softmax':
            A = softmax(Z)

        return A, Z

    # forward propagation through all num_layers
    # uses layer_forward
    # adds A[l] and Z[l] to the cache
    def nn_forward(self, X):
        # set input data as activation from "layer 0"
        # handles input as "A_prev"
        self.cache['A0'] = X
        # loop through layers geting current layers weights bias and activation
        for l in range(1, self.num_iterations + 1):
            W = self.params['W%s' % l]
            b = self.params['b%s' % l]
            activation = self.activations[l]
            # linear and activation step for current layer
            # adds A[l] to cache to use for the next layer input
            # adds Z[l] to cache to use in back propagation
            self.cache['A%s' % l], self.cache['Z%s' % l] = self.layer_forward(
                self.cache['A%s' % (l-1)],
                W, b, activation)

    # cost function
    # find the cost from the forward prop predicitons and true labels
    # predicitons: AL, the activation output from the last layer
    # true labels: Y
    def compute_cost(self, Y):
        # retrieves the output of the last activation layer ... y_hat
        AL = self.cache['A%s' % str(self.num_layers)]
        # Binary cross entropy loss
        if self.activations[self.num_layers] == 'sigmoid':
            loss = -(np.multiply(Y, np.log(AL)) + np.multiply(
                (1-Y), np.log(1-AL)))
        # Cross entropy loss
        elif self.activations[self.num_layers] == 'softmax':
            loss = -np.sum(np.multiply(Y, np.log(AL)), axis=0, keepdims=True)
        else:
            print('Output layer activation not valid....')
            print('Activation must be: \'sigmoid\' or \'softmax\'')
            print('Current activation is: %s' % self.activations[-1])
        # compute the cost from the calculated loss
        cost = np.sum(loss, axis=1, keepdims=True) / np.float(Y.shape[0])
        cost = np.squeeze(cost)

        return cost

    # backward propagation through one layer
    # copmutes gradients for each layer
    def layer_backward(self, dA, A_prev, Z, W, activation):
        if activation == 'sigmoid':
            dZ = np.multiply(dA, sigmoid_derivative(Z))
        elif activation == 'relu':
            dZ = np.multiply(dA, relu_derivative(Z))
        elif activation == 'tanh':
            dZ = np.multiply(dA, tanh_derivative(Z))
        # compute grads to store in grad dict
        dW = np.dot(dZ, A_prev.T)/float(A_prev.shape[1])
        db = np.sum(dZ,  axis=1, keepdims=True)/float(A_prev.shape[1])
        dA_prev = np.dot(W.T, dZ)

        return dA_prev, dW, db

    # back propagation through all layers
    # computes the gradients for the last layer (L)
    # then loops through the rest of the layers (L-1 --> l[1])
    def nn_backward(self, Y):
        # pull params from dictionary for last layer
        AL = self.cache['A%s' % str(self.num_layers)]
        W = self.params['W%s' % str(self.num_layers)]
        A_prev = self.cache['A%s' % str(self.num_layers - 1)]  # from L-1
        # initialize back prop by compute gradients for output layer
        # if output layer is softmax gradients are computed here
        # if not softmax..layer_backward called to handle other activations
        if self.activations[-1] == 'softmax':
            dZ = AL - Y
            dW = np.dot(dZ, A_prev.T)/float(A_prev.shape[1])
            db = np.sum(dZ,  axis=1, keepdims=True)/float(A_prev.shape[1])
            dA_prev = np.dot(W.T, dZ)
        else:
            Z = self.cache['Z%s' % str(self.num_layers)]
            dAL = - (np.divide(Y, AL) - np.divide(1-Y, 1-AL))
            dA_prev, dW, db = self.layer_backward(self, dAL, A_prev, Z, W,
                                                  self.activations[-1])
        # update grads dict with the gradients
        self.grads['dW%s' % str(self.num_layers)] = dW
        self.grads['db%s' % str(self.num_layers)] = db
        self.grads['dA%s' % str(self.num_layers - 1)] = dA_prev

        # loop through the rest of the layers with layer_backward
        for l in reversed(range(self.num_layers - 1)):
            # gather current layer info
            dA = self.grads['dA%s' % str(l)]
            A_prev = self.cache['A%s' % str(l-1)]
            Z = self.cache['Z%s' % str(l)]
            W = self.params['W%s' % str(l)]
            activation = self.activations[l]
            # backward pass through layer
            dA_prev, dW, db = self.layer_backward(self, dA, A_prev, Z, W,
                                                  activation)
            # update grads dict with computed gradients
            self.grads['dA%s' % str(l - 1)] = dA_prev
            self.grads['dW%s' % str(l)] = dW
            self.grads['db%s' % str(l)] = db

    # update params using gradient descent
    # based on the gradients generated in nn_backward() & layer_backward()
    # uses learning rate and gradients to perfrom gradient descent
    def update_params(self):
        for l in range(1, self.num_layers + 1):
            # update weights using gradient descent
            self.params['W%s' % l] = self.params['W%s' % l] - self.learning_rate * self.grads['dW%s']
            # update bias using gradient descent
            self.params['b%s' % l] = self.params['b%s' % l] - self.learning_rate * self.grads['db%s']

    # executes one full pass through network updating params and returning cost
    # nn_forward() --> compute_cost() --> nn_backward() --> update_params()
    def network_pass(self, X_batch, Y_batch):
        # forward propagation
        self.nn_forward(X_batch)
        # cost of forward prop is saved to return
        cost = self.compute_cost(Y_batch)
        # back propagation
        self.nn_backward(Y_batch)
        # update the parameters via gradient descent using params/grads
        self.update_params()

        return cost

    # training the neural network
    # iterates using network_pass() for self.num_iterations
    # plots cost if set to True
    def train(self, X, Y, print_cost=True):
        # initialize parameters (weights randomly, biases -> 0)
        self.initialize_params()
        # create costs list to store the cost for every epoch
        # used to evaluate training
        costs = []
        num_samples = Y.shape[1]
        # iterate training based on num specified when building model
        for i in range(0, self.num_iterations):
            for index in range(0, num_samples, self.mini_batch):
                end = index + self.mini_batch
                cost = self.network_pass(X[:, index:end], Y[:, index:end])
                if print_cost and i % 100 == 0:
                    print("Cost after epoch %i: %f" % (i, cost))
                    costs.append(cost)
        if print_cost:
            # plot the cost
            plt.plot(costs)
            plt.ylabel('cost')
            plt.xlabel('epochs (per 100)')
            plt.title("Learning rate = " + str(self.learning_rate))
            plt.show()
            print(model_accuracy(self.cache['A%s' % self.num_layers], Y))

    # forward pass through network for implementing after model is trained
    def predict(self, X, Y):
        self.nn_forward(X)
        accuracy = model_accuracy(self.cache['A%s' % self.num_layers], Y)

        return accuracy
