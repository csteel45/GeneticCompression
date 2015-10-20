/*
 * Copyright 2014 Software AG Government Solutions
 * All Rights Reserved.
 *
 * This software is the confidential and proprietary information of Softwre AG
 * Government Solutions ("Confidential Information").  You shall not
 * disclose such Confidential Information and shall use it only in
 * accordance with the terms of the license agreement you entered into
 * with Software AG Government Soltuions.
 *
 * SOFTWARE AG GS MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
 * SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
 * PURPOSE, OR NON-INFRINGEMENT. SOFTWARE AG GS SHALL NOT BE LIABLE FOR ANY DAMAGES
 * SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
 * THIS SOFTWARE OR ITS DERIVATIVES.
 */

package com.precognizant.genetics.util;

import java.util.Arrays;

/**
 * @author Christopher Steel - Software AG Government Solutions
 * 
 * @since Nov 7, 2014 2:36:57 PM
 * @version 1.0
 */

public class Statistics {

	public static double getMean(double[] data) {
		double sum = 0.0;
		for (double a : data)
			sum += a;
		return sum / data.length;
	}

	public static double getVariance(double[] data) {
		double mean = getMean(data);
		double temp = 0;
		for (double a : data)
			temp += (mean - a) * (mean - a);
		return temp / data.length;
	}

	public static double getStdDev(double[] data) {
		return Math.sqrt(getVariance(data));
	}

	public static double getMedian(double[] data) {
		double[] b = new double[data.length];
		System.arraycopy(data, 0, b, 0, b.length);
		Arrays.sort(b);

		if (data.length % 2 == 0) {
			return (b[(b.length / 2) - 1] + b[b.length / 2]) / 2.0;
		} else {
			return b[b.length / 2];
		}
	}
	
	public static void main(String[] args) {
		double[] data = {3.0, 4.0, 3.5, 3.7, 2.9, 3.8, 3.55, 3.7, 3.62, 3.45, 3.39, 4.02, 7.5};
		System.out.println("mean: " + getMean(data) + " Variance: " + getVariance(data) + " StdDev: " + getStdDev(data) + " Median: " + getMedian(data));
	}
}
