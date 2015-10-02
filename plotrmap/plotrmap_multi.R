###=============================================================
### plotrmap_multi.R - 20151002a
### Nicola Ferralis <feranick@hotmail.com>
### The entire code is covered by GNU Public License (GPL) v.3
###=============================================================

library(Hmisc);library(akima); library(fields);library(plotrix);
library(spatstat);

step = 60;
dimPlot=7;


##########################################
# Get list of Files
##########################################

listOfFiles <- list.files(pattern= "_map.csv")
inputFile<-as.matrix(listOfFiles)

for (i in 1:nrow(inputFile)){
	rootName=gsub("_map.csv","",inputFile)
	outFile<-paste(rootName,"-plots.pdf",sep="")
	}


for(p in 1:nrow(inputFile)){
	# Read X, Y data in matrix
	t = read.csv(inputFile[p], header = FALSE, skip = 1)


	# Transform into vectors
	x=as.vector(t[,1])
	y=as.vector(t[,2])
	z=as.vector(t[,3])

	# Plot as matrix
	int_z = interp(x,y,z, xo=seq(min(x), max(x), length = length(unique(x))), yo=seq(min(y), max(y), 	length = length(unique(y))), duplicate="mean")

	pdf(file=outFile[p], width=dimPlot, height=dimPlot, onefile=T)

	image.plot(int_z, legend.args=list( text="z",cex=1.0, side=3, line=1), zlim=c(min(z),max(z)), main=paste(inputFile[p],"\nAverage = ", format(round(mean(t[,3]),3),nsmall=3), "\u00b1", format(round(sd(t[,3]),3),nsmall=3)), xlab="um", ylab="um", asp = 1)

	#Plot as image:

	z_im = as.im(int_z)

	plot(z_im, zlim=c(0,max(z)), xlab="um",ylab="um",xlim=c(min(x),max(x)),ylim=c(min(y),max(y)))
	plot(z_im)
	plot(blur(z_im, 0.2, bleed=FALSE))

	dev.off()
}