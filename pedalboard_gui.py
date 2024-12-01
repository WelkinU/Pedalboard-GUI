import gradio as gr
import numpy as np
from pedalboard import (Pedalboard, Chorus, Reverb, Gain, Phaser, Compressor, HighpassFilter, LowpassFilter,
    Distortion, Delay, Bitcrush, MP3Compressor, PitchShift, Limiter, Clipping, time_stretch, 
    GSMFullRateCompressor, Resample, LadderFilter, LowShelfFilter, HighShelfFilter, PeakFilter, NoiseGate)
from pedalboard.io import AudioFile

def process_audio(audio_in, gain,
    noise_gate_enabled, noise_gate_threshold_db, noise_gate_ratio, noise_gate_attack_ms, noise_gate_release_ms,
    reverb_enabled, reverb_room_size, reverb_damping, reverb_wet_level, reverb_dry_level, reverb_width, reverb_freeze_mode,
    delay_enabled, delay_sec, delay_feedback, delay_mix,
    chorus_enabled, chorus_rate_hz, chorus_depth, chorus_center_delay, chorus_feedback, chorus_mix,
    phaser_enabled, phaser_rate_hz, phaser_depth, phaser_center_frequency, phaser_feedback, phaser_mix,
    pitchshift_enabled, pitchshift_semitones,
    compressor_enabled, compressor_threshold_db, compressor_ratio, compressor_attack_ms, compressor_release_ms,

    distortion_enabled, distortion_drive_db,
    bitcrush_enabled, bitcrush_bit_depth,
    gsm_full_rate_compressor,
    mp3_compressor_enabled, mp3_compressor_vbr_quality,
    resample_method, resample_target_sample_rate,

    highpass_filter_enabled, highpass_filter_cutoff_frequency,
    lowpass_filter_enabled, lowpass_filter_cutoff_frequency,
    high_shelf_filter_enabled, high_shelf_filter_cutoff_hz, high_shelf_filter_gain_db, high_shelf_filter_q,
    low_shelf_filter_enabled, low_shelf_filter_cutoff_hz, low_shelf_filter_gain_db, low_shelf_filter_q,
    peak_filter_enabled, peak_filter_cutoff_hz, peak_filter_gain_db, peak_filter_q,
    ladder_filter_enabled, ladder_filter_mode, ladder_filter_cutoff_hz, ladder_filter_resonance, ladder_filter_drive,
    limiter_enabled, limiter_threshold_db, limiter_release_ms,
    clipping_enabled, clipping_threshold,

    padding_start_sec, padding_end_sec,
    time_strech_factor, time_strech_pitch_shift_semitones,
    ):
    board = Pedalboard()

    if noise_gate_enabled:
        board.append(NoiseGate(noise_gate_threshold_db, noise_gate_ratio, noise_gate_attack_ms, noise_gate_release_ms))

    if gain != 0:
        board.append(Gain(gain_db = gain))

    if reverb_enabled:
        board.append(Reverb(reverb_room_size, reverb_damping, reverb_wet_level, reverb_dry_level, reverb_width, reverb_freeze_mode))

    if delay_enabled:
        board.append(Delay(delay_sec, delay_feedback, delay_mix))

    if chorus_enabled:
        board.append(Chorus(chorus_rate_hz, chorus_depth, chorus_center_delay, chorus_feedback, chorus_mix))

    if phaser_enabled:
        board.append(Phaser(phaser_rate_hz, phaser_depth, phaser_center_frequency, phaser_feedback, phaser_mix))

    if pitchshift_enabled:
        board.append(PitchShift(pitchshift_semitones))

    if compressor_enabled:
        board.append(Compressor(compressor_threshold_db, compressor_ratio, compressor_attack_ms, compressor_release_ms))

    if distortion_enabled:
        board.append(Distortion(distortion_drive_db))

    if bitcrush_enabled:
        board.append(Bitcrush(bitcrush_bit_depth))

    if gsm_full_rate_compressor != 'None':
        board.append(GSMFullRateCompressor(quality = getattr(Resample.Quality, gsm_full_rate_compressor)))

    if mp3_compressor_enabled:
        board.append(MP3Compressor(mp3_compressor_vbr_quality))

    if resample_method != 'None':
        board.append(Resample(resample_target_sample_rate, getattr(Resample.Quality, resample_method)))

    if highpass_filter_enabled:
        board.append(HighpassFilter(highpass_filter_cutoff_frequency))

    if lowpass_filter_enabled:
        board.append(LowpassFilter(lowpass_filter_cutoff_frequency))

    if high_shelf_filter_enabled:
        board.append(HighShelfFilter(high_shelf_filter_cutoff_hz, high_shelf_filter_gain_db, high_shelf_filter_q))

    if low_shelf_filter_enabled:
        board.append(LowShelfFilter(low_shelf_filter_cutoff_hz, low_shelf_filter_gain_db, low_shelf_filter_q))

    if peak_filter_enabled:
        board.append(PeakFilter(peak_filter_cutoff_hz, peak_filter_gain_db, peak_filter_q))

    if ladder_filter_enabled:
        board.append(LadderFilter(getattr(LadderFilter.Mode,ladder_filter_mode),
            ladder_filter_cutoff_hz, ladder_filter_resonance, ladder_filter_drive))

    if limiter_enabled:
        board.append(Limiter(limiter_threshold_db, limiter_release_ms))

    if clipping_enabled:
        board.append(Clipping(clipping_threshold))

    print(board)

    sample_rate, audio_data = audio_in

    #Gradio loads audio as int16 - pedalboard needs audio in float32
    #convertion per https://stackoverflow.com/questions/42544661/convert-numpy-int16-audio-array-to-float32/42544738#42544738
    audio_data = np.ascontiguousarray(audio_data.T.astype(np.float32, order='C') / 32768.0)

    if padding_start_sec > 0 or padding_end_sec > 0:
        num_channels = audio_data.shape[0]

        vals = []
        if padding_start_sec > 0:
            vals.append(np.zeros((num_channels, int(sample_rate * padding_start_sec))))
        vals.append(audio_data)
        if padding_end_sec > 0:
            vals.append(np.zeros((num_channels, int(sample_rate * padding_end_sec))))

        audio_data = np.hstack(vals)

    out_audio = board(audio_data, sample_rate)

    if time_strech_factor != 1:
        # a few more args for this function per: https://spotify.github.io/pedalboard/reference/pedalboard.html#pedalboard.time_stretch
        out_audio = time_stretch(out_audio, sample_rate, time_strech_factor, pitchshift_semitones)

    out_audio = (out_audio.T * 32768.0).astype(np.int16) #convert back from float32 to int16 for Gradio frontend
    return (sample_rate, out_audio)
    
    '''#do this for very large audio files, where memory is a constraint
    with AudioFile(audio_in) as f:
        sample_rate = f.samplerate
        num_channels = f.num_channels
        data = f.read(f.frames)
        out_audio = board(data, sample_rate)

    with AudioFile(AUDIO_OUT_PATH, 'w', sample_rate, num_channels) as out:
        out.write(out_audio)

    return None
    '''

with gr.Blocks() as demo:

    with gr.Row():
        audio_in = gr.Audio(
            sources = ['upload','microphone'], #can also include 'microphone' if streaming = True
            type = 'numpy', #can be 'numpy' or 'filepath'
            label = 'Input Audio',
            interactive = True,
            editable = True,
            )

    with gr.Row():
        with gr.Column():
            gain = gr.Slider(label = 'Gain db', value = 0, minimum = -30, maximum = 30)

            with gr.Accordion(label = 'Noise Gate', open = False):
                gr.Markdown('A simple noise gate with standard threshold, ratio, attack time and release time controls. Can be used as an expander if the ratio is low')
                noise_gate_enabled = gr.Checkbox(label = 'Noise Gate Enabled')
                noise_gate_threshold_db = gr.Slider(label = 'Threshold db', value = -100, minimum = -200, maximum = 0)
                noise_gate_ratio = gr.Slider(label = 'Ratio', value = 0, minimum = 10, maximum = 20)
                noise_gate_attack_ms = gr.Slider(label = 'Attack ms', value = 1, minimum = 0, maximum = 10)
                noise_gate_release_ms = gr.Slider(label = 'Release ms', value = 100, minimum = 0, maximum = 300)

            with gr.Accordion(label = 'Reverb', open = False):
                reverb_enabled = gr.Checkbox(label = 'Reverb Enabled')
                reverb_room_size = gr.Slider(label = 'Room Size', value = 0.5, minimum = 0, maximum = 1)
                reverb_damping = gr.Slider(label = 'Damping', value = 0.5, minimum = 0, maximum = 1)
                reverb_wet_level = gr.Slider(label = 'Wet Level', value = 0.33, minimum = 0, maximum = 1)
                reverb_dry_level = gr.Slider(label = 'Dry Level', value = 0.4, minimum = 0, maximum = 1)
                reverb_width = gr.Slider(label = 'Width', value = 1, minimum = 0, maximum = 1)
                reverb_freeze_mode = gr.Slider(label = 'Freeze Mode', value = 0, minimum = 0, maximum = 1)

            with gr.Accordion(label = 'Delay', open = False):
                delay_enabled = gr.Checkbox(label = 'Delay Enabled')
                delay_sec = gr.Slider(label = 'Delay Seconds', value = 0.5, minimum = 0, maximum = 3) #technically max value is 30sec
                delay_feedback = gr.Slider(label = 'Feedback', value = 0, minimum = 0, maximum = 1)
                delay_mix = gr.Slider(label = 'Dry/Wet Mix', value = 0.5, minimum = 0, maximum = 1)


            with gr.Accordion(label = 'Chorus', open = False):
                chorus_enabled = gr.Checkbox(label = 'Chorus Enabled')
                chorus_rate_hz = gr.Slider(label = 'Rate Hz', value = 1, minimum = 0, maximum = 100) #hard limit is 100hz
                chorus_depth = gr.Slider(label = 'Depth', value = 0.25, minimum = 0, maximum = 1) #no hard limits here
                chorus_center_delay = gr.Slider(label = 'Centre Delay ms', value = 7, minimum = 0, maximum = 50) #no hard limits here
                chorus_feedback = gr.Slider(label = 'Feedback', value = 0, minimum = 0, maximum = 1) #no hard limits here
                chorus_mix = gr.Slider(label = 'Mix', value = 0.5, minimum = 0, maximum = 1) #no hard limits here

            with gr.Accordion(label = 'Phaser', open = False):
                phaser_enabled = gr.Checkbox(label = 'Phaser Enabled')
                phaser_rate_hz = gr.Slider(label = 'Rate Hz', value = 1, minimum = 0, maximum = 100)
                phaser_depth = gr.Slider(label = 'Depth', value = 0.25, minimum = 0, maximum = 1) #no hard limits here
                phaser_center_frequency = gr.Slider(label = 'Centre Frequency Hz', value = 1300, minimum = 0, maximum = 3000) #no hard limits here
                phaser_feedback = gr.Slider(label = 'Feedback', value = 0, minimum = 0, maximum = 1) #no hard limits here
                phaser_mix = gr.Slider(label = 'Mix', value = 0.5, minimum = 0, maximum = 1) #no hard limits here

            with gr.Accordion(label = 'Pitch Shift', open = False):
                pitchshift_enabled = gr.Checkbox(label = 'Pitch Shift Enabled (12 = one octave)')
                pitchshift_semitones = gr.Slider(label = 'Semitones', value = 0, minimum = -72, maximum = 72)

            with gr.Accordion(label = 'Compressor', open = False):
                gr.Markdown('Reduce the volume of loud sounds and “compress” the loudness of the signal')
                compressor_enabled = gr.Checkbox(label = 'Compressor Enabled')
                compressor_threshold_db = gr.Slider(label = 'Threshold db', value = 0, minimum = -30, maximum = 10)
                compressor_ratio = gr.Slider(label = 'Ratio', value = 1, minimum = 1, maximum = 20)
                compressor_attack_ms = gr.Slider(label = 'Attack ms', value = 1, minimum = 0, maximum = 10)
                compressor_release_ms = gr.Slider(label = 'Release ms', value = 100, minimum = 0, maximum = 300)

        with gr.Column():
            with gr.Accordion(label = 'Distortion', open = False):
                distortion_enabled = gr.Checkbox(label = 'Distortion Enabled')
                distortion_drive_db = gr.Slider(label = 'Drive db', value = 25, minimum = 0, maximum = 100) #no hard limits here

            with gr.Accordion(label = 'Bitcrush', open = False):
                bitcrush_enabled = gr.Checkbox(label = 'Bitcrush Enabled')
                bitcrush_bit_depth = gr.Slider(label = 'Bit Depth', value = 8, minimum = 0, maximum = 32, step = 1)

            with gr.Accordion(label = 'GSM Full Rate Compressor', open = False):
                gr.Markdown('Applies the GSM “Full Rate” compression algorithm to emulate the sound of a 2G cellular phone connection. Default - WindowedSinc8')
                gsm_full_rate_compressor = gr.Dropdown(label = 'GSM Full Rate Compressor Quality',
                    choices = ['None', 'ZeroOrderHold', 'Linear', 'CatmullRom', 'Lagrange', 'WindowedSinc', 
                        'WindowedSinc256', 'WindowedSinc128', 'WindowedSinc64', 'WindowedSinc32', 'WindowedSinc16',
                         'WindowedSinc8'],
                    value = 'None')

            with gr.Accordion(label = 'MP3 Compressor', open = False):
                gr.Markdown('Runs the LAME MP3 encoder to add compression artifacts to the audio stream')
                mp3_compressor_enabled = gr.Checkbox(label = 'MP3 Compressor Enabled')
                mp3_compressor_vbr_quality = gr.Slider(label = 'VBR Quality', value = 2, minimum = 0, maximum = 10)

            with gr.Accordion(label = 'Resample', open = False):
                gr.Markdown('Downsamples the input audio to the given sample rate, then upsamples it back to the original sample rate. Various quality settings will produce audible distortion and aliasing effects')
                resample_method = gr.Dropdown(label = 'Resample Method',
                    choices = ['None', 'ZeroOrderHold', 'Linear', 'CatmullRom', 'Lagrange', 'WindowedSinc', 
                        'WindowedSinc256', 'WindowedSinc128', 'WindowedSinc64', 'WindowedSinc32', 'WindowedSinc16',
                         'WindowedSinc8'],
                    value = 'None')
                resample_target_sample_rate = gr.Slider(label = 'Target Sample Rate Hz', value = 8000, minimum = 0, maximum = 44100)

            with gr.Accordion(label = 'Padding', open = False):
                padding_start_sec = gr.Slider(label = 'Padding added to start of audio', value = 0, minimum = 0, maximum = 5)
                padding_end_sec = gr.Slider(label = 'Padding added to end of audio', value = 0, minimum = 0, maximum = 5)

            with gr.Accordion(label = 'Time Stretch', open = False):
                # can also put in a numpy array for this, to allow for stretch/pitchshift to vary over time
                # but requires a bit more work on frontend
                time_strech_factor = gr.Slider(label = 'Stretch Factor (Higher = faster / shorter audio). Applied after all other transforms.', 
                    value = 1, minimum = 0, maximum = 4) #not a hard upper limit
                time_strech_pitch_shift_semitones = gr.Slider(label = 'Pitch Shift In Semitones', 
                    value = 0, minimum = -72, maximum = 72)


        with gr.Column():
            with gr.Accordion(label = 'Highpass Filter', open = False):
                highpass_filter_enabled = gr.Checkbox(label = 'Highpass Filter Enabled')
                highpass_filter_cutoff_frequency = gr.Slider(label = 'Cutoff Frequency Hz', value = 50, minimum = 0, maximum = 5000) #no hard limits here

            with gr.Accordion(label = 'Lowpass Filter', open = False):
                lowpass_filter_enabled = gr.Checkbox(label = 'Lowpass Filter Enabled')
                lowpass_filter_cutoff_frequency = gr.Slider(label = 'Cutoff Frequency Hz', value = 50, minimum = 0, maximum = 5000)

            with gr.Accordion(label = 'High Shelf Filter', open = False):
                gr.Markdown('Frequencies above the cutoff frequency will be boosted/cut by the provided gain')
                high_shelf_filter_enabled = gr.Checkbox(label = 'High Shelf Filter Enabled')
                high_shelf_filter_cutoff_hz = gr.Slider(label = 'Cutoff Frequency Hz', value = 440, minimum = 0, maximum = 5000)
                high_shelf_filter_gain_db = gr.Slider(label = 'Gain db', value = 0, minimum = -30, maximum = 30)
                high_shelf_filter_q = gr.Slider(label = 'Q', value = 0.7071, minimum = 0, maximum = 1)

            with gr.Accordion(label = 'Low Shelf Filter', open = False):
                gr.Markdown('Frequencies below the cutoff frequency will be boosted/cut by the provided gain')
                low_shelf_filter_enabled = gr.Checkbox(label = 'Low Shelf Filter Enabled')
                low_shelf_filter_cutoff_hz = gr.Slider(label = 'Cutoff Frequency Hz', value = 440, minimum = 0, maximum = 5000)
                low_shelf_filter_gain_db = gr.Slider(label = 'Gain db', value = 0, minimum = -30, maximum = 30)
                low_shelf_filter_q = gr.Slider(label = 'Q', value = 0.7071, minimum = 0, maximum = 1)

            with gr.Accordion(label = 'Peak Filter', open = False):
                gr.Markdown('Notich filter - frequencies around the cutoff frequency will be boosted/cut by the provided gain')
                peak_filter_enabled = gr.Checkbox(label = 'Peak Filter Enabled')
                peak_filter_cutoff_hz = gr.Slider(label = 'Cutoff Frequency Hz', value = 440, minimum = 0, maximum = 5000)
                peak_filter_gain_db = gr.Slider(label = 'Gain db', value = 0, minimum = -30, maximum = 30)
                peak_filter_q = gr.Slider(label = 'Q', value = 0.7071, minimum = 0, maximum = 1)

            with gr.Accordion(label = 'Ladder Filter', open = False):
                ladder_filter_enabled = gr.Checkbox(label = 'Ladder Filter Enabled')
                ladder_filter_mode = gr.Dropdown(label = 'Mode', choices = ['LPF12', 'HPF12', 'BPF12', 'LPF24', 'HPF24', 'BPF24'])
                ladder_filter_cutoff_hz = gr.Slider(label = 'Cutoff Hz', value = 200, minimum = 0, maximum = 5000)
                ladder_filter_resonance = gr.Slider(label = 'Resonance', value = 0, minimum = 0, maximum = 1)
                ladder_filter_drive = gr.Slider(label = 'Drive', value = 1, minimum = 1, maximum = 10)

            with gr.Accordion(label = 'Limiter', open = False):
                limiter_enabled = gr.Checkbox(label = 'Limiter Enabled')
                limiter_threshold_db = gr.Slider(label = 'Threshold db', value = -10, minimum = -30, maximum = 0)
                limiter_release_ms = gr.Slider(label = 'Release ms', value = 100, minimum = 0, maximum = 500)

            with gr.Accordion(label = 'Clipping', open = False):
                clipping_enabled = gr.Checkbox(label = 'Clipping Enabled')
                clipping_threshold = gr.Slider(label = 'Clipping Threshold db', value = -6, minimum = -30, maximum = 20)

    with gr.Row():
        submit_button = gr.Button('Submit')

    with gr.Row():
        audio_out = gr.Audio(label = 'Output Audio', interactive = False, show_download_button = True, loop = True)

    submit_button.click(fn = process_audio, 
        inputs = [audio_in,
            gain,
            noise_gate_enabled, noise_gate_threshold_db, noise_gate_ratio, noise_gate_attack_ms, noise_gate_release_ms,
            reverb_enabled, reverb_room_size, reverb_damping, reverb_wet_level, reverb_dry_level, reverb_width, reverb_freeze_mode,
            delay_enabled, delay_sec, delay_feedback, delay_mix,
            chorus_enabled, chorus_rate_hz, chorus_depth, chorus_center_delay, chorus_feedback, chorus_mix,
            phaser_enabled, phaser_rate_hz, phaser_depth, phaser_center_frequency, phaser_feedback, phaser_mix,
            pitchshift_enabled, pitchshift_semitones,
            compressor_enabled, compressor_threshold_db, compressor_ratio, compressor_attack_ms, compressor_release_ms,

            distortion_enabled, distortion_drive_db,
            bitcrush_enabled, bitcrush_bit_depth,
            gsm_full_rate_compressor,
            mp3_compressor_enabled, mp3_compressor_vbr_quality,
            resample_method, resample_target_sample_rate,

            highpass_filter_enabled, highpass_filter_cutoff_frequency,
            lowpass_filter_enabled, lowpass_filter_cutoff_frequency,
            high_shelf_filter_enabled, high_shelf_filter_cutoff_hz, high_shelf_filter_gain_db, high_shelf_filter_q,
            low_shelf_filter_enabled, low_shelf_filter_cutoff_hz, low_shelf_filter_gain_db, low_shelf_filter_q,
            peak_filter_enabled, peak_filter_cutoff_hz, peak_filter_gain_db, peak_filter_q,      
            ladder_filter_enabled, ladder_filter_mode, ladder_filter_cutoff_hz, ladder_filter_resonance, ladder_filter_drive,
            limiter_enabled, limiter_threshold_db, limiter_release_ms,
            clipping_enabled, clipping_threshold,

            padding_start_sec, padding_end_sec,
            time_strech_factor, time_strech_pitch_shift_semitones,
            ],
        outputs = [audio_out])

demo.launch(inbrowser = True, server_port = 7680)
