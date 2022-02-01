import matplotlib.pyplot as plt
import os
import glob
import csv
from skimage import io
import numpy as np
from skimage.morphology import opening
from skimage.morphology import disk
from skimage.filters import threshold_local
from skimage import img_as_float
from skimage.segmentation import inverse_gaussian_gradient
from skimage.util import img_as_ubyte
import cv2
from skimage import img_as_float
from skimage.morphology import reconstruction
from skimage.feature import blob_dog

from functions import contour_selection as cont_selection 
from functions import plotting_function as plot_function


date_dir = input ('Data source directory') # data sourse
conditions_number = int(input("Number of conditions to be analyzed"))
conditions_entry = input ('Enter condition names separated space') # list of conditions
if conditions_number > 1:
    conditions = list(map(str,conditions_entry.split(' ')))
else:
    conditions = [conditions_entry]

frame_t0 = int(input ('First frame number')) # reference frame for the original scratch area
frame_last = int(input ('Last frame number')) # last frame

cell_number_list=np.empty([1, frame_last-frame_t0+1]) # create an empty list for further storage of cell numbers

csv_name = os.path.join(date_dir,'test.csv') # create a csv file
row_list=[['Condition', 'Initial area', '0h', '1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h', '12h']] # Column titles in csv file
with open(csv_name, 'a', newline='') as file: # Write column titles in csv
    writer = csv.writer(file)
    writer.writerows(row_list) 

for condition in conditions:  # Loop thrugh conditions  

    for tif_file in glob.glob(os.path.join(date_dir,'*%s*'%condition)): # Loop through multiple files within the condition
        
            timelaps = io.imread(tif_file) # Read the tif file
            frame0 = timelaps[0,:, :] # Extract the first frame
            plot_function.display_img(frame0) # Display the first frame

            img_16bit=frame0.copy() # Copy the first frame

            temp = img_as_float(img_16bit)
            gimage = inverse_gaussian_gradient(temp)
            plot_function.display_img(gimage) # Segmentation using inverse gaussian gradient filter

            edge_pctile = 20
            threshold_g = np.percentile(gimage.flatten(),edge_pctile)
            img_thresholded_g = gimage < threshold_g
            gimage_8bit_thr=img_as_ubyte(img_thresholded_g)
            plot_function.display_img(gimage_8bit_thr) # Thresholding the image below the 20th percentile of the intensity distribution 

            block_size = 41
            adaptive_thresh = threshold_local(gimage_8bit_thr, block_size, offset=10)
            binary_adaptive = gimage_8bit_thr > adaptive_thresh # Local threshold
            plot_function.display_img(binary_adaptive)

            footprint = disk(40)
            opened = opening(binary_adaptive, footprint)
            plot_function.display_img(opened) # Morphological opening 

            seed = np.copy(opened)
            seed[1:-1, 1:-1] = opened.max()
            mask = opened
            filled = reconstruction(seed, mask, method='erosion')
            plot_function.display_img(filled) # Erosion

            mask_filled = filled
            seed = np.copy(filled)
            seed[1:-1, 1:-1] = filled.min()
            rec = reconstruction(seed, mask_filled, method='dilation')
            plot_function.display_img(rec) # Dilation

            rec_8bit = img_as_ubyte(rec)


            contours, hierarchy = cv2.findContours(rec_8bit,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

            countours_image1 = frame0.copy()
            countours_image2 = frame0.copy()

            image_with_contours = cv2.drawContours(countours_image1, contours, -1, (0, 255, 0), 3) # Search of contours
            plot_function.display_img(image_with_contours)

            longest_contour, contourIdx  = cont_selection.contour_selection(contours) # Find the longest contour

            image_with_longest_contour = cv2.drawContours(countours_image2, [longest_contour], 0, (0, 255, 0), 3)
            plot_function.display_img(image_with_longest_contour)

            area = cv2.contourArea(longest_contour) # Area of the scratch

            mask = np.zeros(frame0.shape, np.uint8)
            mask_contours=cv2.drawContours(mask, [longest_contour], 0, (255,255,255),1) # Mask of the scratch
            plot_function.display_img(mask_contours)

            countours_image = frame0.copy()

            filled_mask=cv2.fillPoly(countours_image, pts =[longest_contour], color=(0,0,0))
            plot_function.display_img(filled_mask)

            scratch_only = img_16bit-filled_mask
            plot_function.display_img(scratch_only) # Only scratch area


            blobs = blob_dog(img_16bit, min_sigma = 5, max_sigma=30, threshold=.02) # Search of cells

            blobs_list=[]
            for blob_info in blobs:
                y,x,r = blob_info
                if scratch_only[int(y), int(x)] > 0: # Make sure only included blobs whose center pixel is on the mask  
                    blobs_list.append((y,x))

            fig, axes = plt.subplots(1, 2, figsize=(16, 9), sharex=True, sharey=True) # Labelling cells on the image
            ax = axes.ravel()
            ax[0].imshow(scratch_only, cmap = 'gray', interpolation = 'bicubic')
            ax[1].imshow(scratch_only, cmap = 'gray', interpolation = 'bicubic')
            for filtered_blob in blobs_list:
                y, x = filtered_blob
                c = plt.Circle((x, y), 10, color='red', linewidth=0.5, fill=False)
                ax[1].add_patch(c)

            cell_number_list[0][0]=len(blobs_list)
            
            for stack in range(frame_t0+1, frame_last+1): # Search for cells in the rest of frames withing scratch area found on the first fame

                frame = timelaps[stack,:, :] # Pick the next frame
                plot_function.display_img(frame0)

                img_16bit=frame.copy()

                mask = np.zeros(frame.shape, np.uint8)
                mask_contours=cv2.drawContours(mask, [longest_contour], 0, (255,255,255),1) # Use the mask of the scratch area on the current frame
                plot_function.display_img(mask_contours)

                countours_image = frame.copy()

                filled_mask=cv2.fillPoly(countours_image, pts =[longest_contour], color=(0,0,0))
                plot_function.display_img(filled_mask)

                scratch_only = img_16bit-filled_mask # Image of only original scratch but on the following frames
                plot_function.display_img(scratch_only)

                blobs = blob_dog(img_16bit, min_sigma = 5, max_sigma=30, threshold=.02) # Search for cells within ex-scratch

                blobs_list=[]
                for blob_info in blobs:
                    y,x,r = blob_info
                    if scratch_only[int(y), int(x)] > 0: # Make sure only included blobs whose center pixel is on the mask  
                        blobs_list.append((y,x))
                
                fig, axes = plt.subplots(1, 2, figsize=(16, 9), sharex=True, sharey=True) # Labelling detected cells
                ax = axes.ravel()
                ax[0].imshow(scratch_only, cmap = 'gray', interpolation = 'bicubic')
                ax[1].imshow(scratch_only, cmap = 'gray', interpolation = 'bicubic')
                for filtered_blob in blobs_list:
                    y, x = filtered_blob
                    c = plt.Circle((x, y), 10, color='red', linewidth=0.5, fill=False)
                    ax[1].add_patch(c)

                cell_number_list[0][stack]=len(blobs_list)

            my_string = tif_file.rsplit('/')[-1] # Extracting name of the file
            row_list=np.hstack((my_string, area, cell_number_list[0])) # Formatting the input for csv

            with open(csv_name, 'a', newline='') as file: # Write data in the csv file
                writer = csv.writer(file)
                writer.writerows([row_list])

