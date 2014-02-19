##modified from exp_trial_sled4c.py to add catch trials, breaks, and more trials##from pylink import *import timeimport winsound #####for WINDOWS ONLYimport gcimport sysimport root_luc1 as root1 import root_luc2 as root2import root_luc3 as root3 #ADDED THIS FOR THE 0 SLED PHASEimport root_luc4 as root4 #ADDED THIS FOR THE 0 SLED PHASEimport numpy as npimport serialimport mathimport structimport signalsys.path.append('C:/Users/DCC-User/Documents/GitHub/Rudolph')from sledclient import SledClient##SLED##client = SledClient()client.connect('sled', 3375)# Start streaming positionsclient.startStream()time.sleep(2)client.sendCommand("Lights Off")#go to -0.15client.goto(-0.15)time.sleep(2.5)raw_input("Press any key to continue and START sinusoid")#start Sledclient.sendCommand("Sinusoid Start 0.15 1.6")RIGHT_EYE = 1LEFT_EYE = 0BINOCULAR = 2#LED coordinates#calibration_targets = (99.5,180 187.5,180 275.5,180)FP = (175,93)LP = (87,93)RP = (263, 93)Tp = 60 # therhold mmRTs = 0.60 #reaction time theshold#getEYELINK().sendMessage("Calibration targets FP: %d, LP: %d, RP: %d"%(FP[0], LP[0], RP[0]));#getEYELINK().sendMessage("Fixation Therhold +/- %d"%(Tp));#getEYELINK().sendMessage("RT Therhold +/- %d"%(RTs));def end_trial(ser = None, minimizer1 = None, minimizer2 = None, minimizer3 = None, minimizer4 = None, l = None,l_pos = None,l_pos1 = None,l_time = None,l_res = None,l_phase=None,l_trial = None,l_stim = None,l_RT = None,l_vel=None ):	'''Ends recording: adds 100 msec of data to catch final events'''  	print "went to end_trial"	client.sendCommand("Sinusoid Stop")	time.sleep(1.7)	client.sendCommand("Bye")	client.__del__()		if ser != None:		#LEDb = Ledl[3000]		#ser.write(struct.pack('B',LEDb))		ser.close()		time.sleep(0.5)		print "ser close: close connection to Arduino"				if minimizer1 != None:		# get all the data we collected from Psi		data1 = minimizer1.getData()		data2 = minimizer2.getData()		data3 = minimizer3.getData()		data4 = minimizer4.getData()		#mu, sigma = minimizer.getTheta()		np.savetxt('data1.txt',data1)		np.savetxt('data2.txt',data2)		np.savetxt('data3.txt',data3)		np.savetxt('data4.txt',data4)				if l != None:		l.append("FP")		l.append(FP)		l.append("LP")		l.append(LP)		l.append("RP")		l.append(RP)		l.append("Tp")		l.append(Tp)		l.append("RTs")		l.append(RTs)		file = open('list.txt','a')		for x in range(len(l)):			file.write(str(l[x])+'\n')		file.close()		if l_pos1 != None:		file = open('exp_list.txt','a')		file.write('trial#'+'\t'+'phase(1=R,0=L)'+'\t'+'sled pos(mm)'+'\t'+'time(ms)'+'\t'+'sled pos1(mm)'+'\t'+'RT(ms)'+'\t'+'response(1=R,0=L)'+'\t'+'stim'+'\n')		for x in range(len(l_pos1)):			file.write(str(l_trial[x])+'\t'+str(l_phase[x])+'\t'+str(l_pos[x])+'\t'+str(l_time[x])+'\t'+str(l_pos1[x])+'\t'+str(l_RT[x])+'\t'+str(l_res[x])+'\t'+str(l_stim[x])+'\n')		file.close()		if l_vel != None:		file = open('vel_list.txt','a')		for x in range(len(l_vel)):			file.write(str(l_vel[x])+'\n')		file.close()	pylink.endRealTimeMode();    	pumpDelay(100);        	getEYELINK().stopRecording(); 	while getEYELINK().getkey() :  	 	pass;def sled_phase(state_phase, t0_sled):	'''Determines sled direction and phase '''		T = 1.6 # period		#Get time	time_now = client.time() - t0_sled	#claculate where in the cycle we are	time_cycle = time_now/T	mantissa = math.floor(time_cycle)	fraction = time_cycle - mantissa		if state_phase == "RIGHT": #RIGHT TURNING POINT 		if fraction < 0.5:			time_to_stim = (mantissa)*T + 0.8 + T		elif fraction > 0.5:			time_to_stim = (mantissa + 1)*T + 0.8 				if state_phase == "MIDDLE-LEFT": # LEFT TURNING POINT		if fraction < 0.5:			time_to_stim = (mantissa)*T + 0.8 + T + 0.4 #from right		elif fraction > 0.5:			time_to_stim = (mantissa + 1)*T + 0.8 + 0.4 #from right			if state_phase == "LEFT": # LEFT TURNING POINT		if fraction < 0.5:			time_to_stim = (mantissa)*T + 1.6 		elif fraction > 0.5:			time_to_stim = (mantissa + 1)*T + T				if state_phase == "MIDDLE-RIGHT": #RIGHT TURNING POINT 		if fraction < 0.5:			time_to_stim = (mantissa)*T + 1.6 + 0.4 #from Left		elif fraction > 0.5:			time_to_stim = (mantissa + 1)*T + T + 0.4#from Left				return time_to_stimdef sled_recal():	'''Recalibrates the timer associated with the sinusoid phases'''	while 1:		position = client.getPosition()		if position[0][0,0]<-.14990:			t0_sled = client.time()			break	return t0_sleddef gaze_pos():	'''Calculates gaze position '''	eye_used = getEYELINK().eyeAvailable(); #determine which eye(s) are available 	if eye_used == RIGHT_EYE:  		eye_used = RIGHT_EYE;		#getEYELINK().sendMessage("EYE_USED 1 RIGHT");	elif eye_used == LEFT_EYE or eye_used == BINOCULAR:		#getEYELINK().sendMessage("EYE_USED 0 LEFT");  		eye_used = LEFT_EYE;  	else:  		print "Error in getting the eye information!";  		return TRIAL_ERROR;	dt = getEYELINK().getNewestSample() # check for new sample update	gaze_position = None	gaze_position_time = None	#print dt	if(dt != None):		# Gets the gaze position of the latest sample,		if eye_used == RIGHT_EYE and dt.isRightSample():			gaze_position = dt.getRightEye().getGaze()			gaze_position_time = dt.getTime()		elif eye_used == LEFT_EYE and dt.isLeftSample():			gaze_position = dt.getLeftEye().getGaze()			gaze_position_time = dt.getTime()                         		return gaze_position, gaze_position_timedef calc_vel():	"""calculates velocity between two samples"""	while 1:		gaze_position_time1 = None		gaze_position1 = None		while gaze_position1 == None or abs(gaze_position1) > 5000:			gaze_position1, gaze_position_time1 = gaze_pos()		#print "gaze_position1",gaze_position1		#print "gaze_position_time1",gaze_position_time1		gaze_position_time2 = None		gaze_position2 = None		while gaze_position2 == None:			gaze_position2, gaze_position_time2 = gaze_pos()		while gaze_position_time2 == gaze_position_time1:			gaze_position2, gaze_position_time2 = gaze_pos()		while abs(gaze_position2) > 5000:			gaze_position2, gaze_position_time2 = gaze_pos()		if gaze_position_time2 - gaze_position_time1 > 10.00:			continue		#print "gaze_position2",gaze_position2		#print "gaze_position_time2",gaze_position_time2					diff_gaze_position = gaze_position2[0] - gaze_position1[0]		diff_gaze_position_time = gaze_position_time2 - gaze_position_time1		velocity = 1.*diff_gaze_position/diff_gaze_position_time		break		#print "velocity",velocity		#raw_input("Press any key to continue")	return velocity, gaze_position2def drift_corr(ser, pause = None):	''' Does drift correction and handles the re-do camera setup situations'''		client.sendCommand("Lights On")	time.sleep(2)	client.sendCommand("Lights Off")		pylink.endRealTimeMode();    	pumpDelay(100);        	getEYELINK().stopRecording(); 	print "stopRecording"		if pause != None:		raw_input("Press any key to STOP Sinusoid")		client.sendCommand("Sinusoid Stop")		client.sendCommand("Lights On")		raw_input("Ready to continue the experiment?")		client.sendCommand("Lights Off")		#go to -0.15		client.goto(-0.15)		time.sleep(2.5)		raw_input("Press any key to continue and START sinusoid")		#start Sled		client.sendCommand("Sinusoid Start 0.15 1.6")		print "Drift correction";	error = getEYELINK().doDriftCorrect(FP[0],FP[1],1,1)	if error == 27:		print "Recalibrate, ser connection closed";		ser.close()		getEYELINK().doTrackerSetup();		ser = serial.Serial('COM15', 115200) 		time.sleep(5)		error = getEYELINK().startRecording(1,1,1,1)	print "startRecording"	if error:		return error;	gc.disable();	#begin the realtime mode	pylink.beginRealTimeMode(100)	if not getEYELINK().waitForBlockStart(1000, 1, 0):		end_trial();		print "ERROR: No link samples received!";	t0_eyelink = currentTime()	getEYELINK().sendMessage("SYNCTIME %d"%(currentTime()-t0_eyelink));	print "sleep for 2 seconds"	time.sleep(2)			def drawgc(t0_sled, ser):	'''Sends a stimulus to the Arduino; uses the getNewestSample() to get subjects response; uses the response the calculate the SOA and thus the next stimulus '''	l = [] #creates an empty list to get the positions	l_pos = []	l_pos1 = []	l_time = []	l_res = []	l_phase = []	l_trial = []	l_stim = []	l_RT = []	l_vel = []		#stimulus ranges from -250:-2 in steps of 2ms, and from 2:250 in steps of 2ms	Ledl = dict(zip(range(-2,-251,-2),range(4,129)))	Ledl.update(dict(zip(range(2,251,2),range(130,255))))	Ledl.update({1000:0}) #fixation point	Ledl.update({3000:3}) #all OFF	Ledl.update({2000:255}) #Right LED ON and FP on	Ledl.update({1111:129}) #Left LED ON and FP on		#initializes the state of the catch LED	state_catch = "RIGHT"	#initializes the state phase	state_phase = "RIGHT"	#variables for root function	i = 0	j = 0	ii = 0	jj = 0	ij = -1	ij_c = 25 # catch trials every 25 trials	ij_b = 100 # a new block every 100 trials	x = np.linspace(-250,-2,125)	x1=np.linspace(2,250,125)	x=np.append(x,x1)	# turns the LEDs OFF	LEDb = Ledl[3000]	ser.write(struct.pack('B',LEDb)) 	# turns the FP LED ON	LEDb = Ledl[1000]	ser.write(struct.pack('B',LEDb))		minimizer1 = root1.Psi(-250,250,x,np.linspace(-200,200,41),np.linspace(0.1, 100,41))         # make a kontsevic root finder with a range from 0 to 2	minimizer2 = root2.Psi(-250,250,x,np.linspace(-200,200,41),np.linspace(0.1, 100,41))         # make a kontsevic root finder with a range from 0 to 2	minimizer3 = root3.Psi(-250,250,x,np.linspace(-200,200,41),np.linspace(0.1, 100,41))	minimizer4 = root4.Psi(-250,250,x,np.linspace(-200,200,41),np.linspace(0.1, 100,41)) 	#stimr=np.array([-250, -200, -150, -100, -50, 50, 100, 150, 200, 250])	stimr=np.array([-250,-200,100,150,-150,-50,50,-100,200,250,-150,-250,150,-200,-50,50,200,100,-100,250,150,50,100,-100,250,-250,-50,200,-150,-200,50,-50,-200,150,200,-100,250,-250,100,-150])	#np.random.shuffle(stimr)	size_stimr = len(stimr) #44	####################### size is 32, so first 32 trials per eye come from this one!		getEYELINK().flushKeybuttons(0)	buttons =(0, 0);	while 1:		error = getEYELINK().isRecording()  # First check if recording is aborted 		if error!=0:			end_trial(ser, minimizer1, minimizer2,minimizer3,minimizer4, l,l_pos,l_pos1,l_time,l_res,l_phase,l_trial,l_stim,l_RT,l_vel);			return error		if ij>700:  #finishes the block but make sure to add stimr!			#print "timeout"			getEYELINK().sendMessage("TIMEOUT");			end_trial(ser, minimizer1, minimizer2,minimizer3,minimizer4, l,l_pos,l_pos1,l_time,l_res,l_phase,l_trial,l_stim,l_RT,l_vel);			buttons =(0, 0);			break;		if(getEYELINK().breakPressed()):	# Checks for program termination or ALT-F4 or CTRL-C keys			print "pressed CTRL C"			end_trial(ser, minimizer1, minimizer2,minimizer3,minimizer4, l,l_pos,l_pos1,l_time,l_res,l_phase,l_trial,l_stim,l_RT,l_vel);			return ABORT_EXPT		elif(getEYELINK().escapePressed()): # Checks for local ESC key to abort trial (useful in debugging)			print "pressed ESC"			end_trial(ser, minimizer1, minimizer2,minimizer3,minimizer4, l,l_pos,l_pos1,l_time,l_res,l_phase,l_trial,l_stim,l_RT,l_vel);			return SKIP_TRIAL		buttons = getEYELINK().getLastButtonPress() # Checks for eye-tracker buttons pressed		if(buttons[0] != 0):			getEYELINK().sendMessage("ENDBUTTON %d"%(buttons[0]));			end_trial(ser, minimizer1, minimizer2,minimizer3,minimizer4, l,l_pos,l_pos1,l_time,l_res,l_phase,l_trial,l_stim,l_RT,l_vel);			break;		###########EXPERIMENT STARTS##############################################		print "state_phase:", state_phase		l.append(state_phase)		#starts the root/LED experiment				ij = ij + 1		if ij == ij_b:			pause = 1			LEDb = Ledl[1000]			ser.write(struct.pack('B',LEDb))			drift_corr(ser, pause)			ij_b = ij_b + 100				if ij == ij_c:			if state_catch == "RIGHT":				stim = 2000			elif state_catch == "LEFT":				stim = 1111					elif state_phase == "RIGHT": # Right			print "trial:", i			l.append(i)			if i < size_stimr:				stim = np.round(stimr[i])				i = i + 1			else:				stim = minimizer1()  				i = i + 1		elif state_phase == "MIDDLE-LEFT": # MIDDLE			print "trial:", ii			l.append(ii)			if ii < size_stimr:				stim = np.round(stimr[ii])				ii = ii + 1			else:				stim = minimizer3()  				ii = ii + 1		elif state_phase == "LEFT": # Left			print "trial:", j			l.append(j)			if j < size_stimr:				stim = np.round(stimr[j])				j = j + 1			else:				stim = minimizer2()  				j = j + 1		elif state_phase == "MIDDLE-RIGHT": # Left			print "trial:", jj			l.append(jj)			if jj < size_stimr:				stim = np.round(stimr[jj])				jj = jj + 1			else:				stim = minimizer4()  				jj = jj + 1				l.append(ij)		print ij		state_eye = "NO_FIXATE"		print "state_eye:", state_eye		l.append(state_eye)		a = 1 # this is for a counter to set drift correct				while 1:			if(getEYELINK().escapePressed()): # Checks for local ESC key to abort trial (useful in debugging)				print "pressed ESC"				end_trial(ser, minimizer1, minimizer2,minimizer3,minimizer4, l,l_pos,l_pos1,l_time,l_res,l_phase,l_trial,l_stim,l_RT,l_vel);				return SKIP_TRIAL				break						#calcultes the time to the next phase based on the state_phase			time_to_stim = sled_phase(state_phase, t0_sled)			#getEYELINK().sendMessage("DISPLAY OFF")			print "time_to_stim:", time_to_stim			l.append(time_to_stim)						while (client.time() - t0_sled) < (time_to_stim):				#calculates the velocity from two samples				vel = None				gaze_position2 = None				vel,gaze_position2 = calc_vel()				l_vel.append(vel)							#Determines if subject is fixating, 				if vel < 2.0 and vel > -2.0:					if gaze_position2[0] > (FP[0] - Tp) and gaze_position2[0] < (FP[0] + Tp):						if state_eye == "NO_FIXATE":							state_eye = "START_FIXATE"							t0_FP = client.time()							lsac = []							lsac.append(gaze_position2[0])						elif state_eye == "START_FIXATE":							lsac.append(gaze_position2[0])							#checks whether the subject has fixated for 500ms							if (client.time() - t0_FP) >= 0.50:								state_eye = "END_FIXATE"				else:					state_eye = "NO_FIXATE"							if state_eye ==	"START_FIXATE":				state_eye = "NO_FIXATE"			position = client.getPosition()			if state_phase == "RIGHT": # Right				if position[0][0,0] < 0.1495 :					#start sled timer at correct phase, left turning point					t0_sled = sled_recal()					state_eye = "NO_FIXATE"			elif state_phase == "LEFT": # Left				if position[0][0,0] > -0.1495:					#start sled timer at correct phase, left turning point					t0_sled = sled_recal()					state_eye = "NO_FIXATE"						if state_eye == "NO_FIXATE":				LEDb = Ledl[3000]				ser.write(struct.pack('B',LEDb)) #turns OFF all LEDs				LEDb = Ledl[1000]				ser.write(struct.pack('B',LEDb)) #turns ON FP				a = a + 1				if a > 20:					#turn OFF all LEDs, turns ON FP					LEDb = Ledl[1000]					ser.write(struct.pack('B',LEDb))					drift_corr(ser)					a = 1			print "Position ({} meter)".format(position[0][0,0])			print "state_eye:",state_eye			l.append(position[0][0,0])			l.append(state_eye)			if state_eye == "END_FIXATE":								#Sends a signal to the LED								LEDb = Ledl[stim]				ser.write(struct.pack('B',LEDb))				getEYELINK().sendMessage("DISPLAY ON");#to calculate reaction time				t0_to_saccade = client.time()				l.append(t0_to_saccade)				l_vel.append(t0_to_saccade)				while (client.time() - t0_to_saccade) < RTs: #checks whether the subject makes a saccade within 700 ms					#calculates the velocity from two samples					vel = None					gaze_position2 = None					vel, gaze_position2 = calc_vel()					l_vel.append(vel)					pos_threshold = sum(lsac)/len(lsac) #gets the average position during fixation to get rid of drift					#checks whether subject looked to the lEFT LED, 44 corresponds to 5 degrees					if vel < -2.0 and vel > -10.0:						if (gaze_position2[0] < (pos_threshold - 44)) and (gaze_position2[0] > (pos_threshold - 176)):							response = 0							position1 = client.getPosition()							t_saccade = client.time()							state_eye = "SACCADE"							print "state_eye:", state_eye														if (client.time() - t0_to_saccade) < 0.100:     #reaction time too fast. Does not count.								winsound.Beep(4000,500) # winsound.Beep(freq,duration)								print "RT too fast!"								state_eye = "NO_FIXATE"							elif ij == ij_c:								if state_catch == "RIGHT":									winsound.Beep(4000,500) # winsound.Beep(freq,duration)									state_catch = "LEFT"									l_phase.append(1000)								elif state_catch == "LEFT":									print "good catch!"									state_catch = "RIGHT"									l_phase.append(1000)								ij_c = ij_c + 25							elif state_phase == "RIGHT": # Right:								l_phase.append(1)								state_phase = "MIDDLE-LEFT"								if i >= size_stimr/2:									p = minimizer1.addMeasurement(response,stim)																elif state_phase == "MIDDLE-LEFT": # Left:								l_phase.append(2)								state_phase = "LEFT"								if ii >= size_stimr/2:									p = minimizer3.addMeasurement(response,stim)																elif state_phase == "LEFT": # Left:								l_phase.append(0)								state_phase = "MIDDLE-RIGHT"								if j >= size_stimr/2:									p = minimizer2.addMeasurement(response,stim)																elif state_phase == "MIDDLE-RIGHT": # Left:								l_phase.append(3)								state_phase = "RIGHT"								if jj >= size_stimr/2:									p = minimizer4.addMeasurement(response,stim)							break;					#checks whether subject looked to the RIGHT LED 					elif vel > 2.0 and vel < 10.0:						if (gaze_position2[0] > (pos_threshold + 44)) and (gaze_position2[0] < (pos_threshold + 176)):							response = 1							position1 = client.getPosition()							t_saccade = client.time()							state_eye = "SACCADE"							print "state_eye:",state_eye														if (client.time() - t0_to_saccade) < 0.100:    #reaction time too fast. Does not count.								winsound.Beep(4000,500) # winsound.Beep(freq,duration)								print "RT too fast!"								state_eye = "NO_FIXATE"							elif ij == ij_c:								if state_catch == "RIGHT":									print "good catch!"									state_catch = "LEFT"									l_phase.append(1000)								elif state_catch == "LEFT":									winsound.Beep(4000,500) # winsound.Beep(freq,duration)									state_catch = "RIGHT"									l_phase.append(1000)								ij_c = ij_c + 25							elif state_phase == "RIGHT": # Right:								l_phase.append(1)								state_phase = "MIDDLE-LEFT"								if i >= size_stimr/2:									p = minimizer1.addMeasurement(response,stim)							elif state_phase == "MIDDLE-LEFT": # Left:								l_phase.append(2)								state_phase = "LEFT"								if ii >= size_stimr/2:									p = minimizer3.addMeasurement(response,stim)																elif state_phase == "LEFT": # Left:								l_phase.append(0)								state_phase = "MIDDLE-RIGHT"								if j >= size_stimr/2:									p = minimizer2.addMeasurement(response,stim)																elif state_phase == "MIDDLE-RIGHT": # Left:								l_phase.append(3)								state_phase = "RIGHT"								if jj >= size_stimr/2:									p = minimizer4.addMeasurement(response,stim)								break;								if state_eye == "SACCADE":					RT_saccade = t_saccade - t0_to_saccade					l_vel.append(RT_saccade)					l_pos.append(position[0][0,0])					l_pos1.append(position1[0][0,0])					l_time.append(t0_to_saccade)					l_RT.append(RT_saccade)					l_res.append(response)					l_trial.append(ij)					l_stim.append(stim)					#turn OFF all LEDs, turns ON FP					time.sleep(0.2)					LEDb = Ledl[1000]					ser.write(struct.pack('B',LEDb))					break;								#turn OFF all LEDs, turns ON FP				LEDb = Ledl[1000]				ser.write(struct.pack('B',LEDb))				state_eye = "NO_FIXATE"				print "state_eye:",state_eye				l.append(state_eye)					#end_trial(ser, minimizer1, minimizer2, l);		#The TRIAL_RESULT message defines the end of a trial for the EyeLink Data Viewer. 	#This is different than the end of recording message END that is logged when the trial recording ends. 	#Data viewer will not parse any messages, events, or samples that exist in the data file after this message. 	getEYELINK().sendMessage("TRIAL_RESULT %d"%(buttons[0]));    	return getEYELINK().getRecordingStatus()        trial_condition = ["Block 1", "Block 2", "Block 3", "Block 4 "];		def do_trial(trial):	'''Does the simple trial'''	#This supplies the title at the bottom of the eyetracker display	message ="record_status_message 'Trial %d %s'"%(trial+1, trial_condition[trial])	getEYELINK().sendCommand(message);			#Always send a TRIALID message before starting to record.	#EyeLink Data Viewer defines the start of a trial by the TRIALID message.  	#This message is different than the start of recording message START that is logged when the trial recording begins. 	#The Data viewer will not parse any messages, events, or samples, that exist in the data file prior to this message.	msg = "TRIALID %s"%trial_condition[trial];	getEYELINK().sendMessage(msg);		#The following does drift correction at the begin of each trial	while 1:		# Checks whether we are still connected to the tracker		if not getEYELINK().isConnected():			return ABORT_EXPT;					# Does drift correction and handles the re-do camera setup situations		try:                        #print surf.get_rect().w/2,surf.get_rect().h/2#at.LED_dict(1000) #turn On FP LED			error = getEYELINK().doDriftCorrect(FP[0],FP[1],1,1)			if error != 27: 				break;			else:				getEYELINK().doTrackerSetup();		except:			break #getEYELINK().doTrackerSetup()	raw_input("Press any key to start recording")	#connect to Arduino	ser = serial.Serial('COM15', 115200) 	time.sleep(5)		#start sled timer at correct phase, left turning point	t0_sled = sled_recal()		error = getEYELINK().startRecording(1,1,1,1)	if error:		return error;	gc.disable();	#begin the realtime mode	pylink.beginRealTimeMode(100)	if not getEYELINK().waitForBlockStart(1000, 1, 0):		end_trial(ser);		print "ERROR: No link samples received!";      		return TRIAL_ERROR;	t0_eyelink = currentTime()	getEYELINK().sendMessage("SYNCTIME %d"%(currentTime()-t0_eyelink));	ret_value = drawgc(t0_sled, ser);	pylink.endRealTimeMode();	gc.enable();	return ret_value;	NTRIALS = 1def run_trials():	''' This function is used to run individual trials and handles the trial return values. '''	''' Returns a successful trial with 0, aborting experiment with ABORT_EXPT (3); It also handles	the case of re-running a trial. '''	#Do the tracker setup at the beginning of the experiment.	getEYELINK().doTrackerSetup()			for trial in range(NTRIALS):		if(getEYELINK().isConnected() ==0 or getEYELINK().breakPressed()): break;		while 1:			ret_value = do_trial(trial)			endRealTimeMode()			if (ret_value == TRIAL_OK):				getEYELINK().sendMessage("TRIAL OK");				break;						elif (ret_value == SKIP_TRIAL):				getEYELINK().sendMessage("TRIAL ABORTED");				break;						elif (ret_value == ABORT_EXPT):				getEYELINK().sendMessage("EXPERIMENT ABORTED")				return ABORT_EXPT;			elif (ret_value == REPEAT_TRIAL):				getEYELINK().sendMessage("TRIAL REPEATED");			else: 				getEYELINK().sendMessage("TRIAL ERROR")				break;	return 0;