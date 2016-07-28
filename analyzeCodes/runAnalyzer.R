while(TRUE)
{
	cat('\n1. Get Average Results \n2. Plot the ANN error graph \n3. Plot prediction graph of a day \n4. Exit\n')

	choice <- as.numeric(readline('\nEnter your choice : '))

	if(choice == 1)
	{
		source('getAverageResult.R')
		getAverageResult()
	}

	else if(choice == 2)
	{
		source('plotANNError.R')
		getPlotAnn()
	}

	else if(choice == 3)
	{
		source('plotPredictionResults.R')
		getPlotPrediction()
	}

	else if(choice == 4)
	{
		break
	}
	
	else
	{
		print('Wrong Choice..!!')
	}
}
