# Audio Folder

This folder contains the audio samples (.wav) and their corresponding MIDI transcriptions (.mid) for the violin transcription demo.

## File Structure

Place your audio files in this directory with the following naming convention:
- `filename.wav` - Original audio file
- `filename.mid` - Corresponding MIDI transcription

## Sample Files

To add new samples to the demo:

1. Place your `.wav` and `.mid` files in this folder
2. Update the `samples` array in `index.html` with the new file paths:

```javascript
this.samples = [
    {
        name: "Your Sample Name",
        audioPath: "audio_folder/your_audio_file.wav",
        midiPath: "audio_folder/your_midi_file.mid"
    },
    // ... more samples
];
```

## Supported Formats

- **Audio**: WAV format recommended for best compatibility
- **MIDI**: Standard MIDI files (.mid)

## GitHub Pages Deployment

When deploying to GitHub Pages, ensure that:
1. All files are committed to your repository
2. GitHub Pages is enabled for your repository
3. Audio files are accessible via HTTPS (required for audio playback)

## Example Files

You can test the demo with sample files from:
- [Free MIDI files](https://freemidi.org/)
- [Classical MIDI archives](http://www.kunstderfuge.com/)
- Your own violin recordings and transcriptions 