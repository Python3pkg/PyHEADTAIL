'''
Created on 06.01.2014

@author: Kevin Li, Adrian Oeftiger
'''


import numpy as np


from cobra_functions import stats
from numpy.random import RandomState
from scipy.constants import c, e, m_e, m_p
from generators import GaussianX, GaussianY, GaussianZ


# re = 1 / (4 * pi * epsilon_0) * e ** 2 / c ** 2 / m_e
# rp = 1 / (4 * pi * epsilon_0) * e ** 2 / c ** 2 / m_p


class Particles(object):
    """Single bunch with 6D coordinates
    (x, x', y, y', z, \Delta p) where \Delta p = p - p0.
    These translate to
    self.x
    self.xp
    self.y
    self.yp
    self.z
    self.delta_p
    """

    def __init__(self, charge, gamma, intensity, mass, *phase_space_generators):
        """Initialises the bunch and distributes its particles via the
        given PhaseSpace generator instances (minimum 1) for both the
        transverse and longitudinal plane.
        """
        self.charge = charge
        self.gamma = gamma
        self.intensity = intensity
        self.mass = mass

        for phase_space in phase_space_generators:
            phase_space.generate(self)

        self.id = np.arange(1, self.n_macroparticles + 1, dtype=int)

    @classmethod
    def as_gaussian(cls, n_macroparticles, charge, gamma, intensity, mass,
                    alpha_x, beta_x, epsn_x, alpha_y, beta_y, epsn_y,
                    beta_z, epsn_z, is_accepted = None, generator_seed=None):
        """Initialises a Gaussian bunch from the given optics functions.
        For the argument is_accepted cf. generators.Gaussian_Z .
        """
        betagamma = np.sqrt(gamma ** 2 - 1)
        p0 = betagamma * mass * c

        # Generate seeds for GaussianX,Y and Z.
        random_state = RandomState()
        random_state.seed(generator_seed)
        
        gaussianx = GaussianX.from_optics(n_macroparticles, alpha_x, beta_x, epsn_x, betagamma,
                                          generator_seed=random_state.randint(sys.maxint))
        gaussiany = GaussianY.from_optics(n_macroparticles, alpha_y, beta_y, epsn_y, betagamma,
                                          generator_seed=random_state.randint(sys.maxint))
        gaussianz = GaussianZ(n_macroparticles, beta_z, epsn_z, p0, is_accepted,
                              generator_seed=random_state.randint(sys.maxint))

        return cls(charge, gamma, intensity, mass,
                   gaussianx, gaussiany, gaussianz)

    @property
    def n_macroparticles(self):
        return len(self.z)

    @property
    def beta(self):
        return np.sqrt(1 - 1. / self.gamma ** 2)
    @beta.setter
    def beta(self, value):
        self.gamma = 1. / np.sqrt(1 - value ** 2)

    @property
    def betagamma(self):
        return np.sqrt(self.gamma ** 2 - 1)
    @betagamma.setter
    def betagamma(self, value):
        self.gamma = np.sqrt(value ** 2 + 1)

    @property
    def p0(self):
        return self.mass * self.gamma * self.beta * c
    @p0.setter
    def p0(self, value):
        self.gamma = value / (self.mass * self.beta * c)

    @property
    def dp(self):
        return self.delta_p / self.p0
    @dp.setter
    def dp(self, value):
        self.delta_p = value * self.p0

    def sort_particles(self):
        # update the number of lost particles
        self.n_macroparticles_lost = (self.n_macroparticles -
                                      np.count_nonzero(self.id))

        # sort particles according to z (this is needed for correct
        # functioning of bunch.compute_statistics)
        if self.n_macroparticles_lost:
            # place lost particles at the end of the array
            z_argsorted = np.lexsort((self.z, -np.sign(self.id)))
        else:
            z_argsorted = np.argsort(self.z)

        self.x  = self.x.take(z_argsorted)
        self.xp = self.xp.take(z_argsorted)
        self.y  = self.y.take(z_argsorted)
        self.yp = self.yp.take(z_argsorted)
        self.z  = self.z.take(z_argsorted)
        self.dp = self.dp.take(z_argsorted)
        self.id = self.id.take(z_argsorted)

    def compute_statistics(self):
        self.mean_x  = stats.mean(self.x)
        self.mean_xp = stats.mean(self.xp)
        self.mean_y  = stats.mean(self.y)
        self.mean_yp = stats.mean(self.yp)
        self.mean_z  = stats.mean(self.z)
        self.mean_dp = stats.mean(self.dp)

        self.sigma_x  = stats.std(self.x)
        self.sigma_y  = stats.std(self.y)
        self.sigma_z  = stats.std(self.z)
        self.sigma_dp = stats.std(self.dp)

        self.epsn_x = stats.emittance(self.x, self.xp) * self.gamma * self.beta * 1e6
        self.epsn_y = stats.emittance(self.y, self.yp) * self.gamma * self.beta * 1e6
        self.epsn_z = 4 * np.pi * self.sigma_z * self.sigma_dp * self.p0 / self.charge