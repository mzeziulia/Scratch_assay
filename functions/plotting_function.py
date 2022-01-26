import matplotlib.pyplot as plt

def display_img(image_data, figsize = (9,9), cmap = 'gray'): 
    '''
    Wrapper function for displaying images
    '''
    plt.figure(figsize=figsize)
    plt.imshow(image_data,cmap=cmap)