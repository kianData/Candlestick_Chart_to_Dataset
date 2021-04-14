# Candlestick_Chart_to_Dataset

This python code converts stockmarket candlestick charts into dataset.

The original image needs to be in .bmp or .png. Jpg images will not give reliable results.

The code reads the vertical axes values from the image and asks you to confirm it. You need to install Tesseract-OCR on your machine.

There need to be at least one white pixel (with the backgroun color) between each two adjacent candles.

The grid line colors are defined in 'grid()' function. For images comming from brockers other than IG, change them properly.

The candle colors are set in 'digitImg()' function. For images comming from brockers other than IG, change them properly.

If the original image meet these criteria, the conversion deviation will not be greater than 0.02%.
