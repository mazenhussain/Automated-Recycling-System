ip_address = 'localhost' # Enter your IP Address here
project_identifier = 'P3B' # Enter the project identifier i.e. P2A or P2B

# SERVO TABLE CONFIGURATION
short_tower_angle = 315 # enter the value in degrees for the identification tower 
tall_tower_angle = 90 # enter the value in degrees for the classification tower
drop_tube_angle = 180 # enter the value in degrees for the drop tube. clockwise rotation from zero degrees

# BIN CONFIGURATION
# Configuration for the colors for the bins and the lines leading to those bins.
# Note: The line leading up to the bin will be the same color as the bin 

bin1_offset = 0.15 # offset in meters
bin1_color = [1,0,0] # e.g. [1,0,0] for red
bin1_metallic = False

bin2_offset = 0.15
bin2_color = [0,1,0]
bin2_metallic = False

bin3_offset = 0.15
bin3_color = [0,0,1]
bin3_metallic = False

bin4_offset = 0.15
bin4_color = [1,0,1]
bin4_metallic = False
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
if project_identifier == 'P3A':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    configuration_information = [table_configuration, None] # Configuring just the table
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
else:
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    bin_configuration = [[bin1_offset,bin2_offset,bin3_offset,bin4_offset],[bin1_color,bin2_color,bin3_color,bin4_color],[bin1_metallic,bin2_metallic, bin3_metallic,bin4_metallic]]
    configuration_information = [table_configuration, bin_configuration]
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    bot = qbot(0.1,ip_address,QLabs,project_identifier,hardware)
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------
#import libraries and set a lock variable
#lock variable ensures part of code only runs once
import random
global lock
lock = False

#Function that dispenses container and returns container data
def dispense_container(num):
    return table.dispense_container(num, True)
    
#Function that loads containers on to the qbot
def load_container(destination_index,mass,target_bin):
    #Create placeholder variables and set lock to global
    mass_total = 0
    destination = ''
    i = 0
    global lock
    
        
    #Begin while loop that will cycle through new containers
    while True:
        if lock == False:
        
            #Determine 1 of 6 types of container
            container = random.randint(1,6)
            material, mass, destination_index = dispense_container(container)
            print(destination_index)


            #Determine if bottle is appropriate to pick up
            #If so, set destination and turn on the lock
            if target_bin == '':
                target_bin = destination_index
            else:
                if target_bin != destination_index:
                    break
                
            if mass_total + mass > 90:
                break

            if i > 2:
                break
            destination = destination_index
            lock = True

        
        mass_total =+ mass
        
        #Q-arm loading Process
        time.sleep(2)
        arm.move_arm(0.655, 0.0, 0.272)
        time.sleep(1)
        arm.control_gripper(34)
        time.sleep(3)
        arm.rotate_shoulder(-5)
        time.sleep(1)
        arm.rotate_base(-45)
        time.sleep(1)
        arm.move_arm(0.287, -0.287, 0.483)
        time.sleep(1)
        arm.rotate_elbow(-80)
        time.sleep(1)
        arm.rotate_base(-45)
        time.sleep(1)
        if i == 0:
            arm.move_arm(0.021, -0.572, 0.540)
        elif i == 1:
            arm.move_arm(0.021, -0.524, 0.518)
        elif i == 2:
            arm.move_arm(0.021, -0.436, 0.503)
        time.sleep(2)
        arm.control_gripper(-15)
        time.sleep(2)
        arm.rotate_shoulder(-15)
        arm.home()
        time.sleep(3)

        i += 1

        #Determine a random container from 1-6
        container = random.randint(1,6)
        material, mass, destination_index = dispense_container(container)
        print(destination_index)


        #Determine if container is appropriate to pick up
        if target_bin == '':
            target_bin = destination_index
        else:
            if target_bin != destination_index:
                destination_index,target_bin = target_bin,destination_index
                break
                
        if mass_total + mass > 90:
            break

        if i > 2:
            break
    
    #Return the target destination
    if destination == '':
        destination = destination_index
    return destination, mass,target_bin

#Function that delivers containers to the correct bin
def transfer_container(destination):
    
    bot.activate_line_following_sensor()
    bot.activate_color_sensor()

    #Determine position adjustments based on the container destination
    if destination == "Bin01":
        desired_r,desired_g,desired_b = 1,0,0
        target = 1.087
    elif destination == "Bin02":
        desired_r,desired_g,desired_b = 0,1,0
        target = 0.597
    elif destination == "Bin03":
        desired_r,desired_g,desired_b = 0,0,1
        target = 0.597
    elif destination == "Bin04":
        desired_r,desired_g,desired_b = 1,0,1
        target = 1.031
        

    #Line following algorithm
    while True:
        x,y,z =  bot.position()
        x = round(x,2)
        y = round(y,2)
        
       
        left_sensor,right_sensor = bot.line_following_sensors()
        
        if left_sensor == 1 and right_sensor == 1:
            print("forward")
            bot.set_wheel_speed([0.1,0.1])

        elif left_sensor == 1 and right_sensor == 0:
            print("left")
            bot.set_wheel_speed([0,0.01])
            
        elif left_sensor == 0 and right_sensor == 1:
            print("right")
            bot.set_wheel_speed([0.01,0])

        
        #Read current position and sensor readings
        r, g, b = bot.read_color_sensor()[0]
        print(r,g,b)

        x,y,z =  bot.position()
        x = round(x,2)
        y = round(y,2)

        #Stop once at the correct bin and make a orientational adjustment
        if destination == "Bin01" or destination  == "Bin02":
            if r == desired_r and g == desired_g and b == desired_b:
               if x <= target:
                   bot.stop()
                   bot.rotate(-10)
                   break
        elif destination == "Bin03" or destination == "Bin04":
            if r == desired_r and g == desired_g and b == desired_b:
               if target <= x:
                   bot.stop()
                   bot.rotate(-7)
                   break

         
    bot.deactivate_color_sensor()
    bot.deactivate_line_following_sensor()

#Function for dumping containers
def deposit_container():
    #Movement flow for hopper
    bot.activate_linear_actuator()
    time.sleep(2)
    bot.rotate_hopper(30)
    time.sleep(0.3)
    bot.rotate_hopper(60)
    time.sleep(0.3)
    bot.rotate_hopper(90)
    time.sleep(0.3)
    bot.rotate_hopper(0)
    bot.deactivate_linear_actuator()
    time.sleep(2)


#Function for returning to original position
def return_home():
    #Activate sensors
    bot.activate_line_following_sensor()
    bot.activate_color_sensor()

    #While loop for navigating line
    while True:
        x,y,z =  bot.position()
        x = round(x,2)
        y = round(y,2)

        left_sensor,right_sensor = bot.line_following_sensors()
        if left_sensor == 1 and right_sensor == 1:
            print("forward")
            bot.set_wheel_speed([0.1,0.1])

        elif left_sensor == 1 and right_sensor == 0:
            print("left")
            bot.set_wheel_speed([0,0.02])
            
        elif left_sensor == 0 and right_sensor == 1:
            print("right")
            bot.set_wheel_speed([0.02,0])
            
        #Stop once at correct position
        if x >= 1.3 and y >= 0:
            bot.stop()
            break
            

    #Deactivate sensors
    bot.deactivate_color_sensor()
    bot.deactivate_line_following_sensor()

#Main program
def main():
    #set vplaceholder variables
    last_mass = 0
    container_destination = ''
    next_destination = ''
    #Begin work flow cycle
    while True:
        container_destination,last_mass, next_destination = load_container(container_destination,last_mass,next_destination)
        transfer_container(container_destination)
        deposit_container()
        return_home()


main()




#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
    

    

