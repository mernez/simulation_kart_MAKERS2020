import socket
import sys
import time
from threading import *
import pybullet as p
import pybullet_data

HOST = '127.0.0.1'  # Symbolic name meaning all available interfaces
PORT = int(sys.argv[1])  # Arbitrary non-privileged port

physicsServer = -1

####################################
#############Joint IDs##############
base_link_joint=0
chassis_inertia_joint=1
left_rear_wheel_joint=2
right_rear_wheel_joint=3
left_steering_hinge_joint=4
left_front_wheel_joint=5
right_steering_hinge_joint=6
right_front_wheel_joint=7
hokuyo_joint=8
zed_camera=9
zed_camera_left=10
zed_camera_right=11

####################################
#############Globals################
target = 500
maxForce = 1
maxAngle = 7

wheels = [right_rear_wheel_joint, left_rear_wheel_joint]
steering = [right_steering_hinge_joint, left_steering_hinge_joint]

left_steering_wheel_angle=0
right_steering_wheel_angle=0
applied_force=0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print('Socket bind complete')

# Start listening on socket
s.listen(10)
print('Socket now listening')

# Function for handling connections. This will be used to create threads


def handle_reply(reply):
    """
    Returns either (Boolean,Int) or (Boolean,Int,Int)
    In the first case the Boolean is false and Int is the applied velocity to the rear wheels
    In the first case the Boolean is True and the next two Ints represent respectively the left and right front wheel angles
    If Boolean is False and Int is -1 then the reply couldn't be parsed
    """
    global left_steering_wheel_angle
    global right_steering_wheel_angle
    global applied_force
    if(reply[0] == "z" or reply[0] == "Z"):
        if(applied_force < maxForce):
            applied_force=applied_force+(maxForce/100)
        else:
            applied_force=maxForce
        for k in range(0,2):
            print(k)
            p.setJointMotorControl2(bodyUniqueId=boxId,
                                    jointIndex=wheels[k],
                                    controlMode=p.VELOCITY_CONTROL,
                                    targetVelocity=target,
                                    force=applied_force)
        p.stepSimulation()
        print("Force:",applied_force)
        return (False,applied_force)
    elif(reply[0] == "s" or reply[0] == "s"):
        if(applied_force > -maxForce):
            applied_force=applied_force-(maxForce/100)
        else:
            applied_force=-maxForce
        for k in range(0,2):
            p.setJointMotorControl2(bodyUniqueId=boxId,
                                    jointIndex=wheels[k],
                                    controlMode=p.VELOCITY_CONTROL,
                                    targetVelocity=target,
                                    force=applied_force)
        p.stepSimulation()
        print("Force:",applied_force)
        return (False,applied_force)
    elif(reply[0] == "q" or reply[0] == "Q"):
        if(left_steering_wheel_angle < maxAngle):
            left_steering_wheel_angle=left_steering_wheel_angle+maxAngle/10
        else:
            left_steering_wheel_angle=maxAngle
        if(right_steering_wheel_angle < maxAngle):
            right_steering_wheel_angle=right_steering_wheel_angle+maxAngle/10
        else:
            right_steering_wheel_angle=maxAngle
        p.setJointMotorControl2(bodyUniqueId=boxId,
                                    jointIndex=steering[1],
                                    controlMode=p.POSITION_CONTROL,
                                    targetPosition=left_steering_wheel_angle)
        p.setJointMotorControl2(bodyUniqueId=boxId,
                                    jointIndex=steering[0],
                                    controlMode=p.POSITION_CONTROL,
                                    targetPosition=right_steering_wheel_angle)
        p.stepSimulation()
        print("left:",left_steering_wheel_angle,"right:",right_steering_wheel_angle)
        return (True,left_steering_wheel_angle,right_steering_wheel_angle)
    elif(reply[0] == "d" or reply[0] == "D"):
        if(right_steering_wheel_angle > -maxAngle):
            right_steering_wheel_angle=right_steering_wheel_angle-maxAngle/10
        else:
            right_steering_wheel_angle=-maxAngle
        if(left_steering_wheel_angle > -maxAngle):
            left_steering_wheel_angle=left_steering_wheel_angle-maxAngle/10
        else:
            left_steering_wheel_angle=-maxAngle
        p.setJointMotorControl2(bodyUniqueId=boxId,
                                    jointIndex=steering[1],
                                    controlMode=p.POSITION_CONTROL,
                                    targetPosition=left_steering_wheel_angle)
        p.setJointMotorControl2(bodyUniqueId=boxId,
                                    jointIndex=steering[0],
                                    controlMode=p.POSITION_CONTROL,
                                    targetPosition=right_steering_wheel_angle)
        p.stepSimulation()
        print("left:",left_steering_wheel_angle,"right:",right_steering_wheel_angle)
        return (True,left_steering_wheel_angle,right_steering_wheel_angle)
    return (False,-1)

def clientthread(conn):
    # infinite loop so that function do not terminate and thread do not end.
    while True:
        # Receiving from client
        data = conn.recv(10)
        reply = data.decode()
        if reply:
            res=handle_reply(reply)
            if(res[0]):
                reply="(left:{}°,right:{}°)\n".format(res[1],res[2])
            else:
                if(res[1]>=0):
                    reply="(Force:{})\n".format(res[1])
                else:
                    reply="ERR\n"
        elif reply=="\n" or not reply:
            reply="ERR\n"
        p.stepSimulation()
        conn.sendall("ok\n".encode())
        p.stepSimulation()
    # came out of loop
    conn.close()


# now keep talking with the client
while 1:
    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))
    # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    if(physicsServer != 1):
        physicsServer = 1
        print("Creating physics server...\n")
        p.connect(p.GUI)
        p.setGravity(0,0,-10)
        planeId = p.loadURDF("./plane.urdf")
        cubeStartPos = [0, 0, 0]
        cubeStartOrientation = p.getQuaternionFromEuler([0, 0, 0])
        boxId = p.loadURDF("./f10_racecar/racecar.urdf",
                           cubeStartPos, cubeStartOrientation)  # Body unique ID
    x = Thread(target=clientthread, args=(conn,))
    x.start()
    while(1):
        p.stepSimulation()
    print("here\n");

s.close()
