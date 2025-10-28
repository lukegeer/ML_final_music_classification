import os
import subprocess

# Define the parent directory containing GTZANSeparated folders
parent_directory = "GTZANSeparated"

# Subfolders corresponding to components
components = ["drums", "other", "vocals"]

# Duration of each segment in seconds
segment_duration = 3.0

# Total number of segments per 30-second track
segments_per_track = 10
'''
# Step 1: Stretch all 15-second files to 30 seconds
for component in components:
    component_path = os.path.join(parent_directory, component)
    if os.path.exists(component_path):  # Ensure the folder exists
        for file_name in sorted(os.listdir(component_path)):  # Process all files
            if file_name.endswith(".mp3"):  # Ensure it's an audio file
                input_file = os.path.join(component_path, file_name)

                # Get the duration of the file using FFprobe
                result = subprocess.run(
                    [
                        "ffprobe", "-i", input_file,
                        "-show_entries", "format=duration",
                        "-v", "quiet", "-of", "csv=p=0"
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                duration = float(result.stdout.strip())  # Duration in seconds

                # If the file is 15 seconds, stretch it to 30 seconds
                if duration < 30:
                    stretched_file = input_file.replace(".mp3", "_stretched.mp3")
                    command = [
                        "ffmpeg", "-i", input_file, "-filter:a",
                        "atempo=0.5",  # Half the speed (stretch to 30 seconds)
                        stretched_file
                    ]
                    subprocess.run(command, check=True)
                    os.rename(stretched_file, input_file)  # Replace the original file with stretched file

# Step 1.5: Trim all files to exactly 29.7 seconds
for component in components:
    component_path = os.path.join(parent_directory, component)
    if os.path.exists(component_path):  # Ensure the folder exists
        for file_name in sorted(os.listdir(component_path)):  # Process all files
            if file_name.endswith(".mp3"):  # Ensure it's an audio file
                input_file = os.path.join(component_path, file_name)
                trimmed_file = input_file.replace(".mp3", "_trimmed.mp3")

                # FFmpeg command to trim the file to 29.7 seconds
                command = [
                    "ffmpeg", "-i", input_file,
                    "-to", "29.7",  # Trim up to 29.7 seconds
                    "-c", "copy",  # Avoid re-encoding
                    trimmed_file
                ]
                subprocess.run(command, check=True)
                os.rename(trimmed_file, input_file)  # Replace the original file with trimmed file
'''
# Step 2: Split all files into exactly 10 segments with proper genre-based numbering
for component in components:
    component_path = os.path.join(parent_directory, component)

    # Create a separate folder for split segments (e.g., "bass_segments")
    split_output_path = os.path.join(parent_directory, f"{component}_segments")
    os.makedirs(split_output_path, exist_ok=True)

    if os.path.exists(component_path):  # Ensure the folder exists
        # Group files by genre
        genres = {}
        for file_name in sorted(os.listdir(component_path)):  # Group files by genre
            if file_name.endswith(".mp3"):
                genre, rest = file_name.rpartition(".")[0].split(".", 1)  # Split only on the first dot
                genres.setdefault(genre, []).append(file_name)

        # Process files grouped by genre
        for genre, files in genres.items():
            for file_name in files:
                input_file = os.path.join(component_path, file_name)

                # Extract track number from the file name
                base_name = os.path.splitext(file_name)[0]
                _, rest = base_name.rsplit(".", 1)  # Safely split on the last dot
                track_number, _ = rest.split("_")
                track_number = int(track_number)  # Convert track number to integer

                # Temporary output pattern for FFmpeg to create segments
                temp_output_pattern = os.path.join(split_output_path, f"temp_%03d.mp3")

                # FFmpeg command to split into 3-second segments, ensuring exactly 10
                command = [
                    "ffmpeg", "-i", input_file,
                    "-f", "segment",
                    "-segment_time", str(segment_duration),
                    "-t", "29.99",  # Process only the first 29.99 seconds
                    "-c", "copy",
                    temp_output_pattern
                ]

                # Execute FFmpeg
                subprocess.run(command, check=True)

                # Rename split files with proper global numbering
                segment_files = sorted([f for f in os.listdir(split_output_path) if f.startswith("temp_")])
                for i, segment_file in enumerate(segment_files[:segments_per_track]):  # Limit to 10 segments
                    old_path = os.path.join(split_output_path, segment_file)
                    global_number = 10 * track_number + i  # Proper genre-based numbering
                    new_name = f"{genre}.{global_number:03d}_{component}.mp3"
                    new_path = os.path.join(split_output_path, new_name)
                    os.rename(old_path, new_path)

                # Safely remove leftover temporary files for the current track
                for temp_file in segment_files:
                    temp_path = os.path.join(split_output_path, temp_file)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

        print(f"Finished processing files for {component}, segments stored in {split_output_path}")

print("All files processed successfully!")