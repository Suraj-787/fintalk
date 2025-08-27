"""
Audio processing utilities for FinTalk application.
Handles audio conversion, processing, and manipulation without ffmpeg dependency.
"""

import numpy as np
import io
import wave
import os
import streamlit as st
import base64
from typing import Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional dependencies
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    logger.warning("soundfile not available - limited audio format support")

try:
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy not available - limited audio processing capabilities")


def convert_webm_to_wav(audio_bytes: bytes) -> Optional[bytes]:
    """
    Convert audio bytes to WAV format without using ffmpeg.
    
    Args:
        audio_bytes (bytes): Raw audio data
        
    Returns:
        Optional[bytes]: WAV format audio data or None if conversion fails
    """
    if not audio_bytes or len(audio_bytes) == 0:
        st.error("No audio data received")
        return None
    
    logger.info(f"Received audio data of length: {len(audio_bytes)}")
    
    # Validate minimum audio data size
    if len(audio_bytes) < 100:
        st.error(f"Audio data too small to be valid: {len(audio_bytes)} bytes")
        return None
    
    temp_file = "temp_audio_input"
    wav_data = None
    
    try:
        # Save temporary audio file
        with open(temp_file, "wb") as f:
            f.write(audio_bytes)
        
        # Try multiple conversion methods
        wav_data = _try_soundfile_conversion(temp_file)
        
        if not wav_data:
            wav_data = _check_existing_wav_format(audio_bytes)
        
        if not wav_data:
            wav_data = _create_basic_wav_fallback(audio_bytes)
        
        if wav_data and len(wav_data) > 0:
            logger.info(f"Successfully converted audio, output size: {len(wav_data)} bytes")
            return wav_data
        else:
            st.error("Could not convert audio. Try using a different recording method.")
            st.info("💡 Alternative: Try uploading a WAV or MP3 file instead")
            return None
            
    except Exception as e:
        st.error(f"Error converting audio: {e}")
        logger.error(f"Exception in convert_webm_to_wav: {e}")
        return None
    finally:
        _cleanup_temp_file(temp_file)


def _try_soundfile_conversion(temp_file: str) -> Optional[bytes]:
    """Try converting audio using soundfile library."""
    if not SOUNDFILE_AVAILABLE:
        return None
        
    try:
        logger.info("Attempting conversion with soundfile...")
        data, samplerate = sf.read(temp_file)
        
        wav_io = io.BytesIO()
        sf.write(wav_io, data, samplerate, format='WAV')
        wav_data = wav_io.getvalue()
        
        logger.info(f"Soundfile conversion successful, size: {len(wav_data)} bytes")
        return wav_data
        
    except Exception as e:
        logger.warning(f"Soundfile conversion failed: {e}")
        return None


def _check_existing_wav_format(audio_bytes: bytes) -> Optional[bytes]:
    """Check if audio is already in WAV format."""
    try:
        if audio_bytes[:4] == b'RIFF' and audio_bytes[8:12] == b'WAVE':
            logger.info("Input is already in WAV format")
            return audio_bytes
    except Exception as e:
        logger.warning(f"WAV format check failed: {e}")
    return None


def _create_basic_wav_fallback(audio_data: bytes) -> Optional[bytes]:
    """Create a basic WAV file from raw audio data as fallback."""
    if len(audio_data) <= 1000:  # Too small to be valid audio
        return None
        
    try:
        logger.info("Attempting basic WAV conversion...")
        return create_basic_wav(audio_data)
    except Exception as e:
        logger.warning(f"Basic WAV conversion failed: {e}")
        return None


def _cleanup_temp_file(temp_file: str) -> None:
    """Clean up temporary files."""
    try:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    except Exception as e:
        logger.warning(f"Failed to clean up temp file {temp_file}: {e}")


def create_basic_wav(audio_data: bytes) -> Optional[bytes]:
    """
    Create a basic WAV file from raw audio data.
    This is a fallback method for when other conversions fail.
    
    Args:
        audio_data (bytes): Raw audio data
        
    Returns:
        Optional[bytes]: WAV format audio or None if creation fails
    """
    try:
        # Standard audio parameters
        sample_rate = 44100
        num_channels = 1
        bits_per_sample = 16
        data_length = len(audio_data)
        
        # Create WAV header
        wav_header = bytearray()
        wav_header.extend(b'RIFF')  # Chunk ID
        wav_header.extend((36 + data_length).to_bytes(4, 'little'))  # Chunk size
        wav_header.extend(b'WAVE')  # Format
        wav_header.extend(b'fmt ')  # Subchunk1 ID
        wav_header.extend((16).to_bytes(4, 'little'))  # Subchunk1 size
        wav_header.extend((1).to_bytes(2, 'little'))  # Audio format (PCM)
        wav_header.extend(num_channels.to_bytes(2, 'little'))  # Num channels
        wav_header.extend(sample_rate.to_bytes(4, 'little'))  # Sample rate
        wav_header.extend((sample_rate * num_channels * bits_per_sample // 8).to_bytes(4, 'little'))  # Byte rate
        wav_header.extend((num_channels * bits_per_sample // 8).to_bytes(2, 'little'))  # Block align
        wav_header.extend(bits_per_sample.to_bytes(2, 'little'))  # Bits per sample
        wav_header.extend(b'data')  # Subchunk2 ID
        wav_header.extend(data_length.to_bytes(4, 'little'))  # Subchunk2 size
        
        # Combine header and data
        wav_file = bytes(wav_header) + audio_data
        return wav_file
        
    except Exception as e:
        logger.error(f"Failed to create basic WAV: {e}")
        return None


def detect_silence(audio_bytes: bytes, threshold: float = 0.1) -> bool:
    """
    Detect if audio is mostly silence.
    
    Args:
        audio_bytes (bytes): Audio data to analyze
        threshold (float): Silence threshold (default: 0.1)
        
    Returns:
        bool: True if audio is mostly silent, False otherwise
    """
    try:
        if SOUNDFILE_AVAILABLE:
            return _detect_silence_with_soundfile(audio_bytes, threshold)
        else:
            return _detect_silence_fallback(audio_bytes, threshold)
            
    except Exception as e:
        logger.error(f"Error processing audio for silence detection: {e}")
        st.error(f"Error processing audio: {e}")
        return False


def _detect_silence_with_soundfile(audio_bytes: bytes, threshold: float) -> bool:
    """Detect silence using soundfile library."""
    temp_file = "temp_silence_check"
    try:
        with open(temp_file, "wb") as f:
            f.write(audio_bytes)
        
        data, sample_rate = sf.read(temp_file)
        rms = np.sqrt(np.mean(data**2))
        return rms < threshold
        
    finally:
        _cleanup_temp_file(temp_file)


def _detect_silence_fallback(audio_bytes: bytes, threshold: float) -> bool:
    """Fallback silence detection method."""
    if len(audio_bytes) < 1000:
        return True
    
    # Convert bytes to numpy array (assuming 16-bit audio)
    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
    if len(audio_array) == 0:
        return True
    
    # Normalize and calculate RMS
    normalized = audio_array.astype(np.float32) / 32768.0
    rms = np.sqrt(np.mean(normalized**2))
    return rms < threshold


def split_audio(input_file: str, chunk_length: int = 30) -> List[str]:
    """
    Split audio file into smaller chunks.
    
    Args:
        input_file (str): Path to input audio file
        chunk_length (int): Length of each chunk in seconds (default: 30)
        
    Returns:
        List[str]: List of chunk filenames created
    """
    chunks = []
    
    try:
        with wave.open(input_file, 'rb') as audio:
            frame_rate = audio.getframerate()
            num_frames = audio.getnframes()
            total_duration = num_frames / frame_rate
            
            start_time = 0
            index = 1
            
            while start_time < total_duration:
                end_time = min(start_time + chunk_length, total_duration)
                chunk_filename = _create_audio_chunk(
                    audio, start_time, end_time, frame_rate, index
                )
                
                if chunk_filename:
                    chunks.append(chunk_filename)
                
                start_time += chunk_length
                index += 1
                
    except Exception as e:
        logger.error(f"Error splitting audio: {e}")
        st.error(f"Error splitting audio: {e}")
        
    return chunks


def _create_audio_chunk(audio: wave.Wave_read, start_time: float, 
                       end_time: float, frame_rate: int, index: int) -> Optional[str]:
    """Create individual audio chunk."""
    try:
        start_frame = int(start_time * frame_rate)
        end_frame = int(end_time * frame_rate)
        
        audio.setpos(start_frame)
        frames = audio.readframes(end_frame - start_frame)
        
        chunk_filename = f"chunk_{index}.wav"
        
        with wave.open(chunk_filename, 'wb') as chunk_file:
            chunk_file.setnchannels(audio.getnchannels())
            chunk_file.setsampwidth(audio.getsampwidth())
            chunk_file.setframerate(frame_rate)
            chunk_file.writeframes(frames)
            
        return chunk_filename
        
    except Exception as e:
        logger.error(f"Error creating chunk {index}: {e}")
        return None


def merge_audio(audio_files: List[str], output_filename: str = "final_output.wav") -> None:
    """
    Merge multiple audio files into one.
    
    Args:
        audio_files (List[str]): List of audio file paths to merge
        output_filename (str): Output filename (default: "final_output.wav")
    """
    if not audio_files:
        logger.warning("No valid audio files to merge.")
        return
    
    try:
        if SOUNDFILE_AVAILABLE:
            _merge_with_soundfile(audio_files, output_filename)
        else:
            _merge_with_wave(audio_files, output_filename)
            
        logger.info(f"Final audio saved as {output_filename}")
        
        # Clean up individual files
        for file_path in audio_files:
            _cleanup_temp_file(file_path)
            
    except Exception as e:
        logger.error(f"Error in merge_audio: {e}")


def _merge_with_soundfile(audio_files: List[str], output_filename: str) -> None:
    """Merge audio files using soundfile library."""
    all_audio_data = []
    sample_rate = None
    
    for file_path in audio_files:
        if os.path.exists(file_path):
            data, sr = sf.read(file_path)
            if sample_rate is None:
                sample_rate = sr
            elif sr != sample_rate:
                logger.warning(f"Sample rate mismatch in {file_path}")
            all_audio_data.append(data)
    
    if all_audio_data and sample_rate:
        merged_audio = np.concatenate(all_audio_data)
        sf.write(output_filename, merged_audio, sample_rate)


def _merge_with_wave(audio_files: List[str], output_filename: str) -> None:
    """Merge audio files using wave module (WAV only)."""
    with wave.open(output_filename, 'wb') as output_audio:
        # Configure output file based on first input file
        with wave.open(audio_files[0], 'rb') as first_file:
            output_audio.setnchannels(first_file.getnchannels())
            output_audio.setsampwidth(first_file.getsampwidth())
            output_audio.setframerate(first_file.getframerate())
        
        # Merge all files
        for file_path in audio_files:
            if os.path.exists(file_path):
                with wave.open(file_path, 'rb') as audio_chunk:
                    output_audio.writeframes(
                        audio_chunk.readframes(audio_chunk.getnframes())
                    )


def process_long_audio(input_file: str) -> str:
    """
    Process long audio files by splitting them into chunks.
    
    Args:
        input_file (str): Path to input audio file
        
    Returns:
        str: Complete transcript from all chunks
    """
    try:
        from .api_utils import audio_to_text
        
        if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
            st.error("Audio file not found or empty")
            return ""
        
        # Try processing the whole file first
        chunks = split_audio(input_file)
        if not chunks:
            logger.info("Splitting failed, processing whole file...")
            transcript = audio_to_text(input_file)
            return transcript.strip() if transcript else ""
        
        # Process chunks
        final_transcript = ""
        for chunk in chunks:
            logger.info(f"Processing {chunk}...")
            transcript = audio_to_text(chunk)
            if transcript:
                final_transcript += transcript + " "
            _cleanup_temp_file(chunk)
        
        return final_transcript.strip()
        
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        st.error(f"Error processing audio: {e}")
        return ""
