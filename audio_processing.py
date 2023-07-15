"""
6.1010 Spring '23 Lab 0: Audio Processing
"""

import wave
import struct

# No additional imports allowed!


def backwards(sound):
    new_sound = {}
    new_sound["rate"] = sound["rate"]
    samples = sound["samples"]
    new_sound["samples"] = []
    for i in range(len(samples)):
        new_sound["samples"].append(samples[-i - 1])
    return new_sound


def mix(sound1, sound2, p):
    """
        Three inputs: two sounds (in our dictionary representation)
        and a "mixing parameter" p (a float such that 0<p<1)
        
        The resulting sound should take p times the samples in the
        first sound and 1−p times the samples in the second sound,
        and add them together to produce a new sound.
        
        The two input sounds should have the same sampling rate.
        If you are provided with sounds of two different sampling rates, you
        should return None instead of returning a sound.

        However, despite having the same sampling rate, the input
        sounds might have different durations. The length of the resulting
        sound should be the minimum of the lengths of the two input sounds,
        so that we are guaranteed a result where we can always hear
        both sounds (it would be jarring if one of the sounds cut off in the middle).
    """
    if not (
        "rate" in sound1.keys()
        and "rate" in sound2.keys()
        and sound1["rate"] == sound2["rate"]
    ):
        print("no")
        return

    r = sound1["rate"]  # get rate
    def mix_lists(list1, list2, p):
        length = min(len(list1),len(list2))
        samples = []
        x = 0
        while x <= length:
            s2, s1 = p * list1[x], list2[x] * (1 - p)
            samples.append(s1 + s2)  # add sounds
            x += 1
            if x == length:  # end
                break
        return samples
    if len(sound1) == 2:
        samples = mix_lists(sound1["samples"],sound2["samples"],p)
        return {"rate": r, "samples": samples}  # return new sound
    elif len(sound1) == 3:
        left = mix_lists(sound1["left"],sound2["left"],p)
        right = mix_lists(sound1["right"],sound2["right"],p)
        return {"rate": r, "left": left, "right": right}


def convolve(sound, kernel):
    """
    Applies a filter to a sound, resulting in a new sound that is longer than
    the original mono sound by the length of the kernel - 1.
    Does not modify inputs.

    Args:
        sound: A mono sound dictionary with two key/value pairs:
            * "rate": an int representing the sampling rate, samples per second
            * "samples": a list of floats containing the sampled values
        kernel: A list of numbers

    Returns:
        A new mono sound dictionary.
    """
    samples = sound["samples"]
    sound_length = len(samples)
    kernel_length = len(kernel)
    new_length = sound_length + kernel_length - 1
    final_sample = [0] * new_length
    #samples = []  # a list of scaled sample lists

    for i, scale in enumerate(kernel):
        #scaled_sample = [0] * i  # offset scaled sound by filter index
        #scaled_sample += [scale * x for x in sound["samples"]]
        #samples.append(scaled_sample)
        if scale != 0:
            for number in range(i,i + sound_length):
                final_sample[number] += scale * samples[number - i]

    return {"rate": sound["rate"], "samples": final_sample}


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """
    delay_n = round(delay * sound["rate"])
    echo_filter = [0] * (delay_n * num_echoes + 1)
    echo_filter[0] = 1
    for i in range(num_echoes):
        offset = (1 + i)*delay_n
        echo_filter[offset] = scale ** (i + 1)

    return convolve(sound, echo_filter)


def pan(sound):
    """
    Input: stero sound, a dictionary with sampling rate, left samples, and right samples
    Returns: stereo sound, with channels scaled according to specified rules
    """
    new_sound = {}
    new_sound["rate"] = sound["rate"]
    left = sound["left"]
    right = sound["right"]
    length = len(left)
    new_sound["left"] = []
    new_sound["right"] = []
    for i in range(length):
        new_sound["left"].append(left[i]*(1 - i/(length - 1)))
        new_sound["right"].append(right[i]*(i/(length - 1)))

    return new_sound


def remove_vocals(sound):
    """
    Input: stero sound, a dictionary with sampling rate, left samples, and right samples
    Returns: mono sound, where each sample is equal to the left sample of the input
    minus the right sample
    """
    new_sound = {}
    new_sound["rate"] = sound["rate"]
    left = sound["left"]
    right = sound["right"]
    length = len(left)
    new_sound["samples"] = []
    for i in range(length):
        new_sound["samples"].append(left[i] - right[i])

    return new_sound

# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def bass_boost_kernel(boost, scale=0):
    """
    Constructs a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.

    Args:
        boost: an int that controls the frequencies that are boosted (0 will
            boost all frequencies roughly equally, and larger values allow more
            focus on the lowest frequencies in the input sound).
        scale: a float, default value of 0 means no boosting at all, and larger
            values boost the low-frequency content more);

    Returns:
        A list of floats representing a bass boost kernel.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    kernel = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    for i in range(boost):
        kernel = convolve(kernel, base["samples"])
    kernel = kernel["samples"]

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel) // 2] += 1

    return kernel


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    #hello = load_wav("sounds/hello.wav")

    # write_wav(backwards(hello), "hello_reversed.wav")

    #synth = load_wav("sounds/synth.wav")
    #water = load_wav("sounds/water.wav")

    #write_wav(mix(synth, water, 0.2), "synth_water_mix.wav")

    #kernel = bass_boost_kernel(1000, 1.5)
    #ic = load_wav("sounds/ice_and_chilli.wav")
    #write_wav(convolve(ic, kernel), "bass_boosted_ic.wav")

    #chord = load_wav("sounds/chord.wav")
    #write_wav(echo(chord,5,0.3,0.6),"echo_chord.wav")

    #car = load_wav("sounds/car.wav", stereo=True)
    #write_wav(pan(car),"pan_car.wav")

    #lm = load_wav("sounds/lookout_mountain.wav", stereo=True)
    #write_wav(remove_vocals(lm),"rmv_voc_lm.wav")

    synth = load_wav("sounds/synth.wav", stereo=True)
    water = load_wav("sounds/water.wav", stereo=True)

    write_wav(mix(synth, water, 0.3), "synth_water_remix.wav")
