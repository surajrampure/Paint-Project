#Main.py
#by Suraj Rampure
#iPaint Pro -- A versatile paint program that allows the user to draw with various tools, import images, apply filters and more.
#Paint Program for ICS3U-02
#Started November 29th, 2013 ---- #Finished January 27th, 2014

#Importing of modules --------
from pygame import *
from math import *
from random import *    
#from tkinter import filedialog as filedialog      #Imports filedialog for default Windows save/load screen
font.init()

fpsDisplay = time.Clock()                          #fpsDisplay is for tracking FPS 

screen = display.set_mode((1280,850))
display.set_caption("iPaint Pro")
display.set_icon(image.load("Other/displayseticon.png"))

canvas = Surface((881,641))             #Surface for canvas
canvas.fill((255,255,255))              #Makes the default canvas colour white
canvasRect = Rect(30,43,881,641)        #Rectangle covering the canvas (to see if MB is on canvas)
cover = canvas.copy()                   #Copy of the canvas (for all tools, and undo/redo)

spectrumrect = Rect(971,59,253,162)     #Rectangle for the spectrum (placed in background)
seltoolrect = Rect(1080,252,150,22)     #Rectangle for the display of selected colour

#Returns mouse position on screen
def sp():               
    return mouse.get_pos()

#Returns mouse position relative to canvas --- (30,43) is (0,0)
def cp():               
    return (mouse.get_pos()[0]-30,mouse.get_pos()[1]-43)

#Fill bucket tool
def bucketfill(mpos,col):
    bucketlist = [mpos]                       #Adds the mouse position to a list
    replacecol = screen.get_at((mpos))
    if replacecol != col:                     #If the colour at a pixel hasn't been set to the drawcol:
        while len(bucketlist) > 0:            #While elements still exist in the bucketlist (meaning there are more eligible points to colour replace)
            x,y = bucketlist.pop()            #x,y become the last element in bucketlist; and the corresponding values are removed
            if screen.get_at((x,y)) == replacecol:
                screen.set_at((x,y),col)
                bucketlist.append((x+1,y))
                bucketlist.append((x-1,y))
                bucketlist.append((x,y+1))
                bucketlist.append((x,y-1))

#Filters function: Gets average R G B value for each pixel,
            #and based on the selected filter it applies the respective values
            #to the RGB colours
def applyFilter (surf,filt,col):
    for x in range (surf.get_width()):
        for y in range(surf.get_height()):
            replacecol = surf.get_at((x,y))
            r = replacecol[0]
            g = replacecol[1]
            b = replacecol[2]
            avg = (r+g+b)//3
            if filt == "grey":                #"Filt" is a variable for the filter in use
                filtrgb = (avg,avg,avg)       
            elif filt == "sepia":             #Sepia multiplies each pixel's R G and B values by common ratios (found online)
                nR = (r*0.393) + (g*0.769) + (b*0.189)
                if nR > 255:
                    nR = 255
                nG = (r*0.349) + (g*0.686) + (b*0.168)   
                if nG > 255:
                    nG = 255
                nB = (r*0.272) + (g*0.534) + (b*0.131)
                if nB > 255:
                    nB = 255
                filtrgb = (nR,nG,nB)
            elif filt == "xray":                #X-ray averages the RGB values and inverts them            
                filtrgb = (255-avg,255-avg,255-avg)
            elif filt == "invert":
                filtrgb = (255-r,255-g,255-b)
            elif filt == "swap1":               #The swap filters change the order of the R G B values 
                filtrgb = (r,b,g)
            elif filt == "swap2":
                filtrgb = (g,b,r)
            elif filt == "swap3":
                filtrgb = (g,r,b)
            elif filt == "swap4":
                filtrgb = (b,r,g)
            elif filt == "swap5":
                filtrgb = (b,g,r)
            elif filt == "tint":                #Tint takes the selected drawing colour, multiplies it by the R/G/B value of
                                                #each pixel and applies it, effectively tinting the canvas with the drawcol
                nR = int((r*col[0])/255)
                if nR > 255:
                    nR = 255
                nG = int((g*col[1])/255)
                if nG > 255:
                    nG = 255
                nB = int((b*col[2])/255)
                if nB > 255:
                    nB = 255
                filtrgb = (nR,nG,nB)
            surf.set_at((x,y),filtrgb)

#Unfilled rectangle tool: Draws four lines, effectively fixing the Pygame rectangle that has four little squares in the corners
def unfilledRect(surf,col,start,end,width):
    sm = width//2           #Only drawing four lines will still result in small squares in the corners
                            #I observed that the sides of these squares were about half of the width; I went from there
    if (end[0] - start[0]) >= 0:
        if width%2 == 0:        #If the width is divisible by 2, sm is an integer
            draw.line(surf,col,(start[0]-(sm-1),start[1]),(end[0]+(sm),start[1]),width)
            draw.line(surf,col,start,(start[0],end[1]),width)
            draw.line(surf,col,end,(end[0],start[1]),width)
            draw.line(surf,col,(start[0]-(sm-1),end[1]),(end[0]+(sm),end[1]),width)
        
        elif width%2 == 1:      #The positions of the lines are slightly adjusted when sm has a remainder of 1
            draw.line(surf,col,(start[0]-sm,start[1]),(end[0]+(sm),start[1]),width)
            draw.line(surf,col,start,(start[0],end[1]),width)
            draw.line(surf,col,end,(end[0],start[1]),width)
            draw.line(surf,col,(start[0]-sm,end[1]),(end[0]+(sm),end[1]),width)

    #If the ellipse is drawn from right to left (negative), start and end are reversed and the same arithmetic applies
    elif (end[0] - start[0]) < 0:
        if width%2 == 0:
            draw.line(surf,col,(end[0]-(sm-1),end[1]),(start[0]+(sm),end[1]),width)
            draw.line(surf,col,end,(end[0],start[1]),width)
            draw.line(surf,col,start,(start[0],end[1]),width)
            draw.line(surf,col,(end[0]-(sm-1),start[1]),(start[0]+(sm),start[1]),width)
            
        elif width%2 == 1:
            draw.line(surf,col,(end[0]-(sm),end[1]),(start[0]+(sm),end[1]),width)
            draw.line(surf,col,end,(end[0],start[1]),width)
            draw.line(surf,col,start,(start[0],end[1]),width)
            draw.line(surf,col,(end[0]-(sm),start[1]),(start[0]+(sm),start[1]),width)
            
#Intro screen code, where theme is chosen --------
themechooser = image.load("Other/Theme Chooser.png")
themechooser = themechooser.convert()         #Converts the themes so that we can adjust the alpha for it
for i in range (255):                         #Allows the intro screen to fade in from black
    screen.fill((0,0,0))                      #Fills the screen black
    themechooser.set_alpha(i)                 #Alpha of the theme chooser increases by one each time
    screen.blit(themechooser,(0,0))
    time.wait(1)
    display.flip()

#Rectangles to choose theme
earththeme = Rect(60,544,347,195)             
spacetheme = Rect(469,544,347,195)
animalstheme = Rect(877,544,347,195)

theme = ""                                    #String variable for theme: used to identify theme and import specialized graphics

#Event loop for choice screen --------
running = True
while running:
    for ev in event.get():
        if ev.type == QUIT:
            quit()
            running = False
            
    mb = mouse.get_pressed()
    
    if earththeme.collidepoint(sp()) and mb[0] == 1:
        theme = "Earth"
        switchcol = (112,159,89)              #Variable for colour of the switches used in the UI
    if spacetheme.collidepoint(sp()) and mb[0] == 1:
        theme = "Space"
        switchcol = (10,10,220)
    if animalstheme.collidepoint(sp()) and mb[0] == 1:
        theme = "Animals"
        switchcol = (0,0,0)
    if theme != "":                           #If theme is chosen, loop breaks
        running = False
        

time.wait(100)

loadingscreen = image.load(theme+"/Loading Screen.png")     #Loads the informational screen with graphics corresponding to theme
loadingscreen = loadingscreen.convert()

#Another event loop that only tracks if they click down to advance from the loading screen
running = True
while running:
    for e in event.get():
        if e.type == QUIT:
            quit()
            running = False
        if e.type == MOUSEBUTTONDOWN: running = False
    screen.blit(loadingscreen,(0,0))        
    display.flip()

time.wait(100)

themewallpaper = image.load(theme+"/Theme Wallpaper.png")   #Imports key wallpaper for theme
screen.blit(themewallpaper,(0,0))       #Blits the main theme background for the respective theme

#Image variable naming scheme: "up" means not clicked, "down" means clicked

#Importing of stamps and their corresponding icons, and creating the Rects --------
blit1 = image.load(theme+"/Blit/blit1.png")          
blit1Rect = Rect(952,533,76,59)
blit1up = image.load(theme+"/Blit/blit1up.png")      
blit1down = image.load(theme+"/Blit/blit1down.png")
screen.blit(blit1up,(952,533))

blit2 = image.load(theme+"/Blit/blit2.png")
blit2Rect = Rect(1059,533,76,59)
blit2up = image.load(theme+"/Blit/blit2up.png")
blit2down = image.load(theme+"/Blit/blit2down.png")
screen.blit(blit2up,(1059,533))

blit3 = image.load(theme+"/Blit/blit3.png")
blit3Rect = Rect(1166,533,76,59)
blit3up = image.load(theme+"/Blit/blit3up.png")
blit3down = image.load(theme+"/Blit/blit3down.png")
screen.blit(blit3up,(1166,533))

blit4 = image.load(theme+"/Blit/blit4.png")
blit4Rect = Rect(952,603,76,59)
blit4up = image.load(theme+"/Blit/blit4up.png")
blit4down = image.load(theme+"/Blit/blit4down.png")
screen.blit(blit4up,(952,603))

blit5 = image.load(theme+"/Blit/blit5.png")
blit5Rect = Rect(1059,603,76,59)
blit5up = image.load(theme+"/Blit/blit5up.png")
blit5down = image.load(theme+"/Blit/blit5down.png")
screen.blit(blit5up,(1059,603))

blit6 = image.load(theme+"/Blit/blit6.png")
blit6Rect = Rect(1166,603,76,59)
blit6up = image.load(theme+"/Blit/blit6up.png")
blit6down = image.load(theme+"/Blit/blit6down.png")
screen.blit(blit6up,(1166,603))

#Stamps is a dictionary for the "blitimg" variable that chooses which stamp is to be blitted,
#with the corresponding image variables
#This is so that I can call stamps[blitimg] and the selected stamp will blit, instead of repeating the code 6 times
stamps = {"blit1": blit1, "blit2": blit2, "blit3": blit3, "blit4": blit4, "blit5": blit5, "blit6": blit6}

blitimg = ""                            #Variable for which of the six icons to blit (stamp called by stamps[blitimg])

stampsize = 3                           #Variable for size of stamp

size1Down = image.load("Other/size1.png")      #Four different versions of the bar that displays stamp size (1 2 3 or 4)   
size2Down = image.load("Other/size2.png")
size3Down = image.load("Other/size3.png")
size4Down = image.load("Other/size4.png")

size1Rect = Rect (974,447,62,30)               #Rects to click for the 4 stamp sizes
size2Rect = Rect (1038,447,62,30)
size3Rect = Rect (1103,447,62,30)
size4Rect = Rect (1168,447,62,30)
screen.blit(size3Down,(973,446))               #Default stamp size is 3, blits size 3 selected rect

#Importing of backgrounds and their corresponding icons, and creating the Rects --------
background1 = image.load(theme+"/Backgrounds/background1.png")
background1Rect = Rect(952,673,76,59)
background1up = image.load(theme+"/Backgrounds/background1up.png")
background1down = image.load(theme+"/Backgrounds/background1down.png")
screen.blit(background1up,(952,673))

background2 = image.load(theme+"/Backgrounds/background2.png")
background2Rect = Rect(1059,673,76,59)
background2up = image.load(theme+"/Backgrounds/background2up.png")
background2down = image.load(theme+"/Backgrounds/background2down.png")
screen.blit(background2up,(1059,673))

background3 = image.load(theme+"/Backgrounds/background3.png")
background3Rect = Rect(1166,673,76,59)
background3up = image.load(theme+"/Backgrounds/background3up.png")
background3down = image.load(theme+"/Backgrounds/background3down.png")
screen.blit(background3up,(1166,673))

#Importing tool icons, text descriptions, setting Rects and blitting "up" icons --------
lineUp = image.load("Icons/LineUp.png")
lineDown = image.load("Icons/LineDown.png")
lineDesc = image.load("Desc/LineDesc.png")
linerect = Rect(62,776,55,55)
screen.blit(lineUp,(62,776))

rectUp = image.load("Icons/RectUp.png")
rectDown = image.load("Icons/RectDown.png")
rectDesc = image.load("Desc/RectDesc.png")
rectrect = Rect(172,776,55,55)
screen.blit(rectUp,(172,776)) 

ellipseUp = image.load("Icons/EllipseUp.png")
ellipseDown = image.load("Icons/EllipseDown.png")
ellipseDesc = image.load("Desc/EllipseDesc.png")
ellipserect = Rect(282,776,55,55)
screen.blit(ellipseUp,(282,776))

polyUp = image.load("Icons/PolyUp.png")
polyDown = image.load("Icons/PolyDown.png")
polyDesc = image.load("Desc/PolyDesc.png")
polyrect = Rect (392,776,55,55)
screen.blit(polyUp,(392,776))

pencilUp = image.load("Icons/PencilUp.png")
pencilDown = image.load("Icons/PencilDown.png")
pencilDesc = image.load("Desc/PencilDesc.png")
pencilrect = Rect(502,776,55,55)
screen.blit(pencilUp,(502,776))

brushUp = image.load("Icons/BrushUp.png")
brushDown = image.load("Icons/BrushDown.png")
brushDesc = image.load("Desc/BrushDesc.png")
brushrect = Rect(612,776,55,55)
screen.blit(brushUp,(612,776))

sprayUp = image.load("Icons/SprayUp.png")
sprayDown = image.load("Icons/SprayDown.png")
sprayDesc = image.load("Desc/SprayDesc.png")
sprayrect = Rect(722,776,55,55)
screen.blit(sprayUp,(722,776))

eraserUp = image.load("Icons/EraserUp.png")
eraserDown = image.load("Icons/EraserDown.png")
eraserDesc = image.load("Desc/EraserDesc.png")
eraserrect = Rect (832,776,55,55)
screen.blit(eraserUp,(832,776))

bucketUp = image.load("Icons/BucketUp.png")
bucketDown = image.load("Icons/BucketDown.png")
bucketDesc = image.load("Desc/BucketDesc.png")
bucketrect = Rect (942,776,55,55)
screen.blit(bucketUp,(942,776))

extractUp = image.load("Icons/ExtractUp.png")
extractDown = image.load("Icons/ExtractDown.png")
extractDesc = image.load("Desc/ExtractDesc.png")
extractrect = Rect (1052,776,55,55)
screen.blit(extractUp,(1052,776))

textUp = image.load("Icons/TextUp.png")
textDown = image.load("Icons/TextDown.png")
textDesc = image.load("Desc/TextDesc.png")
textrect = Rect (1162,776,55,55)
screen.blit(textUp,(1162,776))

selectUp = image.load("Icons/selectup.png")
selectDown = image.load("Icons/selectdown.png")
selectDesc = image.load("Desc/SelectDesc.png")
selectrect = Rect (973,333,259,32)
screen.blit(selectUp,(973,333))

#Rects for buttons in the toolbar --------
iPaint = Rect (0,0,100,20)
savecanvas = Rect(120,0,34,20)
loadcanvas = Rect(170,0,38,20)
undoRect = Rect(220,0,41,20)
redoRect = Rect(280,0,36,20)
clearcanvas = Rect(335,0,85,20)
fillcanvas = Rect(440,0,72,20)
filtersRect = Rect(530,0,48,20)

#The about bar is the image that appears when clicking the Apple logo/iPaint Pro
#This rect is created
aboutbar = image.load("Other/aboutbar.png")
aboutRect = Rect (400,200,400,300)

#Rectangles for filled and outline only switch --------
filledrect = Rect(1016,291,43,16)
outlinerect = Rect(1060,291,42,16)
filled = True                           #By default, the rectangles, ovals and polygons will be filled
outline = False

polypoints = []                         #List of points for polygon tool
drawn = False                           #Drawn is a flag for if a polygon has been drawn yet (to clear polypoints list)

tool = "pencil"                         #Variable for tool in use
screen.blit(pencilDown,(502,775))       #Pencil is the default tool, the icon is blitted
screen.blit(pencilDesc,(30,692))        #The text description is also blitted

drawcol = (0,0,0)                       #Default colour is black (drawcol is a variable
draw.rect(screen,drawcol,seltoolrect)   #Fills the selected colour rectangle with black

#Variables for sizes of tools, sets default values
rad = 5                                 #Brush radius
erad = 25                               #Eraser radius
srad = 40                               #Spray paint radius
lthick = 2                              #Line thickness
rthick = 2                              #Outline only rectangle thickness
sprayspeed = 25                         #Speed of while loop for spray tool

m = 0,0                                 #Empty coordinates for pencil tool, which requires tracking of previous mouse pos
oldx,oldy = 0,0                         #Used for brush and eraser as the previous mouse coordinates
toolx,tooly = 0,0                       #Used for brush and eraser (an amount that we increase by each cycle for the smooth brush)             

undolist = [cover,cover]  #Need a blank canvas to start off the undo list,
                          #in case user wants to undo first action
redolist = []

cropRect = Rect (0,0,1,1)       #An empty rectangle for the crop tool

textblit = ''   #String for text to blit with text tool
avenirtool = font.Font("Fonts/Avenir.ttc",14) #Font for info bar (displays mouse coordinates, RGB val)
avenirfont = font.Font("Fonts/Avenir.ttc",40) #Avenir font (text tool) 
helveticafont = font.Font("Fonts/HelveticaNeue.dfont",40) #Helvetica font (-)
lucidafont = font.Font("Fonts/LucidaGrande.ttc",45) #Lucida font (-)
infobar = image.load("Desc/infobar.png")   #To be blit every iteration of the loop, under the updated info

#The 3 versions of the images depicting which font is selected (each one has the corresponding font highlighted)
helveticaDown = image.load("Fonts/helveticadown.png")
avenirDown = image.load("Fonts/avenirdown.png")
lucidaDown = image.load("Fonts/lucidadown.png")
helveticaRect = Rect (973,390,86,32)            #Rects for each of the fonts
avenirRect = Rect (1059,390,86,32)
lucidaRect = Rect (1145,390,86,32)
screen.blit(helveticaDown,(972,388))            #Default font is Helvetica
font = "helvetica"

#Textcycle is a flag for if a copy of the screen has been taken the first time a key has been pressed in a certain string                
textcycle = True

#Importing of filter graphics --------
filtersDesc = image.load("Desc/FiltersDesc.png")
            
FiltersMenu = image.load("Filters/menubar.png")

blurRect = Rect(36,774,130,70)
blurUp = image.load("Filters/blurup.png")
blurDown = image.load("Filters/blurdown.png")

greyRect = Rect(190,774,130,70)
greyUp = image.load("Filters/greyup.png")
greyDown = image.load("Filters/greydown.png")

sepiaRect = Rect (344,774,130,70)
sepiaUp = image.load("Filters/sepiaup.png")
sepiaDown = image.load("Filters/sepiadown.png")

xrayRect = Rect (498,774,130,70)
xrayUp = image.load("Filters/xrayup.png")
xrayDown = image.load("Filters/xraydown.png")

invertRect = Rect (652,774,130,70)
invertUp = image.load("Filters/invertup.png")
invertDown = image.load("Filters/invertdown.png")

#The 5 swap rects are for the 5 sub buttons on the swap icon, each with their own filter 
swap1Rect = Rect(806,774,25,70)
swap2Rect = Rect(832,774,26,70)
swap3Rect = Rect(859,774,26,70)
swap4Rect = Rect(886,774,26,70)
swap5Rect = Rect(912,774,25,70)

#Imports the 5 versions of the swap icon, one with each filter highlighted, and one with none highlighted ('up')
swapNone = image.load("Filters/swapnone.png")
swap1Up = image.load("Filters/swap1up.png")
swap2Up = image.load("Filters/swap2up.png")
swap3Up = image.load("Filters/swap3up.png")
swap4Up = image.load("Filters/swap4up.png")
swap5Up = image.load("Filters/swap5up.png")

pixelateRect = Rect (960,774,130,70)
pixelateUp = image.load("Filters/pixelateup.png")
pixelateDown = image.load("Filters/pixelatedown.png")

tintRect = Rect (1114,774,130,70)
tintUp = image.load("Filters/tintup.png")
tintDown = image.load("Filters/tintdown.png")

closefiltersRect = Rect (0,750,15,15)
closeUp = image.load("Filters/closeup.png")
closeDown = image.load("Filters/closedown.png")

#Dock is a snippet of the screen that must be reblitted after switching back to tools from filters
dock = image.load(theme+"/dock.png")        

#Flags ---- 
showfilters = False                         #Flag for if the filters menu is on screen: if == True, then no tools can be chosen

click = False                               #Click is a flag for if evt.type == MBD (if the mouse is being clicked, not held down)

move = False                                #Move is a flag for if the cropped image in the selected tool is to be blitted at cp() or not

erase = False                               #Erase is a flag triggered by a BACKSPACE key down when tool is select, telling whether or not to
                                            #delete the cropped image

cycle = True                                #Flag for if the tools can be used and if the most recent canvas is to be sent to the screen,
                                            #is triggered False by activating the about bar

drag = False                                #Flag for if the about bar is able to be dragged yet: triggereed True by clicking the about bar itself

screen.blit(canvas,(30,43))
#------------------------------------------------------------------------------------------------------
running = True
while running:
    for evt in event.get():             
        if evt.type == QUIT:
            running = False 

        mb = mouse.get_pressed()
        keys = key.get_pressed()

        if evt.type == MOUSEBUTTONDOWN and canvasRect.collidepoint(sp()):
    
            if blitimg != "" and tool != "poly":
                if evt.button == 3:                           #At any point the user can right click to blit their selected stamp
                    cover = canvas.copy()
                    
            if tool == "brush":
                if evt.button == 4:                           #If the user scrolls up, the brush radius increases by 2 and program waits 5 seconds
                    rad += 2                             #This size changing feature is used with most tools. A 5 sec wait is added so the size doesn't
                    time.wait(5)                         #increase rapidly
                if evt.button == 5 and rad>=2:
                    rad -= 2
                    time.wait(5)
                        
            if tool == "eraser":
                if evt.button == 4:
                    erad += 2
                    time.wait(5)
                if evt.button == 5 and erad>=2:
                    erad -= 2
                    time.wait(5)

            if tool == "line":
                if evt.button == 1:
                    fx,fy = cp()
                    cover = canvas.copy()
                if evt.button == 4 and lthick <4:
                    lthick += 1
                    time.wait(5)
                if evt.button == 5 and lthick>=2:
                    lthick -= 1
                    time.wait(5)
                    
            if tool == "rectangle":
                if evt.button == 1:
                    fx,fy = cp()
                    cover = canvas.copy()
                if evt.button == 4 and rthick < 25:
                    rthick += 1
                    time.wait(5)
                if evt.button == 5 and rthick > 1:
                    rthick -= 1
                    time.wait(5)
                    
            if tool == "ellipse":
                if evt.button == 1:
                    fx,fy = cp()
                    cover = canvas.copy()
                    
            if tool == "spray":
                if evt.button == 4:
                    srad += 2
                    time.wait(5)
                if evt.button == 5 and srad>=2:
                    srad -= 2
                    time.wait(5)

            if tool == "poly":
                if evt.button == 1:
                    cover = canvas.copy()
                    if drawn == True:   #If a polygon has already been drawn the list is cleared
                        del polypoints[:]
                        drawn = False
                    polypoints.append(cp())

            if tool == "select":
                if evt.button == 1:
                    fx,fy = cp()
                    cover = canvas.copy()

        if evt.type == MOUSEBUTTONDOWN: 
            if evt.button == 1: click = True  #Click is a flag for whether or not the left mouse is being clicked down
                                              #After performing actions we can set click to False so they don't occur
                                              #repeatedly if the mouse is held down
            if loadcanvas.collidepoint(sp()):
                cover = canvas.copy
                undolist.append(cover)

            if canvasRect.collidepoint(sp()):       #If we start drawing we empty the redolist, there isn't anything to redo once the user starts drawing
                del redolist[:]

            #The select tool requires two different copies of the canvas, this is the only canvas copy that has a different name than cover 
            if tool == "select" and canvasRect.collidepoint(sp()):
                copy = canvas.copy()

            #If the user clicks while move is true, they blit the cropimg to the canvas permanently, so move must now become false
            if move == True:
                move = False
                    
        if evt.type == MOUSEBUTTONUP:
            if evt.button == 1: click = False
            if evt.button == 1 or evt.button  == 3:     #So that mouse scrolling doesn't add tons of copies
                if canvasRect.collidepoint(sp()):
                    cover = canvas.copy()
                    undolist.append(cover)

            #Once the user has drawn the rectangle encompassing the region they want to move, when they let go of the mouse
            #The region they highlighted turns white (simulating the effect of removing that region)
            if tool == "select" and canvasRect.collidepoint(sp()) and evt.button == 1 and move == False:
                move = True     #The flag 'move' becomes True which then blits the cropped selection at cp()
                draw.rect(canvas,(255,255,255),cropRect)    
                
        if evt.type == KEYDOWN:
            if tool == "text":
                if textcycle == True:   #We only want one canvas copy: for the first time a key is pressed
                    cover = canvas.copy()
                    textcycle = False   #Making textcycle false will stop it from making more copies
                if evt.key < 256:       #If the key has a value less than 256 (is a character) then we add it to the string of what to render as text
                    textblit += evt.unicode
                if evt.key == K_BACKSPACE:
                    textblit = textblit[0:-2]   #Removes last character in string if the user backspaces

            if tool == "select":
                if keys[K_BACKSPACE]:           
                    erase = True                #If the user hits backspace then erase becomes true, which then will delete the cropimg in the select tool
    
    if tool == "pencil":
        fx,fy = m
        m = cp()
        #This makes (fx,fy) the previous mouse position (drawing lines between consecutive positions)
        
        
    if spectrumrect.collidepoint(sp()):
        if mb[0] == 1:                              #If spectrum is clicked, the colour the mouse is over becomes drawcol
            drawcol = screen.get_at((sp()))
            draw.rect(screen,drawcol,seltoolrect)   #Places selected colour in preview box


#Info bar --------
    screen.blit(infobar,(30,721))           #Blits the black bar underneath each time so that the information can be updated each cycle

    #Renders FPS as text --------
    fpsDisplay.tick()
    fps = fpsDisplay.get_fps()   #Gets FPS
    fpsdisplay = avenirtool.render("FPS: "+str(round(fps,1)),True,(255,255,255))
    screen.blit(fpsdisplay,(835,723))
        
    if cycle == True:           
        screen.blit(canvas,(30,43))

        #Renders mouse coordinates as text --------
        if canvasRect.collidepoint(sp()):
            mousecoordblit = avenirtool.render("X: "+str(cp()[0])+"    Y: "+str(cp()[1]),True,(255,255,255)) #Makes a string out of x and y
        else:
            mousecoordblit = avenirtool.render("Mouse off canvas",True,(218,210,0))
        screen.blit(mousecoordblit,(40,723))

        #Renders (R,G,B) colour value --------
        redval = avenirtool.render("R: "+str(drawcol[0]),True,(253,59,46))  #Makes a string out of the first value in drawcol (so on for G and B)
        screen.blit(redval,(200,723))

        greenval = avenirtool.render("G: "+str(drawcol[1]),True,(49,183,1))
        screen.blit(greenval,(250,723))

        blueval = avenirtool.render("B: "+str(drawcol[2]),True,(60,219,240))
        screen.blit(blueval,(300,723))

        #Displays information for each tool (radius, thickness, rectangle length and width) --------
        if tool == "brush":
            thickblit = avenirtool.render("Brush Radius: "+str(rad)+" px",True,(255,255,255))
            screen.blit(thickblit,(500,723))
            
        elif tool == "eraser":
            thickblit = avenirtool.render("Eraser Radius: "+str(erad)+" px",True,(255,255,255))
            screen.blit(thickblit,(500,723))
            
        elif tool == "line":
            if mb[0] == 1:
                #Renders the length of the line as the distance between (fx,fy) and cp()
                linedist = round(sqrt((fx-cp()[0])**2 + (fy-cp()[1])**2),1)
                thickblit = avenirtool.render("Line Thickness: "+str(lthick)+ " px           Line Length: "+str(linedist)+" px",True,(255,255,255))
            else:
                thickblit = avenirtool.render("Line Thickness: "+str(lthick)+ " px",True,(255,255,255))
            
            screen.blit(thickblit,(500,723))
            
        elif tool == "spray":
            thickblit = avenirtool.render("Spray Radius: "+str(srad)+ " px     Spray Density: "+str(sprayspeed)+"/250",True,(255,255,255))
            screen.blit(thickblit,(500,723))
            
        elif tool == "rectangle":
            if mb[0] == 1 and canvasRect.collidepoint(sp()):
                if keys[K_LSHIFT] or keys[K_RSHIFT]:
                    thickblit = avenirtool.render("Square Side Length: "+str(((cp()[0]-fx)+(cp()[1]-fy))/2),True,(255,255,255))
                else:
                    thickblit = avenirtool.render("Rectangle Length: "+str(abs(cp()[0]-fx))+"  Rectangle Height: "+str(abs(cp()[1]-fy)),True,(255,255,255))

                if outline == True and canvasRect.collidepoint(sp()):
                    alsoblit = avenirtool.render("Thickness: "+str(rthick),True,(255,255,255))
                    screen.blit(alsoblit,(400,723))
                    
                screen.blit(thickblit,(500,723))
                
        elif tool == "ellipse":
            if mb[0] == 1 and canvasRect.collidepoint(sp()):
                if keys[K_LSHIFT] or keys[K_RSHIFT]:
                    thickblit = avenirtool.render("Circle Radius: "+str(abs(cp()[0]-fx)/2),True,(255,255,255))
                    screen.blit(thickblit,(500,723))
                else:
                    #Major axis is always the longer of the length/width of the ellipse; minor axis is the other
                    majoraxis = max(abs(cp()[0]-fx),abs(cp()[1]-fy))
                    minoraxis = min(abs(cp()[0]-fx),abs(cp()[1]-fy))
                    thickblit = avenirtool.render("Major Axis: "+str(majoraxis)+"  Minor Axis: "+str(minoraxis),True,(255,255,255))
                    screen.blit(thickblit,(500,723))
                    
        elif tool == "poly":
            thickblit = avenirtool.render("Points in Polygon: "+str(len(polypoints)),True,(255,255,255))
            screen.blit(thickblit,(500,723))

        #Always displaying the canvas or spectrum colour, even when the user is not clicking
        elif tool == "extract":
            if canvasRect.collidepoint(sp()) or spectrumrect.collidepoint(sp()):
                extractcol = screen.get_at(sp())
                thickblit = avenirtool.render("R: "+str(extractcol[0])+"     G: "+str(extractcol[1])+"     B: "+str(extractcol[2]),True,(218,210,0))
                screen.blit(thickblit,(500,723))
    

#Checking which tool button is pressed and changing the icon ------------------------------------------------------


    if showfilters == False:
        
        if linerect.collidepoint(sp()):     
            if mb[0] == 1:                      #If a tool rectangle is clicked, the corresponding tool
                tool = "line"                   #becomes the selected tool
        if tool == "line":
            screen.blit(lineDown,(62,775))      #If this tool is selected, the corresponding "down" (clicked) icon and
            screen.blit(lineDesc,(30,692))      #description are blitted
        if tool != "line":  
            screen.blit(lineUp,(62,775))        #If the tool isn't selected, the "up" icon is blitted                  

        if rectrect.collidepoint(sp()):
            if mb[0] == 1:
                tool = "rectangle"
        if tool == "rectangle":
            screen.blit(rectDown,(172,775))
            screen.blit(rectDesc,(30,692))
        if tool != "rectangle":
            screen.blit(rectUp,(172,775))

        if ellipserect.collidepoint(sp()):
            if mb[0] == 1:
                tool = "ellipse"
        if tool == "ellipse":
            screen.blit(ellipseDown,(282,775))
            screen.blit(ellipseDesc,(30,692))
        if tool != "ellipse":
            screen.blit(ellipseUp,(282,775))

        if polyrect.collidepoint(sp()):
            if mb[0] == 1:
                tool = "poly"
        if tool == "poly":
            screen.blit(polyDown,(392,775))
            screen.blit(polyDesc,(30,692))
        if tool != "poly":
            screen.blit(polyUp,(392,775))
                
        if pencilrect.collidepoint(sp()):
            if mb[0] == 1:
                tool = "pencil"
        if tool == "pencil":
            screen.blit(pencilDown,(502,775))
            screen.blit(pencilDesc,(30,692))
        if tool != "pencil":
            screen.blit(pencilUp, (502,775))

        if brushrect.collidepoint(sp()):
            if mb[0] == 1:
                tool = "brush"
        if tool == "brush":
            screen.blit(brushDown,(612,775))
            screen.blit(brushDesc,(30,692))
        if tool != "brush":
            screen.blit(brushUp,(612,775))

        if sprayrect.collidepoint(sp()):
            if mb[0] == 1:
                tool = "spray"
        if tool == "spray":
            screen.blit(sprayDown,(722,775))
            screen.blit(sprayDesc,(30,692))
        if tool != "spray":
            screen.blit(sprayUp,(722,775))

        if eraserrect.collidepoint(sp()):
            if mb[0] == 1:
                tool = "eraser"
        if tool == "eraser":
            screen.blit(eraserDown,(832,775))
            screen.blit(eraserDesc,(30,692))
        if tool != "eraser":
            screen.blit(eraserUp,(832,775))

        if bucketrect.collidepoint(sp()):
            if mb[0] == 1:
                tool = "bucket"
        if tool == "bucket":
            screen.blit(bucketDown,(942,775))
            screen.blit(bucketDesc,(30,692))
        if tool != "bucket":
            screen.blit(bucketUp,(942,775))

        if extractrect.collidepoint(sp()):
            if mb[0] == 1:
                tool = "extract"
        if tool == "extract":
            screen.blit(extractDown,(1052,775))
            screen.blit(extractDesc,(30,692))
        if tool != "extract":
            screen.blit(extractUp,(1052,775))

        if textrect.collidepoint(sp()):
            if mb[0] == 1:
                tool = "text"
        if tool == "text":
            screen.blit(textDown,(1162,775))
            screen.blit(textDesc,(30,692))
        if tool != "text":
            screen.blit(textUp,(1162,775))

        if selectrect.collidepoint(sp()):
            if mb[0] == 1:
                tool = "select"
        if tool == "select":
            screen.blit(selectDown,(973,333))
            screen.blit(selectDesc,(30,692))
        if tool != "select":
            screen.blit(selectUp,(973,333))


    #If the rect of a stamp size is clicked, the version of the size bar
    #which has that specific size highlighted is blitted, and the stampsize is changed accordingly
    if size1Rect.collidepoint(sp()):
        if mb[0] == 1:
            screen.blit(size1Down,(973,446))
            stampsize = 1
    if size2Rect.collidepoint(sp()):
        if mb[0] == 1:
            screen.blit(size2Down,(973,446))
            stampsize = 2
    if size3Rect.collidepoint(sp()):
        if mb[0] == 1:
            screen.blit(size3Down,(973,446))
            stampsize = 3
    if size4Rect.collidepoint(sp()):
        if mb[0] == 1:
            screen.blit(size4Down,(973,446))
            stampsize = 4

#Following collidepoints are for the icons of the 6 stamps:
        #If a stamp's rectangle is clicked, the "down" icon is displayed
        #And the corresponding stamp becomes the blit image (blitimg)
    if blit1Rect.collidepoint(sp()) and mb[0] == 1:
        screen.blit(blit1down,(952,533))
        blitimg = "blit1"
    if blitimg != "blit1":
        screen.blit(blit1up,(952,533))
        
    if blit2Rect.collidepoint(sp()) and mb[0] == 1:
        screen.blit(blit2down,(1059,533))
        blitimg = "blit2"
    if blitimg != "blit2":
        screen.blit(blit2up,(1059,533))
    
    if blit3Rect.collidepoint(sp()) and mb[0] == 1:
        screen.blit(blit3down,(1166,533))
        blitimg = "blit3"
    if blitimg != "blit3":
        screen.blit(blit3up,(1166,533))

    if blit4Rect.collidepoint(sp()) and mb[0] == 1:
        screen.blit(blit4down,(952,603))
        blitimg = "blit4"
    if blitimg != "blit4":
        screen.blit(blit4up,(952,603))
        
    if blit5Rect.collidepoint(sp()) and mb[0] == 1:
        screen.blit(blit5down,(1059,603))
        blitimg = "blit5"
    if blitimg != "blit5":
        screen.blit(blit5up,(1059,603))

    if blit6Rect.collidepoint(sp()) and mb[0] == 1:
        screen.blit(blit6down,(1166,603))
        blitimg = "blit6"
    if blitimg != "blit6":
        screen.blit(blit6up,(1166,603))

#Collidepoints for the rectangles of the backgrounds
        #Fills the screen with the corresponding background
        #(Doesn't happen with the 6 blit images at this point because
        #those are blitted according to mouse pos)
    if background1Rect.collidepoint(sp()):
        screen.blit(background1down,(952,673))  #Puts the white box around the icon if hover
        if mb[0] == 1:
            canvas.blit(background1,(0,0))
            cover = canvas.copy()
            undolist.append(cover)
            del polypoints[:]   #Deletes the polypoints list so it doesn't keep drawing the existing segments
    else:
        screen.blit(background1up,(952,673))

    if background2Rect.collidepoint(sp()):
        screen.blit(background2down,(1059,673))
        if mb[0] == 1:
            canvas.blit(background2,(0,0))
            cover = canvas.copy()
            undolist.append(cover)
            del polypoints[:]
    else:
        screen.blit(background2up,(1059,673))

    if background3Rect.collidepoint(sp()):
        screen.blit(background3down,(1166,673))
        if mb[0] == 1:
            canvas.blit(background3,(0,0))
            cover = canvas.copy()
            undolist.append(cover)
            del polypoints[:]
    else:
        screen.blit(background3up,(1166,673))

    display.flip()
    
# ---------------------------------------------------------------------

#Filled and outline switch ---------------
    #If filled is clicked, filled = True
    if filledrect.collidepoint(sp()):
        if mb[0] == 1:
            filled = True
            outline = False

    if outlinerect.collidepoint(sp()):
        if mb[0] == 1:
            filled = False
            outline = True

    #Colouring in the selected switch with switchol, and setting "thickness"
    if filled == True:
        thick = 0                             #A thickness of 0 makes shapes filled in
        draw.rect(screen,switchcol,filledrect)  
        draw.rect(screen,(255,255,255),outlinerect)

    if outline == True:
        thick = 1                             #Whereas a thickness of 1 gives shapes an outline
        draw.rect(screen,switchcol,outlinerect)
        draw.rect(screen,(255,255,255),filledrect)
        
#Program now draws based on the selected tool ----------------

    if cycle == True:                   #So that the tools don't work while we drag around the about bar

        #Line Tool -- Draws line from when event was MOUSEBUTTONDOWN to current position
        if tool == "line":
            if mb[0] == 1 and canvasRect.collidepoint(sp()):
               canvas.blit(cover,(0,0))
               draw.line(canvas,drawcol,(fx,fy),cp(),lthick)

        #Rectangle Tool -- Draws rectangle from when event was MOUSEBUTTONDOWN to current position
        if tool == "rectangle":
            if mb[0] == 1 and canvasRect.collidepoint(sp()):
                canvas.blit(cover,(0,0))
                if filled == True:
                    if keys[K_LSHIFT] or keys[K_RSHIFT]:            #Locks to square if shift is held
                        #Locks to square by making both the length and width the average of (fx,fy) and (cp())
                        draw.rect(canvas,drawcol,(fx,fy,((cp()[0]-fx)+(cp()[1]-fy))/2,((cp()[0]-fx)+(cp()[1]-fy))/2),0)
                    else:
                        draw.rect(canvas,drawcol,(fx,fy,(cp()[0])-fx,(cp()[1])-fy),0)
                elif outline == True:
                    #Increases or decreases the thickness of the outline only rect, only when outline only is selected
                    if (keys[K_RIGHT] or keys[K_d]) and rthick < 25:
                        rthick += 1
                        time.wait(5)
                    if keys[K_LEFT] and rthick > 1:
                        rthick -= 1
                        time.wait(5)
                    if keys[K_a] and rthick > 1:
                        rthick -= 1
                        time.wait(5)
                    if keys[K_LSHIFT] or keys[K_RSHIFT]:
                        #For the square locked outline only mode, we add the average of dx and dy to the starting position for the ending coordinates
                        unfilledRect(canvas,drawcol,(fx,fy),(fx+((cp()[0]-fx)+(cp()[1]-fy))/2,fy+((cp()[0]-fx)+(cp()[1]-fy))/2),rthick)
                    else:
                        #Calls the defined unfilledRect tool, drawing 4 lines creating a rectangle without the small squares in the corners
                        unfilledRect(canvas,drawcol,(fx,fy),cp(),rthick)

        #Ellipse tool
        if tool == "ellipse":
            if mb[0] == 1 and canvasRect.collidepoint(sp()):
                canvas.blit(cover,(0,0))
                if keys[K_LSHIFT] or keys[K_RSHIFT]:            #Locks to circle if shift is held
                    if abs(cp()[0]-fx) > 0:
                        draw.circle(canvas,drawcol,(fx,fy),int(abs(cp()[0]-fx)/2),thick)
                else:
                    #This line prevents us from getting the error "width less than ellipse radius": we only draw if this is NOT the case
                    if (abs (cp()[0]-fx)) > thick and (abs(cp()[1]-fy)) > thick:
                        #We draw at whichever point is to the top left, since the draw.ellipse can't draw with negative values
                        #We then take the absolute value of the horizontal and vertical distances between the points so that it doesnt matter
                        #from which point we start at -- the axes will be of the same length
                        drawellipse = Rect (min(fx,cp()[0]),min(fy,cp()[1]),abs(cp()[0]-fx),abs(cp()[1]-fy))
                        draw.ellipse(canvas,drawcol,drawellipse,thick)
                            
        if tool == "poly":
             if len(polypoints) > 1 and drawn == False:
                 canvas.blit(cover,(0,0))
                 draw.lines(canvas,drawcol,False,polypoints,1)        #Draws the sides of the polygon as points are picked
             if mb[2] == 1 and canvasRect.collidepoint(sp()) and len(polypoints) > 2:         #If right clicked, the polygon is closed off
                canvas.blit(cover,(0,0)) 
                draw.polygon(canvas,drawcol,polypoints,thick)
                drawn = True                #Drawn is a flag for if a polygon has already been drawn
                                            #To see if the list of points needs to be cleared
                                            #This is the case if the screen is cleared or filled
            
        if tool == "pencil":
            if mb[0] == 1 and canvasRect.collidepoint(sp()):
                draw.line(canvas,drawcol,(fx,fy),cp(),1) #Always drawing from the most recent previous position to current position

        #Brush tool
        if tool == "brush":
            if keys[K_RIGHT] or keys[K_d]:
                rad += 1
                time.wait(5)
            if keys[K_LEFT] and rad >=2:
                rad -= 1
                time.wait(5)
            if keys[K_a] and rad >= 2:
                rad -= 1
                time.wait(5)
            if canvasRect.collidepoint(sp()) and mb[0] == 1:
                dist = max(1,sqrt((oldx-cp()[0])**2+(oldy-cp()[1])**2))     #Finding the distance between the most recent coordinates and the current coordinates
                sx = (cp()[0]-oldx)/dist                                    #sx is the amount you increase horizontally each time to draw circles at each point 
                sy = (cp()[1]-oldy)/dist                                    #sy is the '' vertically, at each point between (oldx,oldy) and cp()

                for i in range (int(dist)):
                    toolx += sx                             #toolx is originally 0, it represents the cumulative value we add to the oldx each time through the loop
                    tooly += sy                             #same for tooly -- we add tooly to oldy each time
                    draw.circle(canvas,drawcol,(int(oldx + toolx),int(oldy + tooly)),rad)  #This effectively draws circles at each point between the points
            oldx,oldy = cp()    #the oldx and y become the previous mouse coordinates and therefore become cp()
            toolx,tooly = 0,0   #toolx and tooly both need to be 0 since they are accumulators

            #Same code applies for the eraser tool

        if tool == "spray":
            #Increases or decreases the radius of circles in which the smaller circles are drawn
            if keys[K_RIGHT] or keys[K_d]:
                srad += 1
                time.wait(5)
            if keys[K_LEFT] and srad >=2:
                srad -= 1
                time.wait(5)
            if keys[K_a] and srad >= 2:
                srad -= 1
                time.wait(5)
            #Increases or decreases the speed at which the smaller circles are drawn
            if (keys[K_UP] or keys[K_w]) and sprayspeed < 250:
                sprayspeed +=1
                time.wait(5)
            if keys[K_DOWN] and sprayspeed >= 2:
                sprayspeed -= 1
                time.wait(5)
            if keys[K_s] and sprayspeed >= 2:
                sprayspeed -= 1
                time.wait(5)
            
            if mb[0] == 1 and canvasRect.collidepoint(cp()):
                for i in range(sprayspeed):     #sprayspeed changes density (amount of cycles through loop)
                    sprayx = randint(cp()[0]-srad,cp()[0]+srad) #Random integer "srad" away from current x coord
                    sprayy = randint(cp()[1]-srad,cp()[1]+srad) #Random integer "srad" away from current y coord
                    if (sprayx - cp()[0])**2 + (sprayy - cp()[1])**2 <= srad**2:    #If the sprayx and sprayy points are on or in a circle of srad thickness:
                        draw.circle(canvas,drawcol,(sprayx,sprayy),0)

        #Eraser -- Same as the brush tool, except always white 
        if tool == "eraser":
            if keys[K_RIGHT] or keys[K_d]:
                erad += 1
                time.wait(5)
            if keys[K_LEFT] and erad >= 2:
                erad -= 1
                time.wait(5)
            if keys[K_a] and erad >= 2:
                erad -= 1
                time.wait(5)
            if mb[0] == 1 and canvasRect.collidepoint(sp()):
                dist = max(1,sqrt((oldx-cp()[0])**2+(oldy-cp()[1])**2))
                sx = (cp()[0]-oldx)/dist
                sy = (cp()[1]-oldy)/dist

                for i in range (int(dist)):
                    toolx += sx
                    tooly += sy
                    draw.circle(canvas,(255,255,255),(int(oldx + toolx),int(oldy + tooly)),erad)
                    
            oldx,oldy = cp()
            toolx,tooly = 0,0

        #Bucket fill
        if tool == "bucket":
            if mb[0] == 1 and canvasRect.collidepoint(sp()):
                screen.set_clip(canvasRect)
                bucketfill(sp(),drawcol)                #Calls the defined bucket fill function       
                canvas = screen.subsurface(canvasRect).copy()           #We set everything to the screen, this takes a copy of the canvasRect
                screen.set_clip(None)
                
        #Takes colour of pixel under mouse and makes it drawing colour
        #Useful if user wants to go back to a previous colour
        if tool == "extract":                            
            if mb[0] == 1 and canvasRect.collidepoint(sp()):
                drawcol = screen.get_at((cp()))
                draw.rect(screen,drawcol,seltoolrect)


        #Text tool functionality        
        if tool == "text":
            if helveticaRect.collidepoint(sp()):                    #Choosing the font and blitting the corresponding icon with that font highlighted
                if click:
                    screen.blit(helveticaDown,(972,388))
                    font = "helvetica"
            if avenirRect.collidepoint(sp()):
                if click:
                    screen.blit(avenirDown,(972,388))
                    font = "avenir"
            if lucidaRect.collidepoint(sp()):
                if click:
                    screen.blit(lucidaDown,(972,388))
                    font = "lucida"
                    
            screen.set_clip(canvasRect)
            if len(textblit) > 0:
                canvas.blit(cover,(0,0))    #If a canvas copy has been taken we blit it (a copy is taken once the first key is down in the string)
            if font == "helvetica":
                block = helveticafont.render(textblit,True,drawcol) #Renders the "textblit" string based on the selected font
            if font == "avenir":
                block = avenirfont.render(textblit,True,drawcol)
            if font == "lucida":
                block = lucidafont.render(textblit,True,drawcol)
            canvas.blit(block,(cp()[0],cp()[1]-35))      #Blits the text string at the mouse coordinates 
            if (mb[0] == 1 or keys[K_RETURN]) and canvasRect.collidepoint(sp()):        #If the user clicks or hits enter:
                canvas.blit(block,(cp()[0],cp()[1]-35))                                 #We permanently blit the string 
                textblit = ''                                                           #We also empty it so it is fresh for the next user input string
                textcycle = True  #We have to make textcycle true so that it will make a copy the next time the user types
            screen.set_clip(None)

        #Rectangular selection
        if tool == "select":
            if mb[0] == 1 and canvasRect.collidepoint(sp()):
                canvas.blit(cover,(0,0))                        #Constantly blitting the copy of the canvas taken
                cropRect = Rect (fx,fy,cp()[0]-fx,cp()[1]-fy)   #cropRect is a rect made of the time MBD and the cp()
                cropRect.normalize()                            #Normalize the rect eliminating negative values
                draw.rect (canvas,(255,0,0),(fx-1,fy-1,cp()[0]-fx+2,cp()[1]-fy+2),1)   #This draws a rect one away from cropRect in each direction, in Red
                                                                                       #Is drawn one away so that it doesn't interfere with the canvas they are selecting

            #Move == True occurs when the user lifts their mouse off of the canvas
            #Erase == True occurs when the user hits backspace
            if move == True and erase == True:
                #This blits the original canvas copy taken before any alterations, and draws the white rectangle of cropRect
                #Makes move false so that cropimg no longer blits, and also makes erase false
                canvas.blit(copy,(0,0))
                draw.rect (canvas,(255,255,255),cropRect)
                erase = False
                move = False
                
            if move == True and erase == False:         #Move becomes false if the user clicks down
                canvas.blit(copy,(0,0))
                cropimg = canvas.subsurface(cropRect).copy()            #cropimg is the area of the canvas that was selected by cropRect
                draw.rect(canvas,(255,255,255),cropRect)                #continues to draw the white rectangle emulating the experience of removing that area
                canvas.blit(cropimg,cp())                               #cropimg is blitted at the mouse position for the user to move around
        
#Sending the selected stamp to the screen if the right mouse button is clicked down --------

    if blitimg != "" and tool != "poly" and canvasRect.collidepoint(sp()):
        if mb[2] == 1:
            canvas.blit(cover,(0,0))
            screen.set_clip(canvasRect)
            if keys[K_f]:                     #Flips the image vertically if F is held 
                stamp = transform.flip(stamps[blitimg],False,True)
            elif keys[K_h]:                   #Flips the image horizontally if H is held
                stamp = transform.flip(stamps[blitimg],True,False)
            else:                             #Otherwise the original image is used
                stamp = stamps[blitimg]
            if stampsize == 1:
                #Scales the image down to (75,75) and blits it at (cp()[0]-75/2,cp()[1]-75/2)
                #So that it blits at the middle when the mouse is clicked
                canvas.blit(transform.scale(stamp,(75,75)),(cp()[0]-37,cp()[1]-37))
            elif stampsize == 2:
                canvas.blit(transform.scale(stamp,(125,125)),(cp()[0]-63,cp()[1]-63))
            elif stampsize == 3:
                canvas.blit(transform.scale(stamp,(175,175)),(cp()[0]-88,cp()[1]-88))
            elif stampsize == 4:
                canvas.blit(transform.scale(stamp,(250,250)),(cp()[0]-125,cp()[1]-125))
            screen.set_clip(None)

#Filter functionality --------
    if filtersRect.collidepoint(sp()) and click:              #If the user clicks on the filters button in the toolbar, "showfilters" becomes True
            showfilters = True                                #Showfilters being true stops the cycle of choosing other tools, since those tools are
            click = False                                     #under the Filters menu bar
                                        
    #If showfilters is true, we blit the description of the filters functionality
    #and all of the unclicked icons of the filters
            
    if showfilters == True:                 
        screen.blit(filtersDesc,(30,692))
        screen.blit(FiltersMenu,(0,750))

        #NoFilter
        screen.blit(blurUp,(36,774))
        screen.blit(greyUp,(190,774))
        screen.blit(sepiaUp,(344,774))
        screen.blit(xrayUp,(498,774))
        screen.blit(invertUp,(652,774))
        screen.blit(swapNone,(806,774))
        screen.blit(pixelateUp,(960,774))
        screen.blit(tintUp,(1114,774))

        if blurRect.collidepoint(sp()):       #Blur (the only filter that doesn't use the defined filters function)
            screen.blit(blurDown,(36,774))           #Blits "down" icon if the mouse is hovering over the blit rect (simulates the effect)
            if click == True:
                cover = canvas.copy()               #Works by taking a copy of the canvas, scaling it down to 1/16 of the original size with smoothscale
                cover = transform.smoothscale(cover,(110,80))
                cover = transform.smoothscale(cover,(881,641))  #and scaling it back up, giving a blurry effect
                canvas.blit(cover,(0,0))
                click = False
                undolist.append(cover)
                
        elif greyRect.collidepoint(sp()):           
            screen.blit(greyDown,(190,774))             
            if click == True:
                applyFilter(canvas,"grey",drawcol)        #This is where the filter function comes in use
                cover = canvas.copy()                     #Adds the filtered canvas to the undolist
                undolist.append(cover)
                click = False
            
        elif sepiaRect.collidepoint(sp()):    
            screen.blit(sepiaDown,(344,774))
            if click == True:
                applyFilter(canvas,"sepia",drawcol)
                cover = canvas.copy()
                undolist.append(cover)
                click = False
            
        elif xrayRect.collidepoint(sp()):     
            screen.blit(xrayDown,(498,774))
            if click == True:
                applyFilter(canvas,"xray",drawcol)                                                                         
                cover = canvas.copy()
                undolist.append(cover)
                click = False
            
        elif invertRect.collidepoint(sp()):   
            screen.blit(invertDown,(652,774))
            if click == True:
                applyFilter(canvas,"invert",drawcol)
                cover = canvas.copy()
                undolist.append(cover)
                click = False
            
        elif swap1Rect.collidepoint(sp()):     #The following 5 Rects call the 5 swaps 
            screen.blit(swap1Up,(806,774))
            if click == True:
                applyFilter(canvas,"swap1",drawcol)
                cover = canvas.copy()
                undolist.append(cover)
                click = False

        elif swap2Rect.collidepoint(sp()):
            screen.blit(swap2Up,(806,774))
            if click == True:
                applyFilter(canvas,"swap2",drawcol)
                cover = canvas.copy()
                undolist.append(cover)
                click = False

        elif swap3Rect.collidepoint(sp()):
            screen.blit(swap3Up,(806,774))
            if click == True:
                applyFilter(canvas,"swap3",drawcol)
                cover = canvas.copy()
                undolist.append(cover)
                click = False

        elif swap4Rect.collidepoint(sp()):
            screen.blit(swap4Up,(806,774))
            if click == True:
                applyFilter(canvas,"swap4",drawcol)
                cover = canvas.copy()
                undolist.append(cover)
                click = False

        elif swap5Rect.collidepoint(sp()):
            screen.blit(swap5Up,(806,774))
            if click == True:
                applyFilter(canvas,"swap5",drawcol)
                cover = canvas.copy()
                undolist.append(cover)
                click = False
            
        elif pixelateRect.collidepoint(sp()):    #Pixelate -- Scales down the image without using smoothscale and scales it back up, creating a
                                                 #highly pixelated version of the canvas
            screen.blit(pixelateDown,(960,774))
            if click == True:
                cover = canvas.copy()
                cover = transform.scale(cover,(55,40))
                cover = transform.scale(cover,(880,640))
                canvas.blit(cover,(0,0))
                cover = canvas.copy()
                undolist.append(cover)
                click = False
            
        elif tintRect.collidepoint(sp()):     #Tint
            screen.blit(tintDown,(1114,774))
            if click == True:
                if drawcol != (0,0,0):
                    applyFilter(canvas,"tint",drawcol)
                cover = canvas.copy()
                undolist.append(cover)
                click = False

        #If the closefiltersRect is hovered over, the red circle at the top left of the
        #Filters menu turns darker, simulating this effect on the Mac
        #If not, then the version of this icon that is lighter is blitted
        if closefiltersRect.collidepoint(sp()):
            screen.blit(closeDown,(1,751))
        else:
            screen.blit(closeUp,(1,751))

        #If this little circle is clicked, then the filters menu disappears and
        #the regular icon and dock appears (hence the blitting of "dock")
        if closefiltersRect.collidepoint(sp()):
            if mb[0] == 1:
                showfilters = False       #Showfilters is false, now we are able to choose the other dock tools
                screen.blit(dock,(0,749))       #The dock reappears

#Functionality for the about bar that appears if the Apple logo or "iPaint Pro" is clicked ----
    if iPaint.collidepoint(sp()):
        if mb[0] == 1:
            barcanvascopy = canvas.copy()       #Take a copy of the canvas at this point
            barblurcopy = transform.smoothscale(barcanvascopy,(110,80))     
            barblurcopy = transform.smoothscale(barblurcopy,(881,641))
            screen.blit(barblurcopy,(30,43))                    #Blurs the canvas when the about bar is clicked, barblurcopy is the blurred version of the canvas
            screen.blit(aboutbar,(400,200))
            cycle = False                      #Makes cycle false so that we can't draw on the canvas while this about bar is on

    if aboutRect.collidepoint(sp()) and cycle == False:         #If the user clicks the about bar, drag becomes true
        if mb[0] == 1:                     
            drag = True

    #When drag is true the user can drag the about bar around the canvas only
    if drag == True and (30 < sp()[0] < 881+30-400) and (43 < sp()[1] < 641+43-300): #The about bar is 400 by 300, this ensures that no part of it goes off the canvas
        screen.blit(barblurcopy,(30,43))    #Constantly blit the blur copy and the about bar itself
        screen.blit(aboutbar,sp())
        if mb[0] == 0:                      #If the user lets go, then drag becomes false
            drag = False

    if cycle == False and drag == False:
        if canvasRect.collidepoint(sp()) and mb[0] == 1:
            cycle = True                                #Cycle becomes true again so the user can now draw on the screen again
            canvas.blit(barcanvascopy,(0,0))            #Sends the canvas copy taken before the about bar appeared to the screen

#Toolbar buttons for save and load, utilizing tkinter's filedialog --------
    if click == True:
        if savecanvas.collidepoint(sp()):
                cover = canvas.copy()   
                OPTIONS = dict(defaultextension = '.png')      #Sets the default file type to be .png in a dictionary
                savename = filedialog.asksaveasfilename(**OPTIONS)  #This opens the Windows save window where the user can choose a save destination
                                                        #"savename" is a string that has the path and the filename the user inputs
                if len(savename) > 0:                   #Makes sure that the user actually pointed to where they want to save and didn't 'cancel'
                    image.save(cover,savename)          #If so we save the cover to the selected destination
                click = False

        elif loadcanvas.collidepoint(sp()):
                loadname = filedialog.askopenfilename()     #This opens the Windows file open window, loadname is a string of the path + filename to open
                if len(loadname) > 0:                   #This ensures that the user didn't click cancel (which would bug out the program without this line)
                    loadnameimg = image.load(loadname)  #loadnameimg becomes the actual image extracted from the path and file name
                    load_w = loadnameimg.get_width()
                    load_h = loadnameimg.get_height()
                    if load_w > 881 or load_h > 641:    #If the width or height of the image is greater than canvas dimensions,
                        loadnameimg = transform.smoothscale(loadnameimg,(881,641))  #It is scaled down to fit
                    canvas.blit(loadnameimg,(0,0))
                    cover = canvas.copy()
                    undolist.append(cover)
                click = False

#Toolbar buttons for undo and redo --------

        elif undoRect.collidepoint(sp()):
            if len(undolist) > 2:               
                canvas.blit(undolist[-2],(0,0))     #As long as there are more than 2 elements in the undolist and the user clicks undo, the 2nd most recent copy is blitted
                redolist.append(undolist[-1])       #The most recent copy (after the user just drew) is then sent to the undolist and is deleted
                del undolist[-1]
                click = False

        elif redoRect.collidepoint(sp()):
            if len(redolist) > 0:
                canvas.blit(redolist[-1],(0,0))     #Blits the most recent cover in the redolist, which was obviously sent from the last undo in the undolist
                undolist.append(redolist[-1])       #So that the user can undo this action, this canvas copy is sent back to the undolist
                del redolist[-1]                    #This copy is now deleted from the redolist so it cannot be re-redone
                click = False
        #Note that the redolist is cleared if the user clicks on the canvas

#Toolbar buttons for clear canvas and fill canvas --------

        #Fills the canvas white
        elif clearcanvas.collidepoint(sp()):
            canvas.fill((255,255,255))
            del polypoints[:]           #Polypoints list must be cleared, otherwise the already drawn line segments will appear
            cover = canvas.copy()
            undolist.append(cover)

        #Fills the canvas the selected drawing colour
        elif fillcanvas.collidepoint(sp()):
            canvas.fill(drawcol)
            del polypoints[:]
            cover = canvas.copy()
            undolist.append(cover)
            
    display.flip()
    
quit()
