# iOS Recording App

This directory contains the source for the iOS recording component of the project. It's a straightforward, barebones interface around an `AVAudioRecorder`.

### Requirements

- An iOS 10+ device. You should plug in the device, put it in airplane mode, and turn off anything that might interrupt the app (e.g., alarms).
- A calibrated wired microphone (I used a [Dayton Audio iMM-6](www.daytonaudio.com/index.php/imm-6-idevice-calibrated-measurement-microphone.html))

### Building

The app uses [Cocoapods](https://cocoapods.org/), so as usual:

- Install Cocoapods itself by following [these instructions](https://cocoapods.org/#install)
- Run `pod install` in this directory to fetch and configure dependencies
- Open the `NoiseRecorder.xcworkspace` file and build to your device.

### Use

Connect your wired microphone. Once you hit the "Record" button in the app, it will begin recording in 2-hour segments. These files will be listed in the lower table.

To copy files from your iOS device, connect to the HTTP or WebDAV URLs at the bottom of the screen (using a browser or Finder's "Connect to server...", respectively). You can copy and delete files while the app is recording, but be careful not to delete the file the app is currently recording to.

While the app is recording, your device is prevented from sleeping. Do not lock the screen or you will interrupt recording.

### Technical Details

There's not much special sauce here. We're recording to mono AAC at a 44.1kHz sample rate.

The only slightly magical detail is the configuration of the `AVAudioSession`. There's a special mode, `AVAudioSessionModeMeasurement` that, [according to Apple's documentation](https://developer.apple.com/reference/avfoundation/avaudiosessionmodemeasurement), minimizes "the amount of system-supplied signal processing to input and output signals." It disables automatic gain on the microphone, and presumably other niceties that we really don't want in this use case.
