from ParameterSelector import *
import numpy as np
from sklearn.metrics.pairwise import rbf_kernel


class CME(object):

    def __init__(self, null_context_vec, null_treatment_vec, null_rewards):
        reg_pow = -1
        self.reg_param = (10.0 ** reg_pow) / null_context_vec.shape[0]
        self.kernel_param = (10.0 ** 0)
        self.null_context_vec = null_context_vec
        self.null_treatment_vec = null_treatment_vec
        self.null_rewards = null_rewards

        # use median heuristic for the bandwidth parameters
        self.null_context_param = (0.5 * self.kernel_param) / np.median(pdist(null_context_vec, 'sqeuclidean'))
        self.null_treatment_param = (0.5 * self.kernel_param) / np.median(pdist(null_treatment_vec, 'sqeuclidean'))

        nullContextMatrix = rbf_kernel(null_context_vec, null_context_vec, self.null_context_param)
        nullTreatmentMatrix = rbf_kernel(null_treatment_vec, null_treatment_vec, self.null_treatment_param)

        self.n = null_context_vec.shape[0]
        A = np.multiply(nullContextMatrix, nullTreatmentMatrix) + np.diag(np.repeat(self.n * self.reg_param, self.n))
        self.A_inv = scipy.linalg.inv(A)

    def estimate(self, target_context_vec, target_treatment_vec):
        """
         Calculate and return a coefficient vector (beta) of the counterfactual mean embedding of reward distribution.
         """

        targetContextMatrix = rbf_kernel(self.null_context_vec, target_context_vec, self.null_context_param)
        targetTreatmentMatrix = rbf_kernel(self.null_treatment_vec, target_treatment_vec, self.null_treatment_param)

        B = np.dot(np.multiply(targetContextMatrix, targetTreatmentMatrix), np.repeat(1.0 / self.n, self.n, axis=0))
        beta_vec = np.matmul(self.A_inv, B)
        target_reward = beta_vec * self.null_rewards

        return target_reward * len(beta_vec)
