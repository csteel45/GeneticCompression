/*
  * @(#)AlgorithmEnvironment.java $Date: Feb 15, 2011 6:28:27 PM $
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
package com.precognizant.genpress;

import java.math.BigInteger;
import java.util.ArrayList;

import com.precognizant.genetics.core.Chromosome;
import com.precognizant.genetics.core.Environment;
import com.precognizant.genetics.core.Gene;
import com.precognizant.genetics.core.Population;
import com.precognizant.genetics.data.TestData;
import com.precognizant.genetics.node.ConstNode;
import com.precognizant.genetics.node.FunctionNodeBase;
import com.precognizant.genetics.node.Node;
import com.precognizant.genetics.node.ParamNode;
import com.precognizant.genetics.operand.MathOperand;
import com.precognizant.genetics.operand.MathOperand.Operation;
import com.precognizant.genetics.util.Rand;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Feb 15, 2011 6:28:27 PM
 */
public class FunctionEnvironment extends Thread implements Environment {

	private static final long serialVersionUID = 1L;
	protected Population population;
	protected float threshold = 1.5f;
	private BigInteger ZERO = BigInteger.ZERO;
	//private static long seed = 45;
	private static long seed = System.currentTimeMillis();
	//private int DOWN = BigInteger.ROUND_DOWN;
	
	static {
		Rand.init(seed);
	}

	/**
	 * @param args
	 */
	public FunctionEnvironment(int populationSize) {
		super("Main");
		setPopulation(new Population(populationSize, 0));
	}

	/** 
	 * Need to initialize better.
	 */
	public void init() {
		int testSize = 1;
		ArrayList<TestData> testData = new ArrayList<TestData>(testSize);
		ArrayList<BigInteger> set = new ArrayList<BigInteger>(0);

		BigInteger result = (new BigInteger("298374234"));
		System.out.println("Result: " + result);

		TestData datum = new TestData(set, result);
		testData.add(datum);

		System.out.println("Test data = " + testData);
		population.setTestData(testData);
	}
		
	public void run() {
		long generation = 0;
		population.sort();
		while(population.calculateFitness().compareTo(BigInteger.ZERO) != 0) {
			population.evolve();
		}

		if(population.calculateFitness().compareTo(ZERO) != 0) {
			System.out.println("\nEnvironment equilibrium complete. Did not find solution after " + generation + " generations.");
		}
		else {
			System.out.println("\nEnvironment equilibrium complete. Found solution in " + generation + " generations.");
		}

		System.out.println("Fittest chromosome = " + population.getFittest().toString());
	}
	
	public void refactorFittest() {
		Chromosome c = population.getFittest();
		ArrayList<Gene> genes = c.getGenes();
		// Create a new ArrayList to hold each of the inputs plus a constant (as the last param)
		ArrayList<BigInteger> paramList = new ArrayList<BigInteger>(population.getTestData().get(0).getInputs().size() + 1);
		ArrayList<String> termList = new ArrayList<String>();

		for(int i = 0; i < (population.getTestData().get(0).getInputs().size() + 1); i++) {
			paramList.add(BigInteger.ZERO);
		}
		
		for(Gene gene : genes) {
			FunctionNodeBase node = (FunctionNodeBase)gene.getNode();
			if(((MathOperand)node.getOperand()).getOperation().equals(Operation.PLUS)) {
				for(Node param : node.getParamList()) {
					if(param instanceof ConstNode) {
						int paramNum = paramList.size() - 1;
						paramList.set(paramNum, paramList.get(paramNum).add(new BigInteger(((Number)((ConstNode)param).getConstant()).toString())));
					}
					else {
						int paramNum = ((ParamNode)param).getParamNumber();
						//System.out.println("Adding one to parmList[" + paramNum + "]"); 
						BigInteger val = paramList.get(paramNum);
						BigInteger newVal = val.add(BigInteger.valueOf(1));
						paramList.set(paramNum, newVal);
						//System.out.println("parmList[" + paramNum + "] now equals: " + paramList.get(((ParamNode)param).paramNumber)); 
					}
				}
			}
			if(((MathOperand)node.getOperand()).getOperation().equals(Operation.MINUS)) {
				Node param = node.getParamList().get(0);
					if(param instanceof ConstNode) {
						int paramNum = paramList.size() - 1;
						paramList.set(paramNum, paramList.get(paramNum).add(new BigInteger(((Number)((ConstNode)param).getConstant()).toString())));
					}
					else {
						int paramNum = ((ParamNode)param).getParamNumber();
						//System.out.println("Adding one to parmList[" + paramNum + "]"); 
						BigInteger val = paramList.get(paramNum);
						BigInteger newVal = val.add(BigInteger.valueOf(1));
						paramList.set(paramNum, newVal);
						//System.out.println("parmList[" + paramNum + "] now equals: " + paramList.get(((ParamNode)param).paramNumber)); 
					}
					param = node.getParamList().get(1);
					if(param instanceof ConstNode) {
						int paramNum = paramList.size() - 1;
						paramList.set(paramNum, paramList.get(paramNum).subtract(new BigInteger(((Number)((ConstNode)param).getConstant()).toString())));
					}
					else {
						int paramNum = ((ParamNode)param).getParamNumber();
						//System.out.println("Subracting one from parmList[" + paramNum + "]"); 
						BigInteger val = paramList.get(paramNum);
						BigInteger newVal = val.subtract(BigInteger.valueOf(1));
						paramList.set(paramNum, newVal);
						//System.out.println("parmList[" + paramNum + "] now equals: " + paramList.get(((ParamNode)param).paramNumber)); 
					}			
			}
			if(((MathOperand)node.getOperand()).getOperation().equals(Operation.TIMES)) {
				Node param0 = node.getParamList().get(0);
				Node param1 = node.getParamList().get(1);
					if(param0 instanceof ConstNode) {
						int paramNum = ((ParamNode)param1).getParamNumber();
						paramList.set(paramNum, paramList.get(paramNum).add(new BigInteger(((Number)((ConstNode)param0).getConstant()).toString())));
					}
					if(param1 instanceof ConstNode) {
						int paramNum = ((ParamNode)param0).getParamNumber();
						paramList.set(paramNum, paramList.get(paramNum).add(new BigInteger(((Number)((ConstNode)param1).getConstant()).toString())));
					}
			}
			if(((MathOperand)node.getOperand()).getOperation().equals(Operation.DIVIDE)) {
				Node param0 = node.getParamList().get(0);
				Node param1 = node.getParamList().get(1);
 				if (param0.equals(param1)) {
					int paramNum = paramList.size() - 1;
					paramList.set(paramNum, paramList.get(paramNum).add(BigInteger.valueOf(1)));
				} 
				else {
					termList.add(param0.toString() + "/" + param1.toString());
				}
			}
		}
		String terms = new String();
		for(String term : termList) {
			terms += term + " + ";
		}
		
/*		System.out.println("Refactored equation: " + 
				terms
				+ paramList.get(0) + "x"
				+ " + " + paramList.get(1) + "y"
				+ " + " + paramList.get(2) + "z"
//				+ " + " + paramList.get(3) + "a"
//				+ " + " + paramList.get(4) + "b"
//				+ " + " + paramList.get(5)
				);
				*/

	}
	
	public Population getPopulation() {
		return population;
	}


	public void setPopulation(Population population) {
		this.population = population;
	}


	public float getThreshold() {
		return threshold;
	}


	public void setThreshold(float threshold) {
		this.threshold = threshold;
	}


	public static void main(String args[]) {
		FunctionEnvironment env = new FunctionEnvironment(48);
		//env.init();
		env.init();
		env.start();
		System.out.println("Environment started.");
	}
}
