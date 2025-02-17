import numpy as np
import sympy as sp
import math
from scipy.optimize import fsolve
q=[np.radians(90),0,0,0]
q=[-1.1699, np.radians(39.6),np.radians(-81.7),np.radians(42)]
L1, L2, L3, L4 = 0.14, 0.13, 0.12, 0.1  
q1, q2, q3,q4 = sp.symbols('q1 q2 q3 q4')
vx, vy, vz = sp.symbols('vx vy vz')
time = [10.0,0.1]
prevZ = 0
def sysCall_init():
    sim = require('sim')
    self.target_position = -90 * (3.14159/180)
    self.required_duration = 5
    position1=sim.getObject("../1")
    position2=sim.getObject("../2")
    self.position3=sim.getObject("../3")
    position4=sim.getObject("../4")
    position5=sim.getObject("../5")
    EEHandle=sim.getObject("../Grip_respondable")
    distance21=sim.getObjectPosition(position2,position1)
    distance32=sim.getObjectPosition(self.position3,position2)
    distance43=sim.getObjectPosition(position4,self.position3)
    distance54=sim.getObjectPosition(EEHandle,position4)
    BaseHandle=sim.getObject("../base_link_visual")
    EEPosition=sim.getObjectPosition(EEHandle,BaseHandle)
    forwardPosition = forward_kinematics_func()
    print("Forward Position: ")
    print(forwardPosition)
    q_dot = [0.1, 0.2, 0.3, 0.4]  
    J = jacobian_matrix()
    V_F = forward_velocity_kinematics(q, q_dot)
    v_desired = [vx, vy, vz]
    q_dot_numeric = inverse_kinematics_velocity1(v_desired, q)


def sysCall_actuation():
    curr_time = sim.getSimulationTime()
    EEHandle=sim.getObject("../Grip_respondable")
    init_pos= sim.getObjectPosition(EEHandle,sim.handle_world)
    final_Obj =sim.getObject("../../softBody")
    final_pos= sim.getObjectPosition(final_Obj,sim.handle_world)
    position1=sim.getObject("../1")
    position2=sim.getObject("../2")
    position3=sim.getObject("../3")
    position4=sim.getObject("../4")
    if time[1] < time[0]:
        traj1 = task_traj_ellipse(init_pos, final_pos,time[0],time[1])
        IPK = inverse_kinematics_trig(traj1[0],traj1[1],traj1[2])
        print(IPK)
        sim.setJointTargetPosition(position1,IPK[0]*time[1]/time[0])
        sim.setJointTargetPosition(position3,-IPK[2]*time[1]/time[0])
        sim.setJointTargetPosition(position4,IPK[3]*time[1]/time[0])
        time[1]+=0.1
        distance_threshold = 0.12 
        distance = np.linalg.norm(np.array(init_pos) - np.array(final_pos))

        if distance < distance_threshold:
            relative_position = sim.getObjectPosition(final_Obj, EEHandle)
            sim.setObjectParent(final_Obj, EEHandle)
            sim.setObjectPosition(final_Obj, EEHandle, relative_position)
            print("Box gripped successfully.")
    else:
        time_threshold = 20 
        placing_start_time = sim.getSimulationTime()
        EEHandle1=sim.getObject("../Grip_respondable")
        init_pos1= sim.getObjectPosition(EEHandle,sim.handle_world)
        Table= sim.getObject("../../Basket")
        #final_pos1= sim.getObjectPosition(Table,sim.handle_world)
        final_pos1 = (-1.250,1.90001, 1.100)
        traj1 = task_traj(init_pos1, final_pos1,time[0],time[1])
        IPK = inverse_kinematics_trig(traj1[0],traj1[1],traj1[2])
        print(IPK)
        sim.setJointTargetPosition(position1,IPK[0]*time[1]/time_threshold)
        sim.setJointTargetPosition(position3,-IPK[2]*time[1]/time_threshold)
        sim.setJointTargetPosition(position4,IPK[3]*time[1]/time_threshold)
        time[1]+=0.1
        current_time = sim.getSimulationTime()
        EE_pos = sim.getObjectPosition(EEHandle, sim.handle_world)
        distance_to_goal = np.linalg.norm(np.array(init_pos1) - np.array(final_pos1)) 
 
        print(f"Current Time: {current_time}, Placing Start Time: {placing_start_time}")
        print(f"EE Position: {EE_pos}, Distance to Goal: {distance_to_goal}")

        position_threshold = 0.25
        if current_time >= time_threshold and distance_to_goal < position_threshold:
            sim.setObjectParent(final_Obj, -1)  
            print("Box placed successfully on the table.")
            state = "done"
            sim.stopSimulation()
   
    pass

def sysCall_sensing():
    
    pass

def sysCall_cleanup():
   
    q[1]=90
    forward_kinematics_func()
    pass


def transformation_func(q,d,a,adg):
    return np.array([[np.cos(q),-np.sin(q)*np.cos(adg),np.sin(q)*np.sin(adg),a*np.cos(q)],
    [np.sin(q),np.cos(q)*np.cos(adg),-np.cos(q)*np.sin(adg),a*np.sin(q)],
    [0,np.sin(adg),np.cos(adg),d],
    [0,0,0,1]])
    
def forward_kinematics_func():
    position1=sim.getObject("../1")
    position2=sim.getObject("../2")
    position3=sim.getObject("../3")
    position4=sim.getObject("../4")
    position5=sim.getObject("../5")
    distance21=sim.getObjectPosition(position2,position1)
    distance32=sim.getObjectPosition(position3,position2)
    distance43=sim.getObjectPosition(position4,position3)
    distance54=sim.getObjectPosition(position5,position4)
    t1=transformation_func(q[0],distance21[2],0,np.pi/2)
    t2=transformation_func(q[1],0,distance32[0],0)
    t3=transformation_func(q[2],0,-distance43[0],0)
    t4=transformation_func(q[3],0,distance54[0],0)
    tTotal= np.eye(4)
    tTotal=np.dot(tTotal, t1)
    tTotal=np.dot(tTotal, t2)
    tTotal=np.dot(tTotal, t3)
    tTotal=np.dot(tTotal, t4)
    return(tTotal[0][3],tTotal[1][3],tTotal[2][3])

target=[0.0,0.0]
def forward_kinematics_func_symoblic():

    X = L1 * sp.cos(q1) + L2 * sp.cos(q1 + q2) + L3 * sp.cos(q1 + q2 + q3) + L4 * sp.cos(q1 + q2 + q3 + q4)
    Y = L1 * sp.sin(q1) + L2 * sp.sin(q1 + q2) + L3 * sp.sin(q1 + q2 + q3) + L4 * sp.sin(q1 + q2 + q3 + q4)
    Z = 0 
    return X, Y, Z
def inverse_position_kinematics(X, Y, Z):
    q1=np.arctan(Y/X)

    initial_guess = [0.0, 0.0, 0.0]
    target[0] = X*2+Y*2 
    target[1] = Z  
    solution = fsolve(equations, initial_guess)

    theta1, theta2, theta3 = solution
    return [q1,theta1, theta2, theta3]

def equations(angles):
    theta1, theta2, theta3 = angles
   
    x = L1 * np.cos(theta1) + L2 * np.cos(theta1 + theta2) + L3 * np.cos(theta1 + theta2 + theta3)
    y = L1 * np.sin(theta1) + L2 * np.sin(theta1 + theta2) + L3 * np.sin(theta1 + theta2 + theta3)
    
    return [x - target[0], y - target[1], theta1 + theta2 + theta3] 

def jacobian_matrix():
    
    X, Y, Z = forward_kinematics_func_symoblic()
    

    J11 = sp.diff(X, q1)
    J12 = sp.diff(X, q2)
    J13 = sp.diff(X, q3)
    J14 = sp.diff(X, q4)
    J21 = sp.diff(Y, q1)
    J22 = sp.diff(Y, q2)
    J23 = sp.diff(Y, q3)
    J24 = sp.diff(Y, q4)
    J31 = sp.diff(Z, q1)
    J32 = sp.diff(Z, q2)
    J33 = sp.diff(Z, q3)
    J34 = sp.diff(Z, q4)

    J = sp.Matrix([
        [J11, J12, J13, J14],
        [J21, J22, J23, J24],
        [J31, J32, J33, J34]
    ])
    
    return J
    
def forward_velocity_kinematics(q, q_dot):
    
    J = jacobian_matrix()
    
    J_num = J.subs({q1: q[0], q2: q[1], q3: q[2], q4: q[3]})
    
    J_np = np.array(J_num).astype(np.float64)
    
    V_F = J_np @ np.array(q_dot)
    return V_F
    
def inverse_kinematics_velocity(v_desired):
    
    J = jacobian_matrix()
    
    
    if J.shape[0] == J.shape[1]: 
        J_inv = J.inv()
    else:  
        J_inv = J.pinv()
    
   
    v = sp.Matrix(v_desired)
    
    
    q_dot = J_inv * v
    
    return q_dot

def inverse_kinematics_velocity1(v_desired, q):
    J = jacobian_matrix()
    J_func = sp.lambdify((q1, q2, q3, q4), J) 
    J_num = np.array(J_func(q[0], q[1], q[2], q[3]))

    try:
        J_inv = np.linalg.pinv(J_num)  
    except np.linalg.LinAlgError:
        raise ValueError("Jacobian is singular or ill-conditioned.")

    q_dot = J_inv @ v_desired
    return q_dot


def task_traj(X0,Xf,Tf,Ts):
    slopeX = (Xf[0]-X0[0])/Tf
    slopeY = (Xf[1]-X0[1])/Tf
    slopeZ = (Xf[2]-X0[2])/Tf
    pX = X0[0] + (slopeX*Ts)
    pY = X0[1] + (slopeY*Ts)
    pZ = X0[2] + (slopeZ*Ts)
    return [pX,pY,pZ]
    
def task_traj_ellipse(X0, Xf, Tf, Ts):
   
    a = (Xf[0] - X0[0]) / 2  
    b = (Xf[1] - X0[1]) / 2  
    centerX = (X0[0] + Xf[0]) / 2
    centerY = (X0[1] + Xf[1]) / 2
    centerZ = (X0[2] + Xf[2]) / 2
    omega = 2 * np.pi / Tf  
    theta = omega * Ts
    pX = centerX + a * np.cos(theta)
    pY = centerY + b * np.sin(theta)
    slopeZ = (Xf[2] - X0[2]) / Tf
    pZ = X0[2] + slopeZ * Ts
    
    return [pX, pY, pZ]

def inverse_kinematics_trig(X, Y, Z):
    
    theta1=np.arctan(Y/X)
    position1=sim.getObject("../1")
    position2=sim.getObject("../2")
    position3=sim.getObject("../3")
    position4=sim.getObject("../4")
    EEHandle=sim.getObject("../Grip_respondable")
    distance21=sim.getObjectPosition(position2,position1)
    distance32=sim.getObjectPosition(self.position3,position2)
    distance43=sim.getObjectPosition(position4,self.position3)
    distance54=sim.getObjectPosition(EEHandle,position4)
    L1=math.sqrt(distance21[0]*2+distance21[2]*2)
    L2=math.sqrt(distance32[0]*2+distance32[2]*2)
    L3=math.sqrt(distance43[0]*2+distance43[2]*2)
    L4=math.sqrt(distance54[0]*2+distance54[2]*2)
    d = math.sqrt(X*2 + Y*2)
    cos_theta2 = (L1*2 + L22 - d*2) / (2 * L1 * L2)
    print(cos_theta2)
    cos_theta2 = np.clip(cos_theta2, -1, 1)  
    theta2 = np.arccos(cos_theta2)
    alpha = math.atan2(L2 * math.sin(theta2), L1 + L2 * math.cos(theta2))
    if X == 0 and Z == 0:
        theta3 = 0  
    else:
        theta3 = math.atan2(Z, X) - alpha
    theta4 =   np.pi/2 - (theta1 + theta2 + theta3)  

    return [
         (theta1),
         (theta2),
         (theta3),
         (theta4)
    ]
