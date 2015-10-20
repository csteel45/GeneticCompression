/*
 * @(#)TestData.java $Date: Jun 9, 2011 10:38:23 PM $
 * 
 * Copyright 2011 FortMoon Consulting, Inc. All Rights Reserved.
 * 
 * This software is the confidential and proprietary information of FortMoon
 * Consulting, Inc. ("Confidential Information"). You shall not disclose such
 * Confidential Information and shall use it only in accordance with the terms
 * of the license agreement you entered into with FortMoon Consulting.
 * 
 * FORTMOON MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
 * SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR
 * NON-INFRINGEMENT. FORTMOON SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY
 * LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS
 * DERIVATIVES.
 * 
 */
package com.precognizant.genetics.data;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Jun 9, 2011 10:38:23 PM
 */
public class TestData {
	private BigInteger output;
	private ArrayList<BigInteger> inputs;
	private long anomalyCount = 0;
	private BigInteger eval;
	
	public TestData(ArrayList<BigInteger> inputs, BigInteger output) {
		this.inputs = inputs;
		this.output = output;
	}
	
	public ArrayList<BigInteger> getInputs() {
		return inputs;
	}
	
	public BigInteger getOutput() {
		return output;
	}

	/**
	 * @return the anomalyCount
	 */
	public long getAnomalyCount() {
		return anomalyCount;
	}

	/**
	 * @param anomalyCount the anomalyCount to set
	 */
	public void setAnomalyCount(long anomalyCount) {
		this.anomalyCount = anomalyCount;
	}

	/**
	 * @return the eval
	 */
	public BigInteger getEval() {
		return eval;
	}

	/**
	 * @param eval the eval to set
	 */
	public void setEval(BigInteger eval) {
		this.eval = eval;
	}

	public String toString() {
		return new String("inputs: " + inputs + " output: " + output + " anomaly count: " + anomalyCount);
	}
}
