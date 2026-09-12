/*
 * DataGenerator.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
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

