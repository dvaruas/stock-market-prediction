getPlotTrade <- function()
{
	ourMethodData <- read.csv('../stock_quotes/ourMethodReturn.csv')
	baseData <- read.csv('../stock_quotes/baseReturn.csv')

	dateValues <- as.Date(ourMethodData$date, format = '%d-%m-%y')

	ourValues <- as.numeric(ourMethodData$returnValue)
	baseValues <- as.numeric(baseData$returnValue)

	print(paste('Our Method --> Return rate : ', mean(ourValues), sep = ''))
	print(paste('Base Method --> Return rate : ', mean(baseValues), sep = ''))

	plot(dateValues, ourValues, type = 'o', col = 'red', main = 'Trade Value Comparison', xlab = 'Date', ylab = 'Return Value', pch = 2, ylim = c(-500, 2000))

	par(new = TRUE)

	plot(dateValues, baseValues, type = 'o', col = 'green', main = 'Trade Value Comparison', xlab = 'Date', ylab = 'Return Value', ylim = c(-500, 2000), pch = 1)

	legend('topright', legend = c('Our Method', 'Hagneau Method'), col = c('red', 'green'), lty = 1, pch = c(2,1))
}
