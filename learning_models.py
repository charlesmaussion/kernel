import numpy as np
import scipy
from cvxopt import matrix, solvers
#from scipy.optimize import minimize

class SVM(object):
    '''
    A Support Vector Machine class enabling training of SVM models using Kernel methods.
    '''
    def __init__(self, lmbd=0.1, x0=None):
        '''
        Intiates parameters for the SVM learning procedure.

        Arguments :
        - lmbd : a float representing the regularization coefficient in the primal problem
        - x0 : a 1d array representing the starting point for the optimization problem
        '''
        self.lmbd = lmbd
        self.x0= x0
        self.reformated = False

    def train(self, K, y):
        '''
        Trains a SVM classifier using a Kernel method made implicit by the matrix K passed as argument. Uses a dual
        formulation for the optimization problem that is being solved.

        Arguments :
        - K : a 2d array representing the Kernel matrix used
        - y : a 1d array representing the labels. y is supposed to have values in {-1,1} but if y takes values in {0,1} 
              it is reformated to take values in {-1,1} via y <- 2 * (y - 0.5)
        '''
        dim = K.shape[0]
        assert dim == len(y)
        y_values_sorted = np.sort(np.unique(y))
        if len(y_values_sorted) > 2:
            raise ValueError("y must have only 2 possible values")
        if y_values_sorted[0] == 0 and y_values_sorted[1] == 1:
            y = 2 * (y - 0.5)
            self.reformated = True
            print('\n\t\t\t######## y has been reformated to {-1,1} ########\n')
        else:
            if y_values_sorted[0] != -1 or y_values_sorted[1] !=1:
                raise ValueError("y must have values either in {0,1} or {-1,1}")
        diag_y = np.diag(y)
        idt = np.identity(dim)
        P = 1 / (2*self.lmbd) * np.dot(diag_y, np.dot(K, diag_y))
        q = - np.ones(dim)
        G = np.concatenate((idt, -idt))
        h = np.concatenate((np.ones(dim) / dim, np.zeros(dim)))
        if self.x0 is None:
            self.x0 = np.ones(dim)/(2*dim)
        res = solvers.qp(matrix(P), matrix(q), matrix(G), matrix(h), initvals=self.x0)['x']
        self.alpha = np.dot(diag_y, res)/(2*self.lmbd)

    def predict(self, K):
        if self.reformated:
            return 0.5 * (np.sign(np.dot(K,self.alpha).reshape(-1)) + 1)
        else:
            return np.sign(np.dot(K,self.alpha).reshape(-1))



class KRR(object):
    '''
    A class implementing Kernel Ridge Regression
    '''
    def __init__(self, lmbd=0.1):
        self.lmbd = lmbd

    def train(self, K, y):
        A = K + self.lmbd * len(K)*np.eye(len(K))
        self.alpha = scipy.linalg.solve(A, y, sym_pos=True)

    def predict(self, K):
        return np.dot(K, self.alpha)
