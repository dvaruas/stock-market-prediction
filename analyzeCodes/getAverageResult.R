getAverageResult <- function()
{
	fileData <- read.csv('../outputsRun/run1/testResults.csv')

	meanOfErrors <- mean(fileData$error)
	meanOfScp <- mean(fileData$scp)

	print(paste('Error = ', round(meanOfErrors, digits = 3)))
	print(paste('SCP = ', round(meanOfScp, digits = 3)))
}
