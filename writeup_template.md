

## Project: Search and Sample Return
The goal of this project was to navigate and map rocks autonomously with the rover in autonomous mode.

My first goal was to identify the color threshold settings,in the project.
In summary, 
I Defined the source and destination points.
Then Took a perspective transform of the input image.
Applied 3 different thresholds to extract 3 colors images of obstacles, rock samples and navigable terrain.
Converted each of the valid pixels of above images to rover centric coordinates.
Converted each of these 3 images' rover centric coordinates to real world coordinates with pix_to_world().
Updated world_map with red color for obstacle, green for rock sample and blue for navigable terrain. The video is at location. "test_mapping.mp4"

![Alt text](/output/Colored_warped_example2.png?raw=true)

a. For Obstacles: I observed that whichever pixels were not part of the navigable terrain, are part of obstacles. Also, sample stones were detected as navigable terrain. So for detectin obstacles, I have simply used the negation of the condition used to identify navigable terrain pixels. Refer to function rocks(img).

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
        
    def navi_color_thresh(img, rgb_thresh=(160, 160, 160)): # Create an array of zeros same xy size as img, but single channel
    
        mask = cv2.inRange(img, np.array(rgb_thresh), np.array([255,255,255]))
        
        color_select = cv2.bitwise_and(img,img, mask= mask)
        
        return color_select[:,:,0]
            
    warped_navi = navi_color_thresh(warped, rgb_thresh=(160, 160, 160))
    
    warped_obs = obstacles(warped)
    
    warped_rocks = rocks(warped)
    

 

**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

Perception_step() function has been updated with image processing functions to create a map. As of now map is displayed almost 100% and fidelity is around 65% all rocks are being detected. Initially i had issues with fidelity as my threshold but after playing with threshold values my fidelity increased to 65%

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup. 

As of now i have to still work on my drive_rover and mostly decision.py code. I could actually write logic to pickup samples when rock samples. I have to learn how efficiently i can arrive on steering angle calculations as per velocity, yaw , distance of the path and navigation angles. Will be working on improving the code to have efficient steering angles and to remember the traversed path and not to again traverse it forsecond time.

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

