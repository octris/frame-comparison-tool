# Frame Comparison Tool

An open-source desktop application for comparing videos frame by frame.

This tool helps users analyze and compare the frame quality of multiple versions of the same video by randomly selecting
frames at similar positions across different sources.

## Features

- Compare multiple video sources
- Customize frame sampling:
    - Adjust the number of frames to sample
    - Set a specific seed value for reproducible random sampling
    - Filter frames by type (B-type, I-type, P-type)
- Frame manipulation:
    - Adjust frame positions
    - Offset all frames for a specific source
    - Save all frames
- Display options:
    - Choose between cropped or scaled image display
    - Navigate frames and video sources with keyboard shortcuts

### Keyboard Shortcuts

- **Left/Right Arrows**: Navigate between frames
- **Up/Down Arrows**: Switch between video sources
- **Plus/Minus**: Offset current frame
- **Ctrl + Plus/Minus**: Offset all frames for the current source
- **Ctrl + S**: Save frames

## Installation

### Option 1: Using pre-compiled releases

1. Go to the GitHub repository
2. Navigate to the "Actions" tab and select the "build" workflow
3. Choose the latest successful run from the main branch
4. Download the artifact for your operating system and installed Python version
5. Extract the downloaded archive
6. Run the executable file:
    - Windows: ```frame-comparison-tool.exe```
    - Linux/macOS: ```frame-comparison-tool```

### Option 2: Building from source

This project uses Poetry for dependency management. To get started:

1. Make sure you have Python 3.10 or newer installed
2. Install Poetry (if you haven't already)
3. Clone the repository:

```bash 
git clone https://github.com/octris/frame-comparison-tool.git
cd frame-comparison-tool
```

4. Install dependencies:

```bash
poetry install
```

5. Start the application:

```bash
# Basic usage
python -m frame_comparison_tool 

# For a full list of command-line options
python -m frame_comparison_tool --help
```

### Dependencies

- Python >= 3.10
- OpenCV (contrib) 4.10.0
- PySide6 6.7.3
- Pillow 11.0.0
- Additional utilities: aenum, loguru

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.