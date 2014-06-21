# based on epuck.py

import time
import math

class Md25():

    def __init__(self, fake=False):
        """
        call Robot __init__ and set up own instance vars 
        """
        self.wheel_spacing=21.2		# cm  taken down .2
        self.wheel_circumference=32.55	# cm	
        self.wheel_counts_per_rev = 360.0	# 
        self.cm_per_tick = (self.wheel_circumference/self.wheel_counts_per_rev)
        self.full_circle =  self.wheel_counts_per_rev*((self.wheel_spacing*math.pi)/self.wheel_circumference)

        self.robotinfo = {'robot': ['md25'],
                          'robot-version': ['0.2'],
                          }
        self.sensor = {"ir": [1,2],
                       "sonar": [10,20,30,40],
                       "bump": [False,False],
                       "cliff": [False,False] ,
                       "battery": [13.0],
                       "pose": [0.0, 0.0, 0.0],
                       'compass':[0.25],
                       "count":[0,0],
                       "motion":[0.0,0.0],
                       "time":[0.0],
                       "camera":[None, None, None, None],
                       }
        self.config = { "ir": 2, 
                        "sonar":4, 
                        "bump":2, 
                        "cliff":2, 
                        "battery":1, 
                        "compass":1, 
                        "pose":3, 
                        "count":2, 
                        "time":1, 
                        "camera":4, 
                        "motion":2, 
                        }
        self.i2c = None
        self.wii = None
        self.sonar = None
        self.bumpers = None

        self.name = "md25"              # robot name
        self.version = "0.5"            # version number    
        self.startTime = time.time()    # mission time

        self.lastUpdate = time.time()   # time (s since epoch) of last update - used to move simulated robot.
        self.tranSpeed = 200            # Translational speed of simulated robot at 1.0 forward. clicks/s.
        self.rotSpeed = 200             # Rotational simulated robot at 1.0 rot. clicks/s.
        self.SonarMap = None

        self.reset()

    def reset(self):
        """
        reset robot. zero location.
        """
        self._lastTranslate = 0
        self._lastRotate = 0
        self.last_encoder1 = 0
        self.last_encoder2 = 0
        self.encoder1 = 0
        self.encoder2 = 0
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

    def position_update(self):       # calculate new X, Y, Theta 
        left_ticks   = self.encoder1 - self.last_encoder1
        right_ticks  = self.encoder2 - self.last_encoder2
        self.last_encoder1 = self.encoder1
        self.last_encoder2 = self.encoder2
        
        dist_left   = float(left_ticks) * self.cm_per_tick;
        dist_right  = float(right_ticks) * self.cm_per_tick;
        cos_current = math.cos(self.theta);
        sin_current = math.sin(self.theta);
        right_minus_left = float(dist_right-dist_left);
             
        if (left_ticks == right_ticks):            # Moving in a straight line 
            self.x += dist_left*cos_current
            self.y += dist_left*sin_current
        else:                                      # Moving in an arc 
            expr1 = self.wheel_spacing * float(dist_right + dist_left) / 2.0 / float(dist_right - dist_left);
            right_minus_left = dist_right - dist_left
            self.x     += expr1 * (math.sin(right_minus_left/self.wheel_spacing + self.theta) - sin_current)
            self.y     -= expr1 * (math.cos(right_minus_left/self.wheel_spacing + self.theta) - cos_current)
            self.theta += right_minus_left / self.wheel_spacing
            
        if (self.theta<0.0):     
            self.theta = (2*math.pi)+self.theta
        if (self.theta>=(2*math.pi)):
            self.theta = self.theta-(2*math.pi)

# MOVEMENT functions =============================================================================

    ''' MOVEMENT
        all use self._adjustSpeed(translate,rotate), substituting last translate/rotate if not supplied.
        will also pause for a number of seconds and call an all-stop, if 'seconds' arg defined.
        translation and rotation are >=-1.0, <=1.0
        '''

    def move(self, translate, rotate):
        self._adjustSpeed(translate, rotate)

    def stop(self):
        self._adjustSpeed(0, 0)

    def _adjustSpeed(self, translate, rotate):
        self._lastTranslate = translate
        self._lastRotate = rotate

# GET SENSOR DATA =============================================================================

    def getTranslate(self):
        return self._lastTranslate

    def getRotate(self):
        return self._lastRotate

    def get(self, sensor, update):
        '''
        get('all') - return all sensors, all positions
        get('config') - return list of sensors, and their number
        get('name') - return name of robot
        '''
        if update:
	    self.update()

        sensor = sensor.lower()                 
        if sensor == "config":                  # return number and types of sensors
            return self.config
        elif sensor == "name":                  # robot name
            return self.name
        elif sensor == "all":           # 'all' returns all sensors, all positions
            return self.sensor

    def update(self):
        secondsPassed = time.time()-self.lastUpdate         # time in secs since last update
        self.lastUpdate = time.time()
        self.encoder1 += self.tranSpeed*secondsPassed*self.getTranslate()
        self.encoder2 += self.tranSpeed*secondsPassed*self.getTranslate()
        self.encoder1 += self.rotSpeed*secondsPassed*self.getRotate()
        self.encoder2 -= self.rotSpeed*secondsPassed*self.getRotate()

        if self.encoder1>((1<<31)-1): self.encoder1-=(1<<32)
        if self.encoder2>((1<<31)-1): self.encoder2-=(1<<32)
        volts  = self.sensor['battery'][0]-0.0000001
        compass= 0.0
        self.position_update()

        self.sensor['bump']   = [False, True]
        self.sensor['cliff']  = [True, False]
        self.sensor['ir']     = [0, 0]
        self.sensor['sonar']  = [ math.sin(self.lastUpdate/2)*100+150,
                                  math.cos(self.lastUpdate/4)*050+100,  
                                  math.sin(self.lastUpdate/6)*100+200,  
                                  math.cos(self.lastUpdate/3)*100+150,  ]

        #self.sensor['camera'] = self.wii.data
        self.sensor['count']  = [self.encoder1, self.encoder2]
        self.sensor['battery']= [volts]
        self.sensor['battery']= [math.sin(self.lastUpdate/10)*3.0+9.0]
        self.sensor['compass']= [compass]
        angle = self.theta
        if angle>math.pi:
            angle = 0.0-((2*math.pi)-angle)
        self.sensor['pose']   = [self.x, self.y, angle]
        self.sensor['compass']= [angle]

        self.sensor['motion'] = [self.getTranslate(), self.getRotate()]
        self.sensor['time']   = [int(1000*(time.time()-self.startTime))/1000.0]
