//
//  ViewController.m
//  NoiseRecorder
//
//  Created by Timothy Clem on 5/11/17.
//  Under the MIT license; see LICENSE in the root of the repository
//

#import <AVFoundation/AVFoundation.h>
#import <GCDWebServer/GCDWebServer.h>
#import <GCDWebServer/GCDWebUploader.h>
#import <GCDWebServer/GCDWebDAVServer.h>
#import <stdarg.h>
#import "ViewController.h"

// Don't believe the hype, kids:
// massive view controllers are the way to go.

@interface ViewController () <UITableViewDelegate, UITableViewDataSource, AVAudioRecorderDelegate, GCDWebUploaderDelegate, GCDWebDAVServerDelegate>

@property (weak, nonatomic) IBOutlet UIButton *recordButton;
@property (weak, nonatomic) IBOutlet UILabel *durationLabel;
@property (weak, nonatomic) IBOutlet UILabel *averageLabel;
@property (weak, nonatomic) IBOutlet UILabel *peakLabel;

@property (weak, nonatomic) IBOutlet UITextView *logView;

@property (nonatomic, strong) NSArray *audioFileURLs;
@property (weak, nonatomic) IBOutlet UITableView *tableView;

@property (nonatomic, strong) AVAudioRecorder *audioRecorder;
@property (nonatomic, strong) NSTimer *meterTimer;

@property (nonatomic, assign) NSTimeInterval chunkDuration;

@property (nonatomic, assign) BOOL stoppingDueToUserInput;

@property (nonatomic, strong) GCDWebUploader *webUploader;
@property (nonatomic, strong) GCDWebDAVServer *webDAVServer;
@property (weak, nonatomic) IBOutlet UILabel *serverAddressLabel;

@end


@implementation ViewController

-(void)viewDidLoad
{
    self.chunkDuration = 2 * 60 * 60;

    [super viewDidLoad];
    [self refreshTableView];

    [self startWebServers];
}

-(IBAction)recordButtonTapped:(id)sender
{
    if(self.audioRecorder.isRecording) {
        self.stoppingDueToUserInput = YES;
        [self stopRecording];
    }
    else [self startRecording];
}

-(void)stopRecording
{
    [self.audioRecorder stop];
}

-(void)recordingStoppedAndShouldContinue:(BOOL)startNewRecording
{
    self.audioRecorder = nil;

    [self.meterTimer invalidate];
    self.meterTimer = nil;

    NSError *error = nil;
    if(![[AVAudioSession sharedInstance] setActive:NO withOptions:AVAudioSessionSetActiveOptionNotifyOthersOnDeactivation error:&error]) {
        [self logFormat:@"Error deactivating audio session: %@", error];
    }

    [UIApplication sharedApplication].idleTimerDisabled = NO;
    [self refreshTableView];

    if(!startNewRecording) {

        self.recordButton.enabled = YES;
        [self.recordButton setTitle:@"Record" forState:UIControlStateNormal];
    } else {
        [self log:@"---- Starting new chunk ----"];
        [self startRecording];
    }
}

-(void)startRecording
{
    NSError *error = nil;

    // Find input
    // Have to set category on the audio session before hunting for inputs to actually get wired mics to show up
    if(![[AVAudioSession sharedInstance] setCategory:AVAudioSessionCategoryRecord mode:AVAudioSessionModeMeasurement options:0 error:&error]) {
        [self logFormat:@"Error setting audio session category and mode: %@", error];
        return;
    }

    AVAudioSessionPortDescription *wiredMic = [self firstWiredAudioInput];
    if(!wiredMic) {
        [self log:@"No wired mic? Aborting."];
        return;
    }
    else {
        [self logFormat:@"Found wired mic: %@ (UID %@)", wiredMic.portName, wiredMic.UID];
    }


    // Prepare recorder
    NSString *startTimestamp = [self filenameFriendlyTimestamp];
    NSURL *fileURL = [self urlForDocumentsFileNamed:[NSString stringWithFormat:@"%@.aac", startTimestamp]];
    NSDictionary *recordingSettings = @{ AVFormatIDKey: @(kAudioFormatMPEG4AAC),
                                         AVSampleRateKey: @44100.0,
                                         AVNumberOfChannelsKey: @1 };

    self.audioRecorder = [[AVAudioRecorder alloc] initWithURL:fileURL settings:recordingSettings error:&error];
    if(!self.audioRecorder) {
        [self logFormat:@"Error making audio recorder: %@", error];
        return;
    }
    else {
        [self logFormat:@"Successfully made audio recorder. Will record to %@.aac", startTimestamp];
    }

    self.audioRecorder.meteringEnabled = YES;
    self.audioRecorder.delegate = self;

    if(![self.audioRecorder prepareToRecord]) {
        [self log:@"Audio recorder failed to prepare to record. Ignoring for now..."];
    }


    // Finish prepping audio session
    if(![[AVAudioSession sharedInstance] setPreferredInput:wiredMic error:&error]) {
        [self logFormat:@"Error setting audio session input: %@", error];
        self.audioRecorder = nil;
        return;
    }

    if(![[AVAudioSession sharedInstance] setActive:YES error:&error]) {
        [self logFormat:@"Error activating audio session: %@", error];
        self.audioRecorder = nil;
        return;
    }

    [self logFormat:@"Configured and activated audio session"];


    // Go!
    if(![self.audioRecorder recordForDuration:self.chunkDuration]) {
        [self log:@"Audio recorder failed to record! How mysterious. Aborting."];
        self.audioRecorder = nil;
        return;
    }

    [self log:@"Recording has begun!"];

    [self.recordButton setTitle:@"Stop" forState:UIControlStateNormal];

    self.meterTimer = [NSTimer scheduledTimerWithTimeInterval:0.5 target:self selector:@selector(updateMeters) userInfo:nil repeats:YES];

    [UIApplication sharedApplication].idleTimerDisabled = YES;

    [self refreshTableView];
}

-(void)updateMeters
{
    if(self.audioRecorder.isRecording) {
        self.durationLabel.text = [self hmsForTimeInterval:self.audioRecorder.currentTime];

        [self.audioRecorder updateMeters];
        self.averageLabel.text = [NSString stringWithFormat:@"%.2f dBFS", [self.audioRecorder averagePowerForChannel:0]];
        self.peakLabel.text = [NSString stringWithFormat:@"%.2f dBFS", [self.audioRecorder peakPowerForChannel:0]];
    }
    else {
        self.durationLabel.text = self.averageLabel.text = self.peakLabel.text = @"-";
    }
}


#pragma mark - UITableViewDelegate & DataSource

-(void)refreshTableView
{
    NSError *error = nil;
    self.audioFileURLs = [[NSFileManager defaultManager] contentsOfDirectoryAtURL:[self documentsDirectory]
                                                       includingPropertiesForKeys:nil
                                                                          options:NSDirectoryEnumerationSkipsSubdirectoryDescendants
                                                                            error:&error];

    if(!self.audioFileURLs) {
        [self logFormat:@"Error getting list of recordings: %@", error];
    }
    else {
        self.audioFileURLs = [self.audioFileURLs sortedArrayUsingComparator:^NSComparisonResult(NSURL *url1, NSURL *url2) {
            return [url1.lastPathComponent compare:url2.lastPathComponent];
        }];
    }

    [self.tableView reloadData];
}

-(NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

-(NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return self.audioFileURLs.count;
}

-(UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:@"fileCell" forIndexPath:indexPath];

    NSURL *url = self.audioFileURLs[indexPath.row];
    cell.textLabel.text = [[url lastPathComponent] stringByDeletingPathExtension];
    if([url.lastPathComponent isEqual:self.audioRecorder.url.lastPathComponent]) {
        cell.textLabel.text = [NSString stringWithFormat:@"(*) %@", cell.textLabel.text];
    }

    return cell;
}

-(BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath
{
    NSURL *url = self.audioFileURLs[indexPath.row];
    return ![url.lastPathComponent isEqual:self.audioRecorder.url.lastPathComponent];
}

-(void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
    if(editingStyle != UITableViewCellEditingStyleDelete) return;

    NSURL *url = self.audioFileURLs[indexPath.row];
    NSError *error = nil;
    if(![[NSFileManager defaultManager] removeItemAtURL:url error:&error]) {
        [self logFormat:@"Error deleting file: %@", error];
    }

    [self refreshTableView];
}


#pragma mark - AVAudioRecorderDelegate

-(void)audioRecorderEncodeErrorDidOccur:(AVAudioRecorder *)recorder error:(NSError *)error
{
    [self logFormat:@"Audio encoder error: %@", error];
    [self recordingStoppedAndShouldContinue:NO];
}

-(void)audioRecorderDidFinishRecording:(AVAudioRecorder *)recorder successfully:(BOOL)flag
{
    if(!flag) {
        [self log:@"Audio recorder finished unsucessfully!"];
    }
    else {
        [self log:@"Recording finished successfully"];
    }

    [self recordingStoppedAndShouldContinue:!self.stoppingDueToUserInput];
    self.stoppingDueToUserInput = NO;
}


#pragma mark - Web server

-(void)startWebServers
{
    NSString *documentsDirectory = [self documentsDirectory].path.stringByStandardizingPath;
    [[NSFileManager defaultManager] createDirectoryAtURL:[self documentsDirectory] withIntermediateDirectories:YES attributes:nil error:NULL];
    NSError *error;

    self.webUploader = [[GCDWebUploader alloc] initWithUploadDirectory:documentsDirectory];
    self.webUploader.delegate = self;
    error = nil;
    if(![self.webUploader startWithOptions:@{ GCDWebServerOption_Port: @8080 } error:&error]) {
        [self logFormat:@"Error starting HTTP server: %@", error];
        self.webUploader = nil;
    }

    self.webDAVServer = [[GCDWebDAVServer alloc] initWithUploadDirectory:documentsDirectory];
    self.webDAVServer.delegate = self;
    error = nil;
    if(![self.webDAVServer startWithOptions:@{ GCDWebServerOption_Port: @8181 } error:&error]) {
        [self logFormat:@"Error staring WebDAV server: %@", error];
        self.webDAVServer = nil;
    }

    if(self.webUploader) {
        if(self.webDAVServer) {
            self.serverAddressLabel.text = [NSString stringWithFormat:@"HTTP: %@ | WebDAV: %@", self.webUploader.serverURL, self.webDAVServer.serverURL];
        }
        else {
            self.serverAddressLabel.text = [NSString stringWithFormat:@"HTTP: %@", self.webUploader.serverURL];
        }
    }
    else if(self.webDAVServer) {
        self.serverAddressLabel.text = [NSString stringWithFormat:@"WebDAV: %@", self.webDAVServer.serverURL];
    }
}

-(void)stopWebServer
{
    [self.webUploader stop];
    self.webUploader = nil;

    [self.webDAVServer stop];
    self.webDAVServer = nil;

    self.serverAddressLabel.text = @"Server not started";
}

-(void)webUploader:(GCDWebUploader *)uploader didDeleteItemAtPath:(NSString *)path
{
    [self refreshTableView];
}

-(void)davServer:(GCDWebDAVServer *)server didDeleteItemAtPath:(NSString *)path
{
    [self refreshTableView];
}


#pragma mark - Utils

-(nullable AVAudioSessionPortDescription *)firstWiredAudioInput
{
    for(AVAudioSessionPortDescription *input in [AVAudioSession sharedInstance].availableInputs) {
        if([input.portType isEqualToString:AVAudioSessionPortHeadsetMic]) {
            return input;
        }
    }

    return nil;
}

-(void)log:(NSString *)message
{
    NSLog(@"%@", message);
    self.logView.text = [NSString stringWithFormat:@"[%@] %@\n%@", [self filenameFriendlyTimestamp], message, self.logView.text];
}

-(void)logFormat:(NSString *)format, ... NS_FORMAT_FUNCTION(1,2)
{
    va_list args;
    va_start(args, format);
    [self log:[[NSString alloc] initWithFormat:format arguments:args]];
    va_end(args);
}

-(NSString *)filenameFriendlyTimestamp
{
    static NSDateFormatter *formatter = nil;
    if(!formatter) {
        formatter = [NSDateFormatter new];
        formatter.locale = [NSLocale localeWithLocaleIdentifier:@"en_US_POSIX"];
        formatter.timeZone = [NSTimeZone localTimeZone];
        formatter.dateFormat = @"yyyy-MM-dd'T'HH-mm-ss";
    }

    return [formatter stringFromDate:[NSDate date]];
}

-(NSURL *)documentsDirectory
{
    return [[NSFileManager defaultManager] URLsForDirectory:NSDocumentDirectory inDomains:NSUserDomainMask].lastObject;
}

-(NSURL *)urlForDocumentsFileNamed:(NSString *)filename
{
    return [[self documentsDirectory] URLByAppendingPathComponent:filename];
}

-(NSString *)hmsForTimeInterval:(NSTimeInterval)seconds
{
    NSUInteger hours = seconds / 60 / 60;
    NSUInteger minutes = (NSUInteger)(seconds / 60) % 60;
    NSUInteger remainingSeconds = (NSUInteger)seconds % 60;

    return [NSString stringWithFormat:@"%lu:%02lu:%02lu", (unsigned long)hours, (unsigned long)minutes, (unsigned long)remainingSeconds];
}

@end
