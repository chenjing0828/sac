import numpy as np
from rllab.envs.mujoco.humanoid_env import HumanoidEnv
from rllab.misc.overrides import overrides
from rllab.envs.base import Step
from rllab.misc import logger

from .helpers import get_multi_direction_logs

class MultiDirectionHumanoidEnv(HumanoidEnv):
    @overrides
    def step(self, action):
        self.forward_dynamics(action)
        next_obs = self.get_current_obs()

        alive_bonus = self.alive_bonus
        data = self.model.data

        comvel = self.get_body_comvel("torso")

        velocity_reward = np.linalg.norm(comvel[:2])
        lb, ub = self.action_bounds
        scaling = (ub - lb) * 0.5
        ctrl_cost = .5 * self.ctrl_cost_coeff * np.sum(
            np.square(action / scaling))
        impact_cost = .5 * self.impact_cost_coeff * np.sum(
            np.square(np.clip(data.cfrc_ext, -1, 1)))
        vel_deviation_cost = 0.5 * self.vel_deviation_cost_coeff * np.sum(
            np.square(comvel[2:]))
        reward = velocity_reward + alive_bonus - ctrl_cost - \
            impact_cost - vel_deviation_cost
        done = data.qpos[2] < 0.8 or data.qpos[2] > 2.0

        return Step(next_obs, reward, done)

    @overrides
    def log_diagnostics(self, paths, *args, **kwargs):
        logs = get_multi_direction_logs(paths)
        for row in logs:
            logger.record_tabular(*row)