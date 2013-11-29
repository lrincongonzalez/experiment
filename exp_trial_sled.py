#code v3***root might not workfrom pylink import *import timeimport gcimport sysimport root_luc1 as root1 import root_luc2 as root2 import numpy as npfrom scipy import statsimport serialimport mathimport structimport signalsys.path.append('C:/Users/DCC-User/Documents/GitHub/Rudolph')from sledclient import SledClient##SLED##client = SledClient()client.connect('sled', 3375)# Start streaming positionsclient.startStream()time.sleep(2)client.sendCommand("Lights Off")#go to -0.15client.goto(-0.15)time.sleep(2.5)raw_input("Press any key to continue and START sinusoid")#start Sledclient.sendCommand("Sinusoid Start 0.15 1.6")RIGHT_EYE = 1LEFT_EYE = 0BINOCULAR = 2#LED coordinates#calibration_targets = (99.5,180 187.5,180 275.5,180)FP = (175,93)LP = (87,93)RP = (263, 93)Tp = 32 # therhold mmgetEYELINK().sendMessage("Calibration targets FP: %d, LP: %d, RP: %d"%(FP[0], LP[0], RP[0]));getEYELINK().sendMessage("Therhold +/- %d"%(Tp));def end_trial():	'''Ends recording: adds 100 msec of data to catch final events'''  	pylink.endRealTimeMode();    	pumpDelay(100);        	getEYELINK().stopRecording(); 	while getEYELINK().getkey() :  	 	pass;def sled_phase(state_phase, t0_sled):	'''Determines sled direction and phase '''		T = 1.6 # period		#Get time	time_now = client.time() - t0_sled	#claculate where in the cycle we are	time_cycle = time_now/T	mantissa = math.floor(time_cycle)	fraction = time_cycle - mantissa		if state_phase == "RIGHT": #RIGHT TURNING POINT 		if fraction < 0.5:			time_to_stim = (mantissa)*T + 0.8 + T		elif fraction > 0.5:			time_to_stim = (mantissa + 1)*T + 0.8 + T		if state_phase == "LEFT": # LEFT TURNING POINT		if fraction < 0.5:			time_to_stim = (mantissa)*T + 1.6 + T		elif fraction > 0.5:			time_to_stim = (mantissa + 1)*T + T	return time_to_stimdef sled_recal():	'''Recalibrates the timer associated with the sinusoid phases'''	while 1:		position = client.getPosition()		if position[0][0,0]<-.14990:			t0_sled = client.time()			break	return t0_sleddef gaze_pos():	'''Calculates gaze position '''	eye_used = getEYELINK().eyeAvailable(); #determine which eye(s) are available 	if eye_used == RIGHT_EYE:  		eye_used = RIGHT_EYE;		#getEYELINK().sendMessage("EYE_USED 1 RIGHT");	elif eye_used == LEFT_EYE or eye_used == BINOCULAR:		#getEYELINK().sendMessage("EYE_USED 0 LEFT");  		eye_used = LEFT_EYE;  	else:  		print "Error in getting the eye information!";  		return TRIAL_ERROR;	dt = getEYELINK().getNewestSample() # check for new sample update	if(dt != None):		# Gets the gaze position of the latest sample,		if eye_used == RIGHT_EYE and dt.isRightSample():			gaze_position = dt.getRightEye().getGaze()		elif eye_used == LEFT_EYE and dt.isLeftSample():			gaze_position = dt.getLeftEye().getGaze()	return gaze_positiondef drift_corr(ser):	''' Does drift correction and handles the re-do camera setup situations'''		print "Drift correction";	error = getEYELINK().doDriftCorrect(FP[0],FP[1],1,1)	if error != 27:		return 0	else:		print "Recalibrate, ser connection closed";		ser.close()		getEYELINK().doTrackerSetup();		ser = serial.Serial('COM15', 115200) 		time.sleep(5)				def drawgc(t0_sled, ser):	'''Sends a stimulus to the Arduino; uses the getNewestSample() to get subjects response; uses the response the calculate the SOA and thus the next stimulus '''	l = [] #creates an empty list to get the positions	#stimulus ranges from -250:-2 in steps of 2ms, and from 2:250 in steps of 2ms	Ledl = dict(zip(range(-2,-251,-2),range(4,129)))	Ledl.update(dict(zip(range(2,251,2),range(130,255))))	Ledl.update({1000:0})	Ledl.update({3000:3})	#initializes the state phase	state_phase = "RIGHT"	#variables for root function	i = 0	j = 0	x = np.linspace(-250,-2,125)	x1=np.linspace(2,250,125)	x=np.append(x,x1)	# turns the LEDs OFF	LEDb = Ledl[3000]	ser.write(struct.pack('B',LEDb)) 	# turns the FP LED ON	LEDb = Ledl[1000]	ser.write(struct.pack('B',LEDb))   	minimizer1 = root1.Psi(-250,250,x,np.linspace(-200,200,41),np.linspace(0.1, 100,41))         # make a kontsevic root finder with a range from 0 to 2	minimizer2 = root2.Psi(-250,250,x,np.linspace(-200,200,41),np.linspace(0.1, 100,41))         # make a kontsevic root finder with a range from 0 to 2	#stimr=np.array([-250, -200, -150, -100, -50, 50, 100, 150, 200, 250])	stimr=np.array([-50, 200, -150, 100,-200, -250, 50,  150, -100, 250])	#random.shuffle(stimr)		getEYELINK().flushKeybuttons(0)	buttons =(0, 0);		while 1:		error = getEYELINK().isRecording()  # First check if recording is aborted 		if error!=0:			end_trial();			return error		if i>25:  #finishes the trial after 50 iterations			#print "timeout"			getEYELINK().sendMessage("TIMEOUT");			end_trial();			buttons =(0, 0);			break;		if(getEYELINK().breakPressed()):	# Checks for program termination or ALT-F4 or CTRL-C keys			end_trial();			return ABORT_EXPT		elif(getEYELINK().escapePressed()): # Checks for local ESC key to abort trial (useful in debugging)			end_trial();			return SKIP_TRIAL					buttons = getEYELINK().getLastButtonPress() # Checks for eye-tracker buttons pressed		if(buttons[0] != 0):			getEYELINK().sendMessage("ENDBUTTON %d"%(buttons[0]));			end_trial();			break;		###########EXPERIMENT STARTS##############################################		print "state_phase:", state_phase		#starts the root/LED experiment					if state_phase == "RIGHT": # Right			print "trial:", i			l.append(i)			if i < 10:				stim = np.round(stimr[i])				i = i + 1			else:				stim = minimizer1()  				i = i + 1		elif state_phase == "LEFT": # Left			print "trial:", j			l.append(j)			if j < 10:				stim = np.round(stimr[j])				j = j + 1			else:				stim = minimizer2()  				j = j + 1						state_eye = "NO_FIXATE"		print "state_eye:", state_eye		l.append(state_eye)		a = 1 # this is for a counter to set drift correct				while 1:			#calcultes the time to the next phase based on the state_phase			time_to_stim = sled_phase(state_phase, t0_sled)			getEYELINK().sendMessage("DISPLAY OFF")			print "time_to_stim:", time_to_stim			l.append(time_to_stim)			while (client.time() - t0_sled) < (time_to_stim):				#gets eye position				gaze_position = gaze_pos()				#Determines if subject is fixating, +/- 32 pixels of 175				if gaze_position[0] > (FP[0] - Tp) and gaze_position[0] < (FP[0] + Tp):					if state_eye == "NO_FIXATE":						state_eye = "START_FIXATE"						t0_FP = client.time()					elif state_eye == "START_FIXATE":						#checks whether the subject has fixated for 500ms						if (client.time() - t0_FP) >= 0.50:							state_eye = "END_FIXATE"				else:					state_eye = "NO_FIXATE"						if state_eye ==	"START_FIXATE":				state_eye = "NO_FIXATE"			position = client.getPosition()			if state_phase == "RIGHT": # Right				if position[0][0,0] < 0.1495 :					#start sled timer at correct phase, left turning point					t0_sled = sled_recal()					state_eye = "NO_FIXATE"			elif state_phase == "LEFT": # Left				if position[0][0,0] > -0.1495:					#start sled timer at correct phase, left turning point					t0_sled = sled_recal()					state_eye = "NO_FIXATE"						if state_eye == "NO_FIXATE":				a = a + 1				if a > 20:					#turn OFF all LEDs, turns ON FP					LEDb = Ledl[1000]					ser.write(struct.pack('B',LEDb))					drift_corr(ser)			print "Position ({} meter)".format(position[0][0,0])			print "state_eye:",state_eye			l.append(position[0][0,0])			l.append(state_eye)			if state_eye == "END_FIXATE":						######need to check if light flhashed and whether they looked						#Sends a signal to the LED								LEDb = Ledl[stim]				ser.write(struct.pack('B',LEDb))				getEYELINK().sendMessage("DISPLAY ON");#to calculate reaction time				t0_to_saccade = client.time()				while (client.time() - t0_to_saccade) < 0.70: #checks whether the subject makes a saccade within 700 ms					gaze_position = gaze_pos()					#checks whether subject looked to the lEFT LED (+/- 32 pixels of 87)					if gaze_position[0] < (LP[0] + Tp) and gaze_position[0] > (LP[0] - Tp):						response = 0						#turn OFF all LEDs, turns ON FP						LEDb = Ledl[1000]						ser.write(struct.pack('B',LEDb))						state_eye = "SACCADE"						print "state_eye:", state_eye						l.append(state_eye)						if state_phase == "RIGHT": # Right:							p = minimizer1.addMeasurement(response,stim)							state_phase = "LEFT"						elif state_phase == "LEFT": # Left:							p = minimizer2.addMeasurement(response,stim)							state_phase = "RIGHT"						break;					#checks whether subject looked to the RIGHT LED (+/- 22 pixels of 263)					elif gaze_position[0] > (RP[0] - Tp) and gaze_position[0] < (RP[0] + Tp):						response = 1						#turn OFF all LEDs, turns ON FP						LEDb = Ledl[1000]						ser.write(struct.pack('B',LEDb))						state_eye = "SACCADE"						print "state_eye:",state_eye						l.append(state_eye)						if state_phase == "RIGHT": # Right:							p = minimizer1.addMeasurement(response,stim)							state_phase = "LEFT"						elif state_phase == "LEFT": # Left:							p = minimizer2.addMeasurement(response,stim)							state_phase = "RIGHT"						break;				if state_eye == "SACCADE":					break;				#turn OFF all LEDs, turns ON FP				LEDb = Ledl[1000]				ser.write(struct.pack('B',LEDb))				state_eye = "NO_FIXATE"				print "state_eye:",state_eye				l.append(state_eye)					#turn OFF all LEDs	LEDb = Ledl[3000]	ser.write(struct.pack('B',LEDb))	ser.close()	time.sleep(0.5)	client.sendCommand("Sinusoid Stop")	time.sleep(0.5)	client.sendCommand("Bye")	client.__del__()	# get all the data we collected from Psi	data1 = minimizer1.getData()	data2 = minimizer2.getData()	#mu, sigma = minimizer.getTheta()	np.savetxt('data1.txt',data1)	np.savetxt('data2.txt',data2)	#XY = minimizer.getXY()	file = open('list.txt','a')	for x in range(len(l)):		file.write(str(l[x])+'\n')	file.close()	end_trial();		#The TRIAL_RESULT message defines the end of a trial for the EyeLink Data Viewer. 	#This is different than the end of recording message END that is logged when the trial recording ends. 	#Data viewer will not parse any messages, events, or samples that exist in the data file after this message. 	getEYELINK().sendMessage("TRIAL_RESULT %d"%(buttons[0]));        return getEYELINK().getRecordingStatus()        trial_condition = ["Block 1", "Block 2", "Block 3", "Block 4 "];		def do_trial(trial):	'''Does the simple trial'''	#This supplies the title at the bottom of the eyetracker display	message ="record_status_message 'Trial %d %s'"%(trial+1, trial_condition[trial])	getEYELINK().sendCommand(message);			#Always send a TRIALID message before starting to record.	#EyeLink Data Viewer defines the start of a trial by the TRIALID message.  	#This message is different than the start of recording message START that is logged when the trial recording begins. 	#The Data viewer will not parse any messages, events, or samples, that exist in the data file prior to this message.	msg = "TRIALID %s"%trial_condition[trial];	getEYELINK().sendMessage(msg);		#The following does drift correction at the begin of each trial	while 1:		# Checks whether we are still connected to the tracker		if not getEYELINK().isConnected():			return ABORT_EXPT;					# Does drift correction and handles the re-do camera setup situations		try:                        #print surf.get_rect().w/2,surf.get_rect().h/2#at.LED_dict(1000) #turn On FP LED			error = getEYELINK().doDriftCorrect(FP[0],FP[1],1,1)			if error != 27: 				break;			else:				getEYELINK().doTrackerSetup();		except:			break #getEYELINK().doTrackerSetup()	raw_input("Press any key to start recording")	#connect to Arduino	ser = serial.Serial('COM15', 115200) 	time.sleep(5)		#start sled timer at correct phase, left turning point	t0_sled = sled_recal()		error = getEYELINK().startRecording(1,1,1,1)	if error:		return error;	gc.disable();	#begin the realtime mode	pylink.beginRealTimeMode(100)	if not getEYELINK().waitForBlockStart(1000, 1, 0):		end_trial();		print "ERROR: No link samples received!";      		return TRIAL_ERROR;      	  		t0_eyelink = currentTime()		getEYELINK().sendMessage("SYNCTIME %d"%(currentTime()-t0_eyelink));	ret_value = drawgc(t0_sled, ser);	pylink.endRealTimeMode();	gc.enable();	return ret_value;				NTRIALS = 1def run_trials():	''' This function is used to run individual trials and handles the trial return values. '''	''' Returns a successful trial with 0, aborting experiment with ABORT_EXPT (3); It also handles	the case of re-running a trial. '''	#Do the tracker setup at the beginning of the experiment.	getEYELINK().doTrackerSetup()			for trial in range(NTRIALS):		if(getEYELINK().isConnected() ==0 or getEYELINK().breakPressed()): break;		while 1:			ret_value = do_trial(trial)			endRealTimeMode()					if (ret_value == TRIAL_OK):				getEYELINK().sendMessage("TRIAL OK");				break;			elif (ret_value == SKIP_TRIAL):				getEYELINK().sendMessage("TRIAL ABORTED");				break;						elif (ret_value == ABORT_EXPT):				getEYELINK().sendMessage("EXPERIMENT ABORTED")				return ABORT_EXPT;			elif (ret_value == REPEAT_TRIAL):				getEYELINK().sendMessage("TRIAL REPEATED");			else: 				getEYELINK().sendMessage("TRIAL ERROR")				break;					return 0;		