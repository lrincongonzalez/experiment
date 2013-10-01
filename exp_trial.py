## Copyright (c) 1996-2005, SR Research Ltd., All Rights Reserved### For use by SR Research licencees only. Redistribution and use in source# and binary forms, with or without modification, are NOT permitted.#### Redistributions in binary form must reproduce the above copyright# notice, this list of conditions and the following disclaimer in# the documentation and/or other materials provided with the distribution.## Neither name of SR Research Ltd nor the name of contributors may be used# to endorse or promote products derived from this software without# specific prior written permission.## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS# IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.# $Date: 2009/06/30 17:44:52 $# #from pylink import *import timeimport gcimport sysimport root_luc as root import numpy as npfrom scipy import statsfrom matplotlib import pyplot as pltimport matplotlib as mplfrom pylab import *from mpl_toolkits.mplot3d import Axes3Dimport serialimport structimport time#Aurduino controls#check the platform#if sys.platform == 'linux': #linux#elif sys.platform == 'darwin': #mac osx#ser = serial.Serial('/dev/tty.usbserial-A600esYq', 115200) #elif sys.platform == 'win32': #windows#if ser.isOpen():#ser.close()#ser = serial.Serial('COM15', 115200) #time.sleep(5)RIGHT_EYE = 1LEFT_EYE = 0BINOCULAR = 2#LED coordinates#calibration_targets = (99.5,180 187.5,180 275.5,180)FP = (175,93)		def end_trial():	'''Ends recording: adds 100 msec of data to catch final events'''	  	pylink.endRealTimeMode();    	pumpDelay(100);        	getEYELINK().stopRecording(); 	while getEYELINK().getkey() :  	 	pass;def gaze_pos():	'''Calculates gaze position '''		eye_used = getEYELINK().eyeAvailable(); #determine which eye(s) are available 	if eye_used == RIGHT_EYE:  		eye_used = RIGHT_EYE;		#getEYELINK().sendMessage("EYE_USED 1 RIGHT");	elif eye_used == LEFT_EYE or eye_used == BINOCULAR:		#getEYELINK().sendMessage("EYE_USED 0 LEFT");  		eye_used = LEFT_EYE;  	else:  		print "Error in getting the eye information!";  		return TRIAL_ERROR;  			dt = getEYELINK().getNewestSample() # check for new sample update	if(dt != None):		# Gets the gaze position of the latest sample,		if eye_used == RIGHT_EYE and dt.isRightSample():			gaze_position = dt.getRightEye().getGaze()		elif eye_used == LEFT_EYE and dt.isLeftSample():			gaze_position = dt.getLeftEye().getGaze()	return gaze_positiondef drawgc(startTime, ser):	'''Sends a stimulus to the Arduino; uses the getNewestSample() to get subjects response; uses the response the calculate the SOA and thus the next stimulus '''			#stimulus ranges from -250:-2 in steps of 2ms, and from 2:250 in steps of 2ms	Ledl = dict(zip(range(-2,-251,-2),range(4,129)))	Ledl.update(dict(zip(range(2,251,2),range(130,255))))	Ledl.update({1000:0})	Ledl.update({3000:3})		#variables for root function	i = 0	x = np.linspace(-250,-2,125)	x1=np.linspace(2,250,125)	x=np.append(x,x1)	# turns the LEDs OFF	LEDb = Ledl[3000]	ser.write(struct.pack('B',LEDb)) 	time.sleep(1)	# turns the FP LED ON	LEDb = Ledl[1000]	ser.write(struct.pack('B',LEDb))   	time.sleep(1)	minimizer = root.Psi(-250,250,x,np.linspace(-200,200,41),np.linspace(0.1, 100,41))         # make a kontsevic root finder with a range from 0 to 2	#stimr=np.array([-250, -200, -150, -100, -50, 50, 100, 150, 200, 250])	stimr=np.array([-50, 200, -150, 100,-200, -250, 50,  150, -100, 250])	#random.shuffle(stimr)		getEYELINK().flushKeybuttons(0)	buttons =(0, 0);		while 1:		error = getEYELINK().isRecording()  # First check if recording is aborted 		if error!=0:			end_trial();			return error		if i>20:  #finishes the trial after 30 iterations			#print "timeout"			getEYELINK().sendMessage("TIMEOUT");			end_trial();			buttons =(0, 0);			break;		if(getEYELINK().breakPressed()):	# Checks for program termination or ALT-F4 or CTRL-C keys			end_trial();			return ABORT_EXPT		elif(getEYELINK().escapePressed()): # Checks for local ESC key to abort trial (useful in debugging)			end_trial();			return SKIP_TRIAL					buttons = getEYELINK().getLastButtonPress() # Checks for eye-tracker buttons pressed		if(buttons[0] != 0):			getEYELINK().sendMessage("ENDBUTTON %d"%(buttons[0]));			end_trial();			break;				#starts the root/LED experiment					if i < 10:			stim = np.round(stimr[i])			i = i + 1		else:			stim = minimizer()  			i = i + 1				FP_flag = 2			while 1:				#gets eye position			gaze_position = gaze_pos()								#Determines if subject is fixating, +/- 22 pixels of 175			if gaze_position[0] > 153 and gaze_position[0] < 197:				FP_flag = 1				startTime_FP = currentTime()				while 1:					#checks whether the subjects is still fixating					gaze_position = gaze_pos()					if gaze_position[0] > 153 and gaze_position[0] < 197:						#checks whether the subject has fixated for 500ms 						if int(currentTime() -startTime_FP) > 1000:							FP_flag = 0							break;					else:						break;			if FP_flag == 0:				break;										#Sends a signal to the LED						LEDb = Ledl[stim]		ser.write(struct.pack('B',LEDb)) 		while 1:			gaze_position = gaze_pos()			#checks whether subject looked to the lEFT LED (+/- 22 pixels of 87)			if gaze_position[0] < 109 and gaze_position[0] > 65:				response = 0				#turn OFF all LEDs, turns ON FP				LEDb = Ledl[1000]				ser.write(struct.pack('B',LEDb))				break;			#checks whether subject looked to the RIGHT LED (+/- 22 pixels of 263)			elif gaze_position[0] > 241 and gaze_position[0] < 285:				response = 1				#turn OFF all LEDs, turns ON FP				LEDb = Ledl[1000]				ser.write(struct.pack('B',LEDb))				break;		p = minimizer.addMeasurement(response,stim)										#turn OFF all LEDs	LEDb = Ledl[3000]	ser.write(struct.pack('B',LEDb))	ser.close()	# get all the data we collected from Psi	data = minimizer.getData()	mu, sigma = minimizer.getTheta()	np.savetxt('data.txt',data)	XY = minimizer.getXY()	#np.savetxt('XY.txt',XY)	#np.savetxt('mu.txt',mu)	#np.savetxt('sigma.txt',sigma)	#print data	#print mu, sigma	#fig =plt.figure()	#plt.plot(data[:,0],data[:,1], 'or')	#stimo = np.linspace(-250,250,251)	#Po = stats.norm.cdf(stimo, loc=0, scale=2)	#P = stats.norm.cdf(stimo, mu, sigma)	#plt.plot(stimo,Po,'k',stimo,P )	#plt.draw()	#plt.show()					end_trial();		#The TRIAL_RESULT message defines the end of a trial for the EyeLink Data Viewer. 	#This is different than the end of recording message END that is logged when the trial recording ends. 	#Data viewer will not parse any messages, events, or samples that exist in the data file after this message. 	getEYELINK().sendMessage("TRIAL_RESULT %d"%(buttons[0]));        return getEYELINK().getRecordingStatus()        				trial_condition = ["Image-Window", "Image-Mask", "Text-Window", "Text-Mask"];		def do_trial(trial, ser):	'''Does the simple trial'''	#This supplies the title at the bottom of the eyetracker display	message ="record_status_message 'Trial %d %s'"%(trial+1, trial_condition[trial])	getEYELINK().sendCommand(message);			#Always send a TRIALID message before starting to record.	#EyeLink Data Viewer defines the start of a trial by the TRIALID message.  	#This message is different than the start of recording message START that is logged when the trial recording begins. 	#The Data viewer will not parse any messages, events, or samples, that exist in the data file prior to this message.	msg = "TRIALID %s"%trial_condition[trial];	getEYELINK().sendMessage(msg);			#The following does drift correction at the begin of each trial	while 1:		# Checks whether we are still connected to the tracker		if not getEYELINK().isConnected():			return ABORT_EXPT;							# Does drift correction and handles the re-do camera setup situations		try:                        #print surf.get_rect().w/2,surf.get_rect().h/2#at.LED_dict(1000) #turn On FP LED			error = getEYELINK().doDriftCorrect(FP[0],FP[1],1,1)			if error != 27: 				break;			else:				getEYELINK().doTrackerSetup();		except:			break #getEYELINK().doTrackerSetup()						error = getEYELINK().startRecording(1,1,1,1)	if error:	return error;	gc.disable();	#begin the realtime mode	pylink.beginRealTimeMode(100)	if not getEYELINK().waitForBlockStart(1000, 1, 0):		end_trial();		print "ERROR: No link samples received!";      		return TRIAL_ERROR;      	  		startTime = currentTime()		getEYELINK().sendMessage("SYNCTIME %d"%(currentTime()-startTime));	ret_value = drawgc(startTime, ser);	pylink.endRealTimeMode();	gc.enable();	return ret_value;				NTRIALS = 1def run_trials():	''' This function is used to run individual trials and handles the trial return values. '''	''' Returns a successful trial with 0, aborting experiment with ABORT_EXPT (3); It also handles	the case of re-running a trial. '''	#Do the tracker setup at the beginning of the experiment.	getEYELINK().doTrackerSetup()	ser = serial.Serial('COM15', 115200)         time.sleep(5)	for trial in range(NTRIALS):		if(getEYELINK().isConnected() ==0 or getEYELINK().breakPressed()): break;		while 1:			ret_value = do_trial(trial, ser)			endRealTimeMode()					if (ret_value == TRIAL_OK):				getEYELINK().sendMessage("TRIAL OK");				break;			elif (ret_value == SKIP_TRIAL):				getEYELINK().sendMessage("TRIAL ABORTED");				break;						elif (ret_value == ABORT_EXPT):				getEYELINK().sendMessage("EXPERIMENT ABORTED")				return ABORT_EXPT;			elif (ret_value == REPEAT_TRIAL):				getEYELINK().sendMessage("TRIAL REPEATED");			else: 				getEYELINK().sendMessage("TRIAL ERROR")				break;					return 0;		