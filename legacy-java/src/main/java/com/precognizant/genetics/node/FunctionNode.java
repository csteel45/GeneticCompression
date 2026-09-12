/*
 * FunctionNode.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
 */
package com.precognizant.genetics.node;

import com.precognizant.genetics.operand.Operand;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Jan 29, 2011 2:44:49 AM
 */
public class FunctionNode extends BaseNode {
	protected Operand operand;
	protected Node param1;
	protected Node param2;
	
	public <T extends Node> FunctionNode() {
		this.operand = NodeFactory.getRandomOperand();
		this.param1 = NodeFactory.getRandomNode();
		this.param2 = NodeFactory.getRandomNode();
	}
	
	public <T extends Node> FunctionNode(Node param1, Operand operand, Node param2) {
		System.out.println("FunctionNode(param1, operand, param2) called.");
		this.operand = operand;
		this.param1 = param1;
		this.param2 = param2;
//		System.out.println("Creating function node: " + toString());
//		System.out.println("Eval start");
		value = this.operand.evaluate(param1, param2);
//		System.out.println("Eval end");
	}
	
	/**
	 * @param args
	 * @return
	 */
	public <T extends Node> Number evaluate() {
		value = operand.evaluate(param1, param2);
		return value;
	}

	public Operand getOperand() {
		return operand;
	}
	
	@Override
	public String toString() {
		return "(" + param1 + " " + operand.toString() + " " + param2 + ") = " + evaluate() + " size = " + size();
	}

	public static void main(String[] args) {
		FunctionNode node = new FunctionNode();
		System.out.println("Node = [" + node + "] Evaluate = " + node.evaluate());
	}
	
}
