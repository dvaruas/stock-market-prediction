getPlotTrade <- function()
{
	ourMethodData <- read.csv('../stock_quotes/ourMethodReturn.csv')
	baseData <- read.csv('../stock_quotes/baseReturn.csv')

	dateValues <- as.Date(ourMethodData$date, format = '%d-%m-%y')

	ourValues <- as.numeric(ourMethodData$returnValue)
	baseValues <- as.numeric(baseData$returnValue)

	print(paste('Our Method --> Return rate : ', mean(ourValues), sep = ''))
	print(paste('Base Method --> Return rate : ', mean(baseValues), sep = ''))

#	plot(dateValues, ourValues, type = 'o', col = 'red', main = 'Trade Value Comparison', xlab = 'Date', ylab = 'Return Value', pch = 2, ylim = c(-500, 2000))

#	par(new = TRUE)

#	plot(dateValues, baseValues, type = 'o', col = 'green', main = 'Trade Value Comparison', xlab = 'Date', ylab = 'Return Value', ylim = c(-500, 2000), pch = 1)

#	legend('topright', legend = c('Our Method', 'Hagneau Method'), col = c('red', 'green'), lty = 1, pch = c(2,1))

	## Prepare data for input to barplot
	breaks <- pretty(range(c(ourValues, baseValues)), n=20)
	D1 <- hist(ourValues, breaks=breaks, plot=FALSE)$counts
	D2 <- hist(baseValues, breaks=breaks, plot=FALSE)$counts
	dat <- rbind(D1, D2)
	colnames(dat) <- paste(breaks[-length(breaks)], breaks[-1], sep="-")

	## Plot it
	barplot(dat, beside=TRUE, space=c(0, 2), las=2)
}
