#!/usr/bin/env python3
"""
Audio Silence Trimmer

This script automatically trims silence from the start of all .wav files 
in a specified directory using librosa.

Usage:
    python trim_silence.py <directory_path> [options]

Options:
    --output-suffix: Suffix to add to output files (default: '_trimmed')
    --overwrite: Overwrite original files instead of creating new ones
    --recursive: Process subdirectories recursively
    --threshold: Silence threshold in dB (default: -60)
    --frame-length: Frame length for silence detection (default: 2048)
    --hop-length: Hop length for silence detection (default: 512)
"""

import os
import sys
import argparse
import glob
from pathlib import Path
import librosa
import soundfile as sf
import numpy as np
from tqdm import tqdm


def trim_silence_from_start(audio_path, threshold_db=-60, frame_length=2048, hop_length=512):
    """
    Trim silence from the start of an audio file and add 1 second of silence.
    
    Args:
        audio_path (str): Path to the audio file
        threshold_db (float): Silence threshold in dB
        frame_length (int): Frame length for analysis
        hop_length (int): Hop length for analysis
    
    Returns:
        tuple: (trimmed_audio, sample_rate, trim_start_samples)
    """
    try:
        # Load audio file
        audio, sr = librosa.load(audio_path, sr=None)
        
        # Use librosa's trim function to remove silence from start and end
        # We'll only use the start trimming
        trimmed_audio, trim_indices = librosa.effects.trim(
            audio, 
            top_db=-threshold_db,
            frame_length=frame_length,
            hop_length=hop_length
        )
        
        # Get the start trim point
        trim_start_samples = trim_indices[0] if len(trim_indices) > 0 else 0
        
        # Only trim from the start, keep the original end
        if trim_start_samples > 0:
            trimmed_audio = audio[trim_start_samples:]
        else:
            trimmed_audio = audio
        
        # Add 1 second of silence to the beginning
        silence_samples = int(sr * 1.0)  # 1 second of silence
        silence = np.zeros(silence_samples, dtype=trimmed_audio.dtype)
        trimmed_audio = np.concatenate([silence, trimmed_audio])
            
        return trimmed_audio, sr, trim_start_samples
        
    except Exception as e:
        print(f"Error processing {audio_path}: {str(e)}")
        return None, None, 0


def find_wav_files(directory, recursive=False):
    """
    Find all .wav or .mp3 files in the given directory.

    Args:
        directory (str): Directory path to search
        recursive (bool): Whether to search subdirectories

    Returns:
        list: List of .wav and .mp3 file paths
    """
    directory = Path(directory)
    wav_files = []
    mp3_files = []

    if recursive:
        wav_files.extend(directory.glob("**/*.wav"))
        wav_files.extend(directory.glob("**/*.WAV"))
        mp3_files.extend(directory.glob("**/*.mp3"))
        mp3_files.extend(directory.glob("**/*.MP3"))
    else:
        wav_files.extend(directory.glob("*.wav"))
        wav_files.extend(directory.glob("*.WAV"))
        mp3_files.extend(directory.glob("*.mp3"))
        mp3_files.extend(directory.glob("*.MP3"))

    all_files = list(wav_files) + list(mp3_files)
    return sorted(all_files)


def process_directory(directory, output_suffix="_trimmed", overwrite=False, 
                     recursive=False, threshold_db=-60, frame_length=2048, hop_length=512):
    """
    Process all .wav files in a directory to trim silence from the start.
    
    Args:
        directory (str): Directory containing .wav files
        output_suffix (str): Suffix for output files
        overwrite (bool): Whether to overwrite original files
        recursive (bool): Whether to process subdirectories
        threshold_db (float): Silence threshold in dB
        frame_length (int): Frame length for analysis
        hop_length (int): Hop length for analysis
    """
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return
    
    # Find all .wav files
    wav_files = find_wav_files(directory, recursive)
    
    if not wav_files:
        print(f"No .wav files found in '{directory}'")
        return
    
    print(f"Found {len(wav_files)} .wav files to process...")
    
    processed_count = 0
    error_count = 0
    total_trimmed_seconds = 0
    
    # Process each file
    for wav_file in tqdm(wav_files, desc="Processing files"):
        try:
            # Trim silence
            trimmed_audio, sr, trim_start_samples = trim_silence_from_start(
                wav_file, threshold_db, frame_length, hop_length
            )
            
            if trimmed_audio is None:
                error_count += 1
                continue
            
            # Calculate trimmed duration
            trimmed_seconds = trim_start_samples / sr if sr > 0 else 0
            total_trimmed_seconds += trimmed_seconds
            
            # Determine output path
            if overwrite:
                output_path = wav_file
            else:
                # Create output filename with suffix
                file_path = Path(wav_file)
                output_path = file_path.parent / f"{file_path.stem}{output_suffix}{file_path.suffix}"
            
            # Save the trimmed audio
            sf.write(output_path, trimmed_audio, sr)
            
            if trim_start_samples > 0:
                print(f"✓ {wav_file.name}: Trimmed {trimmed_seconds:.3f}s from start, added 1.0s silence")
            else:
                print(f"✓ {wav_file.name}: No silence detected at start, added 1.0s silence")
            
            processed_count += 1
            
        except Exception as e:
            print(f"✗ Error processing {wav_file}: {str(e)}")
            error_count += 1
    
    # Summary
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    print(f"Total files found: {len(wav_files)}")
    print(f"Successfully processed: {processed_count}")
    print(f"Errors: {error_count}")
    print(f"Total silence trimmed: {total_trimmed_seconds:.3f} seconds")
    print(f"Average silence per file: {total_trimmed_seconds/max(processed_count, 1):.3f} seconds")


def main():
    parser = argparse.ArgumentParser(
        description="Trim silence from the start of all .wav files in a directory",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--directory",
        help="Path to directory containing .wav files",
        default="audio_folder"
    )
    
    parser.add_argument(
        "--output-suffix",
        default="_trimmed",
        help="Suffix to add to output files (default: '_trimmed')"
    )
    
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite original files instead of creating new ones"
    )
    
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process subdirectories recursively"
    )
    
    parser.add_argument(
        "--threshold",
        type=float,
        default=-20,
        help="Silence threshold in dB (default: -60)"
    )
    
    parser.add_argument(
        "--frame-length",
        type=int,
        default=2048,
        help="Frame length for silence detection (default: 2048)"
    )
    
    parser.add_argument(
        "--hop-length",
        type=int,
        default=512,
        help="Hop length for silence detection (default: 512)"
    )
    
    args = parser.parse_args()
    
    # Process the directory
    process_directory(
        directory=args.directory,
        output_suffix=args.output_suffix,
        overwrite=args.overwrite,
        recursive=args.recursive,
        threshold_db=args.threshold,
        frame_length=args.frame_length,
        hop_length=args.hop_length
    )


if __name__ == "__main__":
    main() 