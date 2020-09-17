import sys, types,os
from pype import *

class fixationTask:

    def __init__(self):
        self.createParamTable(app)
        self.app = app
        self.mySprites = list()
        self.numStim = 0
        self.mySpriteList = list()

    def createParamTable(self,app):
	parfile = app.taskname()
	# Look for an existing saved parameter file for this task
	if parfile:
		parfile = parfile + '.par'
        self.myTaskParams = ParamTable(self.myTaskNotebook, (
		("Stimulus Pres Params", None, None),
                ("bg_during", "(10, 10, 10)", is_color, "The background color during stimulus presentation"),
                ("bg_before", "(10, 10, 10)", is_color, "The background color before stimulus presentation"),
                ("RF_Params",None,None),
      		("RF_Center_X", "0",is_int,"X coordinate of the receptive field center in pixels"),
      		("RF_Center_Y", "0",is_int,"Y coordinate of the receptive field center in pixels"),
                ("RF Scale On Ecc", "1", is_boolean, "Whether or not to scale based on eccentricity"),
                ("RF Scaling", ".625",        is_float, "If RF_Scale_On_Ecc is 1, Size of RF in degrees equals eccentricity * RF Scaling + RF Offset"),
		("RF Offset", ".5", is_float, "If RF_Scale_On_Ecc is 1,Size of RF in degrees equals eccentricity * RF Scaling + RF Offset"),
		("RF Radius", "100", is_int, "IF RF_Scale_On_Ecc is 0, this is the radius of the RF in pixels"),
                ("Task Params", None, None),
                ("iti",	"2500",		   	is_int, "Inter-trial interval"),
		("IStime",	"200",		   	is_int, "Inter-stimulus interval"),
		("stimon",	"500",			is_int, "Stimulus presentation"),
		("nstim",	"5",			is_int, "Number of stimuli"),
      		("Fixation Params", None, None, "Fixation Parameters"),
       		("fixcolor1",	"(255,255,255)",is_color, 'Color of the fixation dot'),
		("fixcolor2",	"(128,128,128)",is_color),
		("min_err",		"0",		   	is_int),
		("max_err",		"100",		   	is_int),
		("fixwait",		"100",		   	is_int),
		("Reward Params", None, None),
		("numdrops",    "8",           is_int, "Number of juice drops"),
		("rmult",		"1.0",		   	is_float),
		("Misc Params", None, None, "Miscelaneous Parameters"),
		("Recent Buffer Size", "50", is_int, "The number of trials to use to calculate recent performance"),
		("pause_color", "(150,0,0)", is_color, "The screen will turn this color when the task is paused")
                ), file=parfile)

        #create parameter table and window to go along with it

    def encodeTaskParameters(self,app):
        #encode task parameters
	app.encode_plex('rfx')
	app.encode_plex(params['RF_Center_X'])
	app.encode_plex('rfy')
	app.encode_plex(params['RF_Center_Y'] + app.globals.yOffset)
	app.encode_plex('iti')
	app.encode_plex(int(params['iti']))
	app.encode_plex('stim_time')
	app.encode_plex(int(params['stimon']))
	app.encode_plex('isi')
	app.encode_plex(int(params['IStime']))
	app.encode_plex('numstim')
	app.encode_plex(int(params['nstim']))
	
    def encodeISI(self,app):
        pass
    def encodeITI(self,app):
        pass

    def createStimuli(self,app):
        #create stimuli and store in myStims
        pass
        
    def cleanup(self):
        #delete parameter table and anything else we created
        self.myTaskParams.destroy()

    def getSprite(self, index):
        pass

    def getNumStim(self):
        pass
        
    def runSet(self,app):
    	"""
	This is what is run when you hit the 'start' button (set as such in
	the 'main' function, defined at the end of this file).
	"""

	# tally collects the results of the last N trials and displays a
	# running tally at the bottom of the main pype control window
	app.tally(clear=1)
	
	# This erases any information printed to the console
	#app.console.clear()
	
	# Update the task's representation of all the parameters set in the
	# task parameter table, rig_params and monk_params - always called P
        #app.params = ParamTable(None, (), None)        
	P = self.myTaskParams.check(mergewith=app.getcommon())
	params = self.myTaskParams.check()

	# Save this version (in case you've made changes since the last time
	# the .par file was updated).

        #P.save()
	#params.save()



	self.createStimuli(app)
	print 'Done creating Stimuli'

        if(self.warnNumStim()):
            if ask("pype", "%d stimuli, proceed?" % self.getNumStim(), ("yes", "no")) == 0:
                pass
            else:
                return

	#Set the record filename if the task wants to:
	rFileName = self.getRecordFileName()
	if(rFileName is not None):
            if(os.path.exists(rFileName)):
            	if ask("pype", "overwrite file: %s ?" % (rFileName), ("yes", "no")) == 0:
                    app.record_selectfile(fname=rFileName)
                else:
                    return
            else:
                app.record_selectfile(fname=rFileName)



        app.record_note('task_is', __name__)

	# Basic setup stuff, you shouldn't want to change this.
	app.paused = 0
	app.running = 1
	# Makes a little green light/red light on the main pype window
	app.led(1)

        # Set various counters and markers in app.globals.  globals is an
	# instance of the Holder class (initialized in function "main,"
	# below), which just lets you store a bunch of variables inside app
	# in a reasonably neat way.
	# - repnum: number of reps completed, 
	# - ncorrect: number of trials correct
	# - ntrials: number of trials completed
	# - seqcorrect: count of how many trials in a row have been correct
	# - uicount: how many trials have been uninitiated (use with uimax)
	# - number of stimuli that have been seen for complete stim time

	app.globals.repnum = -1
	app.globals.ncorrect = 0
	app.globals.ntrials = 0
	app.globals.seqcorrect = 0
	app.globals.uicount = 0
	app.globals.stimCorrect = 0
        app.globals.yOffset = 600
        #app.globals.yOffset = pype_plex_code_dict('plexYOffset')
	app.globals.plexStimIDOffset = pype_plex_code_dict('plexStimIDOffset')
	app.globals.plexRotOffset = pype_plex_code_dict('plexRotOffset')

        self.encodeTaskParameters(app)



	#initialize ITI timer, we are now in the first ITI
	t = Timer()

	# This call intiates the first ITI before the first trial.
	# Calling encode will make a note in the data record
	# with the current timestamp and whatever comment you give it.

	app.encode_plex(START_ITI)
        app.encode(START_ITI)
        self.encodeITI(app)
	# Calls RunTrial, and calculates a running percentage correct.
	try:
		# I added this to keep a running "recent" percentage correct
		# because perfomance often changes during the task.
		pctbuffer = list()
		
		# Call Run trial only if there are still unshown stimuli in
		# the stimorder buffer
		while app.running and ( app.globals.stimCorrect < self.getNumStim()):
			#This task implements pause (f5) at the trial level
			was_paused = 0
			while(app.paused):
				if(was_paused == 0):
					app.encode_plex('pause')
					app.encode('pause')
					app.globals.dlist.bg = params['pause_color']
					# Update the dlist and flip the framebuffer
					app.globals.dlist.update()
					app.fb.flip()
					was_paused = 1
				app.idlefn()
			if(was_paused): #reset background color
				app.encode_plex('unpause')
				app.encode('unpause')
				app.globals.dlist.bg = params['bg_during']
				# Update the dlist and flip the framebuffer
				app.globals.dlist.update()
				app.fb.flip()
                        P = self.myTaskParams.check(mergewith=app.getcommon())
		
                       	params = self.myTaskParams.check()

			try:
				# RunTrial is a function defined below that runs a
				# single trial.
				result,t = self.RunTrial(app,t)
			except UserAbort:
				# The escape key will abort a trial while it's running.
				result=None
				t.reset()
				pass
			# This if statement avoids a divide-by-zero error if the
			# first trial is aborted before ntrials is incremented
			if (app.globals.ntrials > 0 and params['Recent Buffer Size'] > 0):
				pctbuffer.append(result)
				# Average the performance over the past X trials.
				if(app.globals.ntrials < params['Recent Buffer Size']) :
					recent=100*app.globals.ncorrect/app.globals.ntrials
				else:
					lastX = pctbuffer[len(pctbuffer) - params['Recent Buffer Size']::]
					recent=100*lastX.count(CORRECT_RESPONSE)/len(lastX)

				stimPerTrial =  float(app.globals.stimCorrect)/ float(app.globals.ntrials)
			else:
				stimPerTrial = 0.0
			# This call prints the overall and recent perf % to console
			
			con(app, " %s:%d %d/%d %.0f%% (recent %.0f%%)\n %0.2f stims per trial" % \
				(now(), app.nreps(),app.globals.ncorrect, app.globals.ntrials, 100.0 * app.globals.ncorrect / app.globals.ntrials, recent,stimPerTrial), 'black')
                        #update the behavioral history and tally
                        if(result is None):
                            app.tally(type=USER_ABORT)
                            app.history(USER_ABORT)
                        elif(iscorrect(result)):
                            app.tally(type=CORRECT_RESPONSE)
                            app.history(CORRECT_RESPONSE)
                        elif(result == BREAK_FIX):
                            app.tally(type=BREAK_FIX)
                            app.history(BREAK_FIX)
                        elif(isui(result)):
                            app.tally(type=UNINITIATED_TRIAL)
                            app.history(UNINITIATED_TRIAL)
                        else:
                            app.tally(NO_RESP)
                            app.history(NO_RESP)

                        
	except:
		# If there's an error generated inside the try statement,
		# it drops to here - reporterror tries to exit cleanly instead
		# of crashing the machine.
		reporterror()
	
	# More housekeeping stuff, also shouldn't change.
	app.repinfo()
	app.running = 0
	app.led(0)
	# standard beep sequence when you hit the "stop" button.
	app.warn_run_stop()
	# marks the data file as done so you know everything is complete.
	app.record_done()

        #Set the record filename back to '' so we don't overwrite things
	rFileName = self.getRecordFileName()
	if(rFileName is not None):
            app.record_selectfile(fname='')

	# This is the end of the RunSet function.
	return 1

    def RunTrial(self,app, t):
	"""
	RunTrial is called by RunSet.  It does housekeeping stuff associated
	with recording behavioral data for an individual trial, and calls the
	_RunTrial function which actually does the stimulus presentation and
	task control. 
	"""
	# On every trial, we check to see if any parameters have been updated
	# while the last trial was running
      	P = self.myTaskParams.check(mergewith=app.getcommon())
	params = self.myTaskParams.check()


	# Note the time that the trial started, again explicitly handled
	# in PypeFile class.
	# Do we need this?
	# Note that the comment above is not accurate.  the time is actually the time that RunTrial is called, the actual trial has not yet started, although the ITI has
	app.record_note('trialtime', (app.globals.ntrials, Timestamp()))

	
	# This call starts the data record for this trial. The datafile will
	# have a 'start' event encoded with timestamp = 0. Also plexon will 
	# have an event encoded
	app.record_start()
	
	# This function will actually do the task control and stimulus display
	# and return its results back here for housekeeping.
	(result, rt,t) = self._RunTrial(app,t)
	
	# Stop recording for this trial, reset eye trace and signal trial stop
	# to Plexon.  Encode 'stop' in the datafile, which is the very last
	# thing to get
	app.record_stop()
	
	# VERY IMPORTANT, this call actually writes all of the info collected
	# in this trial into the datafile.  Don't muck with it.
	app.record_write(result, rt, P, taskinfo=None)
	
	# Check to see whether we've exceeded the max allowable uninitiated
	# trials, and if so, pop up a little warning box that will stall the
	# task until the user clicks it.  Note result is one of the variables
	# returned by _RunTrial.
	if result == UNINITIATED_TRIAL:
		app.globals.uicount = app.globals.uicount + 1
		if app.globals.uicount > P['uimax']:
			warn('Warning',
				 'UI Count exceeded @ %s\nPlease intervene.\n' % now(), wait=1)
			app.globals.uicount = 0
	else:
		# Re-set the uicount after every good trial, so uimax can only
		# be exceeded by a number of ui trials in a row.  Otherwise,
		# the count would be cumulative
		app.globals.uicount = 0
	
	# This is the end of RunTrial.  In RunSet, the call to RunTrial expects
	# the 'result' variable to get returned, and this is how we do that:
	return result,t

    def _RunTrial(self,app, t):
	"""
	_RunTrial actually does the behavioral control for the task and shows
	whatever stimuli are specified, etc.  This is the meat of the task,
	and this is where you're going to make changes to make the task do
	what you want it to do. 
	"""
	
	# # # # # # # # # # # # # # # # # #
	# General setup stuff
	# # # # # # # # # # # # # # # # # #

	# Create a second instances of Timer class (also in pype.py), which counts 
	# milliseconds until it's reset. Can be queried without reset
	t2 = Timer()

	# Get the parameters again
      	P = self.myTaskParams.check(mergewith=app.getcommon())

	params = self.myTaskParams.check()

	# Draw a line at the beginning of every trial
	con(app,">---------------------------")
	# You can write anything you want to the console, and in color.
	con(app,"Next trial",'blue')
	
	# Initialize default reaction time in case trial is aborted
	rt = -1
	
	# Check for "testing" mode (rig params table; no eye or bar monitoring)
	TESTING = int(P['testing'])
	if TESTING:
		# put a big red note on the console so I don't forget
		con(app, 'TESTING','red')
	
	# Clear the user display before starting
	app.udpy.display(None)
	
	# The dlist manages what gets shown on the screen, it gets
	# re-initialized every trial.  app.fb is the framebuffer
	app.globals.dlist = DisplayList(app.fb)
	# set the background color - in this case, I've got a color defined
	# for the intertrial interval
	#app.globals.dlist.bg = params['bg_before']
        app.globals.dlist.bg = params['bg_before']
	# Update the dlist and flip the framebuffer
	app.globals.dlist.update()
	app.fb.flip()
	# At this point, screen color is bg_before, and otherwise blank.
	
	# # # # # # # # # # # # # # # # # #
	# Code for making a fixation spot
	# # # # # # # # # # # # # # # # # #
	 
	# Fixation position at P['fix_x'] and P['fix_y'], which are in the
	# monk_params table
	fx, fy = P['fix_x'], P['fix_y']

	# I'm not clear on what this does, but it has something to do with
	# aligning the user display, and you need it.
	app.looking_at(fx, fy)

	# Here is some basic fixation point code. Depth sets the layer of sprite
	# Always set fixspot to be layer 0; other stimuli to be layers below
	# i.e. set depth higher for other stimuli Note that fix_size and 
	# fix_ring are from monk_params, but fixspot color has to be 
	# specified by the task.
	
	if P['fix_ring'] > 0:
		# Create the sprite
		spot = Sprite(2*P['fix_ring'], 2*P['fix_ring'],
					  fx, fy, fb=app.fb, depth=0, on=0, centerorigin=1)
		# fill the square with bg color
		spot.fill([0,0,0,0])
		# make a black circle of radius fix_ring at the center of the
		# sprite
		spot.circlefill((1,1,1), r=P['fix_ring'], x=0, y=0)
		# and now for the actual fixation point...
		if P['fix_size'] > 1:
			# make another circle of radius fix_size
			spot.circlefill(params['fixcolor1'], r=P['fix_size'], x=0, y=0)
		else:
			# just color the center pixel - r=1 doesn't work well
			spot[0,0] = params['fixcolor1']
	else:
		# Create a sprite without the surrounding ring
		spot = Sprite(2*P['fix_size'], 2*P['fix_size'],
					  fx, fy, fb=app.fb, depth=0, on=0, centerorigin=1)
		spot.fill(params['bg_during'])
		if P['fix_size'] > 1:
			spot.circlefill(params['fixcolor1'], r=P['fix_size'], x=0, y=0)
		else:
			spot[0,0] = params['fixcolor1']
	
	# This is redundant with on=0 above, but make sure the sprite is off
	spot.off()
	# Add spot to the dlist
	app.globals.dlist.add(spot)
	
	# # # # # # # # # # # # # # # # # #
	# Code for making the fixation window
	# # # # # # # # # # # # # # # # # #
	
	# This is the virtual boundary that defines a "good" fixation,
	# again only necessary if yours is a fixation task.
	
	# Adjust fixation window size for target eccentricity, since it's
	# harder to fixate on more eccentric points and there's more
	# eye tracker error too.  The min and max error parameters are
	# task-specific.
	#min_e, max_e = params['min_err'], params['max_err']
	#r = ((fx**2)+(fy**2))**0.5
	#z = min_e + (max_e - min_e) * r / ((app.fb.w+app.fb.h)/4.0)
	z = 0
	# Set a parameter value that's the actual window size to use
	# this trial, so it's saved in data file.
	P['_winsize'] = int(round(P['win_size'] + z))
	
	# Create an instance of the FixWin class (defined in pype.py) that
	# will actually keep track of the eye position for you
	fixwin = FixWin(fx, fy, P['_winsize'], app)
	fixwin.draw(color='grey') #draws the fixwin radius on user display

    ##### Now create the visual stimuli
	stim_arr = [] #empty list
	####This is for multiple stimulus presentation; number of stimuli to
        ####be shown in this run is min of P['nstim'] and the number of
	####stimuli left
	stm_start = app.globals.stimCorrect
	con(app,"%d stimuli presented, %d stimuli remaining" % (stm_start,self.getNumStim()-stm_start),"Black")
	sshow = min(params['nstim'], self.getNumStim()-stm_start)
        for i in arange(0,sshow):
            spr = self.getSprite(stm_start+i)
            stim_arr.append(spr)
 #           #app.globals.dlist.add(stim_arr[i])
            stim_arr[i].off()
            app.globals.dlist.update()
									
	
	# # # # # # # # # # # # # # # # # #
	# Initiate the trial
	# # # # # # # # # # # # # # # # # #

	# Start monitoring the eye trace.  This encodes an 'eye_start' event
	# in the datafile that will always be equal to the first timestamp
	# at which eyetrace data are collected.
	app.eyetrace(1)

	# set background color to the color defined for during the trial
	app.globals.dlist.bg = params['bg_during']
	app.globals.dlist.update()
	
	# Note that we haven't flipped the framebuffer yet...
	
	# We put the entire trial inside a try statement 
	# with exceptions to stop trial(correct, incorrect, aborted).
	try:
		# The idlefn method just lets the program do background
		# maintenance stuff.  You can give idlefn an argument that
		# specifies a number of milliseconds to wait
		# Timer t was set at the very beginning of the trial,
		# I want to know how long it's been since then.)
		app.idlefn(params['iti']-t.ms())
		app.encode_plex(END_ITI)
        	app.encode(END_ITI)

		#remember we already encoded START_ITI

		# Reset this timer to zero
		t.reset()
		
		# Flip the framebuffer to show the current dlist
		app.fb.flip()

		fixwin.draw(color='red')
		ttt = fixwin.on()
		# Now the background color is bg_during
		# set a little dummy flag to keep track of stuff
		spot_on=0
		# When we get here either the bar has been grabbed or we're not
		# monitoring it.  If the fixation point is not already
		# on, we'll turn it on now.
		if not spot_on:
			spot.on()
			app.globals.dlist.update()
			app.fb.flip()
			app.udpy.display(app.globals.dlist)
			spot_on=1
		# Now we're waiting for the subject to acquire the fixation point
		info(app, "waiting fix acquisition")
		app.idlefn()
		t.reset()
		# Again, a dummy flag to help with task control
		go_on = 0
		while not go_on:
			# We are waiting for the eye position to move inside the
			# fixation window.  Whether this is the case is one of
			# the things that the FixWin class keeps track of.
			while not fixwin.inside() and not TESTING:
				# We use the same abortafter limit again
				if P['abortafter'] > 0 and t.ms() > P['abortafter']:
					info(app, "no acquisition")
					con(app, "no acquisition", 'blue')
					#app.encode_plex(UNINITIATED_TRIAL)
					beep(2000,100)
					result = UNINITIATED_TRIAL
					raise MonkError
				app.idlefn()
			# At this point, the fixwin.inside returned 1 (meaning eye
			# is inside window).  Sometimes if the spot has just come
			# on and the subject is in the process of saccading across
			# the screen, the eye position will go through the fixwin.
			# Only count this as acquiring fixation if the eye stays in
			# the window for "fixwait" milliseconds.
			t2.reset()
			# First, assume we will continue if eye stays in window
			go_on = 1
			while t2.ms() < params['fixwait']:
				if not fixwin.inside() and not TESTING:
					# If at any time during the fixwait the eye
					# moves back out of the window, go back to waiting
					# for the eye to enter the window again.
					info(app, "passthrough")
					go_on = 0
					# This resets fixwin.inside back to zero
					fixwin.reset()
					# This exits the innermost while loop, and sends
					# us back to the top of the "while not go_on"
					# loop
					break

		# # # # # # # # # # # # # # # # # #
		# Do real trial stuff
		# # # # # # # # # # # # # # # # # #
	
		# Now, fixation has been acquired.  We can start timing the
		# length of the fixation.
		t.reset() # Reset the timer to monitor fixation length for each stim
		t2.reset() #We will now use t2 as an absolute timer for this trial
		#app.encode(FIX_ACQUIRED) # Standard event encoding

		app.encode_plex(FIX_ACQUIRED)
		app.encode(FIX_ACQUIRED)
		fixwin.draw(color='blue') # Blue is our "active" fixwin color

		####This is for multiple stimulus presentation; number of stimuli to
		####be shown in this run is min of P['nstim'] and the number of
		####stimuli left
		scount = 0
		while scount < sshow:
                    	P = self.myTaskParams.check(mergewith=app.getcommon())
                        self.encodeISI(app,scount+stm_start)
			while t.ms() < params['IStime']:
				if fixwin.broke() and not TESTING:
					#app.encode(FIX_LOST) #standard event code
					app.encode_plex(FIX_LOST)
					app.encode(FIX_LOST)
					info(app, "early break")
					con(app, "early break at %d, %d ms into ISI of stim %d, fixwin time of %d" % (t2.ms(),t.ms(),scount, fixwin.break_time()), 'red')
					#app.encode('exact_fix_lost=%d' % fixwin.break_time())
					result = BREAK_FIX
					# Auditory feedback
					app.warn_trial_incorrect(flash=None)
					# Skip to end of trial
					raise MonkError
				# Again, a call to idlefn lets the computer catch up
				# and monitor for key presses.
				app.idlefn()
			# now display stimulus 
			# now turn it on put it on the dlist; update and flip buffer
			app.globals.dlist.add(stim_arr[scount])
			stim_arr[scount].on()
			self.toggle_photo_diode(app) #note: toggle_photo_diode updates the dlist
			app.encode_plex(SAMPLE_ON)
    			app.encode(SAMPLE_ON)

			app.fb.flip()
#			app.encode(SAMPLE_ON)
			app.udpy.display(app.globals.dlist)
 			#import pdb; pdb.set_trace()
			# wait for stimulus time
			t.reset()
			fon = 0			
			#while t.ms() < params['stimon']:
			while fon < params['stimon']/10-1: ### Now stim duration is counted by frame refresh (04/30/18 Taekjun)				
				if fixwin.broke() and not TESTING:
					app.encode(FIX_LOST) #standard event code
					app.encode_plex(FIX_LOST)
      					app.encode(FIX_LOST)

					info(app, "early break")
					con(app, "early break at %d, %d ms into presentation of stim %d, fixwin time of %d" % (t2.ms(),t.ms(), scount,fixwin.break_time()), 'red')
					#app.encode('exact_fix_lost=%d' % fixwin.break_time())
					result = BREAK_FIX
					app.warn_trial_incorrect(flash=None)
					#turn off stimuli
					stim_arr[scount].off()
					app.fb.flip()
					# Skip to end of trial
					raise MonkError
				# Again, a call to idlefn lets the computer catch up
				# and monitor for key presses.
				# app.idlefn()
				#stim_arr[scount].off()
				#stim_arr[scount].on()
				#stim_arr[scount].fastblit()		
				#app.globals.dlist.update()		
				app.fb.flip()                        
				fon = fon + 1              
				
			# now turn off stimulus
			stim_arr[scount].off()
			app.globals.dlist.delete(stim_arr[scount])
			self.toggle_photo_diode(app) #note: toggle_photo_diode updates the dlist
			app.fb.flip()

			t.reset() # Reset the timer to start ISI timer
			#app.encode(SAMPLE_OFF)
			app.encode_plex(SAMPLE_OFF)
			app.encode(SAMPLE_OFF)
			app.globals.stimCorrect = app.globals.stimCorrect + 1
			scount = scount+1
		
################################
		# If you are here then the trial is correct
		#print "Before raising NoProblem at %d abs time = %d" % (t.ms(), t2.ms())
		raise NoProblem

	# # # # # # # # # # # # # # # # # #
	# Handling exceptions generated in the trial
	# # # # # # # # # # # # # # # # # #
	
	except UserAbort:
		# If you pressed the escape key at any time to abort the trial
		# you will end up here.  No counters are incremented or
		# reset basically because this was not the subject's fault.

		# Turn off the fixation spot and tracker dot
		spot.off()
		#app.encode(FIX_OFF)
		#app.encode_plex(FIX_OFF)

		# Stop monitoring eye position, encode 'eye_stop' in the datafile
		# which will always be the last timestamp at which eyetrace data
		# were collected.
		fixwin.clear()
		app.eyetrace(0)
		#app.encode_plex(EYE_STOP)

		# Re-set the background for the intertrial interval
		app.globals.dlist.bg = params['bg_before']
		self.turn_off_photo_diode(app)
		app.fb.flip()

		result = USER_ABORT
		app.encode_plex(result)
                app.encode(result)
		t.reset()
		app.encode_plex(START_ITI)
		app.encode(START_ITI)

		con(app, "Aborted.", 'red')
                return (result, rt, t)
            
	except MonkError:
		# Any of the MonkError exceptions will land you here.  The
		# trial counter is incremented and the seqcorrect counter
		# is reset.

		# Turn off the fixation spot and tracker dot
		spot.off()
		#app.encode(FIX_OFF)
		#app.encode_plex(FIX_OFF)

		# Stop monitoring eye position, encode 'eye_stop' in the datafile
		# which will always be the last timestamp at which eyetrace data
		# were collected.
		fixwin.clear()
		app.eyetrace(0)
		#app.encode_plex(EYE_STOP)

		# Re-set the background for the intertrial interval
		app.globals.dlist.bg = params['bg_before']
		app.globals.dlist.update()
		self.turn_off_photo_diode(app)
		app.fb.flip()

		app.encode_plex(result)
                app.encode(result)
		t.reset()
		app.encode_plex(START_ITI)
		app.encode(START_ITI)

		app.globals.ntrials = app.globals.ntrials + 1
		app.globals.seqcorrect = 0
                return (result, rt, t)
		
	except NoProblem:
		# Having an exception for a correct trial is handy because
		# there are a number of ways of getting the trial correct
		# depending on whether we're monitoring the eye position or
		# touch bar or dot dimming, and we can put all the reward
		# code in one place.

		# Turn off the fixation spot and tracker dot
		spot.off()
		#app.encode(FIX_OFF)
		#app.encode_plex(FIX_OFF)

		# Stop monitoring eye position, encode 'eye_stop' in the datafile
		# which will always be the last timestamp at which eyetrace data
		# were collected.
		fixwin.clear()
		app.eyetrace(0)
		#app.encode_plex(EYE_STOP)

		# Re-set the background for the intertrial interval
		app.globals.dlist.bg = params['bg_before']
		app.globals.dlist.update()
		self.turn_off_photo_diode(app)
		app.fb.flip()

		result = CORRECT_RESPONSE
		app.encode_plex(CORRECT_RESPONSE)
		app.encode(CORRECT_RESPONSE)


		# Without arguments this call dispenses a reward of size
                # 'dropsize' with a variance of 'dropvar' (both specified
		# in monk_params). The multiplier argument multiplies the
		# "standard" reward by whatever value is passed in.
		clk_num = params['numdrops']
		while clk_num > 0:
			app.reward(multiplier=params['rmult'])
			app.idlefn(50)#time between juice drops
			clk_num = clk_num-1

		# Reset the timer and Start the next ITI as soon as the reward for this trial has been dispensed.

		app.warn_trial_correct() #Standard "correct" beep
		#app.encode_plex(REWARD)

		t.reset()
		app.encode_plex(START_ITI)
		app.encode(START_ITI)

		# Increment the sequence correct counter
		app.globals.seqcorrect=app.globals.seqcorrect + 1
		# Reporting stuff, variables returned to RunTrial
		app.globals.ncorrect = app.globals.ncorrect + 1
		app.globals.ntrials = app.globals.ntrials + 1

                return (result, rt, t)

    def toggle_photo_diode(self,app):
            app.globals.dlist.update()
            app.fb.sync_toggle()

    def turn_off_photo_diode(self,app):
            app.fb.sync(0)

    def getRecordFileName(self): #gets the record file for this task
        return None

    def warnNumStim(self):
        return 0
