getPlotAnn <- function()
{
	fileData <- read.csv('../data/myAnn/error_graph_ann.csv')

	iterationValues <- as.numeric(fileData$iteration)
	errorValues <- as.numeric(fileData$error)

	plot(iterationValues, errorValues, type = 'o', main = 'Error graph', xlab = 'Iteration Number', ylab = 'Validation Set Error')
}
