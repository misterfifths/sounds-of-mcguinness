# Sounds of McGuinness

[![May 16 - 21](analyze/graphs/all-together.png)](analyze/graphs)

[More graphs](analyze/graphs).

You can also [listen](https://soundcloud.com/tim-clem-404086192/sounds-of-mcguinness).


### What's this then?

I live on McGuinness Boulevard, a loud, 4-lane road in Brooklyn. This project started because I wondered just how loud it actually is. And how loud is *too* loud, both legally and psychically.

![My apartment](docs/images/home.jpg)
*It looks so calm with no cars on it.*

To that end, I learned a lot about sound (turns out it's really complicated) and the laws concerning traffic noise. I bought a microphone and recorded the street for 6 days. The result is some [pretty graphs](analyze/graphs) and an [obnoxious supercut](https://soundcloud.com/tim-clem-404086192/sounds-of-mcguinness) of all the (potentially) illegal road noise.

This document describes my research and process.


### External Resources

- The supercut of all (potentially) illegal sounds over a 6-day recording period in May 2017 is located [here](https://soundcloud.com/tim-clem-404086192/sounds-of-mcguinness). It was generated with the [analysis scripts](analyze) in this project.
- The raw AAC files captured by the [iOS app](NoiseRecorder) are [here](https://drive.google.com/open?id=0By0v4sT5asPNNmctcjc3ZWFjVXc). They are under the [CC by-attribution 3.0 license](https://creativecommons.org/licenses/by/3.0/us/).


### McGuinness

Greenpoint's own "McGuinness Expressway" (aka the "Pulaski Raceway", aka the "Boulevard of Death") connects the Pulaski Bridge to the BQE. I can't find anything concrete blaming the abomination on Robert Moses, but I'm going to assume he at least smiled upon its creation.

In 2014, as part of a citywide traffic fatality reduction program, the speed limit on the road was [reduced from 30 to 25 MPH](http://gothamist.com/2014/04/23/mcguinness_boulevard_gets_slow_zone.php). I didn't test the speed of vehicles, but [the reduction seems to have made little difference](http://gothamist.com/2014/11/08/speed_limit_mcguinness.php). After all, it's a wide, 4-lane road that connects to a highway.


### dB, dBFS, dBA, and you



### The law and other concerns

#### NYC

Now that we understand a bit about measuring sound, let's turn to the lawbooks. NYC's rules are a little bit complicated. They're the purview of the Department of Environmental Protection, and laid out in the [Administrative Code, Title 24, Subchapter 6, Section 236](http://library.amlegal.com/nxt/gateway.dll/New%20York/admin/title24environmentalprotectionandutiliti/chapter2noisecontrol?f=templates$fn=default.htm$3.0$vid=amlegal:newyork_ny$anc=JD_24-236). If you follow the chain from subsection e, you find that the actual decibel limits are in "section 386 of the vehicle and traffic law."

Below, I've collated what [VAT § 386, tables 1, 2 & 3](http://nyscriminallaws.com/vt/article10.htm#t386) have to say in one table. These measurements are to be collected at 50 feet from the center of the front of the vehicle.

| Vehicle type      | Max. dBA ≤ 35 MPH | Max. dBA > 35 MPH
--------------------|-------------------|------------------
| Truck (>10k lbs)  | 86                | 90
| Motorcycle        | 82                | 86
| Other (e.g., cars)| 76                | 82

Interestingly, [as of 1998](http://www.nonoise.org/lawlib/cities/newyork.htm#232) (and probably later), the limit on the "Other" category was 70 dBA. NYC actually **raised** the limit for cars at some point in recent history. WTF?

One other salient bit of the code is this: on roads with a speed limit of 35 MPH or less, the use of [compression brakes](https://www.youtube.com/watch?v=kc9-hYFQR3I&feature=youtu.be&t=86) (aka jake brakes) is illegal except in emergencies ([NYC AC § 24-236(d)(2)](http://library.amlegal.com/nxt/gateway.dll/New%20York/admin/title24environmentalprotectionandutiliti/chapter2noisecontrol?f=templates$fn=default.htm$3.0$vid=amlegal:newyork_ny$anc=JD_24-236)). I counted at least 58 uses of a jake brake in my 6-day recording session (see runs tagged "jake brake" in the [raw data](analyze/raw)).


#### WHO

For reference, I thought it would be interesting to track down other recommendations on sound limits. The World Health Organization published the [Night Noise Guidelines for Europe](http://www.euro.who.int/__data/assets/pdf_file/0017/43316/E92845.pdf) in 2009. They suggest that "[i]f negative effects on sleep are to be avoided the equivalent sound pressure
level should not exceed 30 dBA indoors for continuous noise."


### Setup


### Processing
