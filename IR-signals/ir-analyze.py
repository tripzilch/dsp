# load utility functions (yes this should be done with actual python modules)
get_ipython().magic('run -i ../matplotlibsnippets.py')
get_ipython().magic('run -i ../wavtools.py')

# badass colour scheme
rc_set_dark_colourscheme()


def process(xx, trigger_level=0.5, trigger_timeout=20, zxt_treshold=20, verbose=True):
    '''Processes frequency-modulated 1bit signal for audio-to-IR device.
    
        Arguments:
        xx -- input waveform. remember to manually cut initial transients (such as the phase-modulated preamble)
        
        Keyword arguments:
        trigger_level -- amplitude at which detection is switched "on", start of a "packet"
        trigger_timeout -- time (in samples) below trigger_level before detection is switched "off", end of a "packet" 
        zxt_threshold -- if time (in samples) between zero-crossings is smaller than this, output a 0, otherwise a 1 bit.
        
        Output:
        ons -- numpy.Array with 0 and 1 showing where detection trigger is "on"
        zxs -- numpy.Array with 0 and 1 showing detection of zero crossings
        zxts -- numpy.Array with count since last zero crossing
        packets -- list with binary strings of decoded packets
        verbose -- whether to print packet string to stdout on successful decoding        
        
    '''
   
    last_trigger = -2 * trigger_timeout
    last_zx = -2 * trigger_timeout
    prev_x = xx[0]
    ons = zeros_like(xx)
    zxs = zeros_like(xx)
    zxts = zeros_like(xx)
    packets = []
    prev_on = False
    packet = ''
    for i,x in enumerate(xx):
        if abs(x) > trigger_level:
            last_trigger = i
        on = (i - last_trigger) < trigger_timeout
        zx = (x * prev_x) < 0 or x == 0
        zxt = i - last_zx
        prev_x = x        
        if zx:
            last_zx = i
        if on and zx:            
            packet += str(int(zxt > zxt_treshold))
        if prev_on and not on:
            if verbose: 
                print packet
            packets.append(packet)
            packet = ''
        prev_on = on
        ons[i] = on
        zxs[i] = zx
        zxts[i] = zxt
    return ons,zxs,zxts,packets

if __name__ == "__main__":
    x = wavread('ir-light-onoff-noheader.wav')
    # pk = pk[10500:11000] # optionally slice a portion of the input file
    
    # process the thing
    on, zx, zxt, code = process(x)
    
    # plot pretty graphs
    
    clf() # clear figure
    
    
    subplot(2,1,1) # two rows, one column, select first subplot
    
    # plot signal and zero crossings
    plot(x)
    plot(zx)   
    
    # enable dotted lines at y=-1, 0 and 1
    yticks([-1,0,1])
    grid(axis='y')
    
    subplot(2,1,2) # select second subplot
    plot(zxt * on) # plot zero crossing distance masked by "on" trigger    
    
    tight_layout() # maximize screen space of plots


