#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <algorithm>

extern "C"
{
	double f1(double x)
	{
		return pow(x, 1 / x - 1);
	}

	double integral(double (*f)(double), double min, double max)
	{
		const int N = 100000;
		double result = 0;
		double delta = (max - min) / N;
		for (int i = 0; i < N; i++)
		{
			result += f(min + (i + 0.5) * delta) * delta;
		}
		return result;
	}
	double costCalculate(int jump, int flow, int spd, int acc, int sta, int pre)
	{
		double cost;
		double cost1, cost2, cost3;
		acc = std::max(acc, 500);
		cost1 = (sqrt((double)jump / 3000) + sqrt((double)flow / 1500)) * (sqrt((double)jump / 3000) + sqrt((double)flow / 1500)) / 4;
		cost1 = cost1 * (1 + (double)pre / 5000) / 1.2;
		cost2 = pow(((double)acc - 500) / 2000, 0.6) * 0.8;
		cost3 = pow(integral(f1, 1, 1 + (double)spd / 1000) / 2, 0.8) * pow(integral(f1, 1, 1 + (double)sta / 1000) / 2, 0.5);
		cost = cost1 + cost2 + cost3;
		return cost;
	}
}