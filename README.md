# Sounds of McGuinness

[![May 16 - 21](analyze/graphs/all-together.png)](analyze/graphs)

[More graphs](analyze/graphs).

You can also [listen](https://soundcloud.com/tim-clem-404086192/sounds-of-mcguinness).


### What's this then?

I live on McGuinness Boulevard, a loud 4-lane road in Brooklyn. This project started because I wondered just how loud it actually is. And how loud is *too* loud, both legally and psychically.

![My apartment](docs/images/home.jpg)
*It looks so calm with no cars on it.*

To that end, I learned a lot about sound (turns out it's really complicated) and the laws concerning traffic noise. I bought a microphone and recorded the street for 6 days. The result is some [pretty graphs](analyze/graphs) and an [obnoxious supercut](https://soundcloud.com/tim-clem-404086192/sounds-of-mcguinness) of all the (potentially) illegal road noise.

This document describes my research and process.


### External Resources

- The supercut of all (potentially) illegal sounds over a 6-day recording period in May 2017 is located [here](https://soundcloud.com/tim-clem-404086192/sounds-of-mcguinness). It was generated with the [analysis scripts](analyze) in this project.
- The raw AAC files captured by the [iOS app](NoiseRecorder) are [here](https://drive.google.com/open?id=0By0v4sT5asPNNmctcjc3ZWFjVXc). They are under the [CC by-attribution 3.0 license](https://creativecommons.org/licenses/by/3.0/us/).


### McGuinness

Greenpoint's own "McGuinness Expressway" (aka the "Pulaski Raceway", aka the "Brooklyn Boulevard of Death") connects the Pulaski Bridge to the BQE. It started life as humble Oakland Street, but was widened in 1954. I can't find anything concrete blaming the project on Robert Moses, but I'm going to assume he strongly approved.

The road is [infamous for reckless driving](http://gothamist.com/2010/04/26/after_fatal_hit-and-run_mcguinness.php). In 2014, as part of a citywide program addressing traffic fatalities, the speed limit on the road was [reduced from 30 to 25 MPH](http://gothamist.com/2014/04/23/mcguinness_boulevard_gets_slow_zone.php). I didn't test the speed of vehicles, but it's probably safe to assume [the reduction made little difference](http://gothamist.com/2014/11/08/speed_limit_mcguinness.php). After all, it's a wide, 4-lane road that connects to two major highways.


### dB, dBFS, dB SPL, dBA, and you

Before turning to the legal limits on sound, let's talk about volume. Measuring loudness turns out to be complicated. You're probably thinking "it's just decibels – that doesn't sound so hard." Right and wrong.

[Wikipedia says](https://en.wikipedia.org/wiki/Decibel) that a decibel (dB) is "a logarithmic unit used to express the ratio of two values", one of which is some "standard reference value". There's the rub. Decibels, with no other qualification, are kind of a nonsense unit. You must describe to what they are relative, or the value has no meaning. When people talk about decibels in sound, they're usually talking about one of dBFS, dB SPL, or a weighted value like dBA.

dbFS is relative to "full scale" - the loudest sound the hardware supports before clipping (making a really horrible garbled noise). dBFS therefore varies with hardware. Somewhat strangly, the values are usually negative, with 0 representing the maximum volume and something like -3 meaning "three decibels below full scale." When using most audio software like, say, Audacity, this is the way volume is measured.

dB SPL is a measure of "sound pressure level." [Quoth Wikipedia](https://en.wikipedia.org/wiki/Sound_pressure#Sound_pressure_level), it's relative to 20 μPa, the threshold of human hearing. The result is a sensible unit, where everyone (mostly) agrees on the reference.

Finally, there's dBA. This is a weighted dB SPL, adjusted to account for human hearing such that equal dBA is roughly equal loudness. We perceive certain pitches more than others, meaning equal dB SPL is not necessarily equal *perceived* volume. Most measurements dealing with human perception of volume are in dBA. The "A" is for [A-weighting](https://en.wikipedia.org/wiki/A-weighting).

On top of the decibel confusion, there's distance to consider. Obviously, as you move farther away from a sound source, it becomes less loud. This fact makes a lot of those ["volume of common sounds" tables](https://www.nidcd.nih.gov/health/i-love-what-i-hear-common-sounds) largely meaningless unless they include the distance at which the measurement was taken.


### The law and other concerns

#### NYC

Now that we understand a bit about measuring sound, let's turn to the lawbooks. NYC's rules are a little bit complicated. They're the purview of the Department of Environmental Protection, and laid out in the [Administrative Code, Title 24, Subchapter 6, Section 236](http://library.amlegal.com/nxt/gateway.dll/New%20York/admin/title24environmentalprotectionandutiliti/chapter2noisecontrol?f=templates$fn=default.htm$3.0$vid=amlegal:newyork_ny$anc=JD_24-236). Subsection (e) states the actual decibel limits are in "section 386 of the vehicle and traffic law."

Below, I've collated [VAT § 386, tables 1, 2 & 3](http://nyscriminallaws.com/vt/article10.htm#t386). These measurements are to be collected at 50 feet from the center of the front of the vehicle.

| Vehicle type       | Max. dBA, speed limit ≤35 MPH | Max. dBA, speed limit >35 MPH
---------------------|-------------------|------------------
| Trucks (>10k lbs.) | 86                | 90
| Motorcycles        | 82                | 86
| Other (e.g., cars) | 76                | 82

Interestingly, [as of 1998](http://www.nonoise.org/lawlib/cities/newyork.htm#232) (and probably later), the limit on the "Other" category was 70 dBA. NYC actually **raised** the limit for cars at some point in recent history.

One other salient bit of the code is this: on roads with a speed limit of 35 MPH or less, the use of [compression brakes](https://www.youtube.com/watch?v=kc9-hYFQR3I&feature=youtu.be&t=86) (aka jake brakes) is illegal except in emergencies ([NYC AC § 24-236(d)(2)](http://library.amlegal.com/nxt/gateway.dll/New%20York/admin/title24environmentalprotectionandutiliti/chapter2noisecontrol?f=templates$fn=default.htm$3.0$vid=amlegal:newyork_ny$anc=JD_24-236)). I counted 58 uses of a jake brake over 70 dBA in my 6-day recording session (see runs tagged "jake brake" in the [raw data](analyze/raw)).

#### Enforcement

If you experience a loud vehicle, [NYC suggests you call 311](http://www1.nyc.gov/nyc-resources/faq/432/how-do-i-report-a-noisy-vehicle). From January 1, 2010 to May 28, 2017, there have been only 59 vehicular noise complaints involving McGuinness in some way (see the [311 data](https://nycopendata.socrata.com/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9)). To me, it makes sense this is so low – calling 311 to report a passing vehicle makes no sense. In fact, the 311 database doesn't even seem to have a category for engine, brake, or general vehicle noise – just music, horns, and idling.

So, how should these laws be enforced? The letter of the law would seemingly require precisely positioned microphones, one per lane, and cameras or humans to note the type of vehicle making noise. That scenario seems unlikely.

#### WHO

For reference, I thought it would be interesting to track down other recommendations on sound limits. The World Health Organization published the [Night Noise Guidelines for Europe](http://www.euro.who.int/__data/assets/pdf_file/0017/43316/E92845.pdf) in 2009. They suggest that "[i]f negative effects on sleep are to be avoided the equivalent sound pressure
level should not exceed 30 dBA indoors for continuous noise."


### Setup


### Processing

