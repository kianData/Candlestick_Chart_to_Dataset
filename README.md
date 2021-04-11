# Candlestick_Chart_to_Dataset
This python code converts stockmarket candlestick charts into dataset.
The original image needs to be in .bmp or .png. Jpg images will not give reliable results.
The candlestick wicks must not be wider than 'one' pixel. Otherwise 'img_data()' function needs to be changed properly (lines 83 and 91).
There needs to be at least one white pixel (with the backgroun color) between each two adjacent candles.
The grid line colors are defined in 'grid_lines()' function. For images comming from brockers other than IG, change them properly.
The candle colors are set in 'img_data()' function. For images comming from brockers other than IG, change them properly.
If the original image meet these criteria, the conversion deviation will not be greater than 0.02%.
