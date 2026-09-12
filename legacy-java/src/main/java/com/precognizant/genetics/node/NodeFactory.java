/*
 * NodeFactory.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
 */
package com.precognizant.genetics.node;

import java.util.ArrayList;

import com.precognizant.genetics.operand.MathOperand;
import com.precognizant.genetics.operand.MathOperand.Operation;
import com.precognizant.genetics.operand.Operand;
import com.precognizant.genetics.util.Rand;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Aug 6, 2016 9:45:29 PM
 */
public class NodeFactory {
	static ArrayList<Operand> operandList = new ArrayList<Operand>();
	
	static {
		// operandList.add(new IfOperand());
		operandList.add(new MathOperand(Operation.PLUS));
//		operandList.add(new MathOperand(Operation.MINUS));
		operandList.add(new MathOperand(Operation.TIMES));
		operandList.add(new MathOperand(Operation.POWER));
//		operandList.add(new MathOperand(Operation.POWPOW));
		//operandList.add(new IfOperand());
	}
	
	/**
	 * Return a random Const or Function Node
	 */
	public static Node getRandomNode() {
		Node node = null;
		if(Rand.nextBoolean())
			node = NodeFactory.getRandomFunctionNode();
		else
			node = NodeFactory.getRandomConstNode();
		
		return node;
	}
	
	/**
	 * Return a Random Operand.
	 */
	public static Operand getRandomOperand() {
		return operandList.get(Rand.nextInt(operandList.size()));
	}

	/**
	 * Return a random Const node.
	 */
	public static Node getRandomConstNode() {
		return new ConstNode(Rand.nextLong());
	}

	/**
	 * Return a random FunctionNode.
	 */
	public static Node getRandomFunctionNode() {
		Node node = null;
		node = new FunctionNode(getRandomConstNode(), getRandomOperand(), getRandomConstNode());

		return node;
	}
	
	public static void main(String[] args) {
		for(int i = 0; i < 100; i++) {
			Node node =  getRandomNode();
			System.out.println("[Random node] = " + node);
		}
	}

}
