#!/usr/bin/env python3

import torch
from ..lazy import DiagLazyTensor
from ..distributions import Delta
from ._variational_distribution import _VariationalDistribution


class DeltaVariationalDistribution(_VariationalDistribution):
    """
    This :obj:`~gpytorch.variational._VariationalDistribution` object replaces a variational distribution
    with a single particle. It is equivalent to doing MAP inference.

    Args:
        :attr:`num_inducing_points` (int):
            Size of the variational distribution. This implies that the variational mean
            should be this size, and the variational covariance matrix should have this many rows and columns.
        :attr:`batch_shape` (torch.Size, optional):
            Specifies an optional batch size for the variational parameters. This is useful for example
            when doing additive variational inference.
        :attr:`mean_init_std` (float, default=1e-3):
            Standard deviation of gaussian noise to add to the mean initialization
    """
    def __init__(self, num_inducing_points, batch_shape=torch.Size([]), mean_init_std=1e-3, **kwargs):
        super().__init__(num_inducing_points=num_inducing_points, batch_shape=batch_shape)
        mean_init = torch.zeros(num_inducing_points)
        mean_init = mean_init.repeat(*batch_shape, 1)
        self.mean_init_std = mean_init_std
        self.register_parameter(name="variational_mean", parameter=torch.nn.Parameter(mean_init))

    def forward(self):
        return Delta(self.variational_mean)

    def initialize_variational_distribution(self, prior_dist):
        self.variational_mean.data.copy_(prior_dist.mean)
        self.variational_mean.data.add_(self.mean_init_std, torch.randn_like(prior_dist.mean))
