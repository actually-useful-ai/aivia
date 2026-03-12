#!/usr/bin/env python3
"""
Google Text-to-Speech CLI - A specialized command-line tool for generating
text-to-speech using Google's TTS service.

This script provides an interface to Google TTS with language selection,
speed control, and other options.
"""

import argparse
import os
import sys
import tempfile
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import textwrap

try:
    import gtts
    from gtts import gTTS
    from gtts.lang import tts_langs
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def success(text: str) -> str:
        """Format text as success message"""
        return f"{Colors.GREEN}✓ {text}{Colors.ENDC}"
    
    @staticmethod
    def info(text: str) -> str:
        """Format text as info message"""
        return f"{Colors.BLUE}{text}{Colors.ENDC}"
    
    @staticmethod
    def warning(text: str) -> str:
        """Format text as warning message"""
        return f"{Colors.YELLOW}! {text}{Colors.ENDC}"
    
    @staticmethod
    def error(text: str) -> str:
        """Format text as error message"""
        return f"{Colors.RED}✗ {text}{Colors.ENDC}"

def print_header():
    """Print a stylish header for the CLI"""
    header = """
╔═════════════════════════════════════════════╗
║        Google Text-to-Speech (gTTS) CLI      ║
║     Convert text to natural-sounding speech  ║
╚═════════════════════════════════════════════╝
"""
    print(header)

def check_gtts_availability():
    """Check if gTTS is available and can connect to Google's service"""
    if not GTTS_AVAILABLE:
        print(Colors.error("Google Text-to-Speech (gTTS) is not installed."))
        print(Colors.info("Install with: pip install gtts"))
        return False
    
    try:
        # Test internet connection by trying to get languages
        languages = tts_langs()
        return True
    except Exception as e:
        print(Colors.error(f"Failed to connect to Google TTS service: {str(e)}"))
        print(Colors.info("Make sure you have a working internet connection."))
        return False

def get_available_languages():
    """Get all available languages supported by Google TTS"""
    try:
        langs = tts_langs()
        return langs
    except Exception as e:
        print(Colors.error(f"Failed to retrieve languages: {str(e)}"))
        return {}

def play_audio(file_path: str) -> bool:
    """Play an audio file using system-specific commands
    
    Args:
        file_path: Path to the audio file to play
        
    Returns:
        bool: True if playback was successful, False otherwise
    """
    try:
        print(Colors.info("Playing generated audio..."))
        
        if sys.platform == "darwin":  # macOS
            subprocess.run(["afplay", file_path], check=True)
        elif sys.platform == "win32":  # Windows
            import winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
        else:  # Linux
            players = [
                ["paplay", file_path],  # PulseAudio
                ["aplay", "-q", file_path],  # ALSA
                ["play", "-q", file_path],  # SoX
                ["mplayer", "-really-quiet", file_path]  # MPlayer
            ]
            for player in players:
                try:
                    subprocess.run(player, check=True)
                    break
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
            else:
                raise RuntimeError("No suitable audio player found")
        
        print(Colors.success("Audio playback complete"))
        return True
    except Exception as e:
        print(Colors.warning(f"Could not play audio: {e}"))
        return False

def generate_tts(text, output_file, lang="en", slow=False, tld=None):
    """Generate Text-to-Speech using Google TTS
    
    Args:
        text: Text to convert to speech
        output_file: Path to save the output file
        lang: Language code to use
        slow: Whether to use slower speech rate
        tld: Top Level Domain for the Google TTS service
        
    Returns:
        bool: True if generation was successful, False otherwise
    """
    try:
        print(Colors.info(f"Generating speech using Google TTS..."))
        print(Colors.info(f"Language: {lang} | Slow mode: {'Yes' if slow else 'No'}"))
        
        # Create gTTS instance with the specified parameters
        tts_options = {
            "text": text,
            "lang": lang,
            "slow": slow
        }
        
        if tld:
            tts_options["tld"] = tld
            print(Colors.info(f"TLD: {tld}"))
        
        tts = gTTS(**tts_options)
        
        # Save to file
        tts.save(output_file)
        
        if not os.path.exists(output_file):
            raise FileNotFoundError("Output file was not created")
        
        file_size = os.path.getsize(output_file) / 1024  # KB
        print(Colors.success(f"Generated audio file ({file_size:.1f} KB)"))
        
        return True
    except Exception as e:
        print(Colors.error(f"Failed to generate TTS: {str(e)}"))
        return False

def interactive_mode():
    """Run the TTS tool in interactive mode"""
    print_header()
    
    # Check if gTTS is available
    if not check_gtts_availability():
        return
    
    # Get available languages
    languages = get_available_languages()
    
    # Step 1: Get text to convert
    print("\nEnter text to convert to speech:")
    print("1) Enter text directly")
    print("2) Read from a file")
    
    while True:
        try:
            text_choice = int(input("\nEnter your choice (1-2): "))
            if text_choice not in [1, 2]:
                print("Invalid choice. Please enter 1 or 2.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    text = ""
    if text_choice == 1:
        print("\nEnter or paste the text (press Enter twice to finish):")
        lines = []
        while True:
            line = input()
            if not line and lines and not lines[-1]:
                # Two consecutive empty lines means we're done
                break
            lines.append(line)
        text = "\n".join(lines[:-1])  # Remove the last empty line
    else:
        file_path = input("\nEnter the path to the text file: ")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"Successfully read {len(text)} characters from file.")
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return
    
    # Step 2: Select language
    print("\nSelect language:")
    
    # Sort languages by name for better display
    sorted_langs = sorted(languages.items(), key=lambda x: x[1])
    
    # Display languages in a formatted way (3 columns)
    col_width = 25
    for i in range(0, len(sorted_langs), 3):
        row = sorted_langs[i:i+3]
        print("".join(f"{code}: {name:{col_width}}" for code, name in row))
    
    while True:
        lang_code = input("\nEnter language code (default: en): ").strip().lower()
        if not lang_code:
            lang_code = "en"
            
        if lang_code in languages:
            print(f"Selected language: {languages[lang_code]} ({lang_code})")
            break
        else:
            print("Invalid language code. Please try again.")
    
    # Step 3: Set speech rate
    while True:
        slow_mode = input("\nUse slower speech rate? (y/n, default: n): ").strip().lower()
        if not slow_mode or slow_mode.startswith('n'):
            slow = False
            break
        elif slow_mode.startswith('y'):
            slow = True
            break
        else:
            print("Invalid input. Please enter y or n.")
    
    # Step 4: Select TLD (optional)
    tld_options = {
        "com": "United States (default)",
        "co.uk": "United Kingdom",
        "com.au": "Australia",
        "co.in": "India",
        "ca": "Canada",
        "co.za": "South Africa",
        "ie": "Ireland"
    }
    
    print("\nSelect Top-Level Domain (TLD) for Google TTS (optional):")
    for tld, desc in tld_options.items():
        print(f"- {tld}: {desc}")
    
    tld = input("\nEnter TLD (press Enter for default): ").strip().lower()
    if not tld:
        tld = None
    
    # Step 5: Set output file
    output_file = None
    output_choice = input("\nDo you want to specify an output file? (y/n): ").strip().lower()
    if output_choice.startswith('y'):
        output_file = input("Enter output file path (e.g., output.mp3): ")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"gtts_output_{lang_code}_{timestamp}.mp3"
        print(f"Using default output file: {output_file}")
    
    # Step 6: Generate TTS
    success = generate_tts(
        text=text,
        output_file=output_file,
        lang=lang_code,
        slow=slow,
        tld=tld
    )
    
    # Step 7: Play the audio (optional)
    if success:
        print(f"Output saved to: {os.path.abspath(output_file)}")
        play_choice = input("\nDo you want to play the audio now? (y/n): ").strip().lower()
        if play_choice.startswith('y'):
            play_audio(output_file)

def main():
    parser = argparse.ArgumentParser(
        description="Generate text-to-speech using Google's TTS service",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("--text", "-t", type=str, help="Text to convert to speech")
    parser.add_argument("--file", "-f", type=str, help="Text file to convert to speech")
    parser.add_argument("--output", "-o", type=str, help="Output MP3 file path (default: auto-generated)")
    parser.add_argument("--lang", "-l", type=str, default="en", 
                        help="Language code (default: en, use --list-langs to see available options)")
    parser.add_argument("--slow", "-s", action="store_true", help="Use slower speech rate")
    parser.add_argument("--tld", type=str, 
                        help=textwrap.dedent("""\
                        Top-level domain for Google TTS service. Options:
                          - com: United States (default)
                          - co.uk: United Kingdom
                          - com.au: Australia
                          - co.in: India
                          - ca: Canada
                          - co.za: South Africa
                          - ie: Ireland
                        """))
    parser.add_argument("--list-langs", action="store_true", help="List available language codes")
    parser.add_argument("--play", "-p", action="store_true", help="Play the audio after generating")
    parser.add_argument("--interactive", "-i", action="store_true", help="Use interactive mode")
    
    args = parser.parse_args()
    
    # Check if gTTS is available
    if not check_gtts_availability():
        sys.exit(1)
    
    # Check if we should run in interactive mode
    if args.interactive or len(sys.argv) == 1:  # Run interactive mode if no args or --interactive
        interactive_mode()
        return
    
    # List available languages if requested
    if args.list_langs:
        languages = get_available_languages()
        print("Available language codes for Google TTS:")
        # Sort languages by name for better display
        sorted_langs = sorted(languages.items(), key=lambda x: x[1])
        # Display languages in a formatted way (3 columns)
        col_width = 25
        for i in range(0, len(sorted_langs), 3):
            row = sorted_langs[i:i+3]
            print("".join(f"{code}: {name:{col_width}}" for code, name in row))
        return
    
    # Get the text to process
    text = ""
    if args.text:
        text = args.text
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return
    else:
        print("Error: Either --text or --file must be provided")
        parser.print_help()
        return
    
    # Generate output filename if not specified
    output_file = args.output
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"gtts_output_{args.lang}_{timestamp}.mp3"
    
    # Validate language
    languages = get_available_languages()
    if args.lang not in languages:
        print(f"Error: Unknown language code '{args.lang}'")
        print("Use --list-langs to see available language codes")
        return
    
    # Generate the TTS
    success = generate_tts(
        text=text,
        output_file=output_file,
        lang=args.lang,
        slow=args.slow,
        tld=args.tld
    )
    
    # Play the audio if requested and generation was successful
    if success:
        print(f"Output saved to: {os.path.abspath(output_file)}")
        if args.play:
            play_audio(output_file)

if __name__ == "__main__":
    main() 