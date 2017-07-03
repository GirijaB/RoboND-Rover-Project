
Project: Search and Sample Return

The goal of this project was to navigate and map rocks autonomously with the rover in autonomous mode.

My first goal was to make changes in perception code.

In summary, I Defined the source and destination points. Then Took a perspective transform of the input image. Applied 3 different thresholds to extract 3 colors images of obstacles, rock samples and navigable terrain.

a. For Obstacles: I observed that whichever pixels were not part of the navigable terrain, are part of obstacles. Also, sample stones were detected as navigable terrain. So for detectin obstacles, I have simply used the negation of the condition used to identify navigable terrain pixels. Refer to function rocks(img).
ds
b. For identifying sample rocks: The rocks are yellow in color. I found that it is easier to threshold for colors in HSV format. I used the cv2 library. First I converted my image from RGB to BGR. Then I converted it to HSV format and applied thresholding. Refer to function obstacle(img).

Applied 3 different thresholds to extract 3 colors, images of obstacles, rock samples and navigable terrain.

    def rocks(img):
    
        low_yellow = np.array([120, 120,0])

        high_yellow = np.array([255,255,20])# convert to HSV space

        img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)    # mask yellow values

         mask_rock = cv2.inRange(img_hsv, low_yellow, high_yellow)

         res = cv2.bitwise_and(img,img, mask= mask_rock)
     
        return res[:,:,0]
        

    def obstacles(img):
    
         mask = cv2.inRange(img, np.array([45,40,30]), np.array([160,120,100]))
    
         color_select = cv2.bitwise_and(img,img, mask= mask)
    
         return color_select[:,:,2]
         
    def navi_color_thresh(img, rgb_thresh=(160, 160, 160)):
    
    
        mask = cv2.inRange(img, np.array(rgb_thresh), np.array([255,255,255]))

        color_select = cv2.bitwise_and(img,img, mask= mask)

        return color_select[:,:,0]
        
    warped_navi = navi_color_thresh(warped, rgb_thresh=(160, 160, 160))

    warped_obs = obstacles(warped)

    warped_rocks = rocks(warped)
    
   ![Alt text](/rock_img.jpg?raw=true)
   
   ![Alt text](/warped_example.jpg?raw=true)
    
   ![Alt text](/Colored_warped_example2.jpg?raw=true)

Converted each of the valid pixels of above images to rover centric coordinates. Converted each of these 3 images' rover centric coordinates to real world coordinates with pix_to_world(). Additionally, distances and angles for Rover's obstacle pixels, rock sample pixels and navigable pixels were added. Obstacle distances are used in decision.py. 
test_mapping.mp4 is in output directory which was the video generated after performing all the above steps.

 code to Convert rover-centric pixel values to world coords:-

        x_world, y_world = pix_to_world(x_navi, y_navi, posx , posy , Rover.yaw , Rover.worldmap.shape[0], scale)

        x_world_obstacle, y_world_obstacle = pix_to_world(x_obs, y_obs, posx , posy , Rover.yaw , Rover.worldmap.shape[0], scale)

        x_world_rock, y_world_rock = pix_to_world(x_rocks, y_rocks, posx , posy , Rover.yaw , Rover.worldmap.shape[0], scale)

  code to Add pixel positions to worldmap and Update worldmap (to be displayed on right side of screen)

        Rover.worldmap[y_world_obstacle, x_world_obstacle,0] = 255

        Rover.worldmap[y_world_rock, x_world_rock, 1] = 255

        Rover.worldmap[y_world, x_world, 2] = 255
      
![Demo](/output/test_mapping.mp4)

Next goal was to edit decision.py:-

 In forward mode, added following functionalities: 
 
 The rover should move close to left side of the wall. For this, average angle of navigable terrain to Rover's left, the left side obstacle distances (where obstacle_angle > 0) and the right side obstacle distances (where obstacle_angle < 0) are used.
 
 he rover keeps to the left side of the wall. If it is very close to the left wall, it turns slightly to right. If it is stuck and doesn't go to 'stop' mode, it turns right. 

 The rover is preferred to go to left, hence in calculating Rover.steer from mean of navigable angles, 8 degrees are added to each angle so that the average inclination is a bit to left than the actual average navigable angles.
 
If right side obstacle is closer than left side obstacle and there is no immediate wall on left (checked through nav_left which is average angle of left side navigable pixels) then the rover turns left.Further if the nav_left is less than certain threshold (i.e. rover is very close to wall), the rover is turned right.

In case the roll and pitch angles are out of certain limit, the rover is stopped and turned and enters into 'stop' mode. Also, if Rover velocity remains zero for more than one second, then Rover enters 'stuck' mode. In stuck mode, it takes a 4 wheel turn for some time period and then goes back to 'forward' mode. 
 
Achievements:

The rover does a pretty well job in remaining close to left wall to detect objects. 

Rover detects all the objects it encounters in its path.

The rover can navigate more than 95% terrain for different starting positions.
For coverage > 90%, I have managed fidelity more than 60%.

Scope of Improvements:-

As of now i have to still work on my drive_rover and mostly decision.py code. I could actually write logic to pickup samples . I have to learn how efficiently i can arrive on steering angle calculations as per velocity, yaw , distance of the path and navigation angles. Will be working on improving the code to have efficient steering angles and to remember the traversed path and not to again traverse it for second time.

The rover simulator settings were as follows in autonomous mode.

Resolution -------------------> 800 * 600

Graphics quality -------------> Fantastic

FPS o/p ----------------------> 5

