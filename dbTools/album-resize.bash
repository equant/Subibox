#!/bin/sh
OUTPUT_WIDTH=600
find -iname "cover.jpg" -o -iname "cover.gif" -o -iname "cover.png" | while read file
#find -iname "cover.jpg" | while read file
    #do convert "$file" -thumbnail 130x130 "${file%/*}"/cover.bmp
    INPUT_PATH=$file
    OUTPUT_PATH="${file%/*}"/cover-foo.jpg
    #OUTPUT_PATH=${file%.jpg}_foo.jpg
    #OUTPUT_PATH=${file}_foo.jpg
    do mogrify -write $OUTPUT_PATH -filter Triangle -define filter:support=2 -thumbnail $OUTPUT_WIDTH -unsharp 0.25x0.08+8.3+0.045 -dither None -posterize 136 -quality 82 -define jpeg:fancy-upsampling=off -define png:compression-filter=5 -define png:compression-level=9 -define png:compression-strategy=1 -define png:exclude-chunk=all -interlace none -colorspace sRGB $INPUT_PATH
done

#mogrify -write foo.jpg -filter Triangle -define filter:support=2 -thumbnail 600 -unsharp 0.25x0.08+8.3+0.045 -dither None -posterize 136 -quality 82 -define jpeg:fancy-upsampling=off -define png:compression-filter=5 -define png:compression-level=9 -define png:compression-strategy=1 -define png:exclude-chunk=all -interlace none -colorspace sRGB cover.jpg
