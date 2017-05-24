"""
Project 1: narcotic melodies.

Ideas:
* Tonic, subdominant and dominant along with the octave are the building blocks
  of a melody, either in minor or major (switch).
* Can be in any key (argument).
* While key is given by user, software operates on intervals.
* Passing of chords, one after another is a state machine with a random element
* Program will also take an integer seed as a parameter and will make random
  decisions (which chord to play next, what to do with it).
"""
from midiutil.MidiFile import MIDIFile
import argparse
import random

MyMidi = MIDIFile(1, False, True, False, 1)  # (numTracks, removeDuplicates, deinterleave, adjust_origin, file_format)
Timer = 0  # Place in a track


def main():
    # Parsing arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("output", help="A filename (with a path), where the music will be saved.")
    parser.add_argument("-t", "--tempo", type=int, help="A tempo in Beats per Minute. Preferably in [60, 300]")
    parser.add_argument("-k", "--key", type=int, default=None, help="A starting key of a music - integer, "
                                                                    "preferably in [36, 96].")
    parser.add_argument("-l", "--length", type=int, default=15, help="A length of a track (in bars).")
    parser.add_argument("-s", "--seed", type=int,
                        help="Make generator deterministic: provide your seed value (integer).")
    parser.add_argument("-v", "--variant", choices=['m', 'M'], help="[m]inor or [M]ajor")
    args = parser.parse_args()

    # Preparing random
    if args.seed is None:
        random.seed()
    else:
        random.seed(args.seed)

    # Setting up remaining parameters
    if args.key and (args.key < 0 or args.key > 101):
        parser.error("A key must be an integer in [0,127] (best results with [36, 96]. Will now close.")

    if args.variant == 'm':
        third = 0
    elif args.variant == "M":
        third = 1
    else:
        third = random.choice([0, 1])

    if args.key is None:
        args.key = random.randint(36, 96)  # 96 is a last key that MAY sound well

    if args.tempo is None:
        args.tempo = random.randint(60, 300)  # 20 is minimum but 60 is reasonable for quality of music.
        # greater than 300 are possible, but make probability for optimal tempo smaller.

    # Setting up MIDIFilie
    MyMidi.addProgramChange(0, 0, 0, 0)  # main: default - piano (track, channel, time, program)
    MyMidi.addProgramChange(0, 1, 0, 48)  # chords: defaults to string ensemble
    MyMidi.addProgramChange(0, 2, 0, 0)  # bass: default - piano
    MyMidi.addTrackName(0, 0, "Narcotic melody")  # (track, time,trackName)
    MyMidi.addTempo(0, 0, args.tempo)  # (track, time, tempo)

    build_music(args.length, args.key, third)  # Actual music creation.

    # Finishing...
    binfile = open(args.output, 'wb')
    MyMidi.writeFile(binfile)
    binfile.close()


def build_music(length, key, third):
    chords = [key, key + 5, key + 7, key + 12]
    if chords[3] > 101:  # Don't let octave outreach the scale
        chords[3] = chords[0] - 12
    up = True
    # Main loop
    for i in range(length - 1):
        chord = Chord(key, third)
        random.choice(chord.pass_array)()
        if random.random() > 0.8:
            random.choice(chord.fx_array)()
        if (key == chords[1] or key == chords[2]) and up:
            key = chords[3]
        elif (key == chords[1] or key == chords[2]) and not up:
            key = chords[0]
        else:
            key = random.choice([chords[1], chords[2]])
            up = not up
    Chord(chords[2], third).ending()  # Finishing with dominant


class Chord:
    """ Class for creating piece of music within a specific chord"""
    def __init__(self, key, third=0):
        global Timer
        self.key = key
        self.third = third
        self.time = Timer
        Timer += 4
        if key > 101:
            self.shift = -12
        else:
            self.shift = 0

        self.pass_array = [self.pass_loop, self.pass_loop_backward, self.pass_all, self.pass_octave,
                           self.pass_triple, self.pass_p1, self.pass_two_seconds, self.pass_second,
                           self.pass_holmes, self.pass_p2, self.pass_got, self.pass_witcher, self.pass_null]
        self.fx_array = [self.fx_bass_key, self.fx_octave_change, self.fx_lead_change,
                         self.fx_background_change]

        # Background:
        MyMidi.addNote(0, 1, self.key, self.time, 4, 80)  # (track, channel, pitch, time, duration, volume)
        MyMidi.addNote(0, 1, self.key + 3 + self.third + self.shift, self.time, 4, 80)
        MyMidi.addNote(0, 1, self.key + 7 + self.shift, self.time, 4, 80)

    def pass_loop(self):
        MyMidi.addNote(0, 0, self.key, self.time, 1, 100)
        MyMidi.addNote(0, 0, self.key + 3 + self.third + self.shift, self.time + 1, 1, 100)
        MyMidi.addNote(0, 0, self.key + 7 + self.shift, self.time + 2, 1, 100)
        MyMidi.addNote(0, 0, self.key + 3 + self.third + self.shift, self.time + 3, 1, 100)

    def pass_loop_backward(self):
        MyMidi.addNote(0, 0, self.key + 7 + self.shift, self.time, 1, 100)
        MyMidi.addNote(0, 0, self.key + 3 + self.third + self.shift, self.time + 1, 1, 100)
        MyMidi.addNote(0, 0, self.key, self.time + 2, 1, 100)
        MyMidi.addNote(0, 0, self.key + 3 + self.third + self.shift, self.time + 3, 1, 100)

    def pass_all(self):
        for i in range(8):
            MyMidi.addNote(0, 0, self.key + i + self.shift, self.time + i * 0.5, 0.5, 100)

    def pass_octave(self):
        MyMidi.addNote(0, 0, self.key + self.shift, self.time, 3.5, 100)
        MyMidi.addNote(0, 0, self.key + 12 + self.shift, self.time, 3.5, 100)

    def pass_triple(self):  # whole chord, four times
        for i in range(4):
            MyMidi.addNote(0, 0, self.key, self.time + i, 0.5, 100)
            MyMidi.addNote(0, 0, self.key + 3 + self.third + self.shift, self.time + i, 0.5, 100)
            MyMidi.addNote(0, 0, self.key + 7 + self.shift, self.time + i, 0.5, 100)

    def pass_p1(self):
        MyMidi.addNote(0, 0, self.key, self.time, 1, 100)
        MyMidi.addNote(0, 0, self.key + 7 + self.shift, self.time + 1, 0.5, 100)
        MyMidi.addNote(0, 0, self.key + 5 + self.shift, self.time + 1.5, 0.5, 100)
        MyMidi.addNote(0, 0, self.key + 3 + self.third + self.shift, self.time + 2, 1, 100)
        MyMidi.addNote(0, 0, self.key, self.time + 3, 1, 100)

    def pass_two_seconds(self):
        MyMidi.addNote(0, 0, self.key, self.time, 1, 100)
        MyMidi.addNote(0, 0, self.key + 2, self.time + 1, 1, 100)
        MyMidi.addNote(0, 0, self.key + 7, self.time + 2, 1, 100)
        MyMidi.addNote(0, 0, self.key + 5, self.time + 3, 1, 100)

    def pass_second(self):
        MyMidi.addNote(0, 0, self.key, self.time, 1, 100)
        MyMidi.addNote(0, 0, self.key + 1 + self.third, self.time + 1, 1, 100)
        MyMidi.addNote(0, 0, self.key, self.time + 2, 1, 100)
        MyMidi.addNote(0, 0, self.key + 1 + self.third, self.time + 3, 1, 100)

    def pass_holmes(self):
        for i in range(4):
            MyMidi.addNote(0, 0, self.key, self.time + i, 0.5, 100)
            MyMidi.addNote(0, 0, self.key + 3 + self.third + self.shift, self.time + 0.5 + i, 1, 100)
            MyMidi.addNote(0, 0, self.key + 7 + self.shift, self.time + 0.5 + i, 1, 100)

    def pass_p2(self):
        MyMidi.addNote(0, 0, self.key + 2, self.time, 1, 100)
        MyMidi.addNote(0, 0, self.key, self.time + 1, 1, 100)
        MyMidi.addNote(0, 0, self.key + 7, self.time + 2, 1, 100)
        MyMidi.addNote(0, 0, self.key + 5, self.time + 3, 1, 100)

    def pass_got(self):
        MyMidi.addNote(0, 0, self.key + 7, self.time, 1, 100)
        MyMidi.addNote(0, 0, self.key + 3 + self.third + self.shift, self.time + 1, 1, 100)
        MyMidi.addNote(0, 0, self.key, self.time + 2, 1, 100)
        MyMidi.addNote(0, 0, self.key + 7, self.time + 3, 1, 100)

    def pass_witcher(self):
        MyMidi.addNote(0, 0, self.key, self.time, 2, 100)
        MyMidi.addNote(0, 0, self.key + 7, self.time + 2, 0.5, 100)
        MyMidi.addNote(0, 0, self.key + 5, self.time + 2.5, 0.5, 100)
        MyMidi.addNote(0, 0, self.key + 2, self.time + 3, 1, 100)

    @staticmethod
    def pass_null():
        pass

    def fx_bass_key(self):
        MyMidi.addNote(0, 2, (self.key - 24) % 128, self.time, 4, 110)

    def fx_octave_change(self):
        min = self.key // 12
        max = (96 - self.key) // 12  # 96 is the last key that sounds good
        multiplier = random.randint(-1 * min, max)
        self.key += multiplier * 12

    def fx_lead_change(self):
        MyMidi.addProgramChange(0, 0, self.time, random.randint(0, 100))

    def fx_background_change(self):
        MyMidi.addProgramChange(0, 1, self.time, random.randint(48, 50))

    def ending(self):
        MyMidi.addNote(0, 0, self.key + 5, self.time, 2, 100)
        MyMidi.addNote(0, 0, self.key + 7, self.time + 2, 6, 100)


if __name__ == "__main__":
    main()
