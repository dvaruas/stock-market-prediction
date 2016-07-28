getPlotPrediction <- function()
{
	enterDate <- readline('Enter date(dd-mm-yyyy) : ')
	date <- unlist(strsplit(enterDate, '-'))

	index <- 1
	for(dateElement in date)
	{
		if(nchar(dateElement) < 2)
		{
			date[index] <- paste('0', date[index], sep = '')
		}	
		index <- index + 1
	}

	date <- paste(rev(date), collapse = '-')

	fileName <- paste(date, '-d_graph.csv', sep = '')
	totalFilePath <- paste('../outputsRun/run1/', fileName, sep = '')

	fileData <- read.csv(totalFilePath)

	timeValues <- strptime(fileData$Time, format = '%H:%M')
	predictedValues <- as.numeric(fileData$Predicted)
	actualValues <- as.numeric(fileData$Actual)

	minValue <- min(predictedValues, actualValues)
	maxValue <- max(predictedValues, actualValues)
	constantGap <- 100

	dev.new(width = 12, height = 7)
	par(mar = c(5,7,5,2) + 0.1)

	plot(timeValues, predictedValues, type = 'o', col = 'red', main = 'Predicted vs. Actual', ylim = c(minValue - constantGap, maxValue + constantGap), ann = FALSE, pch = 2)

	par(new = TRUE)

	plot(timeValues, actualValues, type = 'o', col = 'green', main = 'Predicted vs. Actual', ylim = c(minValue - constantGap, maxValue + constantGap), ann = FALSE, pch = 1)

	mtext(side = 1, text = 'Time', line = 3)
	mtext(side = 2, text = 'Index Value', line = 3)

	legend('topright', legend = c('Predicted', 'Actual'), col = c('red', 'green'), lty = 1, pch = c(2,1))
}
