"""
THIS SCRIPT APPLIES THE ARCGIS SPATIAL ANALYST'S RECLASSIFY TOOL

To create an ArcToolbox tool with which to execute this script, do the following.
1   In  ArcMap > Catalog > Toolboxes > My Toolboxes, either select an existing toolbox
    or right-click on My Toolboxes and use New > Toolbox to create (then rename) a new one.
2   Drag (or use ArcToolbox > Add Toolbox to add) this toolbox to ArcToolbox.
3   Right-click on the toolbox in ArcToolbox, and use Add > Script to open a dialog box.
4   In this Add Script dialog box, use Label to name the tool being created, and press Next.
5   In a new dialog box, browse to the .py file to be invoked by this tool, and press Next.
6   In the next dialog box, specify the following inputs (using dropdown menus wherever possible)
    before pressing OK or Finish.
        DISPLAY NAME            DATA TYPE           PROPERTY>DIRECTION>VALUE    
        Input Grid         	Raster Dataset      Input
        Reclass Instructions    String              Input
        Output  Grid            Raster Dataset      Output
        Output Euclidean Grid   Raster              Output
        
7   To later revise any of this, right-click to the tool's name and select Properties.  

In the dialog box for this new tool,"Reclass Instructions" are used to Reclassify existing grid values
into new values that indicate the number of raindropos in each pixel.  These are to be specified as
        OldValue NewValue; OldValue NewValue; OldValue NewValue ...
        (where each OldValue is an existing value to be replaced by the following NewValue)
or as   InitialOldValue FinalOldValue NewValue
        (where NewValue replaces all existing values from InitialOldValue through FinalOldValue)
and where pixels for which no new value is assigned will be regarded as having no raindrops.

Once the reclass operation isolates feautures of interest (such as roads), the Euclidean Direction
function will create a new raster measuring distance on compass directions. 

"""

# Import external modules
import sys, os, string, arcpy, traceback, time
from arcpy import env
from arcpy.sa import *

# Set environment settings
env.workspace = "D:\GIS_Data\Scratch\Final\HA_Scripts.gdb"

# Check to see if Spatial Analyst license is available
if arcpy.CheckExtension("spatial") == "Available":
    arcpy.CheckOutExtension("spatial") 

    try:

        # Start timing
        timeStart = time.clock()
        
        #########################################################
        ### Part I: Reclassify to Isolate Classes of Interest ###
        
        # Read user inputs from dialog box
      
        inputGridName       = arcpy.GetParameterAsText(0)        
        reassignments       = arcpy.GetParameterAsText(1)
        outputGridName      = arcpy.GetParameterAsText(2)
        outputEucDirName    = arcpy.GetParameterAsText(3)

        # Reclassify       
        newReclassGrid      = arcpy.sa.Reclassify(inputGridName,"Value",reassignments,"DATA")

        # Create pyramids for classified grid
        inras = newReclassGrid
        pylevel = "-1"
        skipfirst = "NONE"
        resample = "NEAREST"
        compress = "DEFAULT"
        quality = "80"
        skipexist = "SKIP_EXISTING"

        arcpy.BuildPyramids_management(inras, pylevel, skipfirst, resample, compress, quality, skipexist)

        # Save newly reclassified grid
        newReclassGrid.save(outputGridName)

        #######################################################
        ### Part II: Measure Euclidean Direction to Classes ###

        ## Set local variables
        inSource = outputGridName
        maxDist = ""
        cellSize = 10
        optOutDistance = ""

        # Execute EucDirections
        outEucDirect = EucDirection(inSource, maxDist, cellSize, optOutDistance)

        # Save the output 
        outEucDirect.save(outputEucDirName)

        # Display a layer with the Euc Distance raster
        currentMap          = arcpy.mapping.MapDocument("CURRENT")
        currentDataFrame    = currentMap.activeDataFrame
        layerToBeDisplayed  = arcpy.mapping.Layer(outputEucDirName)
        arcpy.mapping.AddLayer(currentDataFrame, layerToBeDisplayed,"TOP")
        del currentMap

        # Stop timing
        timeStop = time.clock()
        timeTaken = timeStop - timeStart
        arcpy.AddMessage("\nElapsed time = " + str(timeTaken) + " seconds\n")
                
        # Deactivate ArcGIS Spatial Analyst license
        arcpy.CheckInExtension("spatial")        

    except Exception as e:
        # If unsuccessful, end gracefully by indicating why
        arcpy.AddError('\n' + "Script failed because: \t\t" + e.message )
        # ... and where
        exceptionreport = sys.exc_info()[2]
        fullermessage   = traceback.format_tb(exceptionreport)[0]
        arcpy.AddError("at this location: \n\n" + fullermessage + "\n")

else:
    # Report error message if Spatial Analyst license is unavailable
    arcpy.AddMessage ("Spatial Analyst license is unavailable")
