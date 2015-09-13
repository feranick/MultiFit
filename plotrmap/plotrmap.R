###=============================================================
### plotrmap.R - 20150913a
### Nicola Ferralis <feranick@hotmail.com>
### The entire code is covered by GNU Public License (GPL) v.3
###=============================================================

library(Hmisc);library(akima); library(fields);library(plotrix);
library(spatstat);

inputFile = "Dracken-7-tracky_map1_bs_map_iGmore600.csv"

# HC calibration
a = 0.8692;
b = -0.0545;
maxD5G = 1.5;
maxHC = 1.2;

step = 60;
dimPlot=7;
rootName=gsub(".csv","",inputFile)
outFile<-paste(rootName,"-plots.pdf",sep="")

# Read X, Y data in matrix
t = read.csv(inputFile, header = FALSE, skip = 1)


# Transform into vectors
x=as.vector(t[,1])
y=as.vector(t[,2])
d5g=as.vector(t[,3])
hc=as.vector(t[,3]*a + b)

# Plot as matrix
int_d5g = interp(x,y,d5g, duplicate="mean")
int_hc = interp(x,y,hc,xo=seq(min(x),max(x),length = step), yo=seq(min(y),max(y),length = step), duplicate="mean")

pdf(file=outFile, width=dimPlot, height=dimPlot, onefile=T)

image.plot(int_d5g, legend.args=list( text="D5/G",cex=1.0, side=3, line=1), zlim=c(min(d5g),maxD5G), main=paste(inputFile,"\nAverage D5/G = ", format(round(mean(t[,3]),3),nsmall=3), "\u00b1", format(round(sd(t[,3]),3),nsmall=3)), xlab="um", ylab="um")

image.plot(int_hc, legend.args=list( text="H:C",cex=1.0, side=3, line=1), zlim=c(min(hc),maxHC), main=paste(inputFile,"\nAverage H:C = ", format(round(mean(t[,3]*a + b),3),nsmall=3), "\u00b1", format(round(sd(t[,3]*a + b),3),nsmall=3)), xlab="um", ylab="um")

#Plot as image:

z_d5g = as.im(int_d5g)
z_hc = as.im(interp(x,y,hc, duplicate="mean"))

plot(z_d5g, zlim=c(0,maxD5G))
plot(z_d5g)
plot(z_hc, zlim=c(0,maxHC))
plot(z_hc)
plot(blur(z_hc, 0.2, bleed=FALSE))

dev.off()