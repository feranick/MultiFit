###=============================================================
### plotrmap.R - 20151002a
### Nicola Ferralis <feranick@hotmail.com>
### The entire code is covered by GNU Public License (GPL) v.3
###=============================================================

library(Hmisc);library(akima); library(fields);library(plotrix);
library(spatstat);

inputFile = "Draken_7_map3_bs_denoised_wG_map.csv"

maxZ = 1.5;

step = 60;
dimPlot=7;

rootName=gsub(".csv","",inputFile)
outFile<-paste(rootName,"-plots.pdf",sep="")

# Read X, Y data in matrix
t = read.csv(inputFile, header = FALSE, skip = 1)


# Transform into vectors
x=as.vector(t[,1])
y=as.vector(t[,2])
z=as.vector(t[,3])

# Plot as matrix
int_z = interp(x,y,d5g, xo=seq(min(x), max(x), length = length(unique(x))), yo=seq(min(y), max(y), length = length(unique(y))), duplicate="mean")

pdf(file=outFile, width=dimPlot, height=dimPlot, onefile=T)

image.plot(int_z, legend.args=list( text="",cex=1.0, side=3, line=1), zlim=c(min(d5g),max(z)), main=paste(inputFile,"\nAverage = ", format(round(mean(t[,3]),3),nsmall=3), "\u00b1", format(round(sd(t[,3]),3),nsmall=3)), xlab="um", ylab="um", asp = 1)

#Plot as image:

z_im = as.im(int_z)

plot(z_im, zlim=c(0,max(z)), xlab="um",ylab="um",xlim=c(min(x),max(x)),ylim=c(min(y),max(y)))
plot(z_im)

plot(blur(z_im, 0.2, bleed=FALSE))

dev.off()
