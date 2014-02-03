#modified from exp_trial.py to detect saccades based on velocity and not positionfrom pylink import *import timeimport gcimport sysimport root_luc as root import numpy as npfrom scipy import statsimport serialimport structimport math#Aurduino controls#check the platform#if sys.platform == 'linux': #linux#elif sys.platform == 'darwin': #mac osx#ser = serial.Serial('/dev/tty.usbserial-A600esYq', 115200) #elif sys.platform == 'win32': #windows#if ser.isOpen():#ser.close()#ser = serial.Serial('COM15', 115200) #time.sleep(5)RIGHT_EYE = 1LEFT_EYE = 0BINOCULAR = 2#LED coordinates#calibration_targets = (99.5,180 187.5,180 275.5,180)FP = (175,93)LP = (87,93)RP = (263, 93)Tp = 32 # therhold mmRTs = 0.60 #reaction time theshold	def end_trial(ser = None, minimizer = None, l = None,l_time = None,l_res = None,l_trial = None,l_stim = None,l_RT = None ):		'''Ends recording: adds 100 msec of data to catch final events'''	print "went to end_trial"		if ser != None:		#LEDb = Ledl[3000]		#ser.write(struct.pack('B',LEDb))		ser.close()		time.sleep(0.5)		print "ser close: close connection to Arduino"				if minimizer != None:		# get all the data we collected from Psi		data = minimizer.getData()		#mu, sigma = minimizer.getTheta()		np.savetxt('data.txt',data)				if l != None:		l.append("FP")		l.append(FP)		l.append("LP")		l.append(LP)		l.append("RP")		l.append(RP)		l.append("Tp")		l.append(Tp)		l.append("RTs")		l.append(RTs)		file = open('list.txt','a')		for x in range(len(l)):		    file.write(str(l[x])+'\n')		file.close()		if l_RT != None:		file = open('exp_list.txt','a')		file.write('trial#'+'\t'+'time(ms)'+'\t'+'RT(ms)'+'\t'+'response(1=R,0=L)'+'\t'+'stim'+'\n')		for x in range(len(l_RT)):			file.write(str(l_trial[x])+'\t'+str(l_time[x])+'\t'+str(l_RT[x])+'\t'+str(l_res[x])+'\t'+str(l_stim[x])+'\n')		file.close()	pylink.endRealTimeMode();  	pumpDelay(100);       	getEYELINK().stopRecording();	while getEYELINK().getkey() : 		pass;            def gaze_pos():        '''Calculates gaze position '''	eye_used = getEYELINK().eyeAvailable(); #determine which eye(s) are available 	if eye_used == RIGHT_EYE:		eye_used = RIGHT_EYE;		#getEYELINK().sendMessage("EYE_USED 1 RIGHT");	elif eye_used == LEFT_EYE or eye_used == BINOCULAR:		#getEYELINK().sendMessage("EYE_USED 0 LEFT");  		eye_used = LEFT_EYE;  	else:  		print "Error in getting the eye information!";  		return TRIAL_ERROR;	dt = getEYELINK().getNewestSample() # check for new sample update		if(dt != None):		# Gets the gaze position of the latest sample,		if eye_used == RIGHT_EYE and dt.isRightSample():			gaze_position = dt.getRightEye().getGaze()			gaze_position_time = currentTime()		elif eye_used == LEFT_EYE and dt.isLeftSample():			gaze_position = dt.getLeftEye().getGaze()			gaze_position_time = currentTime()                        		return gaze_position, gaze_position_timedef drift_corr(ser):		''' Does drift correction and handles the re-do camera setup situations'''	pylink.endRealTimeMode();    	pumpDelay(100);        	getEYELINK().stopRecording(); 	print "stopRecording"	print "Drift correction";	error = getEYELINK().doDriftCorrect(FP[0],FP[1],1,1)	if error == 27:		print "Recalibrate, ser connection closed";		ser.close()		getEYELINK().doTrackerSetup();        #ser = serial.Serial('/dev/tty.usbserial-A600esYq', 115200)		ser = serial.Serial('COM15', 115200) 		time.sleep(5)		error = getEYELINK().startRecording(1,1,1,1)	print "startRecording"	if error:		return error;	gc.disable();	#begin the realtime mode	pylink.beginRealTimeMode(100)	if not getEYELINK().waitForBlockStart(1000, 1, 0):		end_trial();		print "ERROR: No link samples received!";	t0_eyelink = currentTime()	getEYELINK().sendMessage("SYNCTIME %d"%(currentTime()-t0_eyelink));	print "sleep for 2 seconds"	time.sleep(2)	def drawgc(ser):	'''Sends a stimulus to the Arduino; uses the getNewestSample() to get subjects response; uses the response the calculate the SOA and thus the next stimulus '''			print "in drawgc"			l = [] #creates an empty list to get the positions	l_time = []	l_res = []	l_trial = []	l_stim = []	l_RT = [] 			#stimulus ranges from -250:-2 in steps of 2ms, and from 2:250 in steps of 2ms	Ledl = dict(zip(range(-2,-251,-2),range(4,129)))	Ledl.update(dict(zip(range(2,251,2),range(130,255))))	Ledl.update({1000:0})	Ledl.update({3000:3})			#variables for root function	i = 0	x = np.linspace(-250,-2,125)	x1=np.linspace(2,250,125)	x=np.append(x,x1)			# turns the LEDs OFF	LEDb = Ledl[3000]	ser.write(struct.pack('B',LEDb)) 	# turns the FP LED ON	LEDb = Ledl[1000]	ser.write(struct.pack('B',LEDb))   			minimizer = root.Psi(-250,250,x,np.linspace(-200,200,41),np.linspace(0.1, 100,41))         # make a kontsevic root finder with a range from 0 to 2	#stimr=np.array([-250, -200, -150, -100, -50, 50, 100, 150, 200, 250])	stimr=np.array([200,-150,100,-200,-250,150,-100,250,200,-150,100,-200,-250,150,-100,250,200,-150,100,-200,-250,150,-100,250,200,-150,100,-200,-250,150,-100,250])	np.random.shuffle(stimr)	size_stimr = len(stimr)	####################### size is 32, so first 32 trials per eye come from this one!					getEYELINK().flushKeybuttons(0)	buttons =(0, 0);						while 1:		error = getEYELINK().isRecording()  # First check if recording is aborted  					if error!=0:			end_trial(ser, minimizer, l,l_time,l_res,l_trial,l_stim,l_RT);			return error				if i>132:  #finishes the trial after 30 iterations			#print "timeout"			getEYELINK().sendMessage("TIMEOUT");			end_trial(ser, minimizer, l,l_time,l_res,l_trial,l_stim,l_RT);			buttons =(0, 0);			break;				if(getEYELINK().breakPressed()):	# Checks for program termination or ALT-F4 or CTRL-C keys			end_trial(ser, minimizer, l,l_time,l_res,l_trial,l_stim,l_RT);			return ABORT_EXPT				elif(getEYELINK().escapePressed()): # Checks for local ESC key to abort trial (useful in debugging)			end_trial(ser, minimizer, l,l_time,l_res,l_trial,l_stim,l_RT);			return SKIP_TRIAL				buttons = getEYELINK().getLastButtonPress() # Checks for eye-tracker buttons pressed				if(buttons[0] != 0):			getEYELINK().sendMessage("ENDBUTTON %d"%(buttons[0]));			end_trial(ser, minimizer, l,l_time,l_res,l_trial,l_stim,l_RT);			break;		###########EXPERIMENT STARTS##############################################		l.append(i)		print "trial:", i		#starts the root/LED experiment					if i < size_stimr:			stim = np.round(stimr[i])			i = i + 1						else:			stim = minimizer()  			i = i + 1						state_eye = "NO_FIXATE"		print "state_eye:", state_eye		l.append(state_eye)						while 1:			if(getEYELINK().escapePressed()): # Checks for local ESC key to abort trial (useful in debugging)				print "pressed ESC"				end_trial(ser, minimizer, l,l_time,l_res,l_trial,l_stim,l_RT);				return SKIP_TRIAL				break						while 1:				gaze_position1, gaze_position_time1 = gaze_pos()				print "gaze_position1",gaze_position1				print "gaze_position_time1",gaze_position_time1				gaze_position2, gaze_position_time2 = gaze_pos()				print "gaze_position2",gaze_position2				print "gaze_position_time2",gaze_position_time2				diff_gaze_position = gaze_position2[0] - gaze_position1[0]				print "diff_gaze_position",diff_gaze_position				diff_gaze_position_time = gaze_position_time2 - gaze_position_time1				print "diff_gaze_position_time",diff_gaze_position_time				vel = 1.*diff_gaze_position/diff_gaze_position_time				print "vel",vel				raw_input("Press any key to continue")							#Determines if subject is fixating, +/- 32 pixels of 175				if vel < 2.0 and vel > -2.0:					if state_eye == "NO_FIXATE":						state_eye = "START_FIXATE"						t0_FP = time.time()						lsac = []						lsac.append(gaze_position2[0])					elif state_eye == "START_FIXATE":						lsac.append(gaze_position2[0])                		#		checks whether the subject has fixated for 500ms						if (time.time() - t0_FP) >= 0.50:							state_eye = "END_FIXATE"							break				else:					state_eye = "NO_FIXATE"					#t0_FP0 = time.time()					#if (time.time() - t0_FP0) >= 2:					#turn OFF all LEDs, turns ON FP			    		#LEDb = Ledl[1000]			    		#ser.write(struct.pack('B',LEDb))			    		#drift_corr(ser)			    		#break						if state_eye ==	"START_FIXATE":				state_eye = "NO_FIXATE"                                			print "state_eye:",state_eye			l.append(state_eye)			if state_eye == "END_FIXATE":				#Sends a signal to the LED				LEDb = Ledl[stim]				ser.write(struct.pack('B',LEDb))				getEYELINK().sendMessage("DISPLAY ON");#to calculate reaction time				t0_to_saccade = time.time()				l.append(t0_to_saccade)								while (time.time() - t0_to_saccade) < RTs: #checks whether the subject makes a saccade within 700 ms					gaze_position1, gaze_position_time1 = gaze_pos()					gaze_position2, gaze_position_time2 = gaze_pos()					diff_gaze_position = gaze_position2[0] - gaze_position1[0]					diff_gaze_position_time = gaze_position_time2 - gaze_position_time1					vel = 1.*diff_gaze_position/diff_gaze_position_time					pos_threshold = sum(lsac)/len(lsac) #gets the average position during fixation to get rid of drift                        					#checks whether subject looked to the lEFT LED (+/- 32 pixels of 87)					if vel < -2.0 and (gaze_position2[0] < (pos_threshold - 52.8)):						response = 0						t_saccade = time.time()						ser.write(struct.pack('B',LEDb))						state_eye = "SACCADE"						print "state_eye:", state_eye						break;					#checks whether subject looked to the RIGHT LED (+/- 22 pixels of 263)					if vel > 2.0 and (gaze_position2[0] > (pos_threshold + 52.8)):						response = 1						t_saccade = time.time()						ser.write(struct.pack('B',LEDb))						state_eye = "SACCADE"						print "state_eye:",state_eye						break;                        				if state_eye == "SACCADE":        					p = minimizer.addMeasurement(response,stim)					RT_saccade = t_saccade - t0_to_saccade					l_time.append(t0_to_saccade)					l_RT.append(RT_saccade)					l_res.append(response)					l_trial.append(i)					l_stim.append(stim)					break;								#turn OFF all LEDs, turns ON FP				time.sleep(0.2)				LEDb = Ledl[1000]				ser.write(struct.pack('B',LEDb))				state_eye = "NO_FIXATE"				print "state_eye:",state_eye				l.append(state_eye)                          	#The TRIAL_RESULT message defines the end of a trial for the EyeLink Data Viewer. 	#This is different than the end of recording message END that is logged when the trial recording ends. 	#Data viewer will not parse any messages, events, or samples that exist in the data file after this message. 	getEYELINK().sendMessage("TRIAL_RESULT %d"%(buttons[0]));	return getEYELINK().getRecordingStatus()        trial_condition = ["Block 1", "Block 2", "Block 3", "Block 4 "];	def do_trial(trial):	'''Does the simple trial'''							#This supplies the title at the bottom of the eyetracker display	message ="record_status_message 'Trial %d %s'"%(trial+1, trial_condition[trial])	getEYELINK().sendCommand(message);									#Always send a TRIALID message before starting to record.	#EyeLink Data Viewer defines the start of a trial by the TRIALID message.  	#This message is different than the start of recording message START that is logged when the trial recording begins. 	#The Data viewer will not parse any messages, events, or samples, that exist in the data file prior to this message.	msg = "TRIALID %s"%trial_condition[trial];	getEYELINK().sendMessage(msg);						#The following does drift correction at the begin of each trial	while 1:		# Checks whether we are still connected to the tracker		if not getEYELINK().isConnected():			return ABORT_EXPT;					# Does drift correction and handles the re-do camera setup situations		try:                        #print surf.get_rect().w/2,surf.get_rect().h/2#at.LED_dict(1000) #turn On FP LED			error = getEYELINK().doDriftCorrect(FP[0],FP[1],1,1)			if error != 27: 				break;			else:				getEYELINK().doTrackerSetup();		except:			break #getEYELINK().doTrackerSetup()	raw_input("Press any key to start recording")	#connect to Arduino	ser = serial.Serial('COM15', 115200)	#ser = serial.Serial('/dev/tty.usbserial-A600esYq', 115200)	time.sleep(5)	error = getEYELINK().startRecording(1,1,1,1)	print error	if error:            return error;	gc.disable();	#begin the realtime mode	pylink.beginRealTimeMode(100)	if not getEYELINK().waitForBlockStart(1000, 1, 0):		end_trial(ser);		print "ERROR: No link samples received!";      		return TRIAL_ERROR;	t0_eyelink = currentTime()	getEYELINK().sendMessage("SYNCTIME %d"%(currentTime()-t0_eyelink));	ret_value = drawgc(ser);	pylink.endRealTimeMode();	gc.enable();	return ret_value;NTRIALS = 1def run_trials():	''' This function is used to run individual trials and handles the trial return values. '''	''' Returns a successful trial with 0, aborting experiment with ABORT_EXPT (3); It also handles	the case of re-running a trial. '''	#Do the tracker setup at the beginning of the experiment.	getEYELINK().doTrackerSetup()	for trial in range(NTRIALS):		if(getEYELINK().isConnected() ==0 or getEYELINK().breakPressed()): break;		while 1:			ret_value = do_trial(trial)			endRealTimeMode()			if (ret_value == TRIAL_OK):				getEYELINK().sendMessage("TRIAL OK");				break;			elif (ret_value == SKIP_TRIAL):				getEYELINK().sendMessage("TRIAL ABORTED");				break;						elif (ret_value == ABORT_EXPT):				getEYELINK().sendMessage("EXPERIMENT ABORTED")				return ABORT_EXPT;			elif (ret_value == REPEAT_TRIAL):				getEYELINK().sendMessage("TRIAL REPEATED");			else: 				getEYELINK().sendMessage("TRIAL ERROR")				break;	return 0;