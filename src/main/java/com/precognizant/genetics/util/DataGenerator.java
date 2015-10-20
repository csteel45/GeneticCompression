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

import java.util.ArrayList;

import com.precognizant.genetics.data.TestData;

/**
 * @author Christopher Steel - Software AG Government Solutions
 *
 * @since Nov 11, 2014 9:09:11 AM
 * @version 1.0
 */
public class DataGenerator {
	ArrayList<Input> inputs;
	public DataGenerator() {
		Rand.init(System.currentTimeMillis());
	}
	
	public void gen(long count, int param) {
		double max = 25;
		for(int i = 0; i < count; i++) {
			double x = Rand.next() * max;
			double y = Rand.next() * max;
			TestData td = new TestData(null, null);
		}
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		DataGenerator dg = new DataGenerator();
		dg.gen(100, 10);
	}
	
	class Input {
		double min;
		double max;
		double drift; 
		double driftCount;
	}
}

