#!/bin/bash

out='/home/axel/Dropbox/Dokumente/studium/WeWi/5Loch/python/data/barbs/'

#convert -density 300 ${out}0.png[25x25+603+386] -colorspace RGB -fuzz 20% -transparent white ${out}0.bak

for file in $(ls $out*.png)
	 do
	 convert $file[110x115+546+363] -colorspace RGB -fuzz 20% -transparent white ${file%.*}.png
done
#convert -density 300 ${out}0.png[25x25+603+386] -fuzz 100% -transparent white ${out}0.png
#mv ${out}0.bak ${out}0.png
#rm -r ${out}*.png
