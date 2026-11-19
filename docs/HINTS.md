# Hint Book (player safe)

Each hint is stronger than the one before. Release them on a timer or for a point cost.

## G1: Power Loss
1. A satellite with a working downlink shouldn't report a battery that is completely empty.
2. Filter for rows where `Battery_pct` is exactly 0. Look at the other values on those rows.
3. Those `Signal_Strength_dBm` values are positive whole numbers. Look up an ASCII table.

## G2: Clock Drift
1. The satellite samples on a regular schedule. Find out what that schedule is.
2. Work out the time between each row and the next. Most gaps are the same.
3. Each unusual gap, measured in seconds, is a character code.

## G3: Thermal Whisper
1. The temperature is recorded more precisely than any real sensor needs.
2. Multiply by 1000 to get whole millidegrees. Look at whether each value is odd or even.
3. Start at the first row. Take the lowest bit of each value, group the bits into 8s and decode them as ASCII.

## V1: SYNC
1. One frequency comes up far more often than chance would allow. Radio astronomers will know it.
2. Filter for `Frequency_MHz == 1420.400`.
3. Read `Pulse_Duration` on those rows, in order, as ASCII.

## V2: VECTOR
1. Ignore what the marker rows say. Look at when they happen.
2. Work out the gaps between consecutive 1420.400 rows. Only a few different values appear.
3. Two values are short and long signals. The others are pauses. Think of a telegraph.

## V3: COORD
1. The sky in the star map isn't all the same black.
2. Look at the exact pixel values, or push the brightness and levels all the way up.
3. Pixels with a value of exactly (1,1,1) form text.

## V4: PRIME
1. Leave out the marker rows. Some of the remaining pulse durations can't be divided by anything but 1 and themselves.
2. Keep only the prime `Pulse_Duration` values, in file order.
3. Take each prime mod 127 and read the result as ASCII.

## FINAL
- There's no hint. Talk to a judge once HANDSHAKE.SYS accepts all four markers.
