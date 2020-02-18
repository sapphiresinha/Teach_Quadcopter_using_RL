import numpy as np
from physics_sim import PhysicsSim

class Task():
    """Task (environment) that defines the goal and provides feedback to the agent."""
    def __init__(self, init_pose=None, init_velocities=None, 
        init_angle_velocities=None, runtime=5., target_pos=None):
        """Initialize a Task object.
        Params
        ======
            init_pose: initial position of the quadcopter in (x,y,z) dimensions and the Euler angles
            init_velocities: initial velocity of the quadcopter in (x,y,z) dimensions
            init_angle_velocities: initial radians/second for each of the three Euler angles
            runtime: time limit for each episode
            target_pos: target/goal (x,y,z) position for the agent
        """
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 
        self.action_repeat = 3

        self.state_size = self.action_repeat * 6
        self.action_low = 0
        self.action_high = 900
        self.action_size = 4

        # Goal
        self.target_pos = target_pos if target_pos is not None else np.array([0., 0., 10.]) 

    def get_reward(self):
        """Uses current pose of sim to return reward."""
        reward = 1.-.001*(abs(self.sim.pose[:3] - self.target_pos)).sum()
        
        if (abs(self.sim.pose[0] - self.target_pos[0])) < 0.25:
            reward += 0.05
        if (abs(self.sim.pose[1] - self.target_pos[1])) < 0.25:
            reward += 0.05
        if (abs(self.sim.pose[2] - self.target_pos[2])) < 0.25:
            reward += 0.05
        
        if self.sim.time < self.sim.runtime and self.sim.done == True:
            reward -= 10

        #reward = 1
        #penalty = 0
        #current_position = self.sim.pose[:3]
        #distance = np.sqrt(((current_position - self.target_pos)**2).sum())
        
        # penalty for euler angles to avoid unecessary rotations
        #penalty += abs(self.sim.pose[3:6]).sum()
        
        #penalty for being distant from the target coordinates
        #penalty += .003*(abs(self.sim.pose[:3] - self.target_pos)).sum()
        
        #penalty for increasing total distance to the target
        #penalty += distance**2
        
        return reward

    def step(self, rotor_speeds):
        """Uses action to obtain next state, reward, done."""
        reward = 0
        pose_all = []
        for _ in range(self.action_repeat):
            done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities
            reward += self.get_reward() 
            pose_all.append(self.sim.pose)
        next_state = np.concatenate(pose_all)
        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = np.concatenate([self.sim.pose] * self.action_repeat) 
        return state