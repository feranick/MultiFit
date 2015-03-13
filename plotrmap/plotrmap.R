###=============================================================
### plotrmap.R
### Nicola Ferralis <feranick@hotmail.com>
### The entire code is covered by GNU Public License (GPL) v.3
###=============================================================

library(Hmisc);library(akima); library(fields);library(plotrix)

inputFile="test_map_map.csv"

dimPlot=7;
rootName=gsub(".csv","",inputFile)
outFile<-paste(rootName,"-plots.pdf",sep="")

# Read X, Y data in matrix
t = read.csv(inputFile, header = FALSE, skip = 1)


# Transform into vectors
x=as.vector(t[,1])
y=as.vector(t[,2])
z=as.vector(t[,3])

pdf(file=outFile, width=dimPlot, height=dimPlot, onefile=T)

image.plot(interp(x,y,z), main=inputFile, xlab="um", ylab="um")

image.plot(interp(x,y,z), legend.args=list( text="D5/G",cex=1.0, side=3, line=1), zlim=c(min(z),max(z)), main=inputFile, xlab="um", ylab="um")

dev.off()