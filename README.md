# VNS-OCR

VNS-OCR is a desktop application developed using the Python tkinter library, which utilizes the VisualNovelSubs (VNS) module to extract text from a video gameplay of a visual novel using Optical Character Recognition (OCR). This application simplifies the process of subtitle generation from visual novel videos.

**Prerequisites:** Prior to using this program, you need to have Tesseract installed in the default path.

**Link to Tesseract Installer for Windows:** [Tesseract Installer](https://github.com/UB-Mannheim/tesseract/wiki)

## Usage Instructions

The VNS-OCR application is used as follows:

1. **Select video**: Choose an mp4 format video containing the visual novel you want to process.

2. **Generate samples**: Enter the number of sample frames you wish to extract from the selected video.

3. **Draw region**: Define the region within the video where the OCR will be performed. Input the parameters [X, Y, Width, Height] to generate a rectangle that visually represents the region in the sample frames.

4. **Start-End**: Determines the start frame and the end frame on which OCR will be performed. 1000000000 indicates that it will be performed until the end, whatever it is. The start frame is inclusive and the end frame is exclusive.

5. **Frame skip**: Enter a number that determines how often the OCR will be performed on frames. A lower value increases accuracy but also extends processing time. It's recommended to keep the default value of 10 for 30 fps or 20 for 60 fps.

6. **Add to queue**: An item is added to the OCR queue with the specified characteristics.

7. **Queue**: Displays the OCR queue, you can right click on an item to remove it from the queue. When you click OK the OCR process will start, this may take several minutes. The generated "*.ocrdata" file cannot be used directly as subtitles, it must be used in [VNS Editor](https://github.com/nidoverso/vns-editor). Warning, if two identical items are added to the queue the OCR will be performed twice and will overwrite the same file, it is recommended not to generate duplicates.

8. **Show Frame**: Displays a specific frame of the selected video, if it does not exist previously in the generated sample frames it is added to them.

## License

VNS-OCR is distributed under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html). This ensures that the source code is available, and you can modify it to suit your needs, provided you comply with the terms of the license.