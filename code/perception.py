import numpy as np
import cv2 # OpenCV for perspective transform

# Instantiate a Databucket().. this will be a global variable/object
# that you can refer to in the process_image() function below

# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to apply a rotation to pixel positions
def rotate_pix(xpix, ypix, yaw):
    # TODO:
    # Convert yaw to radians
    # Apply a rotation
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # TODO:
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated

# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
   
    dst_size = 5 
    # Set a bottom offset to account for the fact that the bottom of the image 
    # is not the position of the rover but a bit in front of it
    # this is just a rough guess, feel free to change it!
    bottom_offset = 3
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], 
                      [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                      ])
    warped = perspect_transform(Rover.img, source, destination)
    
 
    def rocks(img):
        low_yellow = np.array([100, 100,0])
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
    # 4) Convert thresholded image pixel values to rover-centric coords
    # Extract x and y positions of navigable terrain pixels
    # and convert to rover coordinates
    
    warped_navi = navi_color_thresh(warped, rgb_thresh=(160, 160, 160))
    warped_obs = obstacles(warped)
    warped_rocks = rocks(warped)
    scale= 10
    
    # 4) Convert thresholded image pixel values to rover-centric coords
    x_navi, y_navi = rover_coords(warped_navi)
    x_obs, y_obs = rover_coords(warped_obs)
    x_rocks, y_rocks = rover_coords(warped_rocks)
    (posx,posy) =Rover.pos
  
    # 5) Convert rover-centric pixel values to world coords
    x_world, y_world = pix_to_world(x_navi, y_navi, posx , 
                                       posy , Rover.yaw , 
                                    Rover.worldmap.shape[0], scale)
    x_world_obstacle, y_world_obstacle = pix_to_world(x_obs, y_obs, posx , 
                                       posy , Rover.yaw , 
                                    Rover.worldmap.shape[0], scale)
    x_world_rock, y_world_rock = pix_to_world(x_rocks, y_rocks, posx , 
                                       posy , Rover.yaw , 
                                    Rover.worldmap.shape[0], scale)
    # Add pixel positions to worldmap
    # 6) Update worldmap (to be displayed on right side of screen)
    
  
    Rover.worldmap[y_world_obstacle, x_world_obstacle,0] = 255
    Rover.worldmap[y_world_rock, x_world_rock, 1] = 255
    Rover.worldmap[y_world, x_world, 2] = 255
        # Example: data.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          data.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          data.worldmap[navigable_y_world, navigable_x_world, 2] += 1

    # 7) Make a mosaic image, below is some example code
        # First create a blank image (can be whatever shape you like)
    output_image = np.zeros((Rover.img.shape[0] + Rover.worldmap.shape[0], Rover.img.shape[1]*2, 3))
        # Next you can populate regions of the image with various output
        # Here I'm putting the original image in the upper left hand corner
    output_image[0:Rover.img.shape[0], 0:Rover.img.shape[1]] = Rover.img

        # Let's create more images to add to the mosaic, first a warped image
    warped = perspect_transform(Rover.img, source, destination)
        # Add the warped image in the upper right hand corner
    output_image[0:Rover.img.shape[0], Rover.img.shape[1]:] = warped

        # Overlay worldmap with ground truth map
    map_add = cv2.addWeighted(Rover.worldmap, 1, Rover.ground_truth, 0.5, 0)
        # Flip map overlay so y-axis points upward and add to output_image 
    output_image[Rover.img.shape[0]:, 0:Rover.worldmap.shape[1]] = np.flipud(map_add)


        # Then putting some text over the image
    cv2.putText(output_image,"Populate this image with your analyses to make a video!", (20, 20), 
                cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
    #data.count += 1 # Keep track of the index in the Databucket()
    
    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
    Rover.nav_dists, Rover.nav_angles = to_polar_coords(x_navi, y_navi)
    Rover.rock_dists, Rover.rock_angles = to_polar_coords(x_rocks, y_rocks)
    Rover.obstacle_dists, Rover.obstacle_angles = to_polar_coords(x_obs, y_obs)
    mean_dir = np.mean(Rover.nav_angles)    
         
  
    return Rover