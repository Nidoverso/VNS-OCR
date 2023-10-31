# VNS-OCR

VNS-OCR is a desktop application developed using the Python tkinter library, which utilizes the VisualNovelSubs (VNS) module to extract text from a video gameplay of a visual novel using Optical Character Recognition (OCR). This application simplifies the process of subtitle generation from visual novel videos.

## Usage Instructions

The VNS-OCR application is used as follows:

1. **Select video**: Choose an mp4 format video containing the visual novel you want to process.

2. **Generate samples**: Enter the number of sample frames you wish to extract from the selected video.

3. **Draw region**: Define the region within the video where the OCR will be performed. Input the parameters [X, Y, Width, Height] to generate a rectangle that visually represents the region in the sample frames.

4. **Frame skip**: Enter a number that determines how often the OCR will be performed on frames. A lower value increases accuracy but also extends processing time. It's recommended to keep the default value of 10.

5. **OCR Video**: Start the OCR process on the selected video using the specified region and "frame skip" value. The application also offers the option to simplify subtitles. This option removes whitespace, repetitions, and uncommon characters.

6. **Export to SRT**: Export the OCR results in SRT format. Please note that the direct output may be inaccurate, so it's recommended to review it with the [VNS Editor](https://github.com/nidoverso/vns-editor) application to improve subtitle accuracy.

## License

VNS-OCR is distributed under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html). This ensures that the source code is available, and you can modify it to suit your needs, provided you comply with the terms of the license.