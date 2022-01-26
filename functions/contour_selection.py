#Function to find the longest contour
def contour_selection (contour): 
    contour_id = 0
    max = len(contour[contour_id])
    for i in range (len(contour)):
        if len(contour[i])>=max:
            max = len(contour[i])
            contour_id=i
    return(contour[contour_id], contour_id)
