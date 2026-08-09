/*
 * TestData.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
 */
package com.precognizant.genetics.data;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Jun 9, 2011 10:38:23 PM
 */
public class TestData {
	private BigDecimal output;
	private ArrayList<BigDecimal> inputs;
	
	public TestData(ArrayList<BigDecimal> inputs, BigDecimal output) {
		this.inputs = inputs;
		this.output = output;
	}
	
	public ArrayList<BigDecimal> getInputs() {
		return inputs;
	}
	
	public BigDecimal getOutput() {
		return output;
	}
	
	public String toString() {
		return new String("inputs: " + inputs + " output: " + output);
	}
}
