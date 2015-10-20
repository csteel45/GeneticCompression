/*
 * @(#)NodeTreeImpl.java $Date: Feb 15, 2011 6:28:27 PM $
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
package com.precognizant.genetics.node;

import java.math.BigInteger;
import java.util.ArrayList;

import com.precognizant.genetics.operand.MathOperand;
import com.precognizant.genetics.operand.MathOperand.Operation;
import com.precognizant.genetics.operand.Operand;
import com.precognizant.genetics.operand.RandomOperand;
import com.precognizant.genetics.util.Rand;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 * 
 * @since Jan 29, 2011 8:58:43 AM
 */
public class NodeTreeImpl implements NodeTree {
	static ArrayList<Operand> operandList = new ArrayList<Operand>();
	private static int treeDepth = 0;
	private static int treeDepthLimit = 5;
	private RandomOperand randomOp = new RandomOperand(); 

	static {
		// operandList.add(new IfOperand());
		operandList.add(new MathOperand(Operation.PLUS));
		operandList.add(new MathOperand(Operation.MINUS));
		operandList.add(new MathOperand(Operation.TIMES));
		operandList.add(new MathOperand(Operation.POWER));
		operandList.add(new MathOperand(Operation.POWPOW));
		//operandList.add(new IfOperand());
	}

	public NodeTreeImpl() {
	}

	public Node buildTree(int arg1, int arg2) {
		Node rootNode = getNode(arg1, arg2);
		return rootNode;
	}

	/**
	 * @return
	 */
	public Node getNode(int paramSize) {
		Node node = null;
		// node is a FunctionNode
		Operand operand = operandList.get(Rand.nextInt(operandList.size()));
		ArrayList<Node> params = new ArrayList<Node>();
		// I think we need to add something to the list before we can call set. Not sure why.
		//System.out.println("Params size = " + params.size());
		int rand = 0;
		for (int i = 0; i < 2; i++) {
			params.add(new ConstNode(Rand.nextInt(1000)));
		}
		node = new FunctionNodeBase(operand, params);

		return node;
	}

	public Node getNode(int arg1, int arg2) {
		Node node = null;
		treeDepth++;
		if(treeDepth < treeDepthLimit) {
			System.out.println("Exceeded tree depth limit.");
		}
		if (Rand.nextBoolean() && treeDepth < treeDepthLimit) {
			// node is a FunctionNode
			Operand operand = operandList.get(Rand.nextInt(operandList.size()));
			ArrayList<Node> params = new ArrayList<Node>();
			int rand = 5;
			//int lastRand = 5;
			for (int i = 0; i < 2; i++) {
				rand = Rand.nextInt(4);
				if (rand == 0) // Use the first argument as a ConstNode
					params.add(new ConstNode(arg1));
				if (rand == 1) // Use the second argument as a ConstNode
					params.add(new ConstNode(arg2));
				if (rand == 2) { // Use a random number as a ConstNode
					ConstNode cn = new ConstNode(Rand.nextInt(100));
					params.add(cn);
					System.out.println("Created a const node = " + cn);
				}
				if (rand > 2) // Use both args to create a FunctionNode
					params.add(getNode(arg1, arg2));
			}
			node = new FunctionNodeBase(operand, params);
		} else {
			// node is a ConstantNode
			node = new ConstNode(Rand.nextInt(10));
		}
		treeDepth--;
		return node;
	}

	public static void main(String[] argumentss) {
		System.out.println("Long MAX = " + Long.MAX_VALUE);
		//BigInteger num = new BigInteger("12345678901234567899");
		BigInteger num = BigInteger.valueOf(Long.MAX_VALUE);
		System.out.println("Num size = " + num.bitLength());
	}

}
