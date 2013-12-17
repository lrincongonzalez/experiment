#code v3from pylink import *import timeimport gcimport sysimport exp_trial_sledimport osspath = os.path.dirname(sys.argv[0])if len(spath) !=0: os.chdir(spath)eyelinktracker = EyeLink('10.0.0.20')#Here is the starting point of the experiment#Opens the EDF file.edfFileName = "TEST.EDF";getEYELINK().openDataFile(edfFileName)			pylink.flushGetkeyQueue(); getEYELINK().setOfflineMode();                          #Sends a mesage to EDF file;getEYELINK().sendCommand("screen_pixel_coords =  0 0 350 275")getEYELINK().sendMessage("DISPLAY_COORDS  0 0 350 275")getEYELINK().sendCommand("marker_phys_coords = -182.5,122.5 -182.5,-122.5 182.5,122.5 182.5,-122.5")getEYELINK().sendCommand("screen_phys_coords = -175.0,137.5, 137.5,-175.0")tracker_software_ver = 0eyelink_ver = getEYELINK().getTrackerVersion()if eyelink_ver == 3:	tvstr = getEYELINK().getTrackerVersionString()	vindex = tvstr.find("EYELINK CL")	tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))	if eyelink_ver>=2:	getEYELINK().sendCommand("select_parser_configuration 0")	if eyelink_ver == 2: #turn off scenelink camera stuff		getEYELINK().sendCommand("scene_camera_gazemap = NO")else:	getEYELINK().sendCommand("saccade_velocity_threshold = 35")	getEYELINK().sendCommand("saccade_acceleration_threshold = 9500")	# set EDF file contents getEYELINK().sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")if tracker_software_ver>=4:	getEYELINK().sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")else:	getEYELINK().sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")# set link data (used for gaze cursor) getEYELINK().sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")if tracker_software_ver>=4:	getEYELINK().sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")else:	getEYELINK().sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")    getEYELINK().sendCommand("button_function 5 'accept_target_fixation'");#Calibration settings##H3 is the horizontal 3-point calibrationgetEYELINK().sendCommand("calibration_type = H3")getEYELINK().sendCommand("binocular_enabled = YES")#getEYELINK().sendCommand("enable_automatic_calibration = YES")##switch off the randomization of the targets getEYELINK().sendCommand("randomize_calibration_order = NO")getEYELINK().sendCommand("randomize_validation_order = NO")##prevent it from repeating the first calibration pointgetEYELINK().sendCommand("cal_repeat_first_target = NO")getEYELINK().sendCommand("val_repeat_first_target = NO")##so we can tell it which targets to usegetEYELINK().sendCommand("generate_default_targets = NO")##location of the targets in pixel coordinatesgetEYELINK().sendCommand("calibration_targets = 87,93 175,93 263,93")getEYELINK().sendCommand("validation_targets = 87,93 175,93 263,93")pylink.setCalibrationColors( (0, 0, 0),(255, 255, 255));  	#Sets the calibration target and background color#pylink.setTargetSize(int(surf.get_rect().w/70), int(surf.get_rect().w/300));	#select best size for calibration targetpylink.setCalibrationSounds("", "", "");pylink.setDriftCorrectSounds("", "off", "off");if(getEYELINK().isConnected() and not getEYELINK().breakPressed()):	exp_trial_sled1.run_trials()                print "went back to main"if getEYELINK() != None:	# File transfer and cleanup!                print "made it to file transfer and cleanup!"	getEYELINK().setOfflineMode();                          	msecDelay(500);                 	#Close the file and transfer it to Display PC	getEYELINK().closeDataFile()	getEYELINK().receiveDataFile(edfFileName, edfFileName)	getEYELINK().close();