#!/bin/sh
OUTPUT_WIDTH=600
find -iname "cover.jpg" -o -iname "cover.gif" -o -iname "cover.png" | while read file
#for file in `find -iname "cover.jpg" -o -iname "cover.gif" -o -iname "cover.png"`
do
    #do convert "$file" -thumbnail 130x130 "${file%/*}"/cover.bmp
    INPUT_PATH=$file
    OUTPUT_PATH="${file%/*}"/cover-foo.jpg
    #OUTPUT_PATH=${file%.jpg}_foo.jpg
    #OUTPUT_PATH=${file}_foo.jpg
    echo $INPUT_PATH
    if [ -f $OUTPUT_PATH ]; then
        echo "  Skipping."
    fi
    if [ ! -f $OUTPUT_PATH ]; then
        echo "  Making thumbnail..."
        mogrify -write $OUTPUT_PATH -filter Triangle -define filter:support=2 -thumbnail $OUTPUT_WIDTH -unsharp 0.25x0.08+8.3+0.045 -dither None -posterize 136 -quality 82 -define jpeg:fancy-upsampling=off -define png:compression-filter=5 -define png:compression-level=9 -define png:compression-strategy=1 -define png:exclude-chunk=all -interlace none -colorspace sRGB $INPUT_PATH
    fi
done

#mogrify -write foo.jpg -filter Triangle -define filter:support=2 -thumbnail 600 -unsharp 0.25x0.08+8.3+0.045 -dither None -posterize 136 -quality 82 -define jpeg:fancy-upsampling=off -define png:compression-filter=5 -define png:compression-level=9 -define png:compression-strategy=1 -define png:exclude-chunk=all -interlace none -colorspace sRGB cover.jpg
