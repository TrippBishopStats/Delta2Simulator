from vector import Vector
import numpy as np

class Rocket:
    ### TODO: A rocket is a container class that represents a collection of other objects: stages and a payload ###
    def __init__(self, pos, coeff_drag, cross_sec_area):
        self.stages = [] # a list that represents the stages
        self.srbs = [] # a list of solid rocket boosters
        self.payloads = [] # list of payload objects
        
        if isinstance(coeff_drag, float):
            if coeff_drag > 0.0:
                self.coeff_drag = coeff_drag
            else:
                raise ValueError
        else:
            raise TypeError
             
        if isinstance(cross_sec_area, float):
            if cross_sec_area > 0.0:
                self.cross_sec_area = cross_sec_area
            else:
                raise ValueError
        else:
            raise TypeError
        
        if isinstance(pos, Vector):
            self.pos = pos
        else:
            raise TypeError
        
        self.momentum = Vector(0,0,0)
        self.axis = Vector(0,1,0)
        self.roll_rate = 0
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        str = "Rocket Stats: \n\n"
        str += "Drag Coefficient: {:0.2f}\n".format(self.coeff_drag)
        str += "Cross Sectional Area: {:0.2f} m^2\n".format(self.cross_sec_area)
        
        for stage in self.stages:
            str += stage.__str__() + "\n\n"
        
        for payload in self.payloads:
            str += payload.__str__() + "\n\n"
        
        str += "Total mass: {:0.2f} kg".format(self.total_mass)
        
        return str
    
    def add_stage(self, stage):
        if isinstance(stage, Stage):
            self.stages.append(stage)
        else:
            raise TypeError
        
    def add_payload(self, payload):
        if isinstance(payload, Payload):
            self.payloads.append(payload)
        else:
            raise TypeError
            
    def add_srb(self, srb):
        if isinstance(srb, Stage):
            self.srbs.append(srb)
        else:
            raise TypeError
    
    @property
    def total_mass(self):
        total_mass = 0
        
        for srb in self.srbs:
            total_mass += srb.dry_mass + srb.fuel_mass
            
        for stage in self.stages:
            total_mass += stage.dry_mass + stage.fuel_mass
            
        for payload in self.payloads:
            total_mass += payload.mass
            
        return total_mass
    
    @property
    def active_stage_thrust(self):
        if len(self.stages) > 0:
            stage = self.stages[0]
            return stage.current_thrust*self.axis
        else:
            return Vector(0,0,0)
    
    @property
    def srb_thrust(self):
        if len(self.srbs) > 0:
            total_thrust_mag = 0
            for srb in self.srbs:
                total_thrust_mag += srb.current_thrust
            return total_thrust_mag*self.axis
        else:
            return Vector(0,0,0)
    
    @property    
    def total_thrust(self):
        return self.active_stage_thrust + self.srb_thrust
    
    def update_total_mass(self, time_step):
        if isinstance(time_step, float):
            if time_step > 0.0:
                if len(self.stages) > 0:
                    stage = self.stages[0]
                    stage.update_mass(time_step)

                if len(self.srbs) > 0:
                    for srb in self.srbs:
                        srb.update_mass(time_step)
            else:
                raise ValueError
        else:
            raise TypeError
    
    def separate_active_stage(self):
        ### removes the active stage from the rocket and sets the next stage as the active stage.###
        # first, we have to update momentum so that the velocity doesn't suddenly spike
        velocity = self.momentum/self.total_mass
        self.stages.pop(0)
        self.momentum = self.total_mass*velocity
        
    def separate_srbs(self):
        ### currently, only support a single "stage" of SRBs. All SRBs fire on main ignition and are jettisoned at the same time. ### 
        velocity = self.momentum/self.total_mass
        self.srbs = []
        self.momentum = self.total_mass*velocity
    
    @property
    def attitude(self):
        return np.arccos(self.axis.dot(Vector(0,1,0)))
    
    def set_attitude(self, time_step):
        # compute the angle between the launch vehicle's axis and the vertical axis.
        theta = self.attitude
        # update the angle
        theta += self.roll_rate*time_step
        # now change the angle of the launch vehicle's axis.
        self.axis = (Vector(np.sin(theta), np.cos(theta), 0)).hat()
        
            
    def set_roll_rate(self, roll_rate):
        if isinstance(roll_rate, float):
            self.roll_rate = roll_rate
        else:
            raise TypeError
            
    def adjust_throttle(self, throttle):
        if len(self.stages) > 0:
            if isinstance(throttle, float):
                if throttle >= 0.0 and throttle <= 100.0:
                    stage = self.stages[0]
                    stage.set_throttle(throttle)
                else:
                    raise ValueError
            else:
                raise TypeError
                
    def ignite_srbs(self):
        if len(self.srbs) > 0:
            for srb in self.srbs:
                srb.set_throttle(100.0)
        
class Stage:
    ### 
    ### Stage: this class presents a stage. A stage has a dry mass, a fuel mass, a max thrust, and max fuel burn rate. 
    ### options: {
    ###   dry_mass - float - the unfueled mass of the stage.
    ###    fuel_mass - float - the mass of the fuel + oxidizer carried by the stage
    ###    max_thrust_mag - float - the maximum thrust in newtons.
    ###    max_dmdt - float - the maximum rate at which fuel + oxidizer is consumed in kilograms per second
    ###    length - float - the length of the stage in meters
    ### }
    ###
    def __init__(self, options):
        self.dry_mass = options.get('dry_mass') if 'dry_mass' in options else 0.0
        self.fuel_mass = options.get('fuel_mass') if 'fuel_mass' in options else 0.0
        self.max_thrust_mag = options.get('max_thrust_mag') if 'max_thrust_mag' in options else 0.0
        self.max_dmdt = options.get('max_dmdt') if 'max_dmdt' in options else 0.0
        self.throttle = 0 # percentage of stage's mass thrust produced by the engines
        self.length = options.get('length') if 'length' in options else 0.0
        self.axis = Vector(0,0,0)
        
        # in type check the data
        if isinstance(self.dry_mass, float):
            if self.dry_mass < 0.0:
                raise ValueError
        else:
            raise TypeError
            
        if isinstance(self.fuel_mass, float):
            if self.fuel_mass < 0.0:
                raise ValueError
        else:
            raise TypeError
            
        if isinstance(self.max_thrust_mag, float):
            if self.max_thrust_mag < 0.0:
                raise ValueError
        else:
            raise TypeError
            
        if isinstance(self.max_dmdt, float):
            if self.max_dmdt < 0.0:
                raise ValueError
        else:
            raise TypeError
            
    def __repr__(self):
        return "Stage dry mass is {:0.2f}kg, fuel mass is {:0.2f}kg, max thrust is {:0.2f}N, and max fuel comsumption rate is {:0.2f}kg/s.".format(self.dry_mass, self.fuel_mass, self.max_thrust_mag, self.max_dmdt)
    
    def __str__(self):
        return "Stage dry mass is {:0.2f}kg, fuel mass is {:0.2f}kg, max thrust is {:0.2f}N, and max fuel comsumption rate is {:0.2f}kg/s.".format(self.dry_mass, self.fuel_mass, self.max_thrust_mag, self.max_dmdt)
    
    @property
    def attitude(self):
        return self.axis
    
    @attitude.setter
    def attitude(self, attitude):
        if isinstance(attitude, Vector):
            self.axis = attitude
        else:
            raise TypeError
    
    def set_throttle(self, throttle):
        if isinstance(throttle, float):
            if throttle > 100.0 or throttle < 0.0:
                raise ValueError
            else:
                self.throttle = throttle
        else:
            raise TypeError
            
    @property    
    def current_thrust(self):
        return self.max_thrust_mag*self.throttle/100
    
    @property
    def current_fuel_consumption(self):
        return self.max_dmdt*self.throttle/100
    
    def update_mass(self, time_step):
        self.fuel_mass -= self.max_dmdt*self.throttle/100*time_step
        
class Payload:
    ### The payload simply represents a component of a rocket that doesn't contribute to the locomotion. It is simply "dead weight".###
    def __init__(self, mass, length):
        if isinstance(mass, float):
            if mass > 0.0:
                self.mass = mass
            else:
                raise ValueError
        else:
            raise TypeError
            
    def __repr__(self):
        return "Payload mass is {:0.2f}kg.".format(self.mass)
    
    def __str__(self):
        return "Payload mass is {:0.2f}kg.".format(self.mass)
    

class Error(Exception):
   """Base class for other exceptions"""
   pass    
    
class NoFlightPlanError(Error):
    pass